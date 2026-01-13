# Requirement Verification Questions

## 关于LLM服务

**Q1**: 移除Lepton LLM服务后，你希望使用哪种LLM方案？

A) 本地 Ollama（完全离线，需要本地GPU）
B) OpenAI API（需要OpenAI API Key）
C) 其他OpenAI兼容服务（如Azure OpenAI、Groq等）
D) 支持多种方案，通过环境变量切换
E) Other (请在下方描述)

[Answer]: B

---

## 关于缓存存储

**Q2**: 移除Lepton KV后，你希望使用哪种本地缓存方案？

A) 简单文件存储（JSON文件）
B) SQLite数据库
C) Redis（需要额外部署Redis）
D) 不需要缓存功能
E) Other (请在下方描述)

[Answer]: D

---

## 关于部署方式

**Q3**: 你希望如何运行这个项目？

A) 单一Python进程（后端服务前端静态文件）
B) 前后端分离（分别启动Next.js和Python服务）
C) Docker容器化部署
D) Other (请在下方描述)

[Answer]: C

---

## 关于品牌定制

**Q4**: 是否需要移除/替换UI中的"Lepton AI"品牌标识？

A) 是，替换为自定义名称（请在Answer中说明新名称）
B) 是，移除品牌标识但不替换
C) 否，保留原样
D) Other (请在下方描述)

[Answer]: C

---

## 关于功能范围

**Q5**: 是否需要保留所有搜索引擎后端支持（Bing、Google、Serper、SearchApi）？

A) 是，保留全部
B) 只保留Bing
C) 只保留Google相关（Google/Serper/SearchApi）
D) 只保留一个（请在Answer中说明）
E) Other (请在下方描述)

[Answer]: C

---

请直接在每个 `[Answer]:` 后面填写你的选择（如 A、B、C 等），或者描述你的具体需求。
