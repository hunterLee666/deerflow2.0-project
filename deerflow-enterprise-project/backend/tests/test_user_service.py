"""
Unit tests for User Service
"""

import pytest
from sqlalchemy.orm import Session
from app.models import User, UserRole
from app.services.user_service import UserService


class TestUserService:
    """Test suite for UserService"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = UserService.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = UserService.hash_password(password)

        assert UserService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        hashed = UserService.hash_password(password)

        assert UserService.verify_password("wrongpassword", hashed) is False

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User",
            role=UserRole.USER
        )

        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.is_verified is False
        assert user.hashed_password is not None
        assert user.hashed_password != "password123"
        assert UserService.verify_password("password123", user.hashed_password)

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation with duplicate email"""
        UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser1",
            password="password123",
            full_name="Test User 1"
        )

        with pytest.raises(ValueError, match="Email or username already exists"):
            UserService.create_user(
                db=db_session,
                email="test@example.com",
                username="testuser2",
                password="password456",
                full_name="Test User 2"
            )

    def test_create_user_duplicate_username(self, db_session: Session):
        """Test user creation with duplicate username"""
        UserService.create_user(
            db=db_session,
            email="test1@example.com",
            username="testuser",
            password="password123",
            full_name="Test User 1"
        )

        with pytest.raises(ValueError, match="Email or username already exists"):
            UserService.create_user(
                db=db_session,
                email="test2@example.com",
                username="testuser",
                password="password456",
                full_name="Test User 2"
            )

    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID"""
        created_user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        retrieved_user = UserService.get_user_by_id(db_session, str(created_user.id))

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"

    def test_get_user_by_id_not_found(self, db_session: Session):
        """Test getting user by ID when not found"""
        user = UserService.get_user_by_id(db_session, "non-existent-id")
        assert user is None

    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email"""
        UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        user = UserService.get_user_by_email(db_session, "test@example.com")

        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_get_user_by_email_not_found(self, db_session: Session):
        """Test getting user by email when not found"""
        user = UserService.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_username(self, db_session: Session):
        """Test getting user by username"""
        UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        user = UserService.get_user_by_username(db_session, "testuser")

        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_get_user_by_username_not_found(self, db_session: Session):
        """Test getting user by username when not found"""
        user = UserService.get_user_by_username(db_session, "nonexistent")
        assert user is None

    def test_update_user_success(self, db_session: Session):
        """Test successful user update"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        updated_user = UserService.update_user(
            db=db_session,
            user_id=str(user.id),
            full_name="Updated Name",
            avatar_url="http://example.com/avatar.jpg",
            role=UserRole.ADMIN
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.avatar_url == "http://example.com/avatar.jpg"
        assert updated_user.role == UserRole.ADMIN
        assert updated_user.updated_at > user.created_at

    def test_update_user_not_found(self, db_session: Session):
        """Test updating non-existent user"""
        updated_user = UserService.update_user(
            db=db_session,
            user_id="non-existent-id",
            full_name="Updated Name"
        )
        assert updated_user is None

    def test_update_user_only_allowed_fields(self, db_session: Session):
        """Test that only allowed fields can be updated"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        # This should update only allowed fields, not email or username
        updated_user = UserService.update_user(
            db=db_session,
            user_id=str(user.id),
            full_name="Updated Name",
            email="newemail@example.com",  # Should be ignored
            username="newusername"  # Should be ignored
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "test@example.com"  # Should not change
        assert updated_user.username == "testuser"  # Should not change

    def test_update_last_login(self, db_session: Session):
        """Test updating last login timestamp"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        initial_last_login = user.last_login_at

        UserService.update_last_login(db_session, str(user.id))

        updated_user = UserService.get_user_by_id(db_session, str(user.id))
        assert updated_user.last_login_at is not None
        assert updated_user.last_login_at != initial_last_login

    def test_delete_user_soft_delete(self, db_session: Session):
        """Test soft delete user"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="password123",
            full_name="Test User"
        )

        assert user.is_active is True

        result = UserService.delete_user(db_session, str(user.id))

        assert result is True
        deleted_user = UserService.get_user_by_id(db_session, str(user.id))
        assert deleted_user.is_active is False
        assert deleted_user.updated_at > user.created_at

    def test_delete_user_not_found(self, db_session: Session):
        """Test deleting non-existent user"""
        result = UserService.delete_user(db_session, "non-existent-id")
        assert result is False

    def test_list_users(self, db_session: Session):
        """Test listing users"""
        UserService.create_user(
            db=db_session,
            email="user1@example.com",
            username="user1",
            password="password123",
            full_name="User One"
        )
        UserService.create_user(
            db=db_session,
            email="user2@example.com",
            username="user2",
            password="password456",
            full_name="User Two",
            role=UserRole.ADMIN
        )
        UserService.create_user(
            db=db_session,
            email="user3@example.com",
            username="user3",
            password="password789",
            full_name="User Three"
        )

        all_users = UserService.list_users(db_session)
        assert len(all_users) == 3

        admin_users = UserService.list_users(db_session, role=UserRole.ADMIN)
        assert len(admin_users) == 1
        assert admin_users[0].username == "user2"

        inactive_user = UserService.create_user(
            db=db_session,
            email="inactive@example.com",
            username="inactive",
            password="password",
            full_name="Inactive User"
        )
        UserService.delete_user(db_session, str(inactive_user.id))

        active_users = UserService.list_users(db_session, is_active=True)
        assert len(active_users) == 3

    def test_change_password_success(self, db_session: Session):
        """Test successful password change"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="oldpassword",
            full_name="Test User"
        )

        result = UserService.change_password(
            db=db_session,
            user_id=str(user.id),
            old_password="oldpassword",
            new_password="newpassword123"
        )

        assert result is True

        # Verify new password works
        updated_user = UserService.get_user_by_id(db_session, str(user.id))
        assert UserService.verify_password("newpassword123", updated_user.hashed_password)
        assert not UserService.verify_password("oldpassword", updated_user.hashed_password)

    def test_change_password_wrong_old_password(self, db_session: Session):
        """Test password change with wrong old password"""
        user = UserService.create_user(
            db=db_session,
            email="test@example.com",
            username="testuser",
            password="oldpassword",
            full_name="Test User"
        )

        result = UserService.change_password(
            db=db_session,
            user_id=str(user.id),
            old_password="wrongpassword",
            new_password="newpassword123"
        )

        assert result is False

        # Verify old password still works
        updated_user = UserService.get_user_by_id(db_session, str(user.id))
        assert UserService.verify_password("oldpassword", updated_user.hashed_password)

    def test_change_password_user_not_found(self, db_session: Session):
        """Test password change for non-existent user"""
        result = UserService.change_password(
            db=db_session,
            user_id="non-existent-id",
            old_password="oldpassword",
            new_password="newpassword123"
        )

        assert result is False
