import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("[worker] waiting for jobs...")

while True:
    _, raw = r.brpop("jobs")
    job = json.loads(raw)
    print(f"[worker] picked up: {job}")

    if job["task"] == "send_email":
        time.sleep(3)   # simulate slow SMTP
        print(f"[worker] ✅ email sent to {job['user']} (took 3s)")

    if job["task"] == "generate_pdf":
        time.sleep(5)   # simulate slow PDF
        print(f"[worker] ✅ PDF generated for {job['user']} (took 5s)")
