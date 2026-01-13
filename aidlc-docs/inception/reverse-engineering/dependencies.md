# Dependencies

## Internal Dependencies

```
+------------------+          +------------------+
|                  |   HTTP   |                  |
|    Frontend      |--------->|    Backend       |
|    (Next.js)     |  /query  |    (Python)      |
|                  |          |                  |
+------------------+          +------------------+
```

### Frontend depends on Backend
- **Type**: Runtime (HTTP API)
- **Reason**: 前端调用后端 `/query` API获取搜索结果

## External Dependencies

### Backend Dependencies (需要移除的Lepton依赖)

#### leptonai
- **Version**: 未指定
- **Purpose**: 核心框架
- **Usage**:
  - `leptonai.Client` - Lepton API客户端
  - `leptonai.kv.KV` - 键值存储
  - `leptonai.photon.Photon` - Web框架基类
  - `leptonai.photon.StaticFiles` - 静态文件服务
  - `leptonai.photon.types.to_bool` - 布尔值转换
  - `leptonai.api.v0.workspace.WorkspaceInfoLocalRecord` - workspace token
  - `leptonai.api.v0.workspace.login` - workspace登录
  - `leptonai.util.tool` - 函数调用工具
- **License**: Apache 2.0

### Backend Dependencies (保留)

#### openai
- **Version**: 未指定
- **Purpose**: LLM API调用
- **License**: MIT

#### httpx
- **Version**: 未指定
- **Purpose**: HTTP客户端超时配置
- **License**: BSD

#### requests
- **Version**: 未指定
- **Purpose**: 搜索引擎API调用
- **License**: Apache 2.0

#### loguru
- **Version**: 未指定
- **Purpose**: 日志记录
- **License**: MIT

### Frontend Dependencies (保留)

#### next
- **Version**: 14.2.22
- **Purpose**: React框架
- **License**: MIT

#### react / react-dom
- **Version**: ^18
- **Purpose**: UI库
- **License**: MIT

#### react-markdown
- **Version**: ^9.0.1
- **Purpose**: Markdown渲染
- **License**: MIT

#### nanoid
- **Version**: ^5.0.4
- **Purpose**: UUID生成
- **License**: MIT

#### lucide-react
- **Version**: ^0.309.0
- **Purpose**: 图标
- **License**: ISC

#### @radix-ui/react-popover
- **Version**: ^1.0.7
- **Purpose**: 弹窗组件
- **License**: MIT

#### tailwindcss
- **Version**: ^3.3.0
- **Purpose**: CSS框架
- **License**: MIT

### Frontend Dependencies (可能需要移除)

#### @vercel/kv
- **Version**: ^1.0.1
- **Purpose**: Vercel KV存储（未使用）
- **License**: MIT

#### @upstash/ratelimit
- **Version**: ^1.0.0
- **Purpose**: 速率限制（未使用）
- **License**: MIT
