#!/usr/bin/env python3
"""
Gestiona data/skipped_tickers.json con retry logic.
"""
import json
import os
from datetime import datetime, timedelta

SKIPPED_FILE = "data_v2/skipped_tickers.json"

def load_skipped():
    if os.path.exists(SKIPPED_FILE):
        with open(SKIPPED_FILE) as f:
            return json.load(f)
    return {"version": "2.0", "skipped": []}

def save_skipped(data):
    with open(SKIPPED_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_skipped(ticker, asset_type, endpoint, reason, http_code=None, error_message=""):
    data = load_skipped()
    now = datetime.now()
    next_retry = now + timedelta(days=1)
    entry = {
        "ticker": ticker,
        "asset_type": asset_type,
        "endpoint": endpoint,
        "reason": reason,
        "http_code": http_code,
        "timestamp": now.isoformat(),
        "retries": 0,
        "next_retry": next_retry.isoformat(),
        "last_error_message": error_message
    }
    # Update existing or add
    for i, e in enumerate(data["skipped"]):
        if e["ticker"] == ticker and e["endpoint"] == endpoint:
            data["skipped"][i] = entry
            save_skipped(data)
            return
    data["skipped"].append(entry)
    save_skipped(data)

if __name__ == '__main__':
    data = load_skipped()
    print(f"   Skipped: {len(data['skipped'])} entradas")
