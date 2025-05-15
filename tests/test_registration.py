import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_registration():
    url = "http://localhost:8001/api/v1/users/register"
    
    # Test user data
    user_data = {
        "email": "test@example.com",
        "first_name": "John",
        "surname": "Doe",
        "password": "Test123!@#"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=user_data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Registration successful!")
                    logger.info(f"Response: {json.dumps(result, indent=2)}")
                else:
                    error = await response.text()
                    logger.error(f"Registration failed with status {response.status}")
                    logger.error(f"Error: {error}")
    except Exception as e:
        logger.error(f"Error during registration test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_registration()) 