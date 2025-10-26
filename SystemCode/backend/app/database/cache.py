# app/database/cache.py
import os
import redis.asyncio as redis
import logging

log = logging.getLogger("uvicorn.error")

CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours in seconds

# 允许两种配置方式：REDIS_URL 或 REDIS_HOST
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = None

try:
    if REDIS_URL:
        # 完整 URL 写法：redis://:password@host:port/db
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        log.info(f"✅ Connected to Redis via REDIS_URL.")
    elif REDIS_HOST:
        # 主机+端口写法
        pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
        )
        redis_client = redis.Redis(connection_pool=pool)
        log.info(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}.")
    else:
        # 未配置 Redis 时不抛错，设置为 None
        redis_client = None
        log.warning("⚠️  REDIS_HOST or REDIS_URL not set; Redis features disabled.")
except Exception as e:
    redis_client = None
    log.exception(f"❌ Redis init failed: {e}")
