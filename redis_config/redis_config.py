from redis import asyncio as aioredis




redis_url = "redis://localhost/1"
redis_connection = aioredis.from_url(redis_url)