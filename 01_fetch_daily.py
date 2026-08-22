#!/usr/bin/env python3
import os, sys, requests, urllib3
import pandas as pd
urllib3.disable_warnings()

ROIC_API_KEY = os.environ.get("ROIC_API_KEY", "")
if not ROIC_API_KEY:
    print("ERROR: ROIC_API_KEY no configurada")
    sys.exit(1)

ROIC_BASE = "https://api.roic.ai/v3.0.0"
TICKER = "AAPL"

print(f"   Fetching 5y OHLCV de {TICKER}...")
r = requests.get(
    f"{ROIC_BASE}/stock-prices/NASDAQ:{TICKER}",
    params={"apikey": ROIC_API_KEY, "interval": "day"},
    timeout=30, verify=False
)
r.raise_for_status()
data = r.json()

if "data" not in data or not data["data"]:
    print("ERROR: respuesta vacía")
    sys.exit(1)

df = pd.DataFrame(data["data"])
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
df = df[["date", "open", "high", "low", "close", "volume"]]
df.columns = ["date", "open", "high", "low", "close", "volume"]
df.to_csv("data_v2/raw/AAPL_raw.csv", index=False)
print(f"   ✅ {len(df)} velas obtenidas")
