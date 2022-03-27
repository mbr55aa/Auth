import redis

from core import config

redis_db = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)