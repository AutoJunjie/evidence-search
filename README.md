# Evidence Search

A conversational search engine powered by RAG (Retrieval-Augmented Generation) and Strands Agents SDK.

## Features
- Search powered by Serper API (Google Search)
- AI-generated answers with citations using Strands Agents SDK
- Structured output for related questions generation
- Built-in tools: calculator, python_repl, http_request
- Docker containerized deployment

## Quick Start (Docker)

1. Create `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key
SERPER_SEARCH_API_KEY=your_serper_api_key
```

2. Run:
```bash
docker-compose up --build
```

3. Open http://localhost:8080

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_api_key
export SERPER_SEARCH_API_KEY=your_serper_api_key
python app.py
```

### Frontend (Development)
```bash
cd web
npm install
npm run dev
```

### Frontend (Production Build)
```bash
cd web
npm install
npm run build
```
The build output will be in `ui/` directory.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| OPENAI_API_KEY | Yes | OpenAI API key |
| SERPER_SEARCH_API_KEY | Yes | Serper API key |
| LLM_MODEL | No | Model name (default: gpt-4o-mini) |
| RELATED_QUESTIONS | No | Generate related questions (default: true) |

## License
Apache 2.0
