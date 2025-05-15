import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

async def test_registration():
    """Test user registration."""
    logger.info("Testing registration...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/api/v1/users/register", json=TEST_USER) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Registration successful!")
                    logger.info(f"Response: {data}")
                    return data
                else:
                    error_data = await response.json()
                    logger.error(f"Registration failed: {error_data}")
                    return None
        except Exception as e:
            logger.error(f"Registration request failed: {str(e)}")
            return None

async def test_login():
    """Test user login."""
    logger.info("Testing login...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/users/login",
                json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Login successful!")
                    logger.info(f"Response: {data}")
                    return data
                else:
                    error_data = await response.json()
                    logger.error(f"Login failed: {error_data}")
                    return None
        except Exception as e:
            logger.error(f"Login request failed: {str(e)}")
            return None

async def test_resend_verification():
    """Test resending verification email."""
    logger.info("Testing resend verification...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/users/resend-verification",
                json={"email": TEST_USER["email"]}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Resend verification successful!")
                    logger.info(f"Response: {data}")
                    return data
                else:
                    error_data = await response.json()
                    logger.error(f"Resend verification failed: {error_data}")
                    return None
        except Exception as e:
            logger.error(f"Resend verification request failed: {str(e)}")
            return None

async def test_forgot_password():
    """Test forgot password flow."""
    logger.info("Testing forgot password...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/api/v1/users/forgot-password",
                json={"email": TEST_USER["email"]}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Forgot password request successful!")
                    logger.info(f"Response: {data}")
                    return data
                else:
                    error_data = await response.json()
                    logger.error(f"Forgot password request failed: {error_data}")
                    return None
        except Exception as e:
            logger.error(f"Forgot password request failed: {str(e)}")
            return None

async def run_tests():
    """Run all authentication flow tests."""
    logger.info("Starting authentication flow tests...")
    
    # Test registration
    registration_result = await test_registration()
    if not registration_result:
        logger.error("Registration test failed")
        return
    
    # Test login (should fail before verification)
    login_result = await test_login()
    if login_result:
        logger.error("Login test failed - should not be able to login before verification")
        return
    
    # Test resend verification
    resend_result = await test_resend_verification()
    if not resend_result:
        logger.error("Resend verification test failed")
        return
    
    # Test forgot password
    forgot_result = await test_forgot_password()
    if not forgot_result:
        logger.error("Forgot password test failed")
        return
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(run_tests()) 