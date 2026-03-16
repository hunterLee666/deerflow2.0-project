"""
案例 11: DeerFlow 2.0 记忆系统增强
完整代码示例 - 长期记忆、上下文管理
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    category: str  # 'fact', 'preference', 'context', 'summary'
    importance: float  # 0-1
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    related_threads: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class EnhancedMemorySystem:
    """增强型记忆系统"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
        self.memories: Dict[str, MemoryEntry] = {}
        self.thread_memories: Dict[str, List[str]] = {}  # thread_id -> memory_ids
        self.short_term_buffer: List[Dict] = []  # 短期记忆缓冲
        self.max_buffer_size = 10
    
    def _generate_id(self, content: str) -> str:
        """生成记忆ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_memory(
        self,
        content: str,
        category: str = "fact",
        importance: float = 0.5,
        thread_id: Optional[str] = None,
        metadata: Dict = None
    ) -> str:
        """添加记忆"""
        memory_id = self._generate_id(content)
        
        if memory_id in self.memories:
            # 更新现有记忆
            self.memories[memory_id].access_count += 1
            self.memories[memory_id].last_accessed = datetime.now()
        else:
            # 创建新记忆
            memory = MemoryEntry(
                id=memory_id,
                content=content,
                category=category,
                importance=importance,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                metadata=metadata or {}
            )
            self.memories[memory_id] = memory
        
        # 关联到对话线程
        if thread_id:
            if thread_id not in self.thread_memories:
                self.thread_memories[thread_id] = []
            if memory_id not in self.thread_memories[thread_id]:
                self.thread_memories[thread_id].append(memory_id)
                self.memories[memory_id].related_threads.append(thread_id)
        
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取记忆"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
        return memory
    
    def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        min_importance: float = 0.0,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """搜索记忆"""
        results = []
        
        for memory in self.memories.values():
            # 类别过滤
            if category and memory.category != category:
                continue
            
            # 重要性过滤
            if memory.importance < min_importance:
                continue
            
            # 简单关键词匹配（实际应用应使用向量搜索）
            if query.lower() in memory.content.lower():
                results.append(memory)
        
        # 按重要性排序
        results.sort(key=lambda m: m.importance, reverse=True)
        return results[:limit]
    
    def get_thread_context(self, thread_id: str) -> List[MemoryEntry]:
        """获取对话线程的上下文记忆"""
        memory_ids = self.thread_memories.get(thread_id, [])
        return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def add_to_short_term(self, message: Dict):
        """添加到短期记忆"""
        self.short_term_buffer.append({
            **message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持缓冲区大小
        if len(self.short_term_buffer) > self.max_buffer_size:
            self.short_term_buffer.pop(0)
    
    def consolidate_memories(self, thread_id: str):
        """整合短期记忆到长期记忆"""
        if not self.short_term_buffer:
            return
        
        # 提取关键信息
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in self.short_term_buffer
        ])
        
        # 使用 DeerFlow 生成摘要
        prompt = f"""请从以下对话中提取关键事实和偏好:

{conversation_text}

请提取:
1. 用户提到的关键事实
2. 用户的偏好或要求
3. 重要的上下文信息

