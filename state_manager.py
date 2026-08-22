#!/usr/bin/env python3
"""
Gestiona data/state.json para tracking de backfill.
"""
import json
import os
from datetime import datetime

STATE_FILE = "data_v2/state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "version": "2.0",
        "last_run": None,
        "tickers": {}
    }

def save_state(state):
    state["last_run"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def update_ticker(ticker, data_type, **kwargs):
    state = load_state()
    if ticker not in state["tickers"]:
        state["tickers"][ticker] = {}
    if data_type not in state["tickers"][ticker]:
        state["tickers"][ticker][data_type] = {}
    state["tickers"][ticker][data_type].update(kwargs)
    state["tickers"][ticker][data_type]["last_update"] = datetime.now().isoformat()
    save_state(state)

if __name__ == '__main__':
    state = load_state()
    print(f"   State cargado: {len(state.get('tickers', {}))} tickers")
