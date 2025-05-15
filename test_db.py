import asyncio
import asyncpg
import logging
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    try:
        # Test connection
        logger.info(f"Attempting to connect to database with URL: {settings.DATABASE_URL}")
        conn = await asyncpg.connect(settings.DATABASE_URL)
        logger.info("Database connection successful!")

        # Test table existence
        logger.info("Checking users table...")
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        logger.info(f"Users table exists: {table_exists}")

        if table_exists:
            # Count users
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            logger.info(f"Number of users in database: {user_count}")

            # List all users
            users = await conn.fetch("SELECT id, name, email, created_at FROM users")
            logger.info("\nExisting users:")
            for user in users:
                logger.info(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Created: {user['created_at']}")

        await conn.close()
        logger.info("Database connection closed successfully")
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_database_connection()) 