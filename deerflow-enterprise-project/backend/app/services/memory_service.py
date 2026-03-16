"""
Memory Service - Business logic for long-term memory management
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.models import Memory, User, MemoryType
from app.core.database import get_db

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for memory-related operations"""

    @staticmethod
    def create_memory(
        db: Session,
        user_id: str,
        memory_type: MemoryType,
        content: str,
        category: str,
        confidence: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        thread_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Memory:
        """
        Create a new memory entry

        Args:
            db: Database session
            user_id: User ID
            memory_type: Type of memory
            content: Memory content
            category: Memory category
            confidence: Confidence score (0.0 to 1.0)
            context: Additional context
            source: Source of the memory
            thread_id: Related thread ID
            expires_at: Expiration timestamp

        Returns:
            Created Memory object
        """
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            category=category,
            confidence=confidence,
            context=context or {},
            source=source,
            thread_id=thread_id,
            expires_at=expires_at
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        logger.info(f"Created memory {memory.id} for user {user_id}")
        return memory

    @staticmethod
    def get_memory(db: Session, memory_id: str) -> Optional[Memory]:
        """Get memory by ID"""
        return db.get(Memory, memory_id)

    @staticmethod
    def list_memories(
        db: Session,
        user_id: str,
        memory_type: Optional[MemoryType] = None,
        category: Optional[str] = None,
        include_expired: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Memory]:
        """
        List memories for a user

        Args:
            db: Database session
            user_id: User ID
            memory_type: Filter by type
            category: Filter by category
            include_expired: Include expired memories
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of Memory objects
        """
        query = select(Memory).where(Memory.user_id == user_id)

        if memory_type:
            query = query.where(Memory.memory_type == memory_type)
        if category:
            query = query.where(Memory.category == category)
        if not include_expired:
            query = query.where(
                or_(
                    Memory.expires_at == None,
                    Memory.expires_at > datetime.now(timezone.utc)
                )
            )

        query = query.order_by(Memory.created_at.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def get_user_context(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get aggregated user context from memories

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with user context
        """
        memories = MemoryService.list_memories(
            db,
            user_id=user_id,
            memory_type=MemoryType.USER_CONTEXT,
            include_expired=False
        )

        context = {
            "user_context": {},
            "recent_memories": [],
            "facts": [],
            "preferences": []
        }

        for memory in memories:
            if memory.memory_type == MemoryType.USER_CONTEXT:
                context["user_context"][memory.category] = memory.content
            elif memory.memory_type == MemoryType.FACT:
                context["facts"].append({
                    "content": memory.content,
                    "category": memory.category,
                    "confidence": memory.confidence
                })
            elif memory.memory_type == MemoryType.PREFERENCE:
                context["preferences"].append({
                    "content": memory.content,
                    "category": memory.category
                })

        return context

    @staticmethod
    def search_memories(
        db: Session,
        user_id: str,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20
    ) -> List[Memory]:
        """
        Search memories by content

        Args:
            db: Database session
            user_id: User ID
            query: Search query
            memory_type: Filter by type
            limit: Maximum results

        Returns:
            List of matching Memory objects
        """
        query_stmt = select(Memory).where(
            and_(
                Memory.user_id == user_id,
                Memory.content.ilike(f"%{query}%")
            )
        )

        if memory_type:
            query_stmt = query_stmt.where(Memory.memory_type == memory_type)

        query_stmt = query_stmt.limit(limit)
        return db.execute(query_stmt).scalars().all()

    @staticmethod
    def update_memory(
        db: Session,
        memory_id: str,
        **kwargs
    ) -> Optional[Memory]:
        """
        Update memory entry

        Args:
            db: Database session
            memory_id: Memory ID
            **kwargs: Fields to update

        Returns:
            Updated Memory object or None
        """
        memory = MemoryService.get_memory(db, memory_id)
        if not memory:
            return None

        allowed_fields = {
            'content', 'category', 'confidence', 'context',
            'source', 'thread_id', 'expires_at', 'metadata_'
        }

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(memory, key, value)

        memory.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(memory)

        logger.info(f"Updated memory {memory_id}")
        return memory

    @staticmethod
    def delete_memory(db: Session, memory_id: str) -> bool:
        """Delete a memory entry"""
        memory = MemoryService.get_memory(db, memory_id)
        if not memory:
            return False

        db.delete(memory)
        db.commit()

        logger.info(f"Deleted memory {memory_id}")
        return True

    @staticmethod
    def cleanup_expired_memories(db: Session) -> int:
        """
        Delete expired memories

        Args:
            db: Database session

        Returns:
            Number of deleted memories
        """
        now = datetime.now(timezone.utc)
        result = db.execute(
            select(Memory).where(
                and_(
                    Memory.expires_at != None,
                    Memory.expires_at < now
                )
            )
        )

        memories = result.scalars().all()
        count = len(memories)

        for memory in memories:
            db.delete(memory)

        db.commit()
        logger.info(f"Cleaned up {count} expired memories")
        return count

    @staticmethod
    def get_conversation_history(
        db: Session,
        user_id: str,
        days: int = 30
    ) -> List[Memory]:
        """
        Get conversation history for a user

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back

        Returns:
            List of conversation memories
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return MemoryService.list_memories(
            db,
            user_id=user_id,
            memory_type=MemoryType.CONVERSATION,
            include_expired=True
        )
