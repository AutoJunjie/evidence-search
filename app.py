import concurrent.futures
import json
import os
import re
import threading
from typing import Generator, List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx
import requests

# Strands SDK imports
from strands import Agent
from strands.models.openai import OpenAIModel
from strands_tools import calculator, python_repl, http_request


# Structured output model for related questions
class RelatedQuestions(BaseModel):
    """相关问题的结构化输出模型"""
    questions: List[str] = Field(
        description="3-5 related follow-up questions, each no longer than 20 words",
        min_length=1,
        max_length=5
    )

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

stop_words = ["<|im_end|>", "[End]", "[end]", "\nReferences:\n"]


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

# Model configuration
model_id = os.environ.get("LLM_MODEL", "gpt-4o-mini")
should_do_related_questions = os.environ.get("RELATED_QUESTIONS", "true").lower() == "true"


def get_main_response_agent():
    """Get or create the main response Strands Agent with community tools."""
    try:
        return thread_local.main_agent
    except AttributeError:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        model = OpenAIModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params={
                "max_tokens": 1024,
                "temperature": 0.9,
                "stop": stop_words[:4],  # OpenAI max 4 stop sequences
            }
        )
        
        thread_local.main_agent = Agent(
            model=model,
            tools=[calculator, python_repl, http_request],
        )
        return thread_local.main_agent


def get_related_questions_agent():
    """Get or create the related questions Strands Agent."""
    try:
        return thread_local.related_agent
    except AttributeError:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        model = OpenAIModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params={
                "max_tokens": 512,
                "temperature": 0.7,
            }
        )
        
        thread_local.related_agent = Agent(model=model)
        return thread_local.related_agent


executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)


def get_related_questions(query: str, contexts: list) -> List[str]:
    """
    Gets related questions based on the query and context using Strands structured output.
    """
    try:
        # Build context string
        context_str = "\n\n".join([c.get("snippet", "") for c in contexts])
        
        # Build system prompt
        system_prompt = _more_questions_prompt.format(context=context_str)
        
        # Create agent with system prompt
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        model = OpenAIModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params={
                "max_tokens": 512,
                "temperature": 0.7,
            }
        )
        
        agent = Agent(model=model, system_prompt=system_prompt)
        
        # Call agent with structured output
        result = agent(query, structured_output_model=RelatedQuestions)
        
        # Return questions list (same format as before)
        return result.structured_output.questions[:5]
        
    except Exception as e:
        print(f"Error generating related questions: {e}")
        return []


async def raw_stream_response(contexts, agent, system_prompt, query, related_questions_future):
    yield json.dumps(contexts)
    yield "\n\n__LLM_RESPONSE__\n\n"
    if not contexts:
        yield "(The search engine returned nothing for this query. Please take the answer with a grain of salt.)\n\n"
    
    # Stream response from Strands Agent using async streaming
    try:
        # Combine system prompt and query
        full_prompt = f"{system_prompt}\n\n{query}"
        
        # Use stream_async for async streaming
        async for event in agent.stream_async(full_prompt):
            # Strands stream_async yields event dictionaries with nested structure
            if isinstance(event, dict):
                # Extract text from contentBlockDelta events
                if "event" in event and "contentBlockDelta" in event["event"]:
                    delta = event["event"]["contentBlockDelta"].get("delta", {})
                    if "text" in delta:
                        yield delta["text"]
            elif isinstance(event, str):
                yield event
    except Exception as e:
        yield f"Error generating response: {str(e)}"
    
    # Wait for related questions to complete
    if related_questions_future is not None:
        try:
            # Use asyncio.wrap_future to properly await ThreadPoolExecutor future
            import asyncio
            related_questions = await asyncio.wrap_future(related_questions_future)
            
            # Convert to {question: string}[] format for frontend
            related_objects = [{"question": q} for q in related_questions]
            yield "\n\n__RELATED_QUESTIONS__\n\n"
            yield json.dumps(related_objects)
        except Exception as e:
            # If related questions fail, still send empty array
            yield "\n\n__RELATED_QUESTIONS__\n\n"
            yield json.dumps([])


class QueryRequest(BaseModel):
    query: str
    search_uuid: str
    generate_related_questions: Optional[bool] = True


@app.post("/query")
def query_function(request: QueryRequest) -> StreamingResponse:
    query = request.query or _default_query
    query = re.sub(r"\[/?INST\]", "", query)
    
    serper_key = os.environ.get("SERPER_SEARCH_API_KEY")
    if not serper_key:
        raise HTTPException(500, "SERPER_SEARCH_API_KEY environment variable is required")
    contexts = search_with_serper(query, serper_key)
    
    system_prompt = _rag_query_text.format(
        context="\n\n".join([f"[[citation:{i+1}]] {c['snippet']}" for i, c in enumerate(contexts)])
    )
    
    try:
        agent = get_main_response_agent()
        related_questions_future = None
        if should_do_related_questions and request.generate_related_questions:
            related_questions_future = executor.submit(get_related_questions, query, contexts)
    except Exception as e:
        raise HTTPException(503, "Failed to initialize Strands Agent")
    
    return StreamingResponse(
        raw_stream_response(contexts, agent, system_prompt, query, related_questions_future),
        media_type="text/html"
    )


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
