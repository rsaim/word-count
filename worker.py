import os

import redis
from rq import Connection, Queue, Worker

redis_queue = ["default"]
redis_url = os.getenv("REDISTOGO_URL", "redis://localhost:6379")

conn = redis.from_url(redis_url)

def count_and_save_words(url):
    from app import count_and_save_words
    return count_and_save_words(url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(Queue, redis_queue)))
        worker.work()