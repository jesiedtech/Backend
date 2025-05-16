import asyncpg
import logging
from datetime import datetime
from typing import Optional
from app.core.security import get_password_hash, verify_password
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

class User:
    def __init__(
        self,
        id: str,
        email: str,
        first_name: str,
        surname: str,
        hashed_password: str,
        role: str = 'user',
        is_active: bool = True,
        is_verified: bool = False,
        verification_token: Optional[str] = None,
        reset_token: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        last_logout: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.surname = surname
        self.hashed_password = hashed_password
        self.role = role
        self.is_active = is_active
        self.is_verified = is_verified
        self.verification_token = verification_token
        self.reset_token = reset_token
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_login = last_login
        self.last_logout = last_logout

    @classmethod
    async def create(cls, db: asyncpg.Connection, email: str, first_name: str, surname: str, password: str, role: str = 'user') -> 'User':
        """Create a new user."""
        try:
            logger.info("Starting user creation process...")
            hashed_password = get_password_hash(password)
            verification_token = cls.generate_verification_token()
            
            query = """
                INSERT INTO users (email, first_name, surname, hashed_password, role, verification_token)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, email, first_name, surname, hashed_password, role, is_active, is_verified,
                         verification_token, reset_token, created_at, updated_at, last_login, last_logout
            """
            
            logger.info("Executing database query...")
            try:
                row = await db.fetchrow(
                    query,
                    email,
                    first_name,
                    surname,
                    hashed_password,
                    role,
                    verification_token
                )
                logger.info("Database query executed successfully")
            except Exception as db_error:
                logger.error(f"Database error during user creation: {str(db_error)}")
                raise Exception(f"Database error: {str(db_error)}")
            
            if not row:
                logger.error("No data returned after user creation")
                raise Exception("Failed to create user: No data returned")
            
            logger.info(f"User created successfully with ID: {row['id']}")
            return cls(
                id=row['id'],
                email=row['email'],
                first_name=row['first_name'],
                surname=row['surname'],
                hashed_password=row['hashed_password'],
                role=row['role'],
                is_active=row['is_active'],
                is_verified=row['is_verified'],
                verification_token=row['verification_token'],
                reset_token=row['reset_token'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                last_login=row['last_login'],
                last_logout=row['last_logout']
            )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def get_by_email(cls, db: asyncpg.Connection, email: str) -> Optional['User']:
        """Get a user by email."""
        try:
            query = """
                SELECT id, email, first_name, surname, hashed_password, role, is_active, is_verified,
                       verification_token, reset_token, created_at, updated_at, last_login, last_logout
                FROM users
                WHERE email = $1
            """
            row = await db.fetchrow(query, email)
            
            if row:
                return cls(
                    id=row['id'],
                    email=row['email'],
                    first_name=row['first_name'],
                    surname=row['surname'],
                    hashed_password=row['hashed_password'],
                    role=row['role'],
                    is_active=row['is_active'],
                    is_verified=row['is_verified'],
                    verification_token=row['verification_token'],
                    reset_token=row['reset_token'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row['last_login'],
                    last_logout=row['last_logout']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise

    @classmethod
    async def get_by_verification_token(cls, db: asyncpg.Connection, token: str) -> Optional['User']:
        """Get a user by verification token."""
        try:
            query = """
                SELECT id, email, first_name, surname, hashed_password, role, is_active, is_verified,
                       verification_token, reset_token, created_at, updated_at, last_login, last_logout
                FROM users
                WHERE verification_token = $1
            """
            row = await db.fetchrow(query, token)
            
            if row:
                return cls(
                    id=row['id'],
                    email=row['email'],
                    first_name=row['first_name'],
                    surname=row['surname'],
                    hashed_password=row['hashed_password'],
                    role=row['role'],
                    is_active=row['is_active'],
                    is_verified=row['is_verified'],
                    verification_token=row['verification_token'],
                    reset_token=row['reset_token'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row['last_login'],
                    last_logout=row['last_logout']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by verification token: {str(e)}")
            raise

    @classmethod
    async def get_by_reset_token(cls, db: asyncpg.Connection, token: str) -> Optional['User']:
        """Get a user by reset token."""
        try:
            query = """
                SELECT id, email, first_name, surname, hashed_password, role, is_active, is_verified,
                       verification_token, reset_token, created_at, updated_at, last_login, last_logout
                FROM users
                WHERE reset_token = $1
            """
            row = await db.fetchrow(query, token)
            
            if row:
                return cls(
                    id=row['id'],
                    email=row['email'],
                    first_name=row['first_name'],
                    surname=row['surname'],
                    hashed_password=row['hashed_password'],
                    role=row['role'],
                    is_active=row['is_active'],
                    is_verified=row['is_verified'],
                    verification_token=row['verification_token'],
                    reset_token=row['reset_token'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row['last_login'],
                    last_logout=row['last_logout']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by reset token: {str(e)}")
            raise

    @classmethod
    async def get_by_id(cls, db: asyncpg.Connection, user_id: str) -> Optional['User']:
        """Get a user by ID."""
        try:
            query = """
                SELECT id, email, first_name, surname, hashed_password, role, is_active, is_verified,
                       verification_token, reset_token, created_at, updated_at, last_login, last_logout
                FROM users
                WHERE id = $1
            """
            row = await db.fetchrow(query, user_id)
            
            if row:
                return cls(
                    id=row['id'],
                    email=row['email'],
                    first_name=row['first_name'],
                    surname=row['surname'],
                    hashed_password=row['hashed_password'],
                    role=row['role'],
                    is_active=row['is_active'],
                    is_verified=row['is_verified'],
                    verification_token=row['verification_token'],
                    reset_token=row['reset_token'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    last_login=row['last_login'],
                    last_logout=row['last_logout']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise

    async def verify(self, db: asyncpg.Connection) -> None:
        """Verify a user's email."""
        try:
            query = """
                UPDATE users
                SET is_verified = true,
                    verification_token = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """
            await db.execute(query, self.id)
            self.is_verified = True
            self.verification_token = None
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            raise

    async def set_reset_token(self, db: asyncpg.Connection, token: str) -> None:
        """Set a password reset token."""
        try:
            query = """
                UPDATE users
                SET reset_token = $1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await db.execute(query, token, self.id)
            self.reset_token = token
        except Exception as e:
            logger.error(f"Error setting reset token: {str(e)}")
            raise

    async def reset_password(self, db: asyncpg.Connection, new_password: str) -> None:
        """Reset a user's password."""
        try:
            hashed_password = get_password_hash(new_password)
            query = """
                UPDATE users
                SET hashed_password = $1,
                    reset_token = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await db.execute(query, hashed_password, self.id)
            self.hashed_password = hashed_password
            self.reset_token = None
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            raise

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hashed password."""
        return verify_password(password, self.hashed_password)

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a verification token."""
        import secrets
        return secrets.token_urlsafe(32)

    async def save(self, conn: asyncpg.Connection) -> None:
        try:
            # Check if user exists
            existing_user = await self.get_by_email(conn, self.email)
            
            if existing_user:
                logger.info(f"Updating existing user with ID: {self.id}")
                # Update existing user
                await conn.execute('''
                    UPDATE users 
                    SET first_name = $1,
                        surname = $2,
                        email = $3,
                        hashed_password = $4,
                        role = $5,
                        is_active = $6,
                        is_verified = $7,
                        verification_token = $8,
                        reset_token = $9,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = $10
                ''', self.first_name, self.surname, self.email, self.hashed_password,
                    self.role, self.is_active, self.is_verified,
                    self.verification_token, self.reset_token, self.id)
                logger.info(f"User updated successfully with ID: {self.id}")
            else:
                logger.info(f"Creating new user with ID: {self.id}")
                # Insert new user
                await conn.execute('''
                    INSERT INTO users (
                        id, first_name, surname, email, hashed_password, role,
                        is_active, is_verified, verification_token,
                        reset_token, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ''', self.id, self.first_name, self.surname, self.email, self.hashed_password, self.role,
                    self.is_active, self.is_verified, self.verification_token,
                    self.reset_token, self.created_at, self.updated_at)
                logger.info(f"User created successfully with ID: {self.id}")
        except Exception as e:
            logger.error(f"Error saving user: {str(e)}")
            raise

    @classmethod
    async def update_verification_token(cls, db: asyncpg.Connection, user_id: UUID, token: str) -> None:
        """Update the verification token for a user."""
        try:
            query = """
                UPDATE users
                SET verification_token = $1
                WHERE id = $2
            """
            await db.execute(query, token, user_id)
            logger.info(f"Verification token updated for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Error updating verification token: {str(e)}")
            raise 