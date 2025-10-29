"""
VELOX-N8N Security Module
Authentication, authorization, and security utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets
import hashlib
import hmac

from app.core.config import security_settings
from app.core.logging import log_security_event

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate password hash
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.JWT_SECRET_KEY,
        algorithm=security_settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload
    """
    try:
        payload = jwt.decode(
            token,
            security_settings.JWT_SECRET_KEY,
            algorithms=[security_settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        log_security_event(
            "token_verification_failed",
            user_id=None,
            ip_address=None,
            details={"error": str(e)}
        )
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        security_settings.JWT_SECRET_KEY,
        algorithm=security_settings.JWT_ALGORITHM
    )
    return encoded_jwt


def generate_password_reset_token(email: str) -> str:
    """
    Generate secure password reset token
    """
    timestamp = str(datetime.utcnow().timestamp())
    token_data = f"{email}:{timestamp}"
    
    # Create HMAC signature
    signature = hmac.new(
        security_settings.JWT_SECRET_KEY.encode(),
        token_data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{token_data}:{signature}"


def verify_password_reset_token(token: str, max_age_hours: int = 1) -> Optional[str]:
    """
    Verify password reset token
    """
    try:
        token_data, signature = token.rsplit(":", 1)
        email, timestamp_str = token_data.split(":", 1)
        
        # Verify signature
        expected_signature = hmac.new(
            security_settings.JWT_SECRET_KEY.encode(),
            f"{email}:{timestamp_str}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Check token age
        timestamp = float(timestamp_str)
        current_timestamp = datetime.utcnow().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        if current_timestamp - timestamp > max_age_seconds:
            return None
        
        return email
        
    except Exception as e:
        log_security_event(
            "password_reset_token_verification_failed",
            user_id=None,
            ip_address=None,
            details={"error": str(e)}
        )
        return None


def generate_api_key() -> str:
    """
    Generate secure API key
    """
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for storage
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify API key against hash
    """
    return hmac.compare_digest(
        hash_api_key(api_key),
        hashed_key
    )


def create_session_token() -> str:
    """
    Create secure session token
    """
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    """
    errors = []
    score = 0
    
    # Length check
    if len(password) < security_settings.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {security_settings.PASSWORD_MIN_LENGTH} characters")
    else:
        score += 1
    
    if len(password) > security_settings.PASSWORD_MAX_LENGTH:
        errors.append(f"Password must be no more than {security_settings.PASSWORD_MAX_LENGTH} characters")
    else:
        score += 1
    
    # Complexity checks
    if any(c.islower() for c in password):
        score += 1
    
    if any(c.isupper() for c in password):
        score += 1
    
    if any(c.isdigit() for c in password):
        score += 1
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/" for c in password):
        score += 1
    
    # Common password check
    common_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    
    if password.lower() in common_passwords:
        errors.append("Password is too common")
        score -= 2
    
    return {
        "is_valid": len(errors) == 0 and score >= 3,
        "score": score,
        "errors": errors
    }


def encrypt_sensitive_data(data: str) -> str:
    """
    Encrypt sensitive data for storage
    """
    # In a real implementation, use proper encryption
    # This is just a placeholder
    return f"encrypted_{data}"


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data from storage
    """
    # In a real implementation, use proper decryption
    # This is just a placeholder
    if encrypted_data.startswith("encrypted_"):
        return encrypted_data[10:]  # Remove "encrypted_" prefix
    return encrypted_data


def generate_csrf_token() -> str:
    """
    Generate CSRF token
    """
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    """
    Verify CSRF token
    """
    return hmac.compare_digest(token, expected_token)


def get_client_ip(request) -> Optional[str]:
    """
    Get client IP address from request
    """
    # This would be implemented based on your web framework
    # For FastAPI, you might use request.client.host
    return None


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe (for redirects, etc.)
    """
    # Basic implementation - enhance as needed
    if url.startswith(("javascript:", "data:")):
        return False
    
    # Check for same-origin redirects
    # This is a simplified check
    return True


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent XSS
    """
    # Basic HTML sanitization
    import html
    return html.escape(input_str)


def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (Indian format)
    """
    import re
    # Remove spaces and special characters
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    # Check if it's 10 digits (Indian mobile number)
    if len(clean_phone) == 10 and clean_phone.isdigit():
        # Check if it starts with valid Indian mobile prefixes
        valid_prefixes = ['6', '7', '8', '9']
        return clean_phone[0] in valid_prefixes
    
    return False


def rate_limit_check(user_id: int, action: str, limit: int = 10, window_minutes: int = 5) -> bool:
    """
    Check if user exceeds rate limit
    """
    # This would be implemented with Redis or database
    # For now, return True (allow)
    return True


def is_brute_force_attack(user_id: int, failed_attempts: int) -> bool:
    """
    Check if user is attempting brute force attack
    """
    return failed_attempts > 5  # Threshold for brute force detection


def is_suspicious_activity(user_id: int, activities: list) -> bool:
    """
    Check for suspicious activity patterns
    """
    # This would analyze user activity patterns
    # For now, return False (not suspicious)
    return False


def create_security_headers() -> Dict[str, str]:
    """
    Create security headers for HTTP responses
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


def log_security_event_to_db(
    event_type: str,
    user_id: Optional[int],
    details: Dict[str, Any]
):
    """
    Log security event to database
    """
    # This would log to the audit_log table
    # For now, just use the logging module
    log_security_event(
        event_type=event_type,
        user_id=user_id,
        ip_address=None,
        details=details
    )


def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if user role has required permission
    """
    # Define role permissions
    role_permissions = {
        "admin": ["read", "write", "delete", "manage_users", "manage_strategies", "manage_system"],
        "investor": ["read", "write", "manage_strategies"],
        "viewer": ["read"]
    }
    
    return required_permission in role_permissions.get(user_role, [])