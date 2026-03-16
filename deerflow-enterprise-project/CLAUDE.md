# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **enterprise-grade full-stack project** built using the DeerFlow 2.0 harness framework. It demonstrates a complete AI agent system with production-ready frontend and backend implementations.

**Architecture**:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + DeerFlow harness
- **Frontend**: Next.js + React Query + Tailwind CSS + Shadcn UI
- **Infrastructure**: Docker Compose with PostgreSQL, Redis, backend, and frontend services
- **Documentation**: Complete API, architecture, and integration documentation

**Key Features**:
1. **Full-Stack Implementation**: Complete frontend and backend with JWT authentication
2. **Agent Orchestration**: Full agent lifecycle management using DeerFlow harness
3. **Sub-Agent System**: Dynamic task delegation and parallel processing
4. **Sandbox Execution**: Secure code execution environment
5. **Memory Management**: Persistent context and long-term memory
6. **Skill Integration**: Extensible skill system for custom functionality
7. **MCP Support**: Multi-Client Protocol for tool integration
8. **Enterprise Security**: Role-based access control and audit trails
9. **Real-time Communication**: WebSocket streaming for agent responses
10. **Docker Deployment**: Complete containerization with docker-compose

## Development Status

### ✅ Completed
- **Backend**: FastAPI API with all routes (auth, agents, threads, tasks, memory, skills, tools)
- **Frontend**: Next.js app with all pages (Dashboard, Agents, Tasks, Memory, Conversations)
- **Authentication**: JWT-based auth with login/register pages and protected routes
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Docker**: Complete docker-compose.yml with all services
- **API Integration**: Frontend API client with automatic token injection
- **UI Components**: Complete Shadcn UI component library

### 📅 Planned
- WebSocket real-time updates
- File upload functionality
- Performance monitoring
- Multi-language support

## Development Guidelines

### Documentation Update Policy
**CRITICAL: Always update README.md and CLAUDE.md after every code change**

When making code changes, you MUST update the relevant documentation:
- Update `README.md` for user-facing changes (features, setup, usage instructions)
- Update `CLAUDE.md` for development changes (architecture, commands, workflows, internal systems)
- Keep documentation synchronized with the codebase at all times
- Ensure accuracy and timeliness of all documentation

## Commands

### Backend Commands
```bash
cd backend

# Install dependencies
pip install -r requirements.txt
# OR using uv
uv sync

# Run database migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# OR using Makefile
make dev

# Run tests
pytest
# OR
make test

# Lint code
make lint

# Format code
make format
```

### Frontend Commands
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Type check
npm run type-check

# Lint code
npm run lint
```

### Docker Commands (Recommended)
```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild services
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Project-wide Commands
```bash
# Start everything in development mode
make dev

# Run all tests
make test

# Build for production
make build

# Deploy to staging
make deploy-staging

# Deploy to production
make deploy-prod
```

## Architecture

### Full-Stack Architecture

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│  Next.js 16 + React 19 + TypeScript 5   │
│  React Query 5 + Tailwind CSS 4         │
│  Shadcn UI + Radix UI + Lucide React    │
└────────────┬────────────────────────────┘
             │ HTTP / WebSocket
┌────────────▼────────────────────────────┐
│           API Gateway Layer             │
│  FastAPI 0.109 + JWT Auth + CORS        │
│  Pydantic 2.5 + Python 3.12             │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         Service Layer                   │
│  Business Logic + DeerFlow Harness      │
│  Agent Service, Task Service, etc.      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         Data Layer                      │
│  PostgreSQL 15 + SQLAlchemy 2.0         │
│  Redis 7 + Alembic Migrations           │
└─────────────────────────────────────────┘
```

### Backend Structure

**Packages**:
- `packages/harness`: The DeerFlow harness package providing core agent functionality
- `app`: Application layer containing business logic and API endpoints

**App Layer Components**:
- `api/v1`: REST API endpoints
  - `auth.py`: Authentication routes (login, register, me)
  - `agents.py`: Agent management routes
  - `threads.py`: Conversation thread routes
  - `tasks.py`: Task management routes
  - `memory.py`: Memory system routes
  - `skills.py`: Skill management routes
  - `tools.py`: Tool management routes
  - `api.py`: Main API router
- `models`: SQLAlchemy data models (User, Agent, Task, Memory, etc.)
- `services`: Business logic services
  - `auth_service.py`: Authentication logic
  - `user_service.py`: User management
  - `agent_service.py`: Agent operations
  - `task_service.py`: Task management
  - `memory_service.py`: Memory operations
  - `thread_service.py`: Thread management
- `core`: Core configuration
  - `config.py`: Application settings
  - `database.py`: Database connection
- `utils`: Utility functions
  - `security.py`: JWT and password hashing
- `main.py`: FastAPI application entry point

**Database**:
- `alembic/`: Database migration files
  - `env.py`: Migration environment
  - `versions/`: Migration versions

### Frontend Structure

**App Router** (Next.js 16 App Router):
- `app/page.tsx`: Dashboard homepage
- `app/login/page.tsx`: Login page
- `app/register/page.tsx`: Registration page
- `app/agents/page.tsx`: Agent management
- `app/conversations/page.tsx`: Chat interface
- `app/tasks/page.tsx`: Task management
- `app/memory/page.tsx`: Memory browser
- `app/layout.tsx`: Root layout with providers

**Components**:
- `components/layout/`: Layout components
  - `MainLayout.tsx`: Main layout with auth check
  - `Sidebar.tsx`: Navigation sidebar
  - `Header.tsx`: Top header with user menu
- `components/ui/`: Shadcn UI components
  - `button.tsx`, `input.tsx`, `card.tsx`, etc.
- `components/agents/`: Agent-related components
  - `AgentList.tsx`: Agent list component
- `components/conversations/`: Chat components
  - `ChatInterface.tsx`: Real-time chat UI

**Library**:
- `lib/api/`: API client and hooks
  - `client.ts`: Base API client with auth
  - `auth.ts`: Authentication API
  - `agents.ts`: Agent API hooks
  - `tasks.ts`: Task API hooks
  - `memory.ts`: Memory API hooks
- `lib/hooks/`: Custom React hooks
  - `useAuth.ts`: Authentication state management

### DeerFlow Harness Integration

The project uses the DeerFlow 2.0 harness framework which provides:

1. **Agent System**: Lead agent with middleware chain
   - `agents/lead_agent/`: Main agent implementation
   - `agents/middlewares/`: Middleware components
   - `agents/memory/`: Memory management

2. **Sub-Agent Framework**: Task delegation and parallel execution
   - `subagents/`: Sub-agent registry and executor

3. **Sandbox Environment**: Secure code execution
   - `sandbox/`: Local and remote sandbox providers

4. **Memory System**: Context persistence and recall
   - `agents/memory/`: Memory updater and queue

5. **Skill Engine**: Extensible functionality modules
   - `skills/`: Skill loader, parser, and validator

6. **Tool Integration**: MCP and custom tool support
   - `tools/builtins/`: Built-in tools
   - `mcp/`: MCP client and tools

7. **Community Integrations**:
   - `community/tavily/`: Tavily search
   - `community/firecrawl/`: Firecrawl integration
   - `community/jina_ai/`: Jina AI tools
   - `community/aio_sandbox/`: Sandbox backend

### Configuration Management

Configuration is managed through:
- Environment variables (`.env`)
- `backend/config.yaml`: DeerFlow configuration
- `configs/` directory: Additional configurations
- Runtime configuration via API

### API Routes

**Authentication**:
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

**Agents**:
- `GET /api/v1/agents` - List all agents
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents/{id}` - Get agent details
- `POST /api/v1/agents/stream` - Stream agent response

