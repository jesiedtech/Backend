import asyncio
import asyncpg
import logging
import uuid
from app.core.config import settings
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_registration():
    try:
        # Connect to database
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Create test user
        user_id = str(uuid.uuid4())
        name = "Test User"
        email = f"test_{user_id[:8]}@example.com"
        password = "testpassword123"
        hashed_password = get_password_hash(password)
        
        logger.info(f"Attempting to create user with email: {email}")
        
        # Insert user
        await conn.execute('''
            INSERT INTO users (
                id, name, email, hashed_password,
                is_active, is_verified, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', user_id, name, email, hashed_password, True, True)
        
        # Verify user was created
        user = await conn.fetchrow(
            'SELECT * FROM users WHERE email = $1',
            email
        )
        
        if user:
            logger.info("User created successfully!")
            logger.info(f"User details: ID={user['id']}, Name={user['name']}, Email={user['email']}")
        else:
            logger.error("Failed to create user!")
        
        await conn.close()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_user_registration()) 