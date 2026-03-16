"""
API Router for the enterprise AI agent system.
"""

from fastapi import APIRouter

from app.api.v1.agents import router as agents_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.memory import router as memory_router
from app.api.v1.skills import router as skills_router
from app.api.v1.tools import router as tools_router
from app.api.v1.auth import router as auth_router
from app.api.v1.threads import router as threads_router

# Create API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(threads_router, prefix="/threads", tags=["threads"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(memory_router, prefix="/memory", tags=["memory"])
api_router.include_router(skills_router, prefix="/skills", tags=["skills"])
api_router.include_router(tools_router, prefix="/tools", tags=["tools"])