**Threads**:
- `GET /api/v1/threads` - List threads
- `GET /api/v1/threads/{id}` - Get thread

**Tasks**:
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

**Memory**:
- `GET /api/v1/memory` - List memory entries
- `POST /api/v1/memory` - Create memory entry
- `GET /api/v1/memory/search` - Search memory
- `DELETE /api/v1/memory/{id}` - Delete memory

## Testing Strategy

**Test Types**:
1. **Unit Tests**: Individual function and component testing
2. **Integration Tests**: API and service integration testing
3. **End-to-End Tests**: Full system workflow testing

**Backend Testing**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_api.py
```

**Frontend Testing**:
```bash
cd frontend

# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

**Testing Commands**:
```bash
# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run end-to-end tests
make test-e2e

# Run all tests
make test
```

## Workflow Requirements

1. **Research & Reuse**: Before implementing new functionality, search for existing solutions
2. **Plan First**: Use the planner agent for complex features or architectural decisions
3. **TDD Approach**: Write tests first, then implement (RED-GREEN-REFINE cycle)
4. **Code Review**: Use the code-reviewer agent immediately after writing code
5. **Security Review**: Use the security-reviewer agent before any commits
6. **Commit Messages**: Follow conventional commits format (feat:, fix:, refactor:, etc.)
7. **Documentation**: Update README.md and CLAUDE.md with every significant change

## Key Features Implementation

### Full-Stack Authentication
- JWT-based authentication with access tokens
- Protected API routes with Bearer token validation
- Frontend auth context with automatic token injection
- Login/Register pages with form validation
- Automatic redirect to login for unauthenticated users

### Agent Orchestration
Implementation of the DeerFlow lead agent with custom middleware and tool integration.

### Sub-Agent System
Dynamic task delegation system allowing agents to spawn sub-agents for complex tasks.

### Sandbox Execution
Secure code execution environment with file system isolation.

### Memory Management
Persistent context storage and retrieval system for long-term memory.

### Skill Integration
Extensible skill system allowing custom functionality to be added to agents.

### MCP Support
Multi-Client Protocol integration for connecting external tools and services.

### Enterprise Security
Role-based access control, audit trails, and security best practices.

### Real-time Communication
WebSocket streaming for real-time agent responses in the chat interface.

## Docker Services

**PostgreSQL**:
- Image: `postgres:15-alpine`
- Port: `5432`
- Database: `deerflow`
- User: `deerflow`

**Redis**:
- Image: `redis:7-alpine`
- Port: `6379`

**Backend**:
- Build: `backend/Dockerfile`
- Port: `8000`
- Environment: Development with hot reload

**Frontend**:
- Build: `frontend/Dockerfile`
- Port: `3000`
- Environment: Development with hot reload

## Environment Variables

**Backend**:
```env
DATABASE_URL=postgresql://deerflow:deerflow_secret@postgres:5432/deerflow
REDIS_URL=redis://redis:6379
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
DEERFLOW_CONFIG_PATH=/app/config.yaml
```

**Frontend**:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Useful Links

- [DeerFlow 2.0](https://github.com/bytedance/deer-flow) - AI Agent framework
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js Documentation](https://nextjs.org/docs) - Frontend framework
- [Shadcn UI](https://ui.shadcn.com/) - UI component library
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - ORM documentation

---

**Version**: 0.1.0  
**Last Updated**: 2026-03-16  
**Status**: ✅ Full-Stack Implementation Complete
