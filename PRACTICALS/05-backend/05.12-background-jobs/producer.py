import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def signup(username):
    start = time.time()
    # 1. save user (simulated — fast)
    time.sleep(0.01)
    # 2. drop the job into the queue (fast)
    job = {"task": "send_email", "user": username}
    r.lpush("jobs", json.dumps(job))
    elapsed = time.time() - start
    print(f"[producer] signup({username}) returned in {elapsed*1000:.0f}ms")

signup("felix")
signup("wanjiku")
signup("otieno")
