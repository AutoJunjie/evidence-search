# Code Structure

## Build System

### Backend
- **Type**: Python (leptonai photon)
- **Configuration**: 无requirements.txt，依赖在代码中声明 (`requirement_dependency`)

### Frontend
- **Type**: npm/Next.js
- **Configuration**: `web/package.json`

## Key Classes/Modules

### Backend Module Hierarchy

```
search_with_lepton.py
+-- Constants (配置常量)
|   +-- BING_SEARCH_V7_ENDPOINT
|   +-- GOOGLE_SEARCH_ENDPOINT
|   +-- SERPER_SEARCH_ENDPOINT
|   +-- SEARCHAPI_SEARCH_ENDPOINT
|   +-- REFERENCE_COUNT
|   +-- _rag_query_text (RAG提示词)
|   +-- _more_questions_prompt (相关问题提示词)
|   +-- stop_words
|
+-- Search Functions (搜索引擎封装)
|   +-- search_with_bing()
|   +-- search_with_google()
|   +-- search_with_serper()
|   +-- search_with_searchapi()
|
+-- RAG Class (Photon子类)
    +-- init() - 初始化配置
    +-- local_client() - 获取OpenAI客户端
    +-- get_related_questions() - 生成相关问题
    +-- _raw_stream_response() - 原始流式响应生成器
    +-- stream_and_upload_to_kv() - 流式响应并缓存
    +-- query_function() - 主查询处理器 (POST /query)
    +-- ui() - 静态文件服务
    +-- index() - 根路径重定向
```

### Frontend Module Hierarchy

```
web/src/app/
+-- layout.tsx (根布局)
+-- page.tsx (首页)
+-- globals.css (全局样式)
+-- search/
|   +-- page.tsx (搜索结果页)
+-- components/
|   +-- search.tsx (搜索输入框)
|   +-- result.tsx (结果容器)
|   +-- answer.tsx (答案展示，含Markdown渲染)
|   +-- sources.tsx (来源列表)
|   +-- relates.tsx (相关问题)
|   +-- title.tsx (标题)
|   +-- wrapper.tsx (通用包装器)
|   +-- skeleton.tsx (加载骨架)
|   +-- popover.tsx (弹窗组件)
|   +-- logo.tsx (Logo)
|   +-- footer.tsx (页脚)
|   +-- preset-query.tsx (预设查询)
+-- interfaces/
|   +-- source.ts (Source类型定义)
|   +-- relate.ts (Relate类型定义)
+-- utils/
    +-- cn.ts (className工具)
    +-- fetch-stream.ts (流式fetch封装)
    +-- parse-streaming.ts (流式响应解析)
    +-- get-search-url.ts (URL生成)
```

## Existing Files Inventory

### Backend Files
- `search_with_lepton.py` - 主后端服务，包含RAG逻辑、搜索引擎集成、LLM调用

### Frontend Files
- `web/src/app/layout.tsx` - Next.js根布局
- `web/src/app/page.tsx` - 首页
- `web/src/app/search/page.tsx` - 搜索结果页
- `web/src/app/components/search.tsx` - 搜索输入组件
- `web/src/app/components/result.tsx` - 结果容器组件
- `web/src/app/components/answer.tsx` - 答案展示组件
- `web/src/app/components/sources.tsx` - 来源列表组件
- `web/src/app/components/relates.tsx` - 相关问题组件
- `web/src/app/utils/parse-streaming.ts` - 流式响应解析
- `web/src/app/utils/fetch-stream.ts` - 流式fetch工具
- `web/src/app/utils/get-search-url.ts` - URL生成工具
- `web/src/app/interfaces/source.ts` - Source接口定义
- `web/src/app/interfaces/relate.ts` - Relate接口定义

## Design Patterns

### Streaming Response Pattern
- **Location**: `RAG.query_function()`, `parse-streaming.ts`
- **Purpose**: 实现流式输出，提升用户体验
- **Implementation**: 使用Generator和StreamingResponse，前端通过ReadableStream解析

### Factory Pattern (Search Engine)
- **Location**: `RAG.init()`
- **Purpose**: 根据BACKEND环境变量选择搜索引擎
- **Implementation**: 将搜索函数赋值给`self.search_function`

### RAG Pattern
- **Location**: `RAG.query_function()`
- **Purpose**: 检索增强生成
- **Implementation**: 搜索结果作为context注入到LLM提示词中

## Critical Dependencies

### Lepton AI Dependencies (需要移除)
- **leptonai**: Photon框架、KV存储、Client、workspace API
- **Version**: 未指定
- **Usage**: 
  - `Photon` - Web框架基类
  - `KV` - 键值存储
  - `Client` - Lepton API客户端
  - `StaticFiles` - 静态文件服务
  - `WorkspaceInfoLocalRecord` - workspace token获取
  - `tool.get_tools_spec` - 函数调用规范生成
- **Purpose**: 整个后端框架和基础设施

### OpenAI
- **Version**: 未指定
- **Usage**: LLM API调用（OpenAI兼容格式）
- **Purpose**: 生成答案和相关问题

### FastAPI (通过leptonai)
- **Usage**: HTTP路由、请求处理
- **Purpose**: Web API框架

### httpx
- **Usage**: HTTP客户端超时配置
- **Purpose**: OpenAI客户端配置

### requests
- **Usage**: 搜索引擎API调用
- **Purpose**: HTTP请求
