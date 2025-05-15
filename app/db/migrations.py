import asyncpg
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_migrations():
    """Run all migrations for the users table."""
    logger.info("Starting migrations...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        logger.info("Connected to database successfully")
        
        # Create users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
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
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_migrations())