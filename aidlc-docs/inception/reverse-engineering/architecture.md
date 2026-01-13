# System Architecture

## System Overview

这是一个基于RAG的对话式搜索引擎，由Python后端和Next.js前端组成。后端使用Lepton AI的Photon框架，依赖Lepton的LLM服务和KV存储。

## Architecture Diagram

```
+------------------------------------------------------------------+
|                         Frontend (Next.js)                        |
|  +------------+  +------------+  +------------+  +------------+   |
|  |   Search   |  |   Result   |  |   Answer   |  |  Sources   |   |
|  | Component  |  | Component  |  | Component  |  | Component  |   |
|  +------------+  +------------+  +------------+  +------------+   |
+------------------------------------------------------------------+
         |                    |
         | HTTP POST /query   | Static Files
         v                    v
+------------------------------------------------------------------+
|                      Backend (Python/FastAPI)                     |
|  +------------------+  +------------------+  +------------------+ |
|  |   RAG Photon     |  |  Search Engine   |  |   LLM Client     | |
|  |   (Main Class)   |  |  Functions       |  |   (OpenAI API)   | |
|  +------------------+  +------------------+  +------------------+ |
|           |                    |                     |            |
|           v                    v                     v            |
|  +------------------+  +------------------+  +------------------+ |
|  |   Lepton KV      |  | Bing/Google/     |  | Lepton LLM       | |
|  |   (Cache)        |  | Serper/SearchAPI |  | Service          | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
```

## Component Descriptions

### RAG Photon (Backend Main Class)
- **Purpose**: 核心RAG服务，处理搜索查询和生成答案
- **Responsibilities**:
  - 初始化搜索引擎和LLM客户端
  - 处理 `/query` POST请求
  - 流式返回搜索结果、LLM答案和相关问题
  - 管理KV缓存
- **Dependencies**: leptonai, openai, httpx, fastapi
- **Type**: Application

### Search Engine Functions
- **Purpose**: 封装不同搜索引擎的API调用
- **Responsibilities**:
  - `search_with_bing()` - Bing搜索
  - `search_with_google()` - Google Programmable Search
  - `search_with_serper()` - Serper API
  - `search_with_searchapi()` - SearchApi.io
- **Dependencies**: requests
- **Type**: Application

### Frontend (Next.js)
- **Purpose**: 用户界面
- **Responsibilities**:
  - 搜索输入和提交
  - 流式解析和显示结果
  - 引用弹窗展示
- **Dependencies**: next, react, react-markdown
- **Type**: Application

## Data Flow

```
User Query
    |
    v
+-------------------+
| Frontend: Search  |
| Component         |
+-------------------+
    |
    | POST /query {query, search_uuid}
    v
+-------------------+
| Backend: Check KV |
| for cached result |
+-------------------+
    |
    | (if not cached)
    v
+-------------------+
| Search Engine API |
| (Bing/Google/etc) |
+-------------------+
    |
    | contexts (snippets)
    v
+-------------------+
| LLM: Generate     |
| Answer with RAG   |
+-------------------+
    |
    | streaming response
    v
+-------------------+
| Frontend: Parse   |
| and Display       |
+-------------------+
```

## Integration Points

### External APIs
- **Bing Search API**: `https://api.bing.microsoft.com/v7.0/search`
- **Google Custom Search**: `https://customsearch.googleapis.com/customsearch/v1`
- **Serper API**: `https://google.serper.dev/search`
- **SearchApi.io**: `https://www.searchapi.io/api/v1/search`

### LLM Services (Current - Lepton)
- **Lepton LLM**: `https://{model}.lepton.run/api/v1/` (OpenAI兼容API)
- **Lepton Search API**: `https://search-api.lepton.run/` (LEPTON backend模式)

### Storage (Current - Lepton)
- **Lepton KV**: 用于缓存搜索结果，支持结果分享

## Infrastructure Components

### Current (Lepton SaaS)
- **Lepton Photon**: Web框架和部署平台
- **Lepton KV**: 键值存储服务
- **Lepton LLM**: 托管的LLM服务

### Deployment Model
- 当前设计为部署在Lepton AI平台
- 使用 `lep photon run` 命令部署
- 支持环境变量配置不同的搜索后端
