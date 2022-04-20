import os

import redis
from rq import Worker, Queue, Connection

import settings
import data

listen = ['high', 'default', 'stock', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

if os.environ["ENV"] == 'devlocal':
    conn = redis.Redis('localhost', 6379)
else:
    conn = redis.from_url(redis_url)



if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
