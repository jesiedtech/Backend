import asyncio
from app.db.session import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting database initialization...")
        await init_db()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 