from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import create_access_token, get_current_user
from app.core.email import send_email_background, send_email_async
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.crud.user import create_user, get_user_by_email, update_user
from app.core.config import settings
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    user = await get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    user = await create_user(db, user_in)
    
    # Generate verification token
    token = create_access_token(
        data={"sub": user.email, "type": "verification"},
        expires_delta=timedelta(hours=24)
    )
    
    # Send verification email
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    email_body = {
        "title": "Verify your email",
        "message": f"Please click the button below to verify your email address:",
        "button_text": "Verify Email",
        "button_url": verification_url
    }
    
    send_email_background(
        background_tasks,
        subject="Verify your email",
        email_to=user.email,
        body=email_body
    )
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    user = await get_user_by_email(db, email=form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=401,
            detail="Please verify your email first"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify user's email address."""
    try:
        payload = get_current_user(token)
        if payload.get("type") != "verification":
            raise HTTPException(
                status_code=400,
                detail="Invalid token type"
            )
        
        user = await get_user_by_email(db, email=payload.get("sub"))
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        if user.is_verified:
            return {"message": "Email already verified"}
        
        user.is_verified = True
        await db.commit()
        
        return {"message": "Email verified successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Send password reset email."""
    user = await get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Generate reset token
    token = create_access_token(
        data={"sub": user.email, "type": "reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # Send reset email
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    email_body = {
        "title": "Reset your password",
        "message": "Please click the button below to reset your password:",
        "button_text": "Reset Password",
        "button_url": reset_url
    }
    
    send_email_background(
        background_tasks,
        subject="Reset your password",
        email_to=user.email,
        body=email_body
    )
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """Reset user's password."""
    try:
        payload = get_current_user(token)
        if payload.get("type") != "reset":
            raise HTTPException(
                status_code=400,
                detail="Invalid token type"
            )
        
        user = await get_user_by_email(db, email=payload.get("sub"))
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user.set_password(new_password)
        await db.commit()
        
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        ) 