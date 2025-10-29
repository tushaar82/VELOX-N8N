"""
VELOX-N8N User Schemas
Pydantic models for user API validation and serialization
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    INVESTOR = "investor"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    role: UserRole = Field(default=UserRole.INVESTOR, description="User role")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must not be more than 128 characters long')
        # Add more password validation as needed
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        if v and not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        if v and len(v) != 10:
            raise ValueError('Phone number must be exactly 10 digits')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    bio: Optional[str] = Field(None, max_length=500, description="Bio")
    profile_picture: Optional[str] = Field(None, max_length=255, description="Profile picture URL")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        if v and not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        if v and len(v) != 10:
            raise ValueError('Phone number must be exactly 10 digits')
        return v


class UserPreferences(BaseModel):
    """User preferences schema"""
    default_timezone: str = Field('Asia/Kolkata', description="Default timezone")
    default_language: str = Field('en', description="Default language")
    email_notifications: bool = Field(True, description="Email notifications enabled")
    sms_notifications: bool = Field(False, description="SMS notifications enabled")
    two_factor_enabled: bool = Field(False, description="Two-factor authentication enabled")


class UserRiskSettings(BaseModel):
    """User risk settings schema"""
    max_position_size: float = Field(100000.0, ge=0, description="Maximum position size")
    risk_per_trade: float = Field(2.0, ge=0, le=10, description="Risk per trade in percentage")
    max_daily_loss: float = Field(10000.0, ge=0, description="Maximum daily loss")
    max_open_positions: int = Field(10, ge=1, le=50, description="Maximum open positions")
    max_correlation: float = Field(0.7, ge=0, le=1, description="Maximum correlation")


class UserLogin(BaseModel):
    """User login schema"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserChangePassword(BaseModel):
    """User password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('New password must not be more than 128 characters long')
        return v


class UserForgotPassword(BaseModel):
    """User forgot password schema"""
    email: EmailStr = Field(..., description="Email address")


class UserResetPassword(BaseModel):
    """User reset password schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('New password must not be more than 128 characters long')
        return v


class Token(BaseModel):
    """Token schema"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class TokenData(BaseModel):
    """Token data schema"""
    sub: str = Field(..., description="Subject")
    user_id: int = Field(..., description="User ID")
    exp: int = Field(..., description="Expiration time")
    type: Optional[str] = Field(None, description="Token type")


class UserResponse(UserBase):
    """User response schema"""
    id: int = Field(..., description="User ID")
    uuid: str = Field(..., description="User UUID")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="User verified status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(0, description="Login count")
    failed_login_attempts: int = Field(0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    full_name: Optional[str] = Field(None, description="Full name")
    phone_number: Optional[str] = Field(None, description="Phone number")
    profile_picture: Optional[str] = Field(None, description="Profile picture URL")
    bio: Optional[str] = Field(None, description="Bio")
    default_timezone: Optional[str] = Field(None, description="Default timezone")
    default_language: Optional[str] = Field(None, description="Default language")
    email_notifications: Optional[bool] = Field(None, description="Email notifications enabled")
    sms_notifications: Optional[bool] = Field(None, description="SMS notifications enabled")
    two_factor_enabled: Optional[bool] = Field(None, description="Two-factor authentication enabled")
    max_position_size: Optional[float] = Field(None, description="Maximum position size")
    risk_per_trade: Optional[float] = Field(None, description="Risk per trade")
    max_daily_loss: Optional[float] = Field(None, description="Maximum daily loss")
    max_open_positions: Optional[int] = Field(None, description="Maximum open positions")
    max_correlation: Optional[float] = Field(None, description="Maximum correlation")
    display_role: Optional[str] = Field(None, description="Display role name")
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """User list response schema"""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(1, description="Current page")
    per_page: int = Field(20, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class UserStats(BaseModel):
    """User statistics schema"""
    trade_count: int = Field(..., description="Total number of trades")
    strategy_count: int = Field(..., description="Total number of strategies")
    total_pnl: float = Field(..., description="Total P&L")
    join_date: datetime = Field(..., description="Account join date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True


class UserSearch(BaseModel):
    """User search schema"""
    search_term: str = Field(..., min_length=2, max_length=100, description="Search term")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class UserActivity(BaseModel):
    """User activity schema"""
    user_id: int = Field(..., description="User ID")
    activity_type: str = Field(..., description="Activity type")
    details: dict = Field(..., description="Activity details")
    timestamp: datetime = Field(..., description="Activity timestamp")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")


class UserSecurityEvent(BaseModel):
    """User security event schema"""
    user_id: Optional[int] = Field(None, description="User ID")
    event_type: str = Field(..., description="Event type")
    ip_address: Optional[str] = Field(None, description="IP address")
    details: dict = Field(..., description="Event details")
    severity: str = Field("INFO", description="Event severity")
    timestamp: datetime = Field(..., description="Event timestamp")


class UserSession(BaseModel):
    """User session schema"""
    user_id: int = Field(..., description="User ID")
    session_token: str = Field(..., description="Session token")
    expires_at: datetime = Field(..., description="Session expiration")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: datetime = Field(..., description="Session creation timestamp")


class UserAPIKey(BaseModel):
    """User API key schema"""
    api_key: str = Field(..., description="API key")
    expires_at: datetime = Field(..., description="API key expiration")
    last_access: Optional[datetime] = Field(None, description="Last access timestamp")
    permissions: List[str] = Field(..., description="API key permissions")


class UserCreateAPIKey(BaseModel):
    """User API key creation schema"""
    name: str = Field(..., min_length=3, max_length=50, description="API key name")
    permissions: List[str] = Field(..., description="API key permissions")
    expires_days: int = Field(30, ge=1, le=365, description="Expiration in days")


class UserPermission(BaseModel):
    """User permission schema"""
    permission: str = Field(..., description="Permission name")
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action")
    granted: bool = Field(..., description="Permission granted")
    timestamp: datetime = Field(..., description="Permission timestamp")