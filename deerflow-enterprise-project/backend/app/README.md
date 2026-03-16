# Enterprise App Package

This package contains the main application logic for the enterprise AI agent system.

## Package Structure

```
app/
├── __init__.py
├── main.py              # Application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py      # Application settings
│   └── logging.py       # Logging configuration
├── api/
│   ├── __init__.py
│   ├── deps.py          # Dependency injection
│   ├── main.py          # API router
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── api.py       # V1 API router
│   │   ├── agents.py    # Agent endpoints
│   │   ├── tasks.py     # Task endpoints
│   │   ├── memory.py    # Memory endpoints
│   │   ├── skills.py    # Skill endpoints
│   │   └── tools.py     # Tool endpoints
├── models/
│   ├── __init__.py
│   ├── agent.py         # Agent models
│   ├── task.py          # Task models
│   ├── memory.py        # Memory models
│   ├── skill.py         # Skill models
│   └── tool.py          # Tool models
├── services/
│   ├── __init__.py
│   ├── agent_service.py # Agent service logic
│   ├── task_service.py  # Task service logic
│   ├── memory_service.py # Memory service logic
│   ├── skill_service.py # Skill service logic
│   └── tool_service.py  # Tool service logic
├── utils/
│   ├── __init__.py
│   ├── security.py      # Security utilities
│   └── helpers.py       # Helper functions
└── core/
    ├── __init__.py
    ├── database.py      # Database connection
    ├── redis.py         # Redis connection
    └── celery.py        # Celery configuration
```

## Key Components

### Main Application (main.py)
The entry point for the FastAPI application, including:
- Application initialization
- Middleware configuration
- Router registration
- Exception handlers

### Configuration (config/)
Application configuration management:
- Settings from environment variables
- Logging configuration
- Security settings

### API Layer (api/)
REST API endpoints:
- Agent interaction endpoints
- Task management endpoints
- Memory management endpoints
- Skill management endpoints
- Tool integration endpoints

### Models (models/)
Pydantic models for data validation:
- Request/response models
- Database models
- Domain models

### Services (services/)
Business logic implementation:
- Agent orchestration
- Task management
- Memory operations
- Skill management
- Tool execution

### Utilities (utils/)
Helper functions and utilities:
- Security functions
- Common helper functions

### Core (core/)
Core infrastructure components:
- Database connections
- Redis connections
- Celery configuration

## Integration with DeerFlow Harness

The application integrates with the DeerFlow harness through:

1. **Agent Service**: Wrapper around DeerFlowClient for agent operations
2. **Task Service**: Integration with sub-agent system for task delegation
3. **Memory Service**: Extension of DeerFlow memory system
4. **Skill Service**: Management of DeerFlow skills
5. **Tool Service**: Integration with DeerFlow tool system and MCP