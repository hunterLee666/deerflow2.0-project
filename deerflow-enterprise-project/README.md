# 🦌 DeerFlow Enterprise - 企业级AI Agent系统

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个基于DeerFlow 2.0 harness框架构建的完整企业级AI Agent系统，展示了生产就绪的全栈应用开发。

## 🌟 特性

- ✅ **完整的后端实现** - FastAPI + SQLAlchemy + PostgreSQL
- ✅ **完整的前端实现** - Next.js + React Query + Tailwind CSS
- ✅ **JWT认证系统** - 安全的用户认证和授权
- ✅ **RBAC权限控制** - 基于角色的访问控制
- ✅ **Agent生命周期管理** - 创建、更新、删除Agent
- ✅ **对话线程管理** - 支持多轮对话和消息历史
- ✅ **任务执行系统** - 任务创建、追踪、状态管理
- ✅ **长期记忆系统** - 用户上下文和事实存储
- ✅ **审计日志** - 完整的操作审计追踪
- ✅ **PostgreSQL数据库** - 企业级数据持久化
- ✅ **Docker支持** - 容器化部署
- ✅ **实时通信** - WebSocket流式响应

## 📁 项目结构

```
deerflow-enterprise-project/
├── backend/                    # 后端应用 (✅ 完整实现)
│   ├── app/                   # 应用层
│   │   ├── api/               # API路由
│   │   │   └── v1/
│   │   │       ├── schemas.py       # Pydantic验证模式
│   │   │       ├── api.py           # 主路由
│   │   │       ├── auth.py          # 认证路由
│   │   │       ├── agents.py        # Agent管理
│   │   │       ├── threads.py       # 对话管理
│   │   │       ├── tasks.py         # 任务管理
│   │   │       ├── memory.py        # 记忆管理
│   │   │       ├── skills.py        # 技能管理
│   │   │       └── tools.py         # 工具管理
│   │   ├── models/            # 数据模型
│   │   │   └── __init__.py          # 7个核心模型
│   │   ├── services/          # 业务服务
│   │   │   ├── user_service.py
│   │   │   ├── agent_service.py
│   │   │   ├── thread_service.py
│   │   │   ├── task_service.py
│   │   │   ├── memory_service.py
│   │   │   └── auth_service.py
│   │   ├── core/              # 核心模块
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── database.py    # DB连接
│   │   │   └── security.py    # 安全设置
│   │   └── main.py            # FastAPI应用入口
│   ├── alembic/               # 数据库迁移
│   ├── packages/              # DeerFlow harness包
│   ├── tests/                 # 测试套件
│   ├── Dockerfile             # 后端Docker镜像
│   ├── requirements.txt       # Python依赖
│   └── pyproject.toml         # 项目配置
├── frontend/                   # 前端应用 (✅ 完整实现)
│   ├── src/
│   │   ├── app/               # Next.js路由
│   │   │   ├── page.tsx       # Dashboard首页
│   │   │   ├── login/         # 登录页面
│   │   │   ├── register/      # 注册页面
│   │   │   ├── agents/        # Agent管理
│   │   │   ├── conversations/ # 对话页面
│   │   │   ├── tasks/         # 任务管理
│   │   │   └── memory/        # 记忆系统
│   │   ├── components/        # UI组件
│   │   │   ├── layout/        # 布局组件
│   │   │   │   ├── MainLayout.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── ui/            # Shadcn UI组件
│   │   │   ├── agents/        # Agent组件
│   │   │   └── conversations/ # 对话组件
│   │   └── lib/               # 工具库
│   │       ├── api/           # API客户端
│   │       │   ├── client.ts
│   │       │   ├── auth.ts
│   │       │   ├── agents.ts
│   │       │   ├── tasks.ts
│   │       │   └── memory.ts
│   │       └── hooks/         # React Hooks
│   │           └── useAuth.ts
│   ├── Dockerfile             # 前端Docker镜像
│   └── package.json           # Node依赖
├── docker-compose.yml          # Docker编排 (✅)
├── configs/                    # 配置文件
├── scripts/                    # 部署脚本
├── docs/                       # 项目文档
├── IMPLEMENTATION.md           # 完整实现文档
└── README.md                   # 本文件
```

## 🚀 快速开始

### 方式一: Docker Compose (推荐 ⭐)

```bash
# 克隆项目
cd deerflow-enterprise-project

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**访问地址:**
- 🌐 前端应用: http://localhost:3000
- 🔧 后端API: http://localhost:8000
- 📚 API文档: http://localhost:8000/docs

### 方式二: 本地开发

#### 1. 启动数据库

```bash
# 使用Docker启动PostgreSQL和Redis
docker run -d --name deerflow-postgres \
  -e POSTGRES_USER=deerflow \
  -e POSTGRES_PASSWORD=deerflow_secret \
  -e POSTGRES_DB=deerflow \
  -p 5432:5432 postgres:15-alpine

