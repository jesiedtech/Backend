import asyncpg
import logging
from typing import AsyncGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection."""
    logger.info(f"Attempting to connect to database with URL: {settings.DATABASE_URL}")
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        logger.info("Database connection established successfully")
        try:
            yield conn
        finally:
            logger.info("Closing database connection")
            await conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

async def init_db():
    """Initialize database with required tables."""
    logger.info("Initializing database...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        logger.info("Connected to database successfully")
        
        # Create users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NULL,
                is_active BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Users table created successfully")
        
        # Migration: Add role column if it doesn't exist
        await conn.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role') THEN
                    ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user';
                END IF;
            END $$;
        ''')
        logger.info("Migration completed: role column added if not present")
        
        await conn.close()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise 