"""
案例 3: DeerFlow 2.0 + FastAPI 完整 Web 服务
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio

from deerflow.client import DeerFlowClient, StreamEvent
from langgraph.checkpoint.memory import MemorySaver

# 创建 FastAPI 应用
app = FastAPI(
    title="DeerFlow 2.0 API Service",
    description="基于 DeerFlow 2.0 的 AI 服务 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局客户端实例
client = DeerFlowClient(
    checkpointer=MemorySaver(),
    thinking_enabled=True,
    subagent_enabled=True
)


# Pydantic 模型
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    model_name: Optional[str] = None
    thinking_enabled: Optional[bool] = None
    subagent_enabled: Optional[bool] = None
    plan_mode: Optional[bool] = None


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    status: str = "success"


class StreamRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


# API 路由
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    非流式对话接口
    """
    try:
        kwargs = {}
        if request.model_name:
            kwargs["model_name"] = request.model_name
        if request.thinking_enabled is not None:
            kwargs["thinking_enabled"] = request.thinking_enabled
        if request.subagent_enabled is not None:
            kwargs["subagent_enabled"] = request.subagent_enabled
        if request.plan_mode is not None:
            kwargs["plan_mode"] = request.plan_mode
        
        response = client.chat(
            request.message,
            thread_id=request.thread_id,
            **kwargs
        )
        
        return ChatResponse(
            response=response,
            thread_id=request.thread_id or "new-thread"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: StreamRequest):
    """
    流式对话接口 (SSE)
    """
    async def event_generator():
        loop = asyncio.get_event_loop()
        
        # 在线程池中运行同步的 stream
        def stream_sync():
            return list(client.stream(
                request.message,
                thread_id=request.thread_id
            ))
        
        events = await loop.run_in_executor(None, stream_sync)
        
        for event in events:
            if event.type == "messages-tuple":
                yield f"data: {json.dumps({
                    'type': 'message',
                    'data': event.data
                })}\n\n"
            elif event.type == "values":
                yield f"data: {json.dumps({
                    'type': 'state',
                    'data': {
                        'title': event.data.get('title'),
                        'message_count': len(event.data.get('messages', []))
                    }
                })}\n\n"
            elif event.type == "end":
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/api/models")
async def list_models():
    """
    获取可用模型列表
    """
    try:
        return client.list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def list_skills(enabled_only: bool = False):
    """
    获取可用技能列表
    """
    try:
        return client.list_skills(enabled_only=enabled_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills/{skill_name}")
async def get_skill(skill_name: str):
    """
    获取特定技能信息
    """
    try:
        skill = client.get_skill(skill_name)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill {skill_name} not found")
        return skill
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory")
async def get_memory():
    """
    获取当前内存数据
    """
    try:
        return client.get_memory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    健康检查
    """
    return {"status": "healthy", "service": "deerflow-api"}


# 启动命令: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
