#!/usr/bin/env python3

import random
import time
from datetime import datetime, timedelta

LOG_FILE = "/home/morta/workspace/elk-lab/logs/nginx-logs/access.log"
DURATION = 300
RPS = 10

endpoints = [
    ("/products/123", 200),
    ("/products/456", 200),
    ("/products/789", 404),
    ("/cart", 200),
    ("/checkout", 200),
    ("/api/checkout/payment", 200),
    ("/api/checkout/payment", 500),
    ("/health", 200),
    ("/nonexistent", 404),
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

clients = ["192.168.1." + str(random.randint(10, 250)) for _ in range(20)]

def format_nginx_log(client_ip, timestamp, method, endpoint, status, bytes_sent):
    return f'{client_ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {bytes_sent} "-" "{random.choice(user_agents)}"'

def generate_logs():
    print(f"[{datetime.now()}] Starting log generator...")
    print(f"Output: {LOG_FILE}")
    print(f"Duration: {DURATION}s @ {RPS} entries/s")
    print("-" * 50)

    start_time = time.time()
    current_time = datetime.now() - timedelta(minutes=5)

    with open(LOG_FILE, "w") as f:
        while (time.time() - start_time) < DURATION:
            for _ in range(RPS):
                current_time += timedelta(seconds=random.randint(100, 2000))
                endpoint, status = random.choice(endpoints)
                method = random.choice(["GET", "POST"])
                bytes_sent = random.randint(200, 8000)
                client_ip = random.choice(clients)

                timestamp = current_time.strftime("%d/%b/%Y:%H:%M:%S +0000")
                log_entry = format_nginx_log(client_ip, timestamp, method, endpoint, status, bytes_sent)
                f.write(log_entry + "\n")

            f.flush()
            time.sleep(1)

    print("-" * 50)
    print(f"[{datetime.now()}] Log generation complete!")
    print(f"Output: {LOG_FILE}")

if __name__ == "__main__":
    generate_logs()