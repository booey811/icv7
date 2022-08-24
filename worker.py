import os

import redis
import rq
from rq import Worker, Queue, Connection

import settings
import data

listen = ['high', 'default', 'stock', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

if os.environ["ENV"] == 'devlocal':
    conn = redis.Redis('localhost', 6379)
else:
    conn = redis.from_url(redis_url)

q_lo = Queue("low", connection=conn, default_timeout=3600)
q_def = Queue("default", connection=conn, default_timeout=3600)
q_hi = Queue("high", connection=conn, default_timeout=3600)
q_stock = rq.Queue("stock", connection=conn, default_timeout=3600)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
