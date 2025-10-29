"""
VELOX-N8N User Model
Database model for user authentication and management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='investor', index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Profile fields
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Trading preferences
    default_timezone = Column(String(50), default='Asia/Kolkata', nullable=False)
    default_language = Column(String(10), default='en', nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(32), nullable=True)
    
    # Risk management settings
    max_position_size = Column(Float, default=100000.0, nullable=False)
    risk_per_trade = Column(Float, default=2.0, nullable=False)
    max_daily_loss = Column(Float, default=10000.0, nullable=False)
    max_open_positions = Column(Integer, default=10, nullable=False)
    
    # API settings
    api_key = Column(String(100), nullable=True, unique=True)
    api_key_expires = Column(TIMESTAMP(timezone=True), nullable=True)
    last_api_access = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Session management
    session_token = Column(String(255), nullable=True, unique=True)
    session_expires = Column(TIMESTAMP(timezone=True), nullable=True)
    last_ip_address = Column(String(45), nullable=True)
    last_user_agent = Column(Text, nullable=True)
    
    # Relationships
    strategies = relationship("Strategy", back_populates="creator", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    risk_settings = relationship("RiskSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'
    
    @property
    def is_investor(self) -> bool:
        """Check if user is investor"""
        return self.role == 'investor'
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    @property
    def display_role(self) -> str:
        """Get display role name"""
        role_map = {
            'admin': 'Administrator',
            'investor': 'Investor',
            'viewer': 'Viewer'
        }
        return role_map.get(self.role, self.role.capitalize())
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'uuid': str(self.uuid),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'display_role': self.display_role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'default_timezone': self.default_timezone,
            'default_language': self.default_language,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'two_factor_enabled': self.two_factor_enabled,
            'max_position_size': self.max_position_size,
            'risk_per_trade': self.risk_per_trade,
            'max_daily_loss': self.max_daily_loss,
            'max_open_positions': self.max_open_positions,
            'last_api_access': self.last_api_access.isoformat() if self.last_api_access else None,
            'session_expires': self.session_expires.isoformat() if self.session_expires else None
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'api_key': self.api_key,
                'api_key_expires': self.api_key_expires.isoformat() if self.api_key_expires else None,
                'session_token': self.session_token,
                'last_ip_address': self.last_ip_address,
                'last_user_agent': self.last_user_agent
            })
        
        return data
    
    def update_login_info(self, ip_address: str = None, user_agent: str = None):
        """Update user login information"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_ip_address = ip_address
        self.last_user_agent = user_agent
        self.updated_at = datetime.utcnow()
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        self.updated_at = datetime.utcnow()
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.updated_at = datetime.utcnow()
    
    def is_api_key_valid(self) -> bool:
        """Check if API key is valid and not expired"""
        if not self.api_key or not self.api_key_expires:
            return False
        return datetime.utcnow() < self.api_key_expires
    
    def is_session_valid(self) -> bool:
        """Check if session is valid and not expired"""
        if not self.session_token or not self.session_expires:
            return False
        return datetime.utcnow() < self.session_expires
    
    def generate_api_key(self) -> str:
        """Generate new API key"""
        import secrets
        self.api_key = secrets.token_urlsafe(32)
        self.api_key_expires = datetime.utcnow() + timedelta(days=30)
        self.updated_at = datetime.utcnow()
        return self.api_key
    
    def revoke_api_key(self):
        """Revoke API key"""
        self.api_key = None
        self.api_key_expires = None
        self.updated_at = datetime.utcnow()
    
    def generate_session_token(self) -> str:
        """Generate new session token"""
        import secrets
        self.session_token = secrets.token_urlsafe(32)
        self.session_expires = datetime.utcnow() + timedelta(hours=24)
        self.updated_at = datetime.utcnow()
        return self.session_token
    
    def revoke_session_token(self):
        """Revoke session token"""
        self.session_token = None
        self.session_expires = None
        self.updated_at = datetime.utcnow()
    
    def enable_two_factor(self) -> str:
        """Enable two-factor authentication"""
        import secrets
        self.two_factor_secret = secrets.token_urlsafe(16)
        self.two_factor_enabled = True
        self.updated_at = datetime.utcnow()
        return self.two_factor_secret
    
    def disable_two_factor(self):
        """Disable two-factor authentication"""
        self.two_factor_secret = None
        self.two_factor_enabled = False
        self.updated_at = datetime.utcnow()
    
    def verify_two_factor(self, code: str) -> bool:
        """Verify two-factor authentication code"""
        # This is a simplified implementation
        # In a real system, you would use TOTP
        import secrets
        expected_code = secrets.token_hex(3)[:6].upper()
        return code.upper() == expected_code