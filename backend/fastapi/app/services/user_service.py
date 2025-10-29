"""
VELOX-N8N User Service
Business logic for user management and authentication
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.logging import log_security_event, log_error

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: str = 'investor'
    ) -> User:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                is_active=True,
                is_verified=False
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user: {username} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.db.rollback()
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_uuid(self, uuid: str) -> Optional[User]:
        """Get user by UUID"""
        try:
            return self.db.query(User).filter(User.uuid == uuid).first()
        except Exception as e:
            logger.error(f"Error getting user by UUID {uuid}: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_user_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        try:
            return self.db.query(User).filter(
                or_(
                    User.username == identifier,
                    User.email == identifier
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting user by identifier {identifier}: {e}")
            return None
    
    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Updated user {user_id}: {kwargs}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            self.db.rollback()
            return None
    
    async def update_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.hashed_password = hashed_password
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated password for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def update_login_info(self, user_id: int) -> bool:
        """Update user login information"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.update_login_info()
            self.db.commit()
            
            logger.info(f"Updated login info for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating login info for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def increment_failed_login(self, user_id: int) -> bool:
        """Increment failed login attempts"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.increment_failed_login()
            self.db.commit()
            
            logger.warning(f"Incremented failed login for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing failed login for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def reset_failed_login(self, user_id: int) -> bool:
        """Reset failed login attempts"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.reset_failed_login()
            self.db.commit()
            
            logger.info(f"Reset failed login for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting failed login for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def lock_user(self, user_id: int, minutes: int = 15) -> bool:
        """Lock user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
            self.db.commit()
            
            logger.warning(f"Locked user {user_id} for {minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error locking user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def unlock_user(self, user_id: int) -> bool:
        """Unlock user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.locked_until = None
            self.db.commit()
            
            logger.info(f"Unlocked user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def verify_user(self, user_id: int) -> bool:
        """Verify user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Verified user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deactivated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = True
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Activated user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def update_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        bio: Optional[str] = None
    ) -> bool:
        """Update user profile"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if phone_number is not None:
                user.phone_number = phone_number
            if bio is not None:
                user.bio = bio
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated profile for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def update_preferences(
        self,
        user_id: int,
        default_timezone: Optional[str] = None,
        default_language: Optional[str] = None,
        email_notifications: Optional[bool] = None,
        sms_notifications: Optional[bool] = None
    ) -> bool:
        """Update user preferences"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            if default_timezone is not None:
                user.default_timezone = default_timezone
            if default_language is not None:
                user.default_language = default_language
            if email_notifications is not None:
                user.email_notifications = email_notifications
            if sms_notifications is not None:
                user.sms_notifications = sms_notifications
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def update_risk_settings(
        self,
        user_id: int,
        max_position_size: Optional[float] = None,
        risk_per_trade: Optional[float] = None,
        max_daily_loss: Optional[float] = None,
        max_open_positions: Optional[int] = None
        max_correlation: Optional[float] = None
    ) -> bool:
        """Update user risk settings"""
        try:
            from app.models.risk import RiskSettings
            
            # Get or create risk settings
            risk_settings = self.db.query(RiskSettings).filter(
                RiskSettings.user_id == user_id
            ).first()
            
            if not risk_settings:
                risk_settings = RiskSettings(user_id=user_id)
                self.db.add(risk_settings)
            
            if max_position_size is not None:
                risk_settings.max_position_size = max_position_size
            if risk_per_trade is not None:
                risk_settings.risk_per_trade = risk_per_trade
            if max_daily_loss is not None:
                risk_settings.max_daily_loss = max_daily_loss
            if max_open_positions is not None:
                risk_settings.max_open_positions = max_open_positions
            if max_correlation is not None:
                risk_settings.max_correlation = max_correlation
            
            risk_settings.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Updated risk settings for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating risk settings for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        role: Optional[str] = None
    ) -> List[User]:
        """Get list of users"""
        try:
            query = self.db.query(User)
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            if role:
                query = query.filter(User.role == role)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    async def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[User]:
        """Search users by username or email"""
        try:
            return self.db.query(User).filter(
                or_(
                    User.username.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%"),
                    User.first_name.ilike(f"%{search_term}%"),
                    User.last_name.ilike(f"%{search_term}%")
                )
            ).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    async def get_user_stats(self, user_id: int) -> Optional[dict]:
        """Get user statistics"""
        try:
            from app.models.trade import Trade
            from app.models.strategy import Strategy
            
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Get trade count
            trade_count = self.db.query(Trade).filter(
                Trade.user_id == user_id
            ).count()
            
            # Get strategy count
            strategy_count = self.db.query(Strategy).filter(
                Strategy.created_by == user_id
            ).count()
            
            # Get total P&L
            total_pnl = self.db.query(Trade).filter(
                and_(
                    Trade.user_id == user_id,
                    Trade.status == 'EXECUTED'
                )
            ).with_entities(
                Trade.total_pnl
            ).scalar() or 0
            
            return {
                'trade_count': trade_count,
                'strategy_count': strategy_count,
                'total_pnl': total_pnl,
                'join_date': user.created_at,
                'last_login': user.last_login
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete)"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def hard_delete_user(self, user_id: int) -> bool:
        """Hard delete user (permanent)"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Hard deleted user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error hard deleting user {user_id}: {e}")
            self.db.rollback()
            return False