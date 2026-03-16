"""
Unit tests for Authentication Service
"""

import pytest
from datetime import timedelta
from jose import jwt
from app.models import User
from app.services.auth_service import AuthService
from app.core.config import settings


class TestAuthService:
    """Test suite for AuthService"""

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        plain_password = "testpassword123"
        hashed_password = AuthService.get_password_hash(plain_password)

        assert AuthService.verify_password(plain_password, hashed_password) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        plain_password = "testpassword123"
        hashed_password = AuthService.get_password_hash(plain_password)

        assert AuthService.verify_password("wrongpassword", hashed_password) is False

    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user-id-123", "username": "testuser"}
        token = AuthService.create_access_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "user-id-123"
        assert payload["username"] == "testuser"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "user-id-123"}
        expires_delta = timedelta(minutes=30)
        token = AuthService.create_access_token(data, expires_delta)

        assert token is not None

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "user-id-123"

    def test_decode_access_token_valid(self):
        """Test decoding valid access token"""
        data = {"sub": "user-id-123", "username": "testuser"}
        token = AuthService.create_access_token(data)

        payload = AuthService.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user-id-123"
        assert payload["username"] == "testuser"

    def test_decode_access_token_invalid(self):
        """Test decoding invalid access token"""
        invalid_token = "invalid.token.string"
        payload = AuthService.decode_access_token(invalid_token)

        assert payload is None

    def test_decode_access_token_expired(self):
        """Test decoding expired access token"""
        data = {"sub": "user-id-123"}
        # Create token that expired 1 hour ago
        expires_delta = timedelta(hours=-1)
        token = AuthService.create_access_token(data, expires_delta)

        payload = AuthService.decode_access_token(token)

        assert payload is None

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user-id-123"}
        token = AuthService.create_refresh_token(data)

        assert token is not None

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "user-id-123"
        assert payload["type"] == "refresh"

    def test_verify_token_valid(self):
        """Test verifying valid token"""
        data = {"sub": "user-id-123"}
        token = AuthService.create_access_token(data)

        assert AuthService.verify_token(token) is True

    def test_verify_token_invalid(self):
        """Test verifying invalid token"""
        assert AuthService.verify_token("invalid.token") is False

    def test_verify_token_expired(self):
        """Test verifying expired token"""
        data = {"sub": "user-id-123"}
        expires_delta = timedelta(hours=-1)
        token = AuthService.create_access_token(data, expires_delta)

        assert AuthService.verify_token(token) is False

    def test_get_current_user_id_valid(self):
        """Test getting user ID from valid token"""
        user_id = "user-id-123"
        token = AuthService.create_access_token({"sub": user_id})

        result = AuthService.get_current_user_id(token)

        assert result == user_id

    def test_get_current_user_id_invalid(self):
        """Test getting user ID from invalid token"""
        result = AuthService.get_current_user_id("invalid.token")

        assert result is None

    def test_get_current_user_id_no_sub(self):
        """Test getting user ID when token has no 'sub' claim"""
        token = AuthService.create_access_token({"username": "testuser"})

        result = AuthService.get_current_user_id(token)

        assert result is None

    def test_create_token_pair(self):
        """Test creating token pair (access + refresh)"""
        user_id = "user-id-123"
        tokens = AuthService.create_token_pair(user_id)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

        # Verify access token
        access_payload = AuthService.decode_access_token(tokens["access_token"])
        assert access_payload["sub"] == user_id

        # Verify refresh token
        refresh_payload = jwt.decode(
            tokens["refresh_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert refresh_payload["sub"] == user_id
        assert refresh_payload["type"] == "refresh"

    def test_authenticate_user_success(self, db_session, test_user):
        """Test successful user authentication"""
        from app.models import User

        # Create a user for testing
        user = User(
            email="auth@example.com",
            username="authuser",
            hashed_password=AuthService.get_password_hash("password123"),
            full_name="Auth User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        authenticated_user = AuthService.authenticate_user(
            db_session,
            "authuser",
            "password123"
        )

        assert authenticated_user is not None
        assert authenticated_user.username == "authuser"
        assert authenticated_user.email == "auth@example.com"

    def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication with wrong password"""
        from app.models import User

        user = User(
            email="auth@example.com",
            username="authuser",
            hashed_password=AuthService.get_password_hash("password123"),
            full_name="Auth User",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        authenticated_user = AuthService.authenticate_user(
            db_session,
            "authuser",
            "wrongpassword"
        )

        assert authenticated_user is None

    def test_authenticate_user_not_found(self, db_session):
        """Test authentication with non-existent user"""
        authenticated_user = AuthService.authenticate_user(
            db_session,
            "nonexistent",
            "password123"
        )

        assert authenticated_user is None

    def test_authenticate_user_inactive(self, db_session):
        """Test authentication with inactive user"""
        from app.models import User

        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=AuthService.get_password_hash("password123"),
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()

        authenticated_user = AuthService.authenticate_user(
            db_session,
            "inactiveuser",
            "password123"
        )

        assert authenticated_user is None
