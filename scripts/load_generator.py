#!/usr/bin/env python3

import random
import time
import socket

LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5044
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

def generate_load():
    print(f"Starting load generator...")
    print(f"Target: nginx://localhost")
    print(f"Duration: {DURATION}s @ {RPS} req/s")
    print("-" * 50)

    start_time = time.time()
    request_count = 0

    while (time.time() - start_time) < DURATION:
        for _ in range(RPS):
            endpoint, expected_status = random.choice(endpoints)
            url = f"http://localhost{endpoint}"

            try:
                import urllib.request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=1) as resp:
                    status = resp.status
                    request_count += 1

                if request_count % 50 == 0:
                    print(f"Requests: {request_count}")

            except Exception:
                pass

        time.sleep(1)

    print("-" * 50)
    print(f"Load generation complete!")
    print(f"Total requests: {request_count}")

if __name__ == "__main__":
    generate_load()