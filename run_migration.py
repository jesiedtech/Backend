import asyncio
import asyncpg
from app.core.config import settings

async def run_migration():
    # Connect to the database
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        # Read and execute the migration file
        with open('migrations/002_add_login_logout_tracking.sql', 'r') as f:
            migration_sql = f.read()
            await conn.execute(migration_sql)
            print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {str(e)}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration()) 