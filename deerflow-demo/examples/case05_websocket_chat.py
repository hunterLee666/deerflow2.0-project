"""
案例 5: DeerFlow 2.0 WebSocket 实时对话
完整代码示例
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from deerflow.client import DeerFlowClient
import json
import asyncio
from typing import Dict, Set

app = FastAPI()
client = DeerFlowClient(
    thinking_enabled=True,
    subagent_enabled=True
)

# 存储活跃连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket 实时对话端点
    """
    await manager.connect(websocket, client_id)
    thread_id = None
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            message = data.get("message", "")
            thread_id = data.get("thread_id", thread_id)
            
            # 发送开始标记
            await manager.send_message(client_id, {
                "type": "start",
                "thread_id": thread_id
            })
            
            # 在后台线程中运行 DeerFlow
            loop = asyncio.get_event_loop()
            
            def stream_response():
                events = []
                for event in client.stream(message, thread_id=thread_id):
                    events.append(event)
                return events
            
            # 执行流式对话
            events = await loop.run_in_executor(None, stream_response)
            
            # 发送事件流
            for event in events:
                if event.type == "messages-tuple":
                    await manager.send_message(client_id, {
                        "type": "message",
                        "data": event.data
                    })
                elif event.type == "values":
                    await manager.send_message(client_id, {
                        "type": "state",
                        "data": {
                            "title": event.data.get("title"),
                            "message_count": len(event.data.get("messages", []))
                        }
                    })
                elif event.type == "end":
                    await manager.send_message(client_id, {
                        "type": "end",
                        "thread_id": thread_id
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client {client_id} disconnected")
    except Exception as e:
        await manager.send_message(client_id, {
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()


# 简单的 Web 客户端页面
@app.get("/")
async def get():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DeerFlow 2.0 WebSocket Chat</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            #messages { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .message { margin: 5px 0; padding: 8px; border-radius: 4px; }
            .user { background: #e3f2fd; text-align: right; }
            .ai { background: #f5f5f5; text-align: left; }
            .tool { background: #fff3e0; font-size: 0.9em; }
            #input-area { display: flex; gap: 10px; }
            #message-input { flex: 1; padding: 10px; }
            button { padding: 10px 20px; background: #2196f3; color: white; border: none; cursor: pointer; }
            button:hover { background: #1976d2; }
            .status { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>DeerFlow 2.0 实时对话</h1>
        <div id="status" class="status">状态: 未连接</div>
        <div id="messages"></div>
        <div id="input-area">
            <input type="text" id="message-input" placeholder="输入消息..." />
            <button onclick="sendMessage()">发送</button>
        </div>
        
        <script>
            const clientId = 'user-' + Math.random().toString(36).substr(2, 9);
            const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
            let currentThreadId = null;
            
            ws.onopen = function() {
                document.getElementById('status').textContent = '状态: 已连接';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'start') {
                    currentThreadId = data.thread_id;
                    addMessage('系统', '开始处理...', 'status');
                } else if (data.type === 'message') {
                    const msg = data.data;
                    if (msg.type === 'ai' && msg.content) {
                        addMessage('AI', msg.content, 'ai');
                    } else if (msg.type === 'tool') {
                        addMessage('工具', `${msg.name}: ${msg.content.substring(0, 100)}...`, 'tool');
                    }
                } else if (data.type === 'end') {
                    addMessage('系统', '处理完成', 'status');
                } else if (data.type === 'error') {
                    addMessage('错误', data.message, 'status');
                }
            };
            
            ws.onclose = function() {
                document.getElementById('status').textContent = '状态: 已断开';
            };
            
            function addMessage(sender, text, className) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.className = `message ${className}`;
                div.innerHTML = `<strong>${sender}:</strong> ${text}`;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (message && ws.readyState === WebSocket.OPEN) {
                    addMessage('你', message, 'user');
                    ws.send(JSON.stringify({
                        message: message,
                        thread_id: currentThreadId
                    }));
                    input.value = '';
                }
            }
            
            document.getElementById('message-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
