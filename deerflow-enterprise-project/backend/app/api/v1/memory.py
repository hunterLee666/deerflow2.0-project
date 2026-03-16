"""
Memory endpoints for the enterprise AI agent system.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_memories():
    """List all memories"""
    return {"message": "List memories"}

@router.get("/{memory_id}")
async def get_memory(memory_id: str):
    """Get memory by ID"""
    return {"memory_id": memory_id}
