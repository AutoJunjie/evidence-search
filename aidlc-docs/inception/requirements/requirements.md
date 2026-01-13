# Requirements Document

## Intent Analysis Summary

- **User Request**: 将项目改造成完全不依赖leptonai的本地独立运行项目
- **Request Type**: Migration（技术迁移）
- **Scope Estimate**: System-wide（影响整个后端系统）
- **Complexity Estimate**: Moderate（中等复杂度）

## Functional Requirements

### FR-1: 移除Lepton框架依赖
- **描述**: 将后端从leptonai.Photon框架迁移到标准FastAPI
- **验收标准**: 
  - 代码中不再import任何leptonai模块
  - 使用FastAPI提供HTTP API服务
  - 保持原有API接口兼容（POST /query）

### FR-2: LLM服务集成
- **描述**: 使用OpenAI API替代Lepton LLM服务
- **验收标准**:
  - 支持通过`OPENAI_API_KEY`环境变量配置
  - 支持通过`OPENAI_BASE_URL`配置自定义endpoint（可选）
  - 支持通过`LLM_MODEL`配置模型名称

### FR-3: 移除缓存功能
- **描述**: 移除Lepton KV缓存，简化架构
- **验收标准**:
  - 移除所有KV相关代码
  - 每次查询直接执行搜索和LLM调用
  - search_uuid参数可保留用于前端URL分享（但不做服务端缓存）

### FR-4: 搜索引擎支持
- **描述**: 只保留Serper搜索引擎后端
- **验收标准**:
  - 保留 Serper API
  - 移除 Google Programmable Search Engine
  - 移除 SearchApi.io
  - 移除 Bing 搜索支持
  - 移除 LEPTON 后端模式

### FR-5: 静态文件服务
- **描述**: 使用FastAPI StaticFiles替代Lepton StaticFiles
- **验收标准**:
  - 正确挂载前端构建产物
  - 根路径重定向到UI首页

## Non-Functional Requirements

### NFR-1: Docker容器化部署
- **描述**: 提供Docker部署方案
- **验收标准**:
  - 提供Dockerfile
  - 提供docker-compose.yml（包含前后端构建）
  - 支持通过环境变量配置所有必要参数

### NFR-2: 品牌定制
- **描述**: 将UI中的"Lepton AI"替换为"Evidence Search"
- **验收标准**:
  - 前端所有"Lepton AI"文字替换为"Evidence Search"
  - 搜索框placeholder更新
  - 保留原有UI布局和样式

### NFR-3: 依赖最小化
- **描述**: 移除不必要的依赖
- **验收标准**:
  - 创建requirements.txt，只包含必要依赖
  - 移除leptonai相关依赖

## Out of Scope
- 前端代码修改（除API调用路径外）
- 新增功能
- 性能优化
- 测试代码编写

## Environment Variables

| 变量名 | 必需 | 描述 |
|--------|------|------|
| OPENAI_API_KEY | 是 | OpenAI API密钥 |
| OPENAI_BASE_URL | 否 | OpenAI API基础URL（默认官方） |
| LLM_MODEL | 否 | 模型名称（默认gpt-3.5-turbo） |
| SERPER_SEARCH_API_KEY | 是 | Serper API密钥 |
| RELATED_QUESTIONS | 否 | 是否生成相关问题（默认true） |
