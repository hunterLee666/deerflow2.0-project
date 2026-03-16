"""
Database Models for Enterprise AI Agent System

This module defines SQLAlchemy ORM models for the enterprise agent system.
All models use PostgreSQL as the primary database with UUID primary keys.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, ForeignKey,
    JSON, Integer, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum
import uuid

from app.core.database import Base
from .agent_config import AgentConfig


# ============================================================================
# ENUMERATIONS
# ============================================================================


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class AgentStatus(str, enum.Enum):
    """Agent lifecycle status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MemoryType(str, enum.Enum):
    """Types of memory entries"""
    USER_CONTEXT = "user_context"
    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"
    WORKFLOW = "workflow"


# ============================================================================
# USER MODEL
# ============================================================================


class User(Base):
    """User account model with RBAC support"""

    __tablename__ = "users"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    agents: Mapped[List["Agent"]] = relationship(
        "Agent",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    threads: Mapped[List["Thread"]] = relationship(
        "Thread",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    memories: Mapped[List["Memory"]] = relationship(
        "Memory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


# ============================================================================
# AGENT MODEL
# ============================================================================


class Agent(Base):
    """AI Agent configuration and state model"""

    __tablename__ = "agents"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Agent identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Owner reference
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # Agent configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    model_name: Mapped[str] = mapped_column(String(100), default="gpt-4")
    temperature: Mapped[float] = mapped_column(default=0.7)

    # Tool and skill permissions
    enabled_tools: Mapped[List[str]] = mapped_column(JSONB, default=list)
    enabled_skills: Mapped[List[str]] = mapped_column(JSONB, default=list)

    # Sandbox configuration
    sandbox_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sandbox_mode: Mapped[str] = mapped_column(String(50), default="local")

    # Status and metadata
    status: Mapped[AgentStatus] = mapped_column(SQLEnum(AgentStatus), default=AgentStatus.ACTIVE)
    version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="agents")
    threads: Mapped[List["Thread"]] = relationship(
        "Thread",
        back_populates="agent",
        cascade="all, delete-orphan"
    )
    sub_agents: Mapped[List["SubAgent"]] = relationship(
        "SubAgent",
        back_populates="parent_agent",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name={self.name}, status={self.status.value})>"


# ============================================================================
# THREAD MODEL
# ============================================================================


class Thread(Base):
    """Conversation thread between user and agent"""

    __tablename__ = "threads"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Thread metadata
    title: Mapped[Optional[str]] = mapped_column(String(500))
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        index=True
    )

    # Thread state
    messages: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    context: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    artifacts: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)

    # Status and tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="threads")
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="threads")
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="thread",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Thread(id={self.id}, title={self.title}, user_id={self.user_id})>"


# ============================================================================
# TASK MODEL
# ============================================================================


class Task(Base):
    """Task execution and tracking model"""

    __tablename__ = "tasks"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Task identification
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Execution context
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("threads.id", ondelete="SET NULL"),
        index=True
    )
    parent_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True
    )

    # Task configuration
    task_type: Mapped[str] = mapped_column(String(100))  # e.g., "general-purpose", "bash"
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    max_turns: Mapped[int] = mapped_column(Integer, default=50)
    timeout: Mapped[float] = mapped_column(default=900.0)  # 15 minutes

    # Execution state
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    progress: Mapped[float] = mapped_column(default=0.0)  # 0.0 to 1.0
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Agent assignment
    assigned_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    sub_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sub_agents.id", ondelete="SET NULL")
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    thread: Mapped[Optional["Thread"]] = relationship("Thread", back_populates="tasks")
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task",
        remote_side=[id],
        backref="sub_tasks"
    )
    sub_agent: Mapped[Optional["SubAgent"]] = relationship("SubAgent", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name={self.name}, status={self.status.value})>"


# ============================================================================
# SUB AGENT MODEL
# ============================================================================


class SubAgent(Base):
    """Sub-agent for delegated task execution"""

    __tablename__ = "sub_agents"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Sub-agent identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(100), default="general-purpose")
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Parent relationship
    parent_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        index=True
    )

    # Configuration
    config: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    enabled_tools: Mapped[List[str]] = mapped_column(JSONB, default=list)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_concurrent_tasks: Mapped[int] = mapped_column(Integer, default=3)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    parent_agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="sub_agents")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="sub_agent")

    def __repr__(self) -> str:
        return f"<SubAgent(id={self.id}, name={self.name}, type={self.agent_type})>"


# ============================================================================
# MEMORY MODEL
# ============================================================================


class Memory(Base):
    """Long-term memory storage for user context and facts"""

    __tablename__ = "memories"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Memory metadata
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    memory_type: Mapped[MemoryType] = mapped_column(SQLEnum(MemoryType))
    category: Mapped[str] = mapped_column(String(100), index=True)

    # Memory content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)

    # Context and confidence
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    confidence: Mapped[float] = mapped_column(default=1.0)
    source: Mapped[Optional[str]] = mapped_column(String(500))
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memories")

    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, type={self.memory_type.value}, user_id={self.user_id})>"


# ============================================================================
# AUDIT LOG MODEL
# ============================================================================


class AuditLog(Base):
    """Audit trail for security and compliance"""

    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Log metadata
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True
    )

    # Event details
    resource_type: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True)
    action: Mapped[str] = mapped_column(String(100))
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    # IP and user agent
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event={self.event_type}, action={self.action})>"
