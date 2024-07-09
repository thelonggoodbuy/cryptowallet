from redis import asyncio as aioredis
import redis
import os


# redis_url = "redis://localhost/1"
redis_url = os.environ.get("REDIS_URL")
redis_connection = aioredis.from_url(redis_url)

# sync_redis_connection = redis.Redis(host="localhost", port=6379, db=1)
