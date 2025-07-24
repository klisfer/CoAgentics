from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
import logging

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserSession

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (alias for clarity)"""
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are a superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user

def create_user_session(
    db: Session,
    user_id: str,
    token: str,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> UserSession:
    """Create a new user session"""
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    session = UserSession(
        user_id=user_id,
        session_token=token,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at.isoformat(),
        is_active=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def invalidate_user_session(db: Session, token: str):
    """Invalidate a user session"""
    session = db.query(UserSession).filter(UserSession.session_token == token).first()
    if session:
        session.is_active = False
        db.commit()

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

class RequirePermissions:
    """Dependency class to require specific permissions"""
    
    def __init__(self, permissions: list):
        self.permissions = permissions
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        # In a more complex system, you would check user permissions here
        # For now, we'll just ensure the user is authenticated
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        return current_user

# Common permission dependencies
require_financial_access = RequirePermissions(["financial_tools"])
require_admin_access = RequirePermissions(["admin"])

def create_guest_user(db: Session) -> User:
    """Create a temporary guest user for demo purposes"""
    
    guest_user = User(
        email=f"guest_{datetime.utcnow().timestamp()}@example.com",
        username=f"guest_{datetime.utcnow().timestamp()}",
        full_name="Guest User",
        is_active=True,
        is_superuser=False,
        preferences={"guest": True},
        risk_tolerance="moderate",
        investment_experience="beginner"
    )
    
    # Set a default password (in production, this should be more secure)
    guest_user.set_password("guest_password")
    
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)
    
    return guest_user 