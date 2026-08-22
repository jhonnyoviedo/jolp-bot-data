#!/usr/bin/env python3
"""
Wrapper para requests con exponential backoff en 429.
"""
import time
import requests
import urllib3
urllib3.disable_warnings()

def fetch_with_backoff(url, params=None, max_retries=3, timeout=30):
    """
    Fetch con backoff exponencial en rate limit (429).
    Wait: 5s, 10s, 20s
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=timeout, verify=False)
            if response.status_code == 429:
                wait = 5 * (2 ** attempt)
                print(f"   ⚠️  Rate limit 429, esperando {wait}s...")
                time.sleep(wait)
                continue
            return response
        except requests.Timeout:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Timeout, reintento...")
                time.sleep(5)
                continue
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️  Error: {e}, reintento...")
                time.sleep(2)
                continue
            raise
    raise Exception(f"Max retries ({max_retries}) exceeded for {url}")

if __name__ == '__main__':
    import os
    ROIC_API_KEY = os.environ.get("ROIC_API_KEY", "")
    r = fetch_with_backoff(
        "https://api.roic.ai/v3.0.0/tickers/NASDAQ:AAPL",
        params={"apikey": ROIC_API_KEY}
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Test passed")
