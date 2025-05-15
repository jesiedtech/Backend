import asyncio
import logging
from app.db.migrations import run_migrations
from app.core.config import settings

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the database with all migrations."""
    try:
        logger.info("Starting database initialization...")
        await run_migrations()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db()) 