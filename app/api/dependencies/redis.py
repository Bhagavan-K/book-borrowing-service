from redis import asyncio as aioredis
from fastapi import Request
from ...core.config import settings

async def get_redis():
    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()