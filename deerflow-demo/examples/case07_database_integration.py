"""
案例 7: DeerFlow 2.0 数据库集成
完整代码示例 - PostgreSQL + SQLAlchemy + DeerFlow
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from deerflow.client import DeerFlowClient
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

Base = declarative_base()


class Conversation(Base):
    """对话记录表"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(100), unique=True, index=True)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)


class Message(Base):
    """消息记录表"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String(100), index=True)
    role = Column(String(20))  # 'user', 'ai', 'tool'
    content = Column(Text)
    tool_calls = Column(JSON)
    tool_name = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_conversation(self, thread_id: str, title: str = None, metadata: dict = None) -> Conversation:
        """创建新对话"""
        session = self.Session()
        try:
            conversation = Conversation(
                thread_id=thread_id,
                title=title or f"对话 {thread_id[:8]}",
                metadata=metadata or {}
            )
            session.add(conversation)
            session.commit()
            return conversation
        finally:
            session.close()
    
    def save_message(self, thread_id: str, role: str, content: str, 
                     tool_calls: dict = None, tool_name: str = None):
        """保存消息"""
        session = self.Session()
        try:
            message = Message(
                thread_id=thread_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                tool_name=tool_name
            )
            session.add(message)
            session.commit()
        finally:
            session.close()
    
    def get_conversation_history(self, thread_id: str, limit: int = 50) -> List[Dict]:
        """获取对话历史"""
        session = self.Session()
        try:
            messages = session.query(Message).filter(
                Message.thread_id == thread_id
            ).order_by(Message.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "tool_name": msg.tool_name
                }
                for msg in reversed(messages)
            ]
        finally:
            session.close()
    
    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话列表"""
        session = self.Session()
        try:
            conversations = session.query(Conversation).order_by(
                Conversation.updated_at.desc()
            ).all()
            
            return [
                {
                    "thread_id": conv.thread_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        finally:
            session.close()


class DeerFlowWithDatabase:
    """集成数据库的 DeerFlow 客户端"""
    
    def __init__(self, database_url: str):
        self.client = DeerFlowClient()
        self.db = DatabaseManager(database_url)
    
    def chat_with_persistence(self, message: str, thread_id: Optional[str] = None) -> str:
        """
        带持久化的对话
        """
        # 生成 thread_id
        if not thread_id:
            thread_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 检查对话是否存在
        history = self.db.get_conversation_history(thread_id)
        if not history:
            # 创建新对话
            self.db.create_conversation(thread_id, title=message[:50])
        
        # 保存用户消息
        self.db.save_message(thread_id, "user", message)
        
        # 调用 DeerFlow
        response = self.client.chat(message, thread_id=thread_id)
        
        # 保存 AI 响应
        self.db.save_message(thread_id, "ai", response)
        
        return response
    
    def stream_with_persistence(self, message: str, thread_id: Optional[str] = None):
        """
        带持久化的流式对话
        """
        if not thread_id:
            thread_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 检查对话是否存在
        history = self.db.get_conversation_history(thread_id)
        if not history:
            self.db.create_conversation(thread_id, title=message[:50])
        
        # 保存用户消息
        self.db.save_message(thread_id, "user", message)
        
        # 流式处理
        full_response = []
        for event in self.client.stream(message, thread_id=thread_id):
            if event.type == "messages-tuple":
                if event.data.get("type") == "ai" and event.data.get("content"):
                    full_response.append(event.data["content"])
            yield event
        
        # 保存完整响应
        self.db.save_message(thread_id, "ai", "".join(full_response))
    
    def get_conversation(self, thread_id: str) -> Dict[str, Any]:
        """获取完整对话"""
        history = self.db.get_conversation_history(thread_id)
        return {
            "thread_id": thread_id,
            "messages": history
        }
    
    def list_conversations(self) -> List[Dict]:
        """列出所有对话"""
        return self.db.get_all_conversations()


def demonstrate_database_integration():
    """演示数据库集成"""
    
    print("=" * 60)
    print("DeerFlow 2.0 数据库集成演示")
    print("=" * 60)
    
    # 使用 SQLite 进行演示
    database_url = "sqlite:///deerflow_conversations.db"
    
    # 初始化
    deerflow_db = DeerFlowWithDatabase(database_url)
    
    print("\n1. 创建新对话")
    thread_id = "demo_thread_001"
    
    # 第一轮对话
    print("\n2. 第一轮对话")
    response1 = deerflow_db.chat_with_persistence(
        "什么是机器学习？",
        thread_id=thread_id
    )
    print(f"用户: 什么是机器学习？")
    print(f"AI: {response1[:200]}...")
    
    # 第二轮对话（保持上下文）
    print("\n3. 第二轮对话（保持上下文）")
    response2 = deerflow_db.chat_with_persistence(
        "深度学习呢？",
        thread_id=thread_id
    )
    print(f"用户: 深度学习呢？")
    print(f"AI: {response2[:200]}...")
    
    # 获取对话历史
    print("\n4. 获取对话历史")
    conversation = deerflow_db.get_conversation(thread_id)
    print(f"对话 ID: {conversation['thread_id']}")
    print(f"消息数量: {len(conversation['messages'])}")
    for msg in conversation['messages']:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")
    
    # 列出所有对话
    print("\n5. 所有对话列表")
    conversations = deerflow_db.list_conversations()
    for conv in conversations:
        print(f"  - {conv['title']} ({conv['thread_id']})")
    
    print("\n数据库文件: deerflow_conversations.db")


if __name__ == "__main__":
    demonstrate_database_integration()
