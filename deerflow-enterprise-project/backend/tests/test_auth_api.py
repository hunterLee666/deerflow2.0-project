"""
Integration tests for Auth API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import User
from app.services.auth_service import AuthService

client = TestClient(app)


class TestAuthAPI:
    """Test suite for Auth API endpoints"""

    def test_register_user_success(self, db_session: Session):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert data["is_active"] is True

    def test_register_user_duplicate_email(self, db_session: Session):
        """Test registration with duplicate email"""
        # Create first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser1",
                "password": "password123"
            }
        )

        # Try to create another user with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser2",
                "password": "password456"
            }
        )

        assert response.status_code == 400
        assert "Email or username already exists" in response.json()["detail"]

    def test_register_user_duplicate_username(self, db_session: Session):
        """Test registration with duplicate username"""
        # Create first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "test1@example.com",
                "username": "testuser",
                "password": "password123"
            }
        )

        # Try to create another user with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test2@example.com",
                "username": "testuser",
                "password": "password456"
            }
        )

        assert response.status_code == 400
        assert "Email or username already exists" in response.json()["detail"]

    def test_register_user_invalid_email(self, db_session: Session):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "password123"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_register_user_short_password(self, db_session: Session):
        """Test registration with password too short"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_success(self, db_session: Session):
        """Test successful login"""
        # Register user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123",
                "full_name": "Login User"
            }
        )

        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "loginuser",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid
        assert AuthService.verify_token(data["access_token"]) is True

    def test_login_wrong_password(self, db_session: Session):
        """Test login with wrong password"""
        # Register user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123"
            }
        )

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "loginuser",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, db_session: Session):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "password123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_with_email(self, db_session: Session):
        """Test login with email instead of username"""
        # Register user first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "password123"
            }
        )

        # Login with email
        response = client.post(
            "/api/v1/auth/login/email",
            json={
                "username": "login@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_get_current_user(self, db_session: Session, auth_headers: dict):
        """Test getting current user information"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["full_name"] == "Test User"

    def test_get_current_user_unauthorized(self, db_session: Session):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401  # Unauthorized

    def test_update_current_user(self, db_session: Session, auth_headers: dict):
        """Test updating current user profile"""
        response = client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={
                "full_name": "Updated Name",
                "avatar_url": "http://example.com/new-avatar.jpg"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["avatar_url"] == "http://example.com/new-avatar.jpg"

    def test_change_password(self, db_session: Session, auth_headers: dict):
        """Test changing user password"""
        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            params={
                "old_password": "password123",
                "new_password": "newpassword456"
            }
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

        # Verify new password works
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "newpassword456"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, db_session: Session, auth_headers: dict):
        """Test changing password with wrong old password"""
        response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            params={
                "old_password": "wrongpassword",
                "new_password": "newpassword456"
            }
        )

        assert response.status_code == 400
        assert "Failed to change password" in response.json()["detail"]

    def test_list_users(self, db_session: Session, auth_headers: dict):
        """Test listing users"""
        # Create additional users
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "username": "user2",
                "password": "password123",
                "full_name": "User Two"
            }
        )
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user3@example.com",
                "username": "user3",
                "password": "password123",
                "full_name": "User Three"
            }
        )

        response = client.get(
            "/api/v1/auth/users",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # At least the test user + 2 new users

    def test_logout(self, db_session: Session, auth_headers: dict):
        """Test logout endpoint"""
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Enterprise AI Agent System"
        assert data["docs"] == "/docs"
