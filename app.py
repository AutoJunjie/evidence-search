import concurrent.futures
import json
import os
import re
import threading
from typing import Generator, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import requests

# Constants
SERPER_SEARCH_ENDPOINT = "https://google.serper.dev/search"
REFERENCE_COUNT = 8
DEFAULT_SEARCH_ENGINE_TIMEOUT = 5

_default_query = "Who said 'live long and prosper'?"

_rag_query_text = """
You are a large language AI assistant built by Evidence Search. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

Here are the set of contexts:

{context}

Remember, don't blindly repeat the contexts verbatim. And here is the user question:
"""

_more_questions_prompt = """
You are a helpful assistant that helps the user to ask related questions, based on user's original question and the related contexts. Please identify worthwhile topics that can be follow-ups, and write questions no longer than 20 words each. Please make sure that specifics, like events, names, locations, are included in follow up questions so they can be asked standalone. For example, if the original question asks about "the Manhattan project", in the follow up question, do not just say "the project", but use the full name "the Manhattan project". Your related questions must be in the same language as the original question.

Here are the contexts of the question:

{context}

Remember, based on the original question and related contexts, suggest three such further questions. Do NOT repeat the original question. Each related question should be no longer than 20 words. Here is the original question:
"""

stop_words = ["<|im_end|>", "[End]", "[end]", "\nReferences:\n", "\nSources:\n", "End."]


def search_with_serper(query: str, subscription_key: str):
    payload = json.dumps({
        "q": query,
        "num": REFERENCE_COUNT if REFERENCE_COUNT % 10 == 0 else (REFERENCE_COUNT // 10 + 1) * 10,
    })
    headers = {"X-API-KEY": subscription_key, "Content-Type": "application/json"}
    response = requests.post(
        SERPER_SEARCH_ENDPOINT, headers=headers, data=payload, timeout=DEFAULT_SEARCH_ENGINE_TIMEOUT
    )
    if not response.ok:
        raise HTTPException(response.status_code, "Search engine error.")
    json_content = response.json()
    try:
        contexts = []
        if json_content.get("knowledgeGraph"):
            url = json_content["knowledgeGraph"].get("descriptionUrl") or json_content["knowledgeGraph"].get("website")
            snippet = json_content["knowledgeGraph"].get("description")
            if url and snippet:
                contexts.append({"name": json_content["knowledgeGraph"].get("title", ""), "url": url, "snippet": snippet})
        if json_content.get("answerBox"):
            url = json_content["answerBox"].get("url")
            snippet = json_content["answerBox"].get("snippet") or json_content["answerBox"].get("answer")
            if url and snippet:
                contexts.append({"name": json_content["answerBox"].get("title", ""), "url": url, "snippet": snippet})
        contexts += [{"name": c["title"], "url": c["link"], "snippet": c.get("snippet", "")} for c in json_content["organic"]]
        return contexts[:REFERENCE_COUNT]
    except KeyError:
        return []


app = FastAPI()

thread_local = threading.local()


def get_openai_client():
    try:
        return thread_local.client
    except AttributeError:
        import openai
        thread_local.client = openai.OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ["OPENAI_API_KEY"],
            timeout=httpx.Timeout(connect=10, read=120, write=120, pool=10),
        )
        return thread_local.client


executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)
model = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
should_do_related_questions = os.environ.get("RELATED_QUESTIONS", "true").lower() == "true"


def get_related_questions(query: str, contexts: list) -> List[str]:
    try:
        response = get_openai_client().chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _more_questions_prompt.format(context="\n\n".join([c["snippet"] for c in contexts]))},
                {"role": "user", "content": query},
            ],
            max_tokens=512,
        )
        content = response.choices[0].message.content or ""
        questions = [q.strip() for q in content.split("\n") if q.strip() and "?" in q]
        return questions[:3]
    except Exception:
        return []


def raw_stream_response(contexts, llm_response, related_questions_future) -> Generator[str, None, None]:
    yield json.dumps(contexts)
    yield "\n\n__LLM_RESPONSE__\n\n"
    if not contexts:
        yield "(The search engine returned nothing for this query. Please take the answer with a grain of salt.)\n\n"
    for chunk in llm_response:
        if chunk.choices:
            yield chunk.choices[0].delta.content or ""
    if related_questions_future is not None:
        related_questions = related_questions_future.result()
        yield "\n\n__RELATED_QUESTIONS__\n\n"
        yield json.dumps(related_questions)


class QueryRequest(BaseModel):
    query: str
    search_uuid: str
    generate_related_questions: Optional[bool] = True


@app.post("/query")
def query_function(request: QueryRequest) -> StreamingResponse:
    query = request.query or _default_query
    query = re.sub(r"\[/?INST\]", "", query)
    
    contexts = search_with_serper(query, os.environ["SERPER_SEARCH_API_KEY"])
    
    system_prompt = _rag_query_text.format(
        context="\n\n".join([f"[[citation:{i+1}]] {c['snippet']}" for i, c in enumerate(contexts)])
    )
    
    try:
        client = get_openai_client()
        llm_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            max_tokens=1024,
            stop=stop_words,
            stream=True,
            temperature=0.9,
        )
        related_questions_future = None
        if should_do_related_questions and request.generate_related_questions:
            related_questions_future = executor.submit(get_related_questions, query, contexts)
    except Exception:
        raise HTTPException(503, "Internal server error.")
    
    return StreamingResponse(raw_stream_response(contexts, llm_response, related_questions_future), media_type="text/html")


@app.get("/")
def index():
    return RedirectResponse(url="/ui/index.html")


# Mount static files (frontend build output) if directory exists
import os.path
if os.path.isdir("ui"):
    app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
