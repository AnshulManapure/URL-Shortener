import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=0.1,
    socket_timeout=0.1,
    retry_on_timeout=False
)