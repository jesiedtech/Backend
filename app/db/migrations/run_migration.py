import asyncio
import asyncpg
from app.core.config import settings
import os

async def run_migration():
    # Read the migration SQL file
    migration_path = os.path.join(os.path.dirname(__file__), 'add_reset_token.sql')
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    try:
        # Connect to the database
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Start a transaction
        async with conn.transaction():
            # Execute the migration
            await conn.execute(migration_sql)
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Error running migration: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration()) 