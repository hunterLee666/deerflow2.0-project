"""
Agent endpoints for the enterprise AI agent system.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.agent_service import AgentService
from app.api.deps import get_current_active_user

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str

class StreamRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: str = Depends(get_current_active_user)
):
    """Chat with the main agent"""
    try:
        agent_service = AgentService()
        response = await agent_service.chat(request.message, request.thread_id)
        return ChatResponse(response=response, thread_id=request.thread_id or "new-thread")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_agent_response(
    request: StreamRequest,
    current_user: str = Depends(get_current_active_user)
):
    """Stream agent response"""
    try:
        agent_service = AgentService()
        return await agent_service.stream(request.message, request.thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agent_status(
    current_user: str = Depends(get_current_active_user)
):
    """Get agent status"""
    try:
        agent_service = AgentService()
        return await agent_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))