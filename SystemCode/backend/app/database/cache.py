# app/database/cache.py
import os
import logging
import redis.asyncio as redis

log = logging.getLogger("uvicorn.error")

CACHE_TTL_SECONDS = 60 * 60 * 24  # 24h

# 允许两种配置：REDIS_URL 或 主机+端口
REDIS_URL = os.getenv("REDIS_URL") or None
REDIS_HOST = os.getenv("REDIS_HOST") or None
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client = None  # 默认禁用缓存，不抛异常

try:
    if REDIS_URL:
        # 注意：只有在 REDIS_URL 是非空字符串时才会进入这里
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        log.info("✅ Redis connected via REDIS_URL")
    elif REDIS_HOST:
        pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
        )
        redis_client = redis.Redis(connection_pool=pool)
        log.info(f"✅ Redis connected at {REDIS_HOST}:{REDIS_PORT}")
    else:
        log.warning("⚠️ Redis disabled (no REDIS_URL/REDIS_HOST).")
except Exception as e:
    # 连接失败也不要阻止应用启动
    redis_client = None
    log.exception(f"❌ Redis init failed (disabled): {e}")
