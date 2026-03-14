import os
import asyncio
from openai import AsyncOpenAI
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

async def check_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not found in environment.")
        return

    logger.info(f"🔍 Testing key starting with: {api_key[:10]}...")
    
    client = AsyncOpenAI(api_key=api_key)
    
    try:
        # Test 1: Simple Completion to verify key validity
        logger.info("📡 Sending test request to gpt-4o-mini...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, are you active?"}],
            max_tokens=5
        )
        logger.success("✅ API Key is VALID and ACTIVE.")
        logger.info(f"🤖 Response: {response.choices[0].message.content}")
        
    except Exception as e:
        error_msg = str(e).lower()
        if "insufficient_quota" in error_msg or "billing" in error_msg:
            logger.error(f"⚠️ Key is VALID but has NO QUOTA (Insufficient Balance). Error: {e}")
        elif "invalid_api_key" in error_msg:
            logger.error(f"❌ Key is INVALID or REVOKED. Error: {e}")
        else:
            logger.error(f"❓ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_openai())
