"""
Dependency injection for API endpoints
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService


security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[str]:
    """Get current user ID from JWT token"""
    token = credentials.credentials
    user_id = AuthService.get_current_user_id(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    return user_id


async def get_current_active_user(
    current_user: str = Depends(get_current_user_id)
) -> str:
    """
    Get current active user.
    In a real implementation, this would verify the user is active.
    """
    # TODO: Verify user is active in database
    return current_user
