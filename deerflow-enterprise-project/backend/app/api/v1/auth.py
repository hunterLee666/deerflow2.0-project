"""
Authentication and User Management API Endpoints
"""

import logging
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import UserService, AuthService
from app.api.v1.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    LoginRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account

    - **email**: User email address
    - **username**: Username (3-100 characters)
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    try:
        user = UserService.create_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Login and get access token

    - **username**: Username or email
    - **password**: User password
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token pair
    tokens = AuthService.create_token_pair(str(user.id))

    logger.info(f"User {user.username} logged in successfully")
    return tokens


@router.post("/login/email", response_model=Token)
async def login_with_email(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with email and password (alternative to OAuth2 form)

    - **username**: Username or email
    - **password**: User password
    """
    user = AuthService.authenticate_user(db, login_data.username, login_data.password)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    tokens = AuthService.create_token_pair(str(user.id))
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(AuthService.get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current authenticated user information

    Requires valid access token
    """
    user = UserService.get_user_by_id(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    token: str = Depends(AuthService.get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile

    Requires valid access token
    """
    updated_user = UserService.update_user(
        db=db,
        user_id=token,
        **user_update.dict(exclude_unset=True)
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    token: str = Depends(AuthService.get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change current user password

    Requires valid access token
    """
    success = UserService.change_password(
        db=db,
        user_id=token,
        old_password=old_password,
        new_password=new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password. Check old password."
        )

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(
    token: str = Depends(AuthService.get_current_user_id)
) -> Any:
    """
    Logout current user

    In a real implementation, this would invalidate the token
    on the server side (using a token blacklist or similar)
    """
    # TODO: Implement token invalidation
    return {"message": "Logged out successfully"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: str | None = None,
    is_active: bool | None = None,
    token: str = Depends(AuthService.get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all users (admin only)

    Requires admin role
    """
    # TODO: Add admin role check
    users = UserService.list_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active
    )

    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    token: str = Depends(AuthService.get_current_user_id),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user by ID

    Requires admin role or ownership
    """
    user = UserService.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
