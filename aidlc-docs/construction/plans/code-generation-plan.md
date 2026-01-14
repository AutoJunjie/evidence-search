# Code Generation Plan

## Unit Context
- **Unit Name**: leptonai-removal
- **Type**: Framework Migration
- **Workspace Root**: /home/ubuntu/evidence-search

## Generation Steps

### Step 1: Create Backend Application (app.py)
- [ ] Create new `app.py` with FastAPI application
- [ ] Implement search_with_serper function (from original)
- [ ] Implement OpenAI client setup
- [ ] Implement RAG query logic
- [ ] Implement streaming response
- [ ] Implement related questions generation
- [ ] Mount static files for frontend
- [ ] Implement error handling middleware for API compatibility

### Step 2: Create Python Dependencies (requirements.txt)
- [ ] Create `requirements.txt` with minimal dependencies

### Step 3: Update Frontend Branding
- [ ] Update `web/src/app/components/search.tsx` - placeholder text
- [ ] Update `web/src/app/components/logo.tsx` - brand name (if applicable)

### Step 4: Create Docker Configuration
- [ ] Create `Dockerfile` for containerized deployment
- [ ] Create `docker-compose.yml` for easy startup

### Step 5: Update README
- [ ] Update `README.md` with new setup instructions

## Files to Create/Modify

| Action | File | Description |
|--------|------|-------------|
| Create | app.py | FastAPI backend replacing search_with_lepton.py |
| Create | requirements.txt | Python dependencies |
| Modify | web/src/app/components/search.tsx | Update placeholder |
| Create | Dockerfile | Container build |
| Create | docker-compose.yml | Container orchestration |
| Modify | README.md | Updated instructions |

## Story Traceability
- FR-1: 移除Lepton框架依赖 → Step 1
- FR-2: LLM服务集成 → Step 1
- FR-3: 移除缓存功能 → Step 1
- FR-4: 搜索引擎支持(Serper only) → Step 1
- FR-5: 静态文件服务 → Step 1
- NFR-1: Docker容器化部署 → Step 4
- NFR-2: 品牌定制 → Step 3
