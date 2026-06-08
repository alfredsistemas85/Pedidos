import redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_redis_client() -> redis.Redis:
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        return r
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None

redis_client = get_redis_client()
