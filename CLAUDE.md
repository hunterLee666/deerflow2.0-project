# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive DeerFlow 2.0 project containing:
1. **deerflow-demo** - 23 complete example cases demonstrating DeerFlow 2.0 capabilities
2. **deerflow-enterprise-project** - Full-stack enterprise AI agent application
3. **Documentation** - Architecture docs and development guides

## Repository Structure

```
deerflow2.0-project/
├── deerflow-demo/              # Example cases (23 Python files)
│   ├── examples/               # case01 - case23
│   └── README.md
│
├── deerflow-enterprise-project/ # Full-stack application
│   ├── backend/                # FastAPI + SQLAlchemy + PostgreSQL
│   ├── frontend/               # Next.js + React + TypeScript
│   ├── docker-compose.yml
│   ├── README.md
│   └── CLAUDE.md
│
├── DEERFLOW2.0_ARCHITECTURE.md
├── CLAUDE.md                   # This file
└── README.md
```

## Development Guidelines

### General Principles
- Follow the user's global coding standards defined in ~/.claude/rules/common/
- Use immutable data patterns - never mutate existing objects
- Organize code into many small, focused files (200-400 lines typical, 800 max)
- Always validate inputs at system boundaries
- Handle errors comprehensively at every level
- Maintain 80%+ test coverage using Test-Driven Development

### Documentation Update Policy
**CRITICAL: Always update relevant documentation after code changes**

When making changes:
- Update `deerflow-demo/README.md` for example changes
- Update `deerflow-enterprise-project/README.md` for user-facing changes
- Update `deerflow-enterprise-project/CLAUDE.md` for development changes
- Update root `README.md` for repository-level changes
- Keep all documentation synchronized

## Working with deerflow-demo

### Structure
- 23 example cases in `deerflow-demo/examples/`
- Each case is a standalone Python file
- Cases cover: basic usage, FastAPI, multi-agent, WebSocket, database, etc.

### Commands
```bash
cd deerflow-demo

# View examples
ls examples/
cat examples/case01_basic_usage.py

# Run an example (if applicable)
python examples/case01_basic_usage.py
```

### Adding New Examples
1. Create new file: `examples/caseXX_topic.py`
2. Follow existing naming convention
3. Add comprehensive docstring
4. Update `deerflow-demo/README.md`
5. Update examples table in root README.md

## Working with deerflow-enterprise-project

### Quick Start
```bash
cd deerflow-enterprise-project

# Start all services
docker-compose up -d

# Or develop locally:
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Backend Development

**Structure:**
```
backend/
├── app/
│   ├── api/v1/          # API routes
│   │   ├── auth.py      # Authentication
│   │   ├── agents.py    # Agent management
│   │   ├── tasks.py     # Task management
│   │   ├── memory.py    # Memory system
│   │   └── api.py       # Router assembly
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   ├── core/            # Config & database
│   └── main.py          # FastAPI entry
├── packages/harness/    # DeerFlow harness
├── alembic/             # Migrations
└── tests/               # Test suite
```

**Key Commands:**
```bash
cd deerflow-enterprise-project/backend

# Install dependencies
pip install -r requirements.txt

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest
pytest --cov=app --cov-report=html
```

**Adding New API Routes:**
1. Create/update file in `app/api/v1/`
2. Define Pydantic schemas in `app/api/v1/schemas.py`
3. Register router in `app/api/v1/api.py`
4. Add tests in `tests/`
5. Update documentation

### Frontend Development

**Structure:**
```
frontend/
├── src/
│   ├── app/             # Next.js pages
│   │   ├── page.tsx     # Dashboard
│   │   ├── login/       # Login page
│   │   ├── agents/      # Agent management
│   │   ├── tasks/       # Task management
│   │   └── memory/      # Memory browser
│   ├── components/
│   │   ├── layout/      # Layout components
│   │   ├── ui/          # Shadcn UI
│   │   └── agents/      # Feature components
│   └── lib/
│       ├── api/         # API clients
│       └── hooks/       # React hooks
```

**Key Commands:**
```bash
cd deerflow-enterprise-project/frontend

