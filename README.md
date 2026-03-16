# DeerFlow 2.0 Project

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This repository contains a comprehensive collection of DeerFlow 2.0 resources, including example cases, a full-stack enterprise application, and architectural documentation.

## 📁 Repository Structure

```
deerflow2.0-project/
├── deerflow-demo/              # DeerFlow 2.0 Example Cases
│   ├── examples/               # 23 complete example files
│   │   ├── case01_basic_usage.py
│   │   ├── case02_advanced_config.py
│   │   ├── case03_fastapi_integration.py
│   │   ├── case04_multi_agent.py
│   │   ├── case05_websocket_chat.py
│   │   ├── case06_mcp_config.py
│   │   ├── case07_database_integration.py
│   │   ├── case08_file_upload.py
│   │   ├── case09_custom_tool.py
│   │   ├── case10_task_scheduler.py
│   │   ├── case11_memory_system.py
│   │   ├── case12_multimodal.py
│   │   ├── case13_api_gateway.py
│   │   ├── case14_monitoring.py
│   │   ├── case15_ab_testing.py
│   │   ├── case16_cache_optimization.py
│   │   ├── case17_distributed.py
│   │   ├── case18_data_pipeline.py
│   │   ├── case19_security.py
│   │   ├── case20_performance.py
│   │   ├── case21_testing.py
│   │   ├── case22_cicd.py
│   │   └── case23_kubernetes.py
│   └── README.md               # Examples documentation
│
├── deerflow-enterprise-project/ # Full-Stack Enterprise Application
│   ├── backend/                # FastAPI Backend
│   │   ├── app/               # Application layer
│   │   │   ├── api/v1/        # API routes (auth, agents, tasks, memory...)
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   ├── services/      # Business logic
│   │   │   └── core/          # Configuration & database
│   │   ├── packages/harness/  # DeerFlow 2.0 harness
│   │   ├── alembic/           # Database migrations
│   │   ├── tests/             # Test suite
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── frontend/               # Next.js Frontend
│   │   ├── src/app/           # Pages (Dashboard, Agents, Tasks, Memory...)
│   │   ├── src/components/    # UI components (Shadcn UI)
│   │   ├── src/lib/api/       # API clients & hooks
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── docker-compose.yml      # Complete Docker orchestration
│   ├── README.md               # Project documentation
│   ├── CLAUDE.md               # Development guide
│   └── docs/                   # Additional documentation
│
├── DEERFLOW2.0_ARCHITECTURE.md # Architecture documentation
├── CLAUDE.md                   # Development guidelines
└── README.md                   # This file
```

## 🚀 Quick Start

### Option 1: Run the Enterprise Application (Recommended)

```bash
cd deerflow-enterprise-project

# Start all services with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Explore Example Cases

```bash
cd deerflow-demo

# View the examples
cat examples/case01_basic_usage.py
cat examples/case04_multi_agent.py

# Read the documentation
cat README.md
```

## 📚 Contents

### 1. deerflow-demo - Example Cases

23 complete, runnable examples demonstrating DeerFlow 2.0 capabilities:

| Case | Topic | Description |
|------|-------|-------------|
| 01 | Basic Usage | Client initialization and basic operations |
| 02 | Advanced Config | Configuration management and environment setup |
| 03 | FastAPI Integration | Building REST APIs with DeerFlow |
| 04 | Multi-Agent | Multi-agent collaboration patterns |
| 05 | WebSocket Chat | Real-time chat implementation |
| 06 | MCP Config | Multi-Client Protocol configuration |
| 07 | Database | Database integration with SQLAlchemy |
| 08 | File Upload | File processing and handling |
| 09 | Custom Tool | Building custom tools for agents |
| 10 | Task Scheduler | Task scheduling and workflow automation |
| 11 | Memory System | Long-term memory implementation |
| 12 | Multimodal | Multimodal content generation |
| 13 | API Gateway | API gateway design patterns |
| 14 | Monitoring | Monitoring, logging, and alerting |
| 15 | A/B Testing | A/B testing for AI systems |
| 16 | Cache Optimization | Caching strategies |
| 17 | Distributed | Distributed deployment |
| 18 | Data Pipeline | Data pipeline and ETL |
| 19 | Security | Security hardening |
| 20 | Performance | Performance optimization |
| 21 | Testing | Testing strategies |
| 22 | CI/CD | CI/CD with GitHub Actions |
| 23 | Kubernetes | Kubernetes deployment |

### 2. deerflow-enterprise-project - Full-Stack Application

A production-ready enterprise AI agent system with:

**Backend (FastAPI)**:
- ✅ Complete REST API with JWT authentication
- ✅ Agent management (CRUD operations)
- ✅ Task management with status tracking
- ✅ Memory system for long-term context
- ✅ Thread/conversation management
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Alembic database migrations
- ✅ DeerFlow 2.0 harness integration

**Frontend (Next.js)**:
- ✅ Modern React with TypeScript
- ✅ Shadcn UI component library
- ✅ Tailwind CSS styling
- ✅ React Query for data fetching
- ✅ Protected routes with authentication
- ✅ Dashboard with statistics
- ✅ Agent management interface
- ✅ Task management UI
- ✅ Memory browser
- ✅ Real-time chat interface

**Infrastructure**:
- ✅ Docker Compose with PostgreSQL, Redis, Backend, Frontend
- ✅ Environment configuration
- ✅ CORS and security settings

## 🏗️ Architecture

### Full-Stack Architecture

```
┌─────────────────────────────────────────┐
│           Frontend Layer                │
│  Next.js 16 + React 19 + TypeScript 5   │
│  React Query 5 + Tailwind CSS 4         │
│  Shadcn UI + Radix UI                   │
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
│  Agent, Task, Memory Services           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│         Data Layer                      │
│  PostgreSQL 15 + SQLAlchemy 2.0         │
│  Redis 7 + Alembic Migrations           │
└─────────────────────────────────────────┘
```

## 📖 Documentation

- [DEERFLOW2.0_ARCHITECTURE.md](DEERFLOW2.0_ARCHITECTURE.md) - Detailed architecture documentation
- [deerflow-enterprise-project/README.md](deerflow-enterprise-project/README.md) - Enterprise app documentation
- [deerflow-enterprise-project/CLAUDE.md](deerflow-enterprise-project/CLAUDE.md) - Development guide
- [deerflow-demo/README.md](deerflow-demo/README.md) - Examples documentation

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI 0.109+** - Web framework
- **SQLAlchemy 2.0+** - ORM
- **PostgreSQL 15+** - Database
- **Redis 7+** - Cache
- **DeerFlow 2.0** - AI Agent framework

### Frontend
- **Next.js 16+**
- **React 19+**
- **TypeScript 5+**
- **Tailwind CSS 4+**
- **Shadcn UI** - Component library
- **React Query 5+** - Data fetching

### Infrastructure
- **Docker & Docker Compose**
- **Nginx** (optional)
- **Kubernetes** (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [DeerFlow 2.0](https://github.com/bytedance/deer-flow) - AI Agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Next.js](https://nextjs.org/) - React framework
- [Shadcn UI](https://ui.shadcn.com/) - UI components

---

**Version**: 0.1.0  
**Last Updated**: 2026-03-16  
**Status**: ✅ Complete with Examples + Enterprise Application
