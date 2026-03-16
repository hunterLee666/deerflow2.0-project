"""
Model tests for database models
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import User, Agent, Thread, Task, Memory, UserRole, AgentStatus, TaskStatus, MemoryType


class TestUserModel:
    """Test suite for User model"""

    def test_user_creation(self, db_session: Session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_default_values(self, db_session: Session):
        """Test user default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        assert user.full_name is None
        assert user.avatar_url is None
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.is_verified is False
        assert user.last_login_at is None

    def test_user_repr(self, db_session: Session):
        """Test user __repr__ method"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User"
        )
        db_session.add(user)
        db_session.commit()

        repr_str = repr(user)
        assert "User" in repr_str
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str


class TestAgentModel:
    """Test suite for Agent model"""

    def test_agent_creation(self, db_session: Session):
        """Test creating an agent"""
        # Create user first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        agent = Agent(
            name="Test Agent",
            slug="test-agent",
            description="A test agent",
            user_id=user.id,
            model_name="gpt-4",
            temperature=0.7,
            enabled_tools=["tool1", "tool2"],
            enabled_skills=["skill1"],
            sandbox_enabled=True,
            sandbox_mode="local"
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.id is not None
        assert agent.name == "Test Agent"
        assert agent.slug == "test-agent"
        assert agent.description == "A test agent"
        assert agent.user_id == user.id
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.7
        assert agent.enabled_tools == ["tool1", "tool2"]
        assert agent.enabled_skills == ["skill1"]
        assert agent.sandbox_enabled is True
        assert agent.sandbox_mode == "local"
        assert agent.status == AgentStatus.ACTIVE
        assert agent.version == 1
        assert agent.created_at is not None
        assert agent.updated_at is not None

    def test_agent_default_values(self, db_session: Session):
        """Test agent default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        agent = Agent(
            name="Test Agent",
            slug="test-agent",
            user_id=user.id
        )
        db_session.add(agent)
        db_session.commit()

        assert agent.description is None
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.7
        assert agent.enabled_tools == []
        assert agent.enabled_skills == []
        assert agent.sandbox_enabled is True
        assert agent.sandbox_mode == "local"
        assert agent.status == AgentStatus.ACTIVE

    def test_agent_repr(self, db_session: Session):
        """Test agent __repr__ method"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        agent = Agent(
            name="Test Agent",
            slug="test-agent",
            user_id=user.id
        )
        db_session.add(agent)
        db_session.commit()

        repr_str = repr(agent)
        assert "Agent" in repr_str
        assert "Test Agent" in repr_str
        assert "active" in repr_str.lower()


class TestThreadModel:
    """Test suite for Thread model"""

    def test_thread_creation(self, db_session: Session):
        """Test creating a thread"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        thread = Thread(
            title="Test Thread",
            user_id=user.id,
            messages=[{"role": "user", "content": "Hello"}],
            context={"key": "value"},
            artifacts=[{"type": "file", "name": "test.txt"}]
        )
        db_session.add(thread)
        db_session.commit()

        assert thread.id is not None
        assert thread.title == "Test Thread"
        assert thread.user_id == user.id
        assert thread.messages == [{"role": "user", "content": "Hello"}]
        assert thread.context == {"key": "value"}
        assert thread.artifacts == [{"type": "file", "name": "test.txt"}]
        assert thread.is_active is True
        assert thread.is_archived is False
        assert thread.created_at is not None
        assert thread.updated_at is not None

    def test_thread_default_values(self, db_session: Session):
        """Test thread default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        thread = Thread(
            user_id=user.id
        )
        db_session.add(thread)
        db_session.commit()

        assert thread.title is None
        assert thread.agent_id is None
        assert thread.messages == []
        assert thread.context == {}
        assert thread.artifacts == []
        assert thread.is_active is True
        assert thread.is_archived is False
        assert thread.metadata_ == {}

    def test_thread_repr(self, db_session: Session):
        """Test thread __repr__ method"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        thread = Thread(
            title="Test Thread",
            user_id=user.id
        )
        db_session.add(thread)
        db_session.commit()

        repr_str = repr(thread)
        assert "Thread" in repr_str
        assert "Test Thread" in repr_str


class TestTaskModel:
    """Test suite for Task model"""

    def test_task_creation(self, db_session: Session):
        """Test creating a task"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            name="Test Task",
            description="A test task",
            user_id=user.id,
            task_type="general-purpose",
            parameters={"param1": "value1"},
            max_turns=50,
            timeout=900.0,
            status=TaskStatus.PENDING,
            progress=0.0
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.name == "Test Task"
        assert task.description == "A test task"
        assert task.user_id == user.id
        assert task.task_type == "general-purpose"
        assert task.parameters == {"param1": "value1"}
        assert task.max_turns == 50
        assert task.timeout == 900.0
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_default_values(self, db_session: Session):
        """Test task default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            name="Test Task",
            user_id=user.id,
            task_type="test"
        )
        db_session.add(task)
        db_session.commit()

        assert task.description is None
        assert task.thread_id is None
        assert task.parent_task_id is None
        assert task.parameters == {}
        assert task.max_turns == 50
        assert task.timeout == 900.0
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0
        assert task.result is None
        assert task.error_message is None
        assert task.assigned_agent_id is None
        assert task.sub_agent_id is None
        assert task.started_at is None
        assert task.completed_at is None

    def test_task_repr(self, db_session: Session):
        """Test task __repr__ method"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        task = Task(
            name="Test Task",
            user_id=user.id,
            task_type="test"
        )
        db_session.add(task)
        db_session.commit()

        repr_str = repr(task)
        assert "Task" in repr_str
        assert "Test Task" in repr_str
        assert "pending" in repr_str.lower()


class TestMemoryModel:
    """Test suite for Memory model"""

    def test_memory_creation(self, db_session: Session):
        """Test creating a memory"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        memory = Memory(
            user_id=user.id,
            memory_type=MemoryType.FACT,
            category="test",
            content="This is a test fact",
            confidence=0.9,
            context={"source": "test"},
            source="manual"
        )
        db_session.add(memory)
        db_session.commit()

        assert memory.id is not None
        assert memory.user_id == user.id
        assert memory.memory_type == MemoryType.FACT
        assert memory.category == "test"
        assert memory.content == "This is a test fact"
        assert memory.confidence == 0.9
        assert memory.context == {"source": "test"}
        assert memory.source == "manual"
        assert memory.created_at is not None
        assert memory.updated_at is not None

    def test_memory_default_values(self, db_session: Session):
        """Test memory default values"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        memory = Memory(
            user_id=user.id,
            memory_type=MemoryType.FACT,
            category="test",
            content="Test content"
        )
        db_session.add(memory)
        db_session.commit()

        assert memory.confidence == 1.0
        assert memory.context is None
        assert memory.source is None
        assert memory.thread_id is None
        assert memory.expires_at is None
        assert memory.metadata_ == {}

    def test_memory_repr(self, db_session: Session):
        """Test memory __repr__ method"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()

        memory = Memory(
            user_id=user.id,
            memory_type=MemoryType.FACT,
            category="test",
            content="Test content"
        )
        db_session.add(memory)
        db_session.commit()

        repr_str = repr(memory)
        assert "Memory" in repr_str
        assert "fact" in repr_str.lower()
