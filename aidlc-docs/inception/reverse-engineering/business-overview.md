# Business Overview

## Business Context Diagram

```
+------------------+     +-------------------+     +------------------+
|                  |     |                   |     |                  |
|   User/Browser   |---->|  Search Engine    |---->|  Search APIs     |
|                  |     |  (RAG System)     |     |  (Bing/Google)   |
|                  |     |                   |     |                  |
+------------------+     +--------+----------+     +------------------+
                                  |
                                  v
                         +--------+----------+
                         |                   |
                         |   LLM Service     |
                         |   (Lepton/OpenAI) |
                         |                   |
                         +-------------------+
```

## Business Description

- **Business Description**: 这是一个基于RAG（检索增强生成）的对话式搜索引擎。用户输入问题后，系统会从搜索引擎获取相关网页内容作为上下文，然后使用LLM生成带有引用的答案，并推荐相关问题。

- **Business Transactions**:
  1. **搜索查询处理**: 用户提交问题 → 调用搜索API获取参考资料 → LLM生成答案 → 返回带引用的回答
  2. **相关问题生成**: 基于原始问题和上下文，LLM生成3个相关的后续问题
  3. **结果缓存**: 搜索结果通过UUID存储在KV存储中，支持分享和重复访问

- **Business Dictionary**:
  - **RAG (Retrieval-Augmented Generation)**: 检索增强生成，结合搜索结果和LLM生成答案
  - **Citation**: 引用标记，格式为 `[citation:N]`，指向搜索结果来源
  - **Context**: 从搜索引擎获取的网页摘要，作为LLM生成答案的参考
  - **Related Questions**: 基于当前问题和上下文生成的相关后续问题

## Component Level Business Descriptions

### Backend (search_with_lepton.py)
- **Purpose**: 提供RAG搜索服务的核心业务逻辑
- **Responsibilities**:
  - 接收用户查询请求
  - 调用搜索引擎API获取参考资料
  - 构建RAG提示词并调用LLM
  - 流式返回答案和相关问题
  - 缓存搜索结果到KV存储

### Frontend (web/)
- **Purpose**: 提供用户交互界面
- **Responsibilities**:
  - 展示搜索输入框
  - 流式显示LLM生成的答案
  - 展示引用来源和相关问题
  - 支持通过URL分享搜索结果
