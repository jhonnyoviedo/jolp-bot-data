#!/usr/bin/env python3
import os, sys
import pandas as pd
import numpy as np

print("   Cargando raw...")
df = pd.read_csv("data_v2/raw/AAPL_raw.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)
print(f"   {len(df)} velas")

# Core (8)
df["SMA_20"] = df["close"].rolling(20).mean()
df["SMA_50"] = df["close"].rolling(50).mean()
df["SMA_200"] = df["close"].rolling(200).mean()
df["EMA_20"] = df["close"].ewm(span=20, adjust=False).mean()
df["EMA_50"] = df["close"].ewm(span=50, adjust=False).mean()
df["EMA_100"] = df["close"].ewm(span=100, adjust=False).mean()
df["EMA_200"] = df["close"].ewm(span=200, adjust=False).mean()
delta = df["close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
rs = gain.rolling(14).mean() / loss.rolling(14).mean()
df["RSI_14"] = 100 - (100 / (1 + rs))

# MACD (4)
ema12 = df["close"].ewm(span=12, adjust=False).mean()
ema26 = df["close"].ewm(span=26, adjust=False).mean()
df["MACD"] = ema12 - ema26
df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
df["MACD_Hist_Subiendo"] = (df["MACD_Hist"] > df["MACD_Hist"].shift(1)).astype(int)

# Volatilidad (3)
tr = pd.concat([df["high"]-df["low"], (df["high"]-df["close"].shift(1)).abs(), (df["low"]-df["close"].shift(1)).abs()], axis=1).max(axis=1)
df["ATR_14"] = tr.rolling(14).mean()

# Volumen (4)
df["Vol_SMA_10"] = df["volume"].rolling(10).mean()
df["Vol_SMA_20"] = df["volume"].rolling(20).mean()
df["VolRel10"] = df["volume"] / df["Vol_SMA_10"]
df["VolRel20"] = df["volume"] / df["Vol_SMA_20"]

# Stochastic (2)
low14 = df["low"].rolling(14).min()
high14 = df["high"].rolling(14).max()
df["Stoch_K"] = 100*(df["close"]-low14)/(high14-low14)
df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

# Candle (3)
df["Body"] = (df["close"]-df["open"]).abs()
df["Mecha_Sup"] = df["high"] - df[["open","close"]].max(axis=1)
df["Mecha_Inf"] = df[["open","close"]].min(axis=1) - df["low"]

# Posición (9)
h52 = df["high"].rolling(252).max()
l52 = df["low"].rolling(252).min()
df["Position_52w_Pct"] = (df["close"]-l52)/(h52-l52)
df["RS_vs_SPY"] = 0
df["Dist_EMA_20_pct"] = (df["close"]-df["EMA_20"])/df["close"]*100
df["Dist_SMA_20_pct"] = (df["close"]-df["SMA_20"])/df["close"]*100
df["Dist_SMA_50_pct"] = (df["close"]-df["SMA_50"])/df["close"]*100
df["Dist_SMA_200_pct"] = (df["close"]-df["SMA_200"])/df["close"]*100
df["Dist_BUY_ZONE"] = (df["close"] < df["SMA_200"]*0.95).astype(int)
df["High_52W"] = h52
df["Low_52W"] = l52

# Returns (3)
df["Ret_1"] = df["close"].pct_change(1)*100
df["Ret_5"] = df["close"].pct_change(5)*100
df["Ret_20"] = df["close"].pct_change(20)*100

# TP Dinámico (3)
df["Swing_High_20"] = df["high"].rolling(20).max()
df["Dist_EMA_20"] = (df["close"]-df["EMA_20"])/df["EMA_20"]*100
df["TP_Dinamico"] = df["Swing_High_20"]

# Momentum (4)
df["VWAP"] = (df["close"]*df["volume"]).cumsum() / df["volume"].cumsum()
df["ADX_14"] = 25
df["Plus_DI"] = 20
df["Minus_DI"] = 20

# Ichimoku (5)
df["Tenkan"] = (df["high"].rolling(9).max() + df["low"].rolling(9).min())/2
df["Kijun"] = (df["high"].rolling(26).max() + df["low"].rolling(26).min())/2
df["Senkou_A"] = (df["Tenkan"]+df["Kijun"])/2
df["Senkou_B"] = (df["high"].rolling(52).max() + df["low"].rolling(52).min())/2
df["Chikou"] = df["close"]

# Fibonacci (5)
df["Fib_236"] = h52 - 0.236*(h52-l52)
df["Fib_382"] = h52 - 0.382*(h52-l52)
df["Fib_500"] = h52 - 0.500*(h52-l52)
df["Fib_618"] = h52 - 0.618*(h52-l52)
df["Fib_786"] = h52 - 0.786*(h52-l52)

# Pivots (7)
pp = (df["high"]+df["low"]+df["close"])/3
df["Pivot_PP"] = pp
df["Pivot_R1"] = 2*pp - df["low"]
df["Pivot_R2"] = pp + (df["high"]-df["low"])
df["Pivot_R3"] = df["high"] + 2*(pp-df["low"])
df["Pivot_S1"] = 2*pp - df["high"]
df["Pivot_S2"] = pp - (df["high"]-df["low"])
df["Pivot_S3"] = df["low"] - 2*(df["high"]-pp)

# Flags (22 - placeholders)
for col in ["Vol_Dryup","Vol_Climax","BB_Squeeze","BB_Breakout","MACD_Cross_Up","Golden_Cross","SMA20_Cross_Up","Oversold","Overbought","Trend_Up","Breakout_Vol","TP_Agotamiento","Vol_Climax_Up","MACD_Divergence","Trend_Weakness","Overextended","Exhaustion_Gap","Stoch_Extreme","Stop_Loss_Triggered","BUY_ZONE","ACC","REB"]:
    df[col] = 0

# Fundamentals (12 - placeholders)
for col in ["ROIC","ROE","Net_Margin","Gross_Margin","Operating_Margin","EBITDA_Margin","Current_PE","Current_PB","Current_EV_EBITDA","Current_EV_Sales","Current_FCF_Yield","Market_Cap"]:
    df[col] = np.nan

# P/E 5y (5 - placeholders)
df["PE_5y_mean"] = np.nan
df["PE_5y_max"] = np.nan
df["PE_5y_min"] = np.nan
df["PE_5y_pct"] = np.nan
df["PE_5y_signal"] = ""

# Metadata (3)
df["Currency"] = "USD"
df["FX_Rate"] = 1.0
df["Asset_Type"] = "stock"

# Risk_Score (1)
import sys
sys.path.insert(0, "src_v2")
from calculate_risk_score import calculate_for_row
df["Risk_Score"] = df.apply(lambda row: calculate_for_row(row, row.get("Sector", "Unknown")), axis=1)

# Guardar
os.makedirs("data_v2/daily", exist_ok=True)
df.to_csv("data_v2/daily/AAPL.csv", index=False)
print(f"   ✅ {df.shape[1]} cols × {len(df)} rows")
