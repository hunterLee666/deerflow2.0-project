"""
案例 13: DeerFlow 2.0 API 网关
完整代码示例 - 统一入口、认证、限流
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from deerflow.client import DeerFlowClient
import time
import hashlib
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio


@dataclass
class APIKey:
    """API 密钥"""
    key: str
    name: str
    tier: str  # 'free', 'basic', 'premium'
    rate_limit: int  # 每分钟请求数
    quota: int  # 每月配额
    used: int = 0
    created_at: datetime = None
    last_used: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class APIKeyManager:
    """API 密钥管理器"""
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}
        self._load_default_keys()
    
    def _load_default_keys(self):
        """加载默认密钥"""
        # 测试密钥
        self.keys["test-key-001"] = APIKey(
            key="test-key-001",
            name="Test Account",
            tier="free",
            rate_limit=10,
            quota=1000
        )
        
        # 基础版密钥
        self.keys["basic-key-001"] = APIKey(
            key="basic-key-001",
            name="Basic Account",
            tier="basic",
            rate_limit=60,
            quota=10000
        )
        
        # 高级版密钥
        self.keys["premium-key-001"] = APIKey(
            key="premium-key-001",
            name="Premium Account",
            tier="premium",
            rate_limit=300,
            quota=100000
        )
    
    def validate_key(self, key: str) -> Optional[APIKey]:
        """验证 API 密钥"""
        api_key = self.keys.get(key)
        if api_key and api_key.used < api_key.quota:
            return api_key
        return None
    
    def use_key(self, key: str):
        """记录密钥使用"""
        if key in self.keys:
            self.keys[key].used += 1
            self.keys[key].last_used = datetime.now()
    
    def get_usage(self, key: str) -> Dict:
        """获取使用情况"""
        api_key = self.keys.get(key)
        if not api_key:
            return {}
        
        return {
            "tier": api_key.tier,
            "quota": api_key.quota,
            "used": api_key.used,
            "remaining": api_key.quota - api_key.used,
            "rate_limit": api_key.rate_limit
        }


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}  # key -> timestamps
        self.window = 60  # 60秒窗口
    
    def is_allowed(self, key: str, limit: int) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        # 清理旧请求
        if key in self.requests:
            self.requests[key] = [
                ts for ts in self.requests[key]
                if now - ts < self.window
            ]
        else:
            self.requests[key] = []
        
        # 检查限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 记录请求
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str, limit: int) -> int:
        """获取剩余配额"""
        now = time.time()
        
        if key in self.requests:
            recent = len([ts for ts in self.requests[key] if now - ts < self.window])
            return max(0, limit - recent)
        
        return limit


class DeerFlowGateway:
    """DeerFlow API 网关"""
    
    def __init__(self):
        self.app = FastAPI(
            title="DeerFlow API Gateway",
            description="统一的 DeerFlow API 入口",
            version="1.0.0"
        )
        
        self.client = DeerFlowClient()
        self.key_manager = APIKeyManager()
        self.rate_limiter = RateLimiter()
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """设置中间件"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 请求日志
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            print(f"{request.method} {request.url.path} - {response.status_code} - {duration:.2f}s")
            return response
    
    def _setup_routes(self):
        """设置路由"""
        security = HTTPBearer()
        
        async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
            """验证 API 密钥"""
            key = credentials.credentials
            api_key = self.key_manager.validate_key(key)
            
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired API key"
                )
            
            # 速率限制检查
            if not self.rate_limiter.is_allowed(key, api_key.rate_limit):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # 记录使用
            self.key_manager.use_key(key)
            
            return api_key
        
        @self.app.post("/v1/chat/completions")
        async def chat_completion(
            request: Request,
            api_key: APIKey = Depends(verify_api_key)
        ):
            """OpenAI 兼容的聊天接口"""
            body = await request.json()
            
            messages = body.get("messages", [])
            stream = body.get("stream", False)
            model = body.get("model", "gpt-4")
            
            # 转换消息格式
            if messages:
                last_message = messages[-1].get("content", "")
            else:
                last_message = ""
            
            # 调用 DeerFlow
            if stream:
                from fastapi.responses import StreamingResponse
                
                async def generate():
                    response_text = self.client.chat(last_message)
                    
                    # 模拟流式输出
                    chunk_size = 10
                    for i in range(0, len(response_text), chunk_size):
                        chunk = response_text[i:i+chunk_size]
                        data = {
                            "id": f"chatcmpl-{int(time.time())}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": chunk},
                                "finish_reason": None
                            }]
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                    
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(generate(), media_type="text/event-stream")
            
            else:
                response_text = self.client.chat(last_message)
                
                return {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_text
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(last_message.split()),
                        "completion_tokens": len(response_text.split()),
                        "total_tokens": len(last_message.split()) + len(response_text.split())
                    }
                }
        
        @self.app.get("/v1/models")
        async def list_models(api_key: APIKey = Depends(verify_api_key)):
            """列出可用模型"""
            return {
                "object": "list",
                "data": [
                    {
                        "id": "gpt-4",
                        "object": "model",
                        "created": 1677610602,
                        "owned_by": "deerflow"
                    },
                    {
                        "id": "gpt-3.5-turbo",
                        "object": "model",
                        "created": 1677610602,
                        "owned_by": "deerflow"
                    }
                ]
            }
        
        @self.app.get("/v1/usage")
        async def get_usage(api_key: APIKey = Depends(verify_api_key)):
            """获取使用情况"""
            # 从请求头中获取密钥
            key = api_key.key
            usage = self.key_manager.get_usage(key)
            remaining = self.rate_limiter.get_remaining(key, api_key.rate_limit)
            
            return {
                "tier": usage.get("tier"),
                "quota": usage.get("quota"),
                "used": usage.get("used"),
                "remaining_quota": usage.get("remaining"),
                "rate_limit": usage.get("rate_limit"),
                "rate_limit_remaining": remaining
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {"status": "healthy", "service": "deerflow-gateway"}


def create_gateway():
    """创建网关应用"""
    gateway = DeerFlowGateway()
    return gateway.app


if __name__ == "__main__":
    import uvicorn
    
    app = create_gateway()
    uvicorn.run(app, host="0.0.0.0", port=8000)
