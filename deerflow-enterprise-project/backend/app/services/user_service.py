"""
User Service - Business logic for user management and authentication
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
import bcrypt

from app.models import User, UserRole
from app.core.database import get_db

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related operations"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Create a new user account

        Args:
            db: Database session
            email: User email address
            username: Username
            password: Plain text password (will be hashed)
            full_name: Optional full name
            role: User role

        Returns:
            Created User object

        Raises:
            ValueError: If email or username already exists
        """
        # Check if user already exists
        existing = db.execute(
            select(User).where((User.email == email) | (User.username == username))
        ).scalar_one_or_none()

        if existing:
            raise ValueError("Email or username already exists")

        # Create new user
        user = User(
            email=email,
            username=username,
            hashed_password=UserService.hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new user: {user.username} ({user.email})")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.get(User, user_id)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        **kwargs
    ) -> Optional[User]:
        """
        Update user profile

        Args:
            db: Database session
            user_id: User ID
            **kwargs: Fields to update (full_name, avatar_url, role, etc.)

        Returns:
            Updated User object or None
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        # Update allowed fields
        allowed_fields = {
            'full_name', 'avatar_url', 'role', 'is_active', 'is_verified'
        }

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        logger.info(f"Updated user: {user.username}")
        return user

    @staticmethod
    def update_last_login(db: Session, user_id: str) -> None:
        """Update user's last login timestamp"""
        user = UserService.get_user_by_id(db, user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Updated last login for user: {user.username}")

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Soft delete a user by marking as inactive"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Soft deleted user: {user.username}")
        return True

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with optional filters"""
        query = select(User)

        if role is not None:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        query = query.offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password

        Args:
            db: Database session
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        # Verify old password
        if not UserService.verify_password(old_password, user.hashed_password):
            return False

        # Update password
        user.hashed_password = UserService.hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Changed password for user: {user.username}")
        return True
