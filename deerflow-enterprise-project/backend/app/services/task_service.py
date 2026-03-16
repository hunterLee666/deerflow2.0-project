"""
Task Service - Business logic for task execution and tracking
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
import asyncio

from app.models import Task, User, Thread, TaskStatus
from app.core.database import get_db

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task-related operations"""

    @staticmethod
    def create_task(
        db: Session,
        user_id: str,
        name: str,
        task_type: str,
        description: Optional[str] = None,
        thread_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        max_turns: int = 50,
        timeout: float = 900.0,
        parent_task_id: Optional[str] = None
    ) -> Task:
        """
        Create a new task

        Args:
            db: Database session
            user_id: User ID
            name: Task name
            task_type: Type of task (e.g., "general-purpose", "bash")
            description: Optional description
            thread_id: Optional associated thread ID
            parameters: Task parameters
            max_turns: Maximum execution turns
            timeout: Timeout in seconds
            parent_task_id: Parent task ID for sub-tasks

        Returns:
            Created Task object
        """
        task = Task(
            name=name,
            description=description,
            user_id=user_id,
            thread_id=thread_id,
            parent_task_id=parent_task_id,
            task_type=task_type,
            parameters=parameters or {},
            max_turns=max_turns,
            timeout=timeout,
            status=TaskStatus.PENDING,
            progress=0.0
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")
        return task

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return db.get(Task, task_id)

    @staticmethod
    def get_task_by_user(
        db: Session,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """Get task by ID and verify user ownership"""
        task = TaskService.get_task(db, task_id)
        if task and task.user_id == user_id:
            return task
        return None

    @staticmethod
    def list_tasks(
        db: Session,
        user_id: str,
        status: Optional[TaskStatus] = None,
        thread_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Task]:
        """
        List tasks for a user

        Args:
            db: Database session
            user_id: User ID
            status: Filter by status
            thread_id: Filter by thread
            skip: Number to skip
            limit: Maximum to return

        Returns:
            List of Task objects
        """
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
        if thread_id:
            query = query.where(Task.thread_id == thread_id)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def update_task_status(
        db: Session,
        task_id: str,
        status: TaskStatus,
        progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update task status and progress

        Args:
            db: Database session
            task_id: Task ID
            status: New status
            progress: Progress percentage (0.0 to 1.0)
            result: Task result data
            error_message: Error message if failed

        Returns:
            Updated Task object or None
        """
        task = TaskService.get_task(db, task_id)
        if not task:
            return None

        task.status = status
        if progress is not None:
            task.progress = progress
        if result is not None:
            task.result = result
        if error_message is not None:
            task.error_message = error_message
            task.status = TaskStatus.FAILED

        # Update timestamps
        if status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.now(timezone.utc)

        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)

        logger.info(f"Updated task {task_id} to status {status.value}")
        return task

    @staticmethod
    def mark_running(db: Session, task_id: str) -> Optional[Task]:
        """Mark task as running"""
        return TaskService.update_task_status(
            db,
            task_id,
            TaskStatus.RUNNING
        )

    @staticmethod
    def mark_completed(
        db: Session,
        task_id: str,
        result: Dict[str, Any]
    ) -> Optional[Task]:
        """Mark task as completed"""
        return TaskService.update_task_status(
            db,
            task_id,
            TaskStatus.COMPLETED,
            progress=1.0,
            result=result
        )

    @staticmethod
    def mark_failed(
        db: Session,
        task_id: str,
        error_message: str
    ) -> Optional[Task]:
        """Mark task as failed"""
        return TaskService.update_task_status(
            db,
            task_id,
            TaskStatus.FAILED,
            error_message=error_message
        )

    @staticmethod
    def cancel_task(db: Session, task_id: str) -> Optional[Task]:
        """Cancel a task"""
        return TaskService.update_task_status(
            db,
            task_id,
            TaskStatus.CANCELLED
        )

    @staticmethod
    def get_sub_tasks(db: Session, task_id: str) -> List[Task]:
        """Get all sub-tasks of a task"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return []

        return db.execute(
            select(Task).where(Task.parent_task_id == task_id)
        ).scalars().all()

    @staticmethod
    def delete_task(db: Session, task_id: str) -> bool:
        """Delete a task"""
        task = TaskService.get_task(db, task_id)
        if not task:
            return False

        db.delete(task)
        db.commit()

        logger.info(f"Deleted task {task_id}")
        return True

    @staticmethod
    async def execute_task(
        db: Session,
        task_id: str,
        agent_executor: Any  # This would be the DeerFlow agent executor
    ) -> Dict[str, Any]:
        """
        Execute a task using the agent system

        Args:
            db: Database session
            task_id: Task ID
            agent_executor: Agent executor instance

        Returns:
            Task execution result
        """
        task = TaskService.get_task(db, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not in PENDING state")

        try:
            # Mark as running
            TaskService.mark_running(db, task_id)

            # Execute task (this would integrate with DeerFlow harness)
            logger.info(f"Executing task {task_id}: {task.name}")

            # TODO: Integrate with DeerFlow agent executor
            # result = await agent_executor.execute(
            #     task=task.parameters.get("instruction", ""),
            #     agent_type=task.task_type,
            #     max_turns=task.max_turns,
            #     timeout=task.timeout
            # )

            # For now, simulate execution
            await asyncio.sleep(1)
            result = {
                "status": "success",
                "output": f"Executed task: {task.name}",
                "details": {}
            }

            # Mark as completed
            TaskService.mark_completed(db, task_id, result)

            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Task {task_id} execution failed: {error_msg}")
            TaskService.mark_failed(db, task_id, error_msg)
            raise

    @staticmethod
    def get_task_stats(db: Session, user_id: str) -> Dict[str, int]:
        """
        Get task statistics for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with task counts by status
        """
        tasks = TaskService.list_tasks(db, user_id)

        stats = {
            "total": len(tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }

        for task in tasks:
            status = task.status.value
            if status in stats:
                stats[status] += 1

        return stats