docker run -d --name deerflow-redis \
  -p 6379:6379 redis:7-alpine
```

#### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📚 API文档

### 认证相关

#### 注册用户
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

#### 登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

#### 获取当前用户
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Agent管理

#### 列出所有Agent
```bash
curl -X GET "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 创建Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Assistant",
    "description": "Helps with research tasks",
    "capabilities": ["web_search", "data_analysis"]
  }'
```

### 对话管理

#### 流式对话
```bash
curl -X POST "http://localhost:8000/api/v1/agents/stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can you help me?",
    "thread_id": "optional-thread-id"
  }'
```

### 任务管理

#### 创建任务
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research AI trends",
    "description": "Research the latest AI trends in 2026",
    "agent": "Research Assistant"
  }'
```

#### 获取任务列表
```bash
curl -X GET "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 记忆系统

#### 获取记忆列表
```bash
curl -X GET "http://localhost:8000/api/v1/memory" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 搜索记忆
```bash
curl -X GET "http://localhost:8000/api/v1/memory/search?q=AI" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ 架构设计

### 全栈架构

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│  (Next.js + React Query + Tailwind)     │
└────────────┬────────────────────────────┘
             │ HTTP / WebSocket
┌────────────▼────────────────────────────┐
│           API Gateway Layer             │
│  (FastAPI + JWT Auth + CORS)            │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         Service Layer                   │
│  (Business Logic + DeerFlow Harness)    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         Data Layer                      │
│  (PostgreSQL + Redis + Alembic)         │
└─────────────────────────────────────────┘
```

### 核心模型关系

```
User ────< owns >──── Agent
 │                       │
 │                       ├───< has >─── Thread
 │                       │
 │                       └───< delegates >─── Task
 │
 ├───< creates >─── Task
 │                    │
 │                    └───< tracks >─── SubTask
 │
 └───< stores >─── Memory
```

## 🔒 安全特性

- ✅ **JWT认证** - 安全的令牌认证机制
- ✅ **密码哈希** - bcrypt加密存储
- ✅ **RBAC权限** - 基于角色的访问控制
- ✅ **CORS配置** - 跨域资源共享
- ✅ **SQL注入防护** - 参数化查询
- ✅ **输入验证** - Pydantic类型验证
- ✅ **API认证** - Bearer Token自动注入

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_auth_api.py

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行测试
npm test

# 类型检查
npm run type-check

# 代码检查
npm run lint
```

## 🐳 Docker部署

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重建服务
docker-compose up -d --build

# 停止并删除
docker-compose down -v
```

### 生产环境

```bash
# 使用生产配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📊 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 编程语言 |
| FastAPI | 0.109+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.5+ | 数据验证 |
| PostgreSQL | 15+ | 主数据库 |
| Redis | 7+ | 缓存 |
| JWT | - | 认证 |
| bcrypt | - | 密码哈希 |
| Alembic | - | 数据库迁移 |
| pytest | 7.4+ | 测试 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 16+ | React框架 |
| React | 19+ | UI库 |
| TypeScript | 5+ | 类型系统 |
| Tailwind CSS | 4+ | CSS框架 |
| Shadcn UI | - | UI组件库 |
| React Query | 5+ | 数据获取 |
| Radix UI | - | 底层组件 |
| Lucide React | - | 图标库 |

## 🗺️ 路线图

### ✅ 第一阶段 - 后端核心 (已完成)
- [x] 数据模型设计
- [x] 服务层实现
- [x] API路由
- [x] 认证系统
- [x] 数据库集成
- [x] 测试套件

### ✅ 第二阶段 - 前端开发 (已完成)
- [x] UI组件库 (Shadcn UI)
- [x] 页面路由 (Next.js)
- [x] 状态管理 (React Query)
- [x] API集成
- [x] 认证系统
- [x] Dashboard
- [x] Agent管理
- [x] 对话功能
- [x] 任务管理
- [x] 记忆系统

### 📅 第三阶段 - 高级功能 (规划中)
- [ ] WebSocket实时通信
- [ ] 文件上传处理
- [ ] 性能优化
- [ ] 监控告警
- [ ] 多语言支持
- [ ] 移动端适配

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

- [DeerFlow 2.0](https://github.com/bytedance/deer-flow) - AI Agent框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Next.js](https://nextjs.org/) - React框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包
- [Shadcn UI](https://ui.shadcn.com/) - UI组件库
- 所有开源贡献者

---

**版本**: 0.1.0  
**最后更新**: 2026-03-16  
**状态**: ✅ 完整实现 (后端 + 前端)
