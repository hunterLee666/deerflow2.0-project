"""
Thread endpoints for the enterprise AI agent system.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_threads():
    """List all threads"""
    return {"message": "List threads"}

@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    """Get thread by ID"""
    return {"thread_id": thread_id}
