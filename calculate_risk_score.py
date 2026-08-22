#!/usr/bin/env python3
"""
Calcula Risk_Score (0-100) combinando 4 componentes:
- V13_score (backtest)
- Sector_risk (hardcoded)
- Tech_risk (basado en flags e indicadores)
- Fund_risk (basado en métricas fundamentales)

Pesos: V13=0.30, Sector=0.20, Tech=0.25, Fund=0.25
"""
import json
import os

SECTOR_RISK = {
    'Technology': 45,
    'Healthcare': 35,
    'Financials': 55,
    'Consumer Discretionary': 60,
    'Consumer Staples': 25,
    'Energy': 75,
    'Utilities': 20,
    'Industrials': 50,
    'Materials': 65,
    'Real Estate': 50,
    'Communication Services': 40,
    'Crypto': 90,
    'Unknown': 50,
}

def get_v13_score(ticker, signals_history=None):
    if not signals_history:
        return 50.0
    wins = sum(1 for s in signals_history if s.get('result') == 'win')
    win_rate = wins / len(signals_history)
    return round(100 - (win_rate * 100), 2)

def get_sector_risk(sector):
    return SECTOR_RISK.get(sector, 50)

def get_technical_risk(row):
    risk = 0
    exit_flags = ['TP_Agotamiento', 'Vol_Climax_Up', 'MACD_Divergence',
                  'Trend_Weakness', 'Overextended', 'Exhaustion_Gap',
                  'Stoch_Extreme', 'Stop_Loss_Triggered']
    active_exits = sum(1 for f in exit_flags if row.get(f, 0))
    risk += min(active_exits * 8, 64)
    rsi = row.get('RSI_14', 50)
    if pd_is_nan(rsi):
        rsi = 50
    if rsi > 80 or rsi < 20:
        risk += 15
    elif rsi > 70 or rsi < 30:
        risk += 8
    dist = row.get('Dist_EMA_20_pct', 0)
    if pd_is_nan(dist):
        dist = 0
    if abs(dist) > 15:
        risk += 12
    elif abs(dist) > 10:
        risk += 6
    return min(risk, 100)

def get_fundamental_risk(row):
    risk = 0
    roic = row.get('ROIC', None)
    if roic is not None and not pd_is_nan(roic):
        if roic < 0:
            risk += 30
        elif roic < 5:
            risk += 20
        elif roic < 10:
            risk += 10
    pe = row.get('Current_PE', None)
    if pe is not None and not pd_is_nan(pe) and pe > 0:
        if pe > 50:
            risk += 25
        elif pe > 30:
            risk += 15
        elif pe > 20:
            risk += 8
    roe = row.get('ROE', None)
    if roe is not None and not pd_is_nan(roe) and roe < 5:
        risk += 15
    margin = row.get('Net_Margin', None)
    if margin is not None and not pd_is_nan(margin) and margin < 0:
        risk += 20
    return min(risk, 100)

def pd_is_nan(x):
    """Check if value is NaN/None without importing pandas."""
    if x is None:
        return True
    if isinstance(x, float):
        return x != x  # NaN != NaN
    return False

def calculate_risk_score(v13_score, sector_risk, technical_risk, fundamental_risk):
    if not all(0 <= x <= 100 for x in [v13_score, sector_risk, technical_risk, fundamental_risk]):
        raise ValueError("All components must be 0-100")
    return round(
        v13_score * 0.30 +
        sector_risk * 0.20 +
        technical_risk * 0.25 +
        fundamental_risk * 0.25,
        2
    )

def calculate_for_row(row, sector, signals_history=None):
    v13 = get_v13_score(row.get('Ticker', ''), signals_history)
    sec = get_sector_risk(sector)
    tech = get_technical_risk(row)
    fund = get_fundamental_risk(row)
    return calculate_risk_score(v13, sec, tech, fund)

if __name__ == '__main__':
    import sys
    import pandas as pd
    df = pd.read_csv(sys.argv[1])
    if 'Sector' not in df.columns:
        df['Sector'] = 'Unknown'
    df['Risk_Score'] = df.apply(lambda row: calculate_for_row(row, row.get('Sector', 'Unknown')), axis=1)
    df.to_csv(sys.argv[1], index=False)
    print(f"   ✅ Risk_Score calculado para {len(df)} filas")
