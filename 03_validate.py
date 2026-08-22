#!/usr/bin/env python3
import sys, pandas as pd
df = pd.read_csv("data_v2/daily/AAPL.csv")
errors = []
if df.shape[1] not in [107, 109, 113]: errors.append(f"Cols: {df.shape[1]} != 109")
if len(df) < 250: errors.append(f"Rows: {len(df)} < 1100")
if df[["open","high","low","close"]].isna().any().any(): errors.append("OHLC con NaN")
if "Risk_Score" not in df.columns: errors.append("Falta Risk_Score")
if "SMA_200" not in df.columns: errors.append("Falta SMA_200")
if errors:
    print(f"   ❌ {len(errors)} errores:")
    for e in errors: print(f"      - {e}")
    sys.exit(1)
print(f"   ✅ Shape: {df.shape[0]} rows × {df.shape[1]} cols")
print(f"   ✅ Date range: {df['date'].iloc[0]} → {df['date'].iloc[-1]}")
