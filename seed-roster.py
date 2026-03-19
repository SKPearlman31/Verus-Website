#!/usr/bin/env python3
"""One-time script to push current roster data to WordPress."""
import json
import os
import ssl
import sys
import urllib.request

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def main():
    site_url = input("Enter your WordPress site URL (e.g., https://verusteam.com): ").strip().rstrip("/")
    api_key = input("Enter your Verus Stats API key: ").strip()

    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "players.json")
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run update_stats.py first.")
        sys.exit(1)

    with open(data_path) as f:
        data = json.load(f)

    endpoint = f"{site_url}/wp-json/verus/v1/update-stats"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Verus-Key": api_key,
            "User-Agent": "VerusStatsSeeder/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f"Success: {result.get('message', 'OK')}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