# Install dependencies
npm install

# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build
```

**Adding New Pages:**
1. Create directory in `src/app/[page-name]/`
2. Add `page.tsx` with component
3. Use `MainLayout` for protected routes
4. Create API hooks in `src/lib/api/`
5. Add to sidebar navigation

### API Integration

**Backend API Pattern:**
```python
# backend/app/api/v1/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_items():
    return {"items": []}

@router.post("/")
async def create_item(data: ItemCreate):
    return {"id": "...", **data.dict()}
```

**Frontend API Pattern:**
```typescript
// frontend/src/lib/api/example.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiFetch } from './client';

export function useItems() {
  return useQuery({
    queryKey: ['items'],
    queryFn: () => apiFetch('items'),
  });
}

export function useCreateItem() {
  return useMutation({
    mutationFn: (data) => apiFetch('items', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  });
}
```

## Docker Development

### Services
- **postgres**: PostgreSQL 15 database
- **redis**: Redis 7 cache
- **backend**: FastAPI application
- **frontend**: Next.js application

### Commands
```bash
cd deerflow-enterprise-project

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild after changes
docker-compose up -d --build

# Stop everything
docker-compose down

# Reset (remove volumes)
docker-compose down -v
```

## Testing Strategy

### Backend Tests
```bash
cd deerflow-enterprise-project/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth_api.py -v
```

### Frontend Tests
```bash
cd deerflow-enterprise-project/frontend

# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint
```

## Workflow Requirements

1. **Research & Reuse**: Before implementing, search for existing solutions
2. **Plan First**: Use planner agent for complex features
3. **TDD Approach**: Write tests first (RED-GREEN-REFINE)
4. **Code Review**: Use code-reviewer agent after writing code
5. **Security Review**: Use security-reviewer agent before commits
6. **Documentation**: Update docs with every significant change
7. **Commit Messages**: Follow conventional commits (feat:, fix:, refactor:, etc.)

## Common Tasks

### Adding a New Feature

1. **Backend:**
   - Add model (if needed) in `app/models/`
   - Add service in `app/services/`
   - Add API routes in `app/api/v1/`
   - Add tests in `tests/`
   - Run migrations: `alembic revision --autogenerate -m "Add feature"`

2. **Frontend:**
   - Add API hooks in `src/lib/api/`
   - Add components in `src/components/`
   - Add page in `src/app/`
   - Update navigation in `Sidebar.tsx`

3. **Documentation:**
   - Update `deerflow-enterprise-project/README.md`
   - Update `deerflow-enterprise-project/CLAUDE.md`
   - Update root `README.md` (if major feature)

### Database Changes

```bash
cd deerflow-enterprise-project/backend

# Generate migration
alembic revision --autogenerate -m "Description of changes"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback (if needed)
alembic downgrade -1
```

### Adding UI Components

```bash
cd deerflow-enterprise-project/frontend

# Add Shadcn UI component
npx shadcn add [component-name]

# Or create custom component in src/components/ui/
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://deerflow:deerflow_secret@localhost:5432/deerflow
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
DEERFLOW_CONFIG_PATH=/app/config.yaml
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Troubleshooting

### Backend Issues
- **Database connection error**: Check PostgreSQL is running
- **Migration errors**: Try `alembic downgrade -1` then `alembic upgrade head`
- **Import errors**: Ensure virtual environment is activated

### Frontend Issues
- **Module not found**: Run `npm install`
- **Type errors**: Run `npm run type-check`
- **API connection error**: Check backend is running on port 8000

### Docker Issues
- **Port already in use**: Stop existing services or change ports
- **Volume permission errors**: Run `docker-compose down -v` and restart
- **Build errors**: Run `docker-compose build --no-cache`

## Useful Links

- [DeerFlow 2.0](https://github.com/bytedance/deer-flow)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Shadcn UI](https://ui.shadcn.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [React Query](https://tanstack.com/query/latest)

---

**Version**: 0.1.0  
**Last Updated**: 2026-03-16  
**Status**: ✅ Complete Documentation
