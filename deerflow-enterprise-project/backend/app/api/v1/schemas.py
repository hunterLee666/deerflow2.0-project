"""
Pydantic Schemas for API Validation and Serialization

This module defines Pydantic schemas for request validation
and response serialization for the API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


# ============================================================================
# ENUMERATIONS
# ============================================================================


class UserRoleEnum(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class AgentStatusEnum(str, Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class TaskStatusEnum(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MemoryTypeEnum(str, Enum):
    """Memory type enumeration"""
    USER_CONTEXT = "user_context"
    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"
    WORKFLOW = "workflow"


# ============================================================================
# USER SCHEMAS
# ============================================================================


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# AGENT SCHEMAS
# ============================================================================


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    model_name: str = Field(default="gpt-4", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    enabled_tools: List[str] = Field(default_factory=list)
    enabled_skills: List[str] = Field(default_factory=list)
    sandbox_enabled: bool = True
    sandbox_mode: str = "local"


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    enabled_tools: Optional[List[str]] = None
    enabled_skills: Optional[List[str]] = None
    sandbox_enabled: Optional[bool] = None
    sandbox_mode: Optional[str] = None
    status: Optional[AgentStatusEnum] = None


class AgentResponse(AgentBase):
    """Schema for agent response"""
    id: UUID
    user_id: UUID
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled_tools: List[str] = Field(default_factory=list)
    enabled_skills: List[str] = Field(default_factory=list)
    sandbox_enabled: bool
    sandbox_mode: str
    status: AgentStatusEnum
    version: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# THREAD SCHEMAS
# ============================================================================


class ThreadBase(BaseModel):
    """Base thread schema"""
    title: Optional[str] = Field(None, max_length=500)
    agent_id: Optional[UUID] = None


class ThreadCreate(ThreadBase):
    """Schema for creating a thread"""
    pass


class ThreadUpdate(BaseModel):
    """Schema for updating a thread"""
    title: Optional[str] = Field(None, max_length=500)
    messages: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    is_archived: Optional[bool] = None


class ThreadResponse(BaseModel):
    """Schema for thread response"""
    id: UUID
    title: Optional[str]
    user_id: UUID
    agent_id: Optional[UUID]
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool
    is_archived: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# TASK SCHEMAS
# ============================================================================


class TaskBase(BaseModel):
    """Base task schema"""
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    task_type: str = Field(..., max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    thread_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    max_turns: int = Field(default=50, ge=1)
    timeout: float = Field(default=900.0, ge=1.0)


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    status: Optional[TaskStatusEnum] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    id: UUID
    name: str
    description: Optional[str]
    user_id: UUID
    thread_id: Optional[UUID]
    parent_task_id: Optional[UUID]
    task_type: str
    parameters: Dict[str, Any]
    max_turns: int
    timeout: float
    status: TaskStatusEnum
    progress: float
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    assigned_agent_id: Optional[UUID]
    sub_agent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# MEMORY SCHEMAS
# ============================================================================


class MemoryBase(BaseModel):
    """Base memory schema"""
    memory_type: MemoryTypeEnum
    content: str = Field(..., min_length=1)
    category: str = Field(..., max_length=100)


class MemoryCreate(MemoryBase):
    """Schema for creating a memory"""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    thread_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class MemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    thread_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class MemoryResponse(BaseModel):
    """Schema for memory response"""
    id: UUID
    user_id: UUID
    memory_type: MemoryTypeEnum
    category: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]]
    confidence: float
    source: Optional[str]
    thread_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# AUTH SCHEMAS
# ============================================================================


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[UUID] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================


class PaginatedResponse(BaseModel):
    """Generic paginated response schema"""
    items: List[Any]
    total: int
    skip: int
    limit: int


# ============================================================================
# RESPONSE WRAPPER
# ============================================================================


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
