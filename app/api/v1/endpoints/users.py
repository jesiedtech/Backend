from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password, create_access_token, generate_verification_token
from app.core.email import send_verification_email, send_password_reset_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserVerify, PasswordReset, PasswordResetConfirm, UserResponse
from datetime import timedelta, datetime
from app.core.config import settings
import uuid
import asyncpg
from typing import AsyncGenerator
import logging
from jose import JWTError, jwt
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: asyncpg.Connection = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        logger.info("Attempting to decode JWT token")
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing 'sub' claim")
            raise credentials_exception
        logger.info(f"Successfully decoded token for user ID: {user_id}")
    except JWTError as jwt_error:
        logger.error(f"JWT decode error: {str(jwt_error)}", exc_info=True)
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}", exc_info=True)
        raise credentials_exception
    
    try:
        # Get the user from the database
        logger.info(f"Fetching user from database with ID: {user_id}")
        user = await User.get_by_id(db, UUID(user_id))
        if user is None:
            logger.warning(f"No user found for ID: {user_id}")
            raise credentials_exception
        logger.info(f"Successfully retrieved user: {user.email}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user from database: {str(e)}", exc_info=True)
        raise credentials_exception

@router.get("/me", response_model=UserResponse)
async def get_current_user_details(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's details.
    """
    try:
        logger.info(f"Getting details for user: {current_user.email}")
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            surname=current_user.surname,
            role=current_user.role,
            is_verified=current_user.is_verified,
            is_active=current_user.is_active
        )
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user details"
        )

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = await User.get_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        try:
            new_user = await User.create(
                db=db,
                email=user.email,
                first_name=user.first_name,
                surname=user.surname,
                password=user.password,
                role=user.role
            )
            logger.info(f"User created successfully with ID: {new_user.id}")
        except Exception as create_error:
            logger.error(f"Error creating user: {str(create_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(create_error)}"
            )
        
        # Generate verification token
        verification_token = generate_verification_token()
        await User.update_verification_token(db, new_user.id, verification_token)
        
        # Send verification email
        await send_verification_email(user.email, verification_token)
        
        return {"message": "Registration successful. Please check your email to verify your account."}
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Login endpoint that authenticates a user and returns a JWT token.
    """
    try:
        logger.info(f"Login attempt for email: {user_data.email}")
        
        # Get user from database
        try:
            user = await User.get_by_email(db, user_data.email)
            logger.info(f"Database query completed for user: {user_data.email}")
        except Exception as db_error:
            logger.error(f"Database error during login: {str(db_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}"
            )
        
        if not user:
            logger.warning(f"Login failed: User not found for email {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        try:
            password_valid = verify_password(user_data.password, user.hashed_password)
            logger.info(f"Password verification result for {user.email}: {password_valid}")
        except Exception as pwd_error:
            logger.error(f"Password verification error: {str(pwd_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying password"
            )
        
        if not password_valid:
            logger.warning(f"Login failed: Invalid password for user {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is verified
        if not user.is_verified:
            logger.warning(f"Login failed: Unverified user {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your email before logging in"
            )
        
        # Update last login time
        try:
            user.last_login = datetime.utcnow()
            await user.save(db)
            logger.info(f"Updated last login time for user {user.email}")
        except Exception as update_error:
            logger.error(f"Error updating last login time: {str(update_error)}", exc_info=True)
            # Don't fail the login if we can't update the last login time
        
        # Create access token
        try:
            access_token = create_access_token(
                data={"sub": str(user.id)}
            )
            logger.info(f"Access token created for user {user.email}")
        except Exception as token_error:
            logger.error(f"Error creating access token: {str(token_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating access token"
            )
        
        logger.info(f"Login successful for user {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during login: {str(e)}"
        )

@router.post("/verify-email/{token}", response_model=dict)
async def verify_email(token: str, conn: asyncpg.Connection = Depends(get_db)):
    user = await User.get_by_verification_token(conn, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    await user.save(conn)
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    email: str = Query(..., description="Email address to send password reset link"),
    conn: asyncpg.Connection = Depends(get_db)
):
    try:
        user = await User.get_by_email(conn, email)
        if not user:
            # Don't reveal that the email doesn't exist
            return {"message": "If your email is registered, you will receive a password reset link"}
        
        # Generate password reset token
        reset_token = generate_verification_token()
        user.reset_token = reset_token
        await user.save(conn)
        
        # Send password reset email
        try:
            logger.info("Attempting to send password reset email")
            await send_password_reset_email(user.email, reset_token)  # Added await here
            logger.info("Password reset email sent successfully")
        except Exception as email_error:
            logger.error(f"Failed to send password reset email: {str(email_error)}")
            # Don't raise an exception here, just log the error
        
        return {"message": "If your email is registered, you will receive a password reset link"}
    except Exception as e:
        logger.error(f"Error in forgot_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process password reset request: {str(e)}"
        )

@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset_data: PasswordResetConfirm,
    conn: asyncpg.Connection = Depends(get_db)
):
    user = await User.get_by_reset_token(conn, reset_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    await user.save(conn)
    
    return {"message": "Password has been reset successfully"}

@router.post("/resend-verification", response_model=dict)
async def resend_verification(
    email: str = Query(..., description="Email address to resend verification link"),
    conn: asyncpg.Connection = Depends(get_db)
):
    try:
        user = await User.get_by_email(conn, email)
        if not user:
            # Don't reveal that the email doesn't exist
            return {"message": "If your email is registered, you will receive a verification link"}
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new verification token
        verification_token = generate_verification_token()
        user.verification_token = verification_token
        await user.save(conn)
        
        # Send new verification email
        try:
            logger.info("Attempting to resend verification email")
            send_verification_email(user.email, verification_token)  # Removed await
            logger.info("Verification email resent successfully")
        except Exception as email_error:
            logger.error(f"Failed to resend verification email: {str(email_error)}")
            # Don't raise an exception here, just log the error
        
        return {"message": "If your email is registered, you will receive a verification link"}
    except Exception as e:
        logger.error(f"Error in resend_verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}"
        )

@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint that invalidates the current user's token.
    """
    try:
        logger.info(f"User {current_user.email} logging out")
        
        # Update the user's last logout time
        current_user.last_logout = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Successfully logged out",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        ) 