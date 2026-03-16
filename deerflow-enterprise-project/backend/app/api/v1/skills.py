"""
Skills endpoints for the enterprise AI agent system.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_skills():
    """List all skills"""
    return {"message": "List skills"}
