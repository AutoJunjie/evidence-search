# Evidence Search

A conversational search engine powered by RAG (Retrieval-Augmented Generation).

## Features
- Search powered by Serper API (Google Search)
- AI-generated answers with citations using Strands Agents SDK
- Support for multiple LLM providers (Bedrock, Anthropic, OpenAI, Gemini)
- Related questions suggestions
- Docker containerized deployment

> **Note**: This project now uses Strands Agents SDK instead of direct OpenAI integration. See [STRANDS_MIGRATION.md](STRANDS_MIGRATION.md) for migration details.

## Quick Start (Docker)

1. Create `.env` file:
```bash
# Using Bedrock (default, recommended)
AWS_BEDROCK_API_KEY=your_bedrock_api_key
SERPER_SEARCH_API_KEY=your_serper_api_key
MODEL_PROVIDER=bedrock
LLM_MODEL=anthropic.claude-sonnet-4-20250514-v1:0

# Or using OpenAI
# OPENAI_API_KEY=your_openai_api_key
# SERPER_SEARCH_API_KEY=your_serper_api_key
# MODEL_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
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

# Using Bedrock (default)
export AWS_BEDROCK_API_KEY=your_bedrock_api_key
export SERPER_SEARCH_API_KEY=your_serper_api_key
export MODEL_PROVIDER=bedrock
python app_strands.py

# Or using OpenAI
# export OPENAI_API_KEY=your_openai_api_key
# export SERPER_SEARCH_API_KEY=your_serper_api_key
# export MODEL_PROVIDER=openai
# pip install 'strands-agents[openai]'
# python app_strands.py
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
| OPENAI_BASE_URL | No | Custom OpenAI API endpoint |
| LLM_MODEL | No | Model name (default: gpt-3.5-turbo) |
| RELATED_QUESTIONS | No | Generate related questions (default: true) |

## License
Apache 2.0
