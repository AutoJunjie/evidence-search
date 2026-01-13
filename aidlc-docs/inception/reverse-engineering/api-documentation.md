# API Documentation

## REST APIs

### POST /query
- **Method**: POST
- **Path**: `/query`
- **Purpose**: 执行RAG搜索查询，返回流式响应
- **Request**:
  ```json
  {
    "query": "string",           // 用户查询
    "search_uuid": "string",     // 搜索结果UUID（用于缓存）
    "generate_related_questions": true  // 是否生成相关问题（可选）
  }
  ```
- **Response**: StreamingResponse (text/html)
  ```
  [JSON array of sources]
  
  __LLM_RESPONSE__
  
  [LLM generated answer with citations]
  
  __RELATED_QUESTIONS__
  
  [JSON array of related questions]
  ```

### GET /
- **Method**: GET
- **Path**: `/`
- **Purpose**: 重定向到UI首页
- **Response**: RedirectResponse → `/ui/index.html`

### Static Files /ui/*
- **Method**: GET
- **Path**: `/ui/*`
- **Purpose**: 提供前端静态文件
- **Response**: 静态文件内容

## Internal APIs

### Search Functions

#### search_with_bing(query, subscription_key)
- **Parameters**:
  - `query: str` - 搜索查询
  - `subscription_key: str` - Bing API密钥
- **Return Type**: `List[dict]` - 搜索结果列表
- **Fields**: `name`, `url`, `snippet`

#### search_with_google(query, subscription_key, cx)
- **Parameters**:
  - `query: str` - 搜索查询
  - `subscription_key: str` - Google API密钥
  - `cx: str` - 自定义搜索引擎ID
- **Return Type**: `List[dict]` - 搜索结果列表

#### search_with_serper(query, subscription_key)
- **Parameters**:
  - `query: str` - 搜索查询
  - `subscription_key: str` - Serper API密钥
- **Return Type**: `List[dict]` - 搜索结果列表（标准化格式）

#### search_with_searchapi(query, subscription_key)
- **Parameters**:
  - `query: str` - 搜索查询
  - `subscription_key: str` - SearchApi API密钥
- **Return Type**: `List[dict]` - 搜索结果列表（标准化格式）

### RAG Class Methods

#### RAG.init()
- **Purpose**: 初始化Photon配置
- **Actions**:
  - 登录Lepton workspace
  - 根据BACKEND环境变量配置搜索函数
  - 初始化LLM模型名称
  - 创建线程池执行器
  - 初始化KV存储

#### RAG.local_client()
- **Return Type**: `openai.OpenAI`
- **Purpose**: 获取线程本地的OpenAI客户端

#### RAG.get_related_questions(query, contexts)
- **Parameters**:
  - `query: str` - 原始查询
  - `contexts: List[dict]` - 搜索上下文
- **Return Type**: `List[str]` - 相关问题列表（最多5个）

## Data Models

### Source (Frontend Interface)
```typescript
interface Source {
  id: string;
  name: string;
  url: string;
  isFamilyFriendly: boolean;
  displayUrl: string;
  snippet: string;
  deepLinks: { snippet: string; name: string; url: string }[];
  dateLastCrawled: string;
  cachedPageUrl: string;
  language: string;
  primaryImageOfPage?: {
    thumbnailUrl: string;
    width: number;
    height: number;
    imageId: string;
  };
  isNavigational: boolean;
}
```

### Relate (Frontend Interface)
```typescript
type Relate = string;
```

### Search Context (Backend)
```python
# 标准化的搜索结果格式
{
    "name": str,      # 页面标题
    "url": str,       # 页面URL
    "snippet": str    # 页面摘要
}
```

## Streaming Response Protocol

响应分为三个部分，用特殊分隔符分隔：

1. **Sources Section**: JSON数组，包含搜索结果
2. **LLM Response Section**: 以 `__LLM_RESPONSE__` 开始，包含LLM生成的答案
3. **Related Questions Section**: 以 `__RELATED_QUESTIONS__` 开始，包含JSON数组的相关问题

```
[{"name":"...", "url":"...", "snippet":"..."}, ...]

__LLM_RESPONSE__

Based on the search results, [citation:1] ...

__RELATED_QUESTIONS__

["Question 1?", "Question 2?", "Question 3?"]
```
