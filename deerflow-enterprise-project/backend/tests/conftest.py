"""
Pytest configuration and fixtures
"""

import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://localhost/deerflow_test"

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.services import UserService
from app.models import User

import os
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# Test database URL

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """
    Create a test user
    """
    user = UserService.create_user(
        db=db_session,
        email="test@example.com",
        username="testuser",
        password="password123",
        full_name="Test User"
    )
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user: User, db_session: Session) -> dict:
    """
    Create authentication headers with valid token
    """
    from app.services import AuthService

    tokens = AuthService.create_token_pair(str(test_user.id))
    return {
        "Authorization": f"Bearer {tokens['access_token']}"
    }
