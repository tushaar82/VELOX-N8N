"""
VELOX-N8N Authentication API
User authentication, registration, and session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.http import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.config import security_settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user_from_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import UserService
from app.core.logging import log_security_event, log_api_request

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        user_service = UserService(db)
        
        if await user_service.get_user_by_email(user_data.email):
            log_security_event(
                "registration_failed",
                user_id=None,
                ip_address=None,  # Will be set by middleware
                details={"reason": "email_already_exists", "email": user_data.email}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if await user_service.get_user_by_username(user_data.username):
            log_security_event(
                "registration_failed",
                user_id=None,
                ip_address=None,
                details={"reason": "username_already_exists", "username": user_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        log_security_event(
            "user_registered",
            user_id=user.id,
            ip_address=None,
            details={"username": user.username, "email": user.email}
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "registration_error",
            user_id=None,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        user_service = UserService(db)
        
        # Get user by username
        user = await user_service.get_user_by_username(form_data.username)
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            log_security_event(
                "login_failed",
                user_id=user.id if user else None,
                ip_address=None,
                details={"username": form_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            log_security_event(
                "login_blocked",
                user_id=user.id,
                ip_address=None,
                details={"reason": "account_inactive", "username": form_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            log_security_event(
                "login_blocked",
                user_id=user.id,
                ip_address=None,
                details={
                    "reason": "account_locked",
                    "locked_until": user.locked_until.isoformat(),
                    "username": form_data.username
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is temporarily locked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        # Update user login info
        await user_service.update_login_info(user.id)
        
        log_security_event(
            "login_success",
            user_id=user.id,
            ip_address=None,
            details={"username": form_data.username}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=access_token_expires.total_seconds()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "login_error",
            user_id=None,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user_from_token)
):
    """Refresh access token"""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username, "user_id": current_user.id},
            expires_delta=access_token_expires
        )
        
        log_security_event(
            "token_refreshed",
            user_id=current_user.id,
            ip_address=None,
            details={"username": current_user.username}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=access_token_expires.total_seconds()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "token_refresh_error",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user_from_token)
):
    """Logout user (invalidate token)"""
    try:
        # In a real implementation, you would add the token to a blacklist
        # For now, we'll just log the event
        log_security_event(
            "user_logout",
            user_id=current_user.id,
            ip_address=None,
            details={"username": current_user.username}
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        log_security_event(
            "logout_error",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(current_password, current_user.hashed_password):
            log_security_event(
                "password_change_failed",
                user_id=current_user.id,
                ip_address=None,
                details={"reason": "incorrect_current_password"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        # Update password
        user_service = UserService(db)
        hashed_password = get_password_hash(new_password)
        await user_service.update_password(current_user.id, hashed_password)
        
        log_security_event(
            "password_changed",
            user_id=current_user.id,
            ip_address=None,
            details={"username": current_user.username}
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "password_change_error",
            user_id=current_user.id,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    db: Session = Depends(get_db)
):
    """Initiate password reset process"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email is registered, a reset link will be sent"}
        
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "type": "password_reset"},
            expires_delta=timedelta(hours=1)  # Token expires in 1 hour
        )
        
        # In a real implementation, send email with reset token
        # For now, we'll just log it
        log_security_event(
            "password_reset_requested",
            user_id=user.id,
            ip_address=None,
            details={"email": email}
        )
        
        return {"message": "If the email is registered, a reset link will be sent"}
        
    except Exception as e:
        log_security_event(
            "password_reset_error",
            user_id=None,
            ip_address=None,
            details={"email": email, "error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset"
        )


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    try:
        # Verify token
        payload = verify_token(token)
        
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        # Update password
        user_service = UserService(db)
        hashed_password = get_password_hash(new_password)
        await user_service.update_password(user_id, hashed_password)
        
        log_security_event(
            "password_reset_completed",
            user_id=user_id,
            ip_address=None,
            details={"username": payload.get("sub")}
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            "password_reset_error",
            user_id=None,
            ip_address=None,
            details={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )