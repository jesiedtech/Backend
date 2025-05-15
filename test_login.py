import asyncio
import asyncpg
import logging
import uuid
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_login():
    try:
        # Connect to database
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Create test user with specific credentials
        user_id = str(uuid.uuid4())
        name = "Test User"
        email = "user@gmail.com"
        password = "password"
        hashed_password = get_password_hash(password)
        
        logger.info(f"Creating test user with email: {email}")
        
        # Create and save user
        test_user = User(
            id=user_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True
        )
        
        await test_user.save(conn)
        logger.info("Test user created successfully")
        
        # Test 1: Successful login
        logger.info("\nTest 1: Testing successful login...")
        user = await User.get_by_email(conn, email)
        if user and verify_password(password, user.hashed_password):
            logger.info("✓ Login successful!")
            # Create access token
            access_token = create_access_token(data={"sub": user.email})
            logger.info(f"Access token generated: {access_token[:20]}...")
        else:
            logger.error("✗ Login failed!")
        
        # Test 2: Wrong password
        logger.info("\nTest 2: Testing wrong password...")
        wrong_password = "wrongpassword123"
        if user and not verify_password(wrong_password, user.hashed_password):
            logger.info("✓ Correctly rejected wrong password!")
        else:
            logger.error("✗ Wrong password was accepted!")
        
        # Test 3: Non-existent user
        logger.info("\nTest 3: Testing non-existent user...")
        non_existent_email = "nonexistent@example.com"
        non_existent_user = await User.get_by_email(conn, non_existent_email)
        if non_existent_user is None:
            logger.info("✓ Correctly identified non-existent user!")
        else:
            logger.error("✗ Found non-existent user!")
        
        await conn.close()
        logger.info("Database connection closed")
        
        # Return the test user credentials for API testing
        return {
            "email": email,
            "password": password
        }
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    credentials = asyncio.run(test_login())
    print("\nTest user credentials for API testing:")
    print(f"Email: {credentials['email']}")
    print(f"Password: {credentials['password']}") 