以 JSON 格式返回:
{{
    "facts": ["事实1", "事实2"],
    "preferences": ["偏好1", "偏好2"],
    "context": ["上下文1"]
}}"""
        
        try:
            response = self.client.chat(prompt, thread_id=f"memory-consolidation-{thread_id}")
            
            # 解析响应并添加为记忆
            # 简化处理：将响应内容作为记忆
            self.add_memory(
                content=response,
                category="summary",
                importance=0.7,
                thread_id=thread_id
            )
            
            # 清空短期记忆
            self.short_term_buffer.clear()
            
        except Exception as e:
            print(f"记忆整合失败: {e}")
    
    def get_relevant_context(
        self,
        query: str,
        thread_id: Optional[str] = None,
        max_tokens: int = 2000
    ) -> str:
        """获取相关上下文"""
        context_parts = []
        
        # 1. 线程特定记忆
        if thread_id:
            thread_memories = self.get_thread_context(thread_id)
            for memory in sorted(thread_memories, key=lambda m: m.importance, reverse=True)[:3]:
                context_parts.append(f"[历史] {memory.content}")
        
        # 2. 全局相关记忆
        relevant = self.search_memories(query, limit=5)
        for memory in relevant:
            if memory not in thread_memories:
                context_parts.append(f"[知识] {memory.content}")
        
        # 3. 短期记忆
        for msg in self.short_term_buffer[-3:]:
            context_parts.append(f"[近期] {msg.get('role', 'unknown')}: {msg.get('content', '')}")
        
        # 合并并截断
        context = "\n".join(context_parts)
        if len(context) > max_tokens * 4:  # 粗略估计
            context = context[:max_tokens * 4]
        
        return context
    
    def chat_with_memory(
        self,
        message: str,
        thread_id: Optional[str] = None,
        use_memory: bool = True
    ) -> str:
        """带记忆的对话"""
        
        # 添加到短期记忆
        self.add_to_short_term({"role": "user", "content": message})
        
        # 构建提示词
        if use_memory and thread_id:
            context = self.get_relevant_context(message, thread_id)
            prompt = f"""基于以下上下文回答问题:

{context}

用户问题: {message}

请结合上下文提供准确的回答。"""
        else:
            prompt = message
        
        # 调用 DeerFlow
        response = self.client.chat(prompt, thread_id=thread_id)
        
        # 添加到短期记忆
        self.add_to_short_term({"role": "assistant", "content": response})
        
        # 定期整合记忆
        if len(self.short_term_buffer) >= self.max_buffer_size:
            self.consolidate_memories(thread_id or "default")
        
        return response
    
    def export_memories(self, filepath: str):
        """导出记忆到文件"""
        data = {
            "memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "category": m.category,
                    "importance": m.importance,
                    "created_at": m.created_at.isoformat(),
                    "access_count": m.access_count
                }
                for m in self.memories.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_memories(self, filepath: str):
        """从文件导入记忆"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for item in data.get("memories", []):
            self.add_memory(
                content=item["content"],
                category=item.get("category", "fact"),
                importance=item.get("importance", 0.5)
            )


# 使用示例
def demonstrate_memory_system():
    """演示记忆系统"""
    
    print("=" * 60)
    print("DeerFlow 2.0 记忆系统演示")
    print("=" * 60)
    
    memory_system = EnhancedMemorySystem()
    thread_id = "demo-thread-001"
    
    # 1. 添加初始记忆
    print("\n1. 添加用户偏好记忆")
    memory_system.add_memory(
        content="用户喜欢简洁的回答，不喜欢冗长的解释",
        category="preference",
        importance=0.8,
        thread_id=thread_id
    )
    
    memory_system.add_memory(
        content="用户是 Python 开发者，熟悉机器学习",
        category="fact",
        importance=0.9,
        thread_id=thread_id
    )
    
    # 2. 多轮对话
    print("\n2. 多轮对话（带记忆）")
    
    questions = [
        "我应该学习什么新技术？",
        "能推荐一些学习资源吗？",
        "之前说的那个技术有什么优缺点？"
    ]
    
    for question in questions:
        print(f"\n用户: {question}")
        response = memory_system.chat_with_memory(
            question,
            thread_id=thread_id
        )
        print(f"AI: {response[:200]}...")
    
    # 3. 搜索记忆
    print("\n3. 搜索记忆")
    results = memory_system.search_memories("Python", category="fact")
    print(f"找到 {len(results)} 条相关记忆:")
    for memory in results:
        print(f"  - [{memory.category}] {memory.content}")
    
    # 4. 获取线程上下文
    print("\n4. 线程上下文")
    context = memory_system.get_thread_context(thread_id)
    print(f"线程 {thread_id} 有 {len(context)} 条记忆")
    
    # 5. 导出记忆
    print("\n5. 导出记忆")
    memory_system.export_memories("memories.json")
    print("记忆已导出到 memories.json")


if __name__ == "__main__":
    demonstrate_memory_system()
