import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0,
    decode_responses=True,
    socket_connect_timeout=0.1,
    socket_timeout=0.1,
    retry_on_timeout=False
)