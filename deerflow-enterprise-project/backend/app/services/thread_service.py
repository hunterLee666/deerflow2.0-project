"""
Thread Service - Business logic for conversation threads
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Thread, User, Agent
from app.core.database import get_db

logger = logging.getLogger(__name__)


class ThreadService:
    """Service for thread-related operations"""

    @staticmethod
    def create_thread(
        db: Session,
        user_id: str,
        title: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> Thread:
        """
        Create a new conversation thread

        Args:
            db: Database session
            user_id: User ID who owns the thread
            title: Optional thread title
            agent_id: Optional agent ID to associate with

        Returns:
            Created Thread object
        """
        thread = Thread(
            title=title,
            user_id=user_id,
            agent_id=agent_id,
            messages=[],
            context={},
            artifacts=[]
        )

        db.add(thread)
        db.commit()
        db.refresh(thread)

        logger.info(f"Created thread {thread.id} for user {user_id}")
        return thread

    @staticmethod
    def get_thread(db: Session, thread_id: str) -> Optional[Thread]:
        """Get thread by ID"""
        return db.get(Thread, thread_id)

    @staticmethod
    def get_thread_by_user(
        db: Session,
        thread_id: str,
        user_id: str
    ) -> Optional[Thread]:
        """Get thread by ID and verify ownership"""
        thread = ThreadService.get_thread(db, thread_id)
        if thread and thread.user_id == user_id:
            return thread
        return None

    @staticmethod
    def list_threads(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        include_archived: bool = False
    ) -> List[Thread]:
        """
        List threads for a user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_archived: Include archived threads

        Returns:
            List of Thread objects
        """
        query = select(Thread).where(Thread.user_id == user_id)

        if not include_archived:
            query = query.where(Thread.is_archived == False)

        query = query.order_by(Thread.last_message_at.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def update_thread(
        db: Session,
        thread_id: str,
        **kwargs
    ) -> Optional[Thread]:
        """
        Update thread properties

        Args:
            db: Database session
            thread_id: Thread ID
            **kwargs: Fields to update

        Returns:
            Updated Thread object or None
        """
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return None

        allowed_fields = {
            'title', 'messages', 'context', 'artifacts',
            'is_active', 'is_archived', 'metadata_'
        }

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(thread, key, value)

        thread.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(thread)

        logger.info(f"Updated thread {thread_id}")
        return thread

    @staticmethod
    def add_message(
        db: Session,
        thread_id: str,
        message: dict
    ) -> Optional[Thread]:
        """
        Add a message to thread

        Args:
            db: Database session
            thread_id: Thread ID
            message: Message dictionary

        Returns:
            Updated Thread object or None
        """
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return None

        # Append message
        thread.messages.append(message)
        thread.last_message_at = datetime.now(timezone.utc)
        thread.updated_at = datetime.now(timezone.utc)

        # Auto-generate title if not set and this is the first user message
        if not thread.title and message.get('role') == 'user':
            content = message.get('content', '')
            thread.title = content[:100] if len(content) <= 100 else content[:97] + "..."

        db.commit()
        db.refresh(thread)

        return thread

    @staticmethod
    def add_artifact(
        db: Session,
        thread_id: str,
        artifact: dict
    ) -> Optional[Thread]:
        """
        Add an artifact to thread

        Args:
            db: Database session
            thread_id: Thread ID
            artifact: Artifact dictionary

        Returns:
            Updated Thread object or None
        """
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return None

        thread.artifacts.append(artifact)
        thread.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(thread)

        logger.info(f"Added artifact to thread {thread_id}")
        return thread

    @staticmethod
    def archive_thread(db: Session, thread_id: str) -> bool:
        """Archive a thread"""
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return False

        thread.is_archived = True
        thread.is_active = False
        thread.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Archived thread {thread_id}")
        return True

    @staticmethod
    def unarchive_thread(db: Session, thread_id: str) -> bool:
        """Unarchive a thread"""
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return False

        thread.is_archived = False
        thread.is_active = True
        thread.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Unarchived thread {thread_id}")
        return True

    @staticmethod
    def delete_thread(db: Session, thread_id: str) -> bool:
        """Delete a thread"""
        thread = ThreadService.get_thread(db, thread_id)
        if not thread:
            return False

        db.delete(thread)
        db.commit()

        logger.info(f"Deleted thread {thread_id}")
        return True

    @staticmethod
    def search_threads(
        db: Session,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Thread]:
        """
        Search threads by title or message content

        Args:
            db: Database session
            user_id: User ID
            query: Search query
            limit: Maximum results

        Returns:
            List of matching Thread objects
        """
        # Search by title
        threads = db.execute(
            select(Thread)
            .where(Thread.user_id == user_id)
            .where(Thread.is_archived == False)
            .where(Thread.title.ilike(f"%{query}%"))
            .limit(limit)
        ).scalars().all()

        return threads
