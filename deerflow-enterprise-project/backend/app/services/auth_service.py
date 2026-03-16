"""
Authentication Service - JWT-based authentication and authorization
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models import User

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: Dict[str, str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, str]]:
        """
        Decode and validate a JWT access token

        Args:
            token: JWT token string

        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token decode error: {e}")
            return None

    @staticmethod
    def authenticate_user(
        db_session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user by username and password

        Args:
            db_session: Database session
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        from app.services import UserService

        user = UserService.get_user_by_username(db_session, username)
        if not user:
            return None

        if not user.is_active:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        # Update last login
        UserService.update_last_login(db_session, str(user.id))

        return user

    @staticmethod
    def create_refresh_token(
        data: Dict[str, str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Verify if a token is valid

        Args:
            token: JWT token string

        Returns:
            True if token is valid, False otherwise
        """
        return AuthService.decode_access_token(token) is not None

    @staticmethod
    def get_current_user_id(token: str) -> Optional[str]:
        """
        Get user ID from token

        Args:
            token: JWT token string

        Returns:
            User ID string or None
        """
        payload = AuthService.decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return user_id

    @staticmethod
    def create_token_pair(user_id: str) -> Dict[str, str]:
        """
        Create both access and refresh tokens for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = AuthService.create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

        refresh_token = AuthService.create_refresh_token(
            data={"sub": user_id},
            expires_delta=timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
