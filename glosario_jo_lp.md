# JO-LP Glosario v3 (Mavis Edition)

> **Versión:** 3.0 (20-ago-2026)
> **Para:** Mavis (asistente de análisis de inversiones) - chat "JO-LP Análisis"
> **Stack:** Twelve Data (ETF/intraday) + ROIC (stocks fundamentals) + Binance (crypto)

---

## 1. Arquitectura del Sistema

JO-LP es un sistema distribuido de análisis de inversiones con:
- **VPS Hetzner** ejecutando el bot (cron 9-12 pasos)
- **GitHub repo público** `jhonnyoviedo/jolp-bot-data` con todos los CSV
- **Telegram bot** `@JOLPAcciones_bot` para consultas
- **Mavis** (este chat) para análisis profundo

```
data/
├── daily/{stocks,etf,crypto}/{TICKER}.csv       # 30 días × 68 cols
├── weekly/{stocks,etf,crypto}/{TICKER}.csv      # 52 semanas × 68 cols (vela semanal)
├── monthly/{stocks,etf,crypto}/{TICKER}.csv     # 60 meses × 68 cols (vela mensual)
├── fundamentals/
│   ├── current_full.csv                         # 162 × 89 cols (snapshot HOY)
│   ├── historical/quarterly/{TICKER}.json      # 5 años × 4 quarters = 20
│   ├── historical/annual_pe/ticker_pe_historical.json  # P/E 5y × 162
│   └── sector_pe.json
├── snapshots/
│   ├── ephemeral/{apertura,pre_cierre,ondemand}/*.csv   # se eliminan al final del día
│   └── historical/post_cierre_YYYY-MM-DD.csv            # 6 meses
├── indicators/current.csv
├── flags/current.csv
├── fx/{current,history}.csv
├── macro/*.json
└── ia_reports/
    ├── ephemeral/                              # se eliminan
    └── historical/post_cierre_YYYY-MM-DD/{report.md, report.json}  # 6 meses
```

---

## 2. Daily File (68 columnas)

Cada archivo `data/daily/{asset_type}/{TICKER}.csv` tiene **30 filas × 68 columnas**.

### 2.1 Vela cruda (6)
- `Date` - Fecha
- `Open`, `High`, `Low`, `Close` - OHLC
- `Volume` - Volumen

### 2.2 Indicadores core (8)
- `SMA_20`, `SMA_50`, `SMA_200` - Medias móviles simples
- `EMA_20`, `EMA_50`, `EMA_100`, `EMA_200` - Medias móviles exponenciales
- `RSI_14` - Relative Strength Index (0-100)

### 2.3 Momentum (4)
- `MACD`, `MACD_Signal`, `MACD_Hist` - MACD
- `MACD_Hist_Subiendo` - True si histograma subiendo

### 2.4 Volatilidad (3)
- `ATR_14` - Average True Range
- `BB_PctB` - %B (posición del precio dentro de BB)
- `BB_Width` - Amplitud BB (para detectar squeeze)

### 2.5 Volumen (4) ⭐ VolRel10/20
- `Vol_SMA_10`, `Vol_SMA_20` - Promedios
- `VolRel10` - Volume / Vol_SMA_10 (usado en Vol_Dryup, Vol_Climax)
- `VolRel20` - Volume / Vol_SMA_20

### 2.6 Stochastic (2)
- `Stoch_K`, `Stoch_D` - Stochastic %K y %D

### 2.7 Vela japonesa (3)
- `Cuerpo` - |Close - Open|
- `Mecha_Sup` - High - max(Open, Close)
- `Mecha_Inf` - min(Open, Close) - Low

### 2.8 Posición/Market (5)
- `Position_52w_Pct` - % del rango 52 semanas
- `RS_vs_SPY` - Relative Strength vs S&P 500
- `Distance_to_EMA_20_pct`
- `Distance_to_SMA_200_pct`
- `Distance_to_BUY_ZONE_pct`

### 2.9 TP Dinámico (3) ⭐
- `Swing_High_20` - High máximo 20 períodos
- `Distancia_EMA_20` - Close - EMA_20
- `TP_Dinamico` - Swing_High_20 + Distancia_EMA_20 (línea naranja del chart)

### 2.10 Flags entrada (11)
- `Vol_Dryup` - VolRel10<0.5 + RSI<30
- `Vol_Climax` - VolRel10>3.0 + RSI>70
- `BB_Squeeze` - BB_Width < p10 histórico
- `BB_Breakout` - Close > BB_Upper
- `MACD_Cross_Up` - Cruce MACD hacia arriba
- `Golden_Cross` - SMA50 > SMA200
- `SMA20_Cross_Up` - Precio cruza SMA20
- `Oversold` - RSI<30
- `Overbought` - RSI>70
- `Trend_Up` - Close > SMA50
- `Breakout_Vol` - High rompe anterior + VolRel10>1.5

### 2.11 Flags exit (8)
- `TP_Agotamiento` - RSI>65
- `Vol_Climax_Up` - VolRel10>3.0 + RSI>70 + vela verde
- `MACD_Divergence` - Precio sube, MACD baja
- `Trend_Weakness` - Close < SMA50
- `Overextended` - Close > EMA20 + ATR*0.5
- `Exhaustion_Gap` - Mecha_Sup > Cuerpo*1.2
- `Stoch_Extreme` - Stoch_K>95
- `Stop_Loss_Triggered` - -5% en 1 día

### 2.12 Flags custom (3) ⭐
- `BUY_ZONE` - Close<EMA100 + RSI<40 + MACD_Hist_Subiendo + Rechazo_Inf
- `ACC` - Close<EMA50 + RSI<35 + MACD_cross_up + vela verde + Rechazo_Inf
- `REB` - Close<EMA50 + MACD_cross_up + RSI>45 + Close>EMA20 + Ruptura_High

### 2.13 P/E snapshot (5) ⭐ INCLUYE MAX/MIN
- `Current_PE` - P/E actual
- `PE_5y_mean` - Promedio 5 años
- `PE_5y_max` - Máximo 5 años ⭐
- `PE_5y_min` - Mínimo 5 años ⭐
- `PE_5y_pct` - % posición actual vs histórico

### 2.14 Fundamentals live (3)
- `ROIC` - Return on Invested Capital
- `ROE` - Return on Equity
- `Net_Margin` - Margen neto

---

## 3. Weekly / Monthly

Misma estructura de 68 cols. La diferencia es la **vela**:

| Timeframe | Vela | Rango |
|-----------|------|-------|
| Daily | 1 día | 30 filas |
| Weekly | 1 semana | 52 filas (52 semanas) |
| Monthly | 1 mes | 60 filas (5 años) |

**Cálculo:**
- Weekly: agrega daily (Mon-Fri) → OHLCV semanal + recalcula indicadores
- Monthly: agrega daily → OHLCV mensual + recalcula indicadores

---

## 4. Multi-Timeframe Analysis (MTA)

**Concepto:** Mavis puede leer el mismo activo en 3 timeframes y **contrastar** señales.

**Ejemplo (BSX):**
- Daily: muestra REB, ACC múltiples durante el downtrend (muchas señales falsas)
- Weekly: confirma ACC en buy zone = el último piso (única señal real)
- Monthly: trend macro de fondo

**Tier de señales (a validar en backtest P-020):**
- Tier 1: Daily REB + Weekly ACC + Monthly BUY_ZONE (alta convicción)
- Tier 2: Daily REB + Weekly ACC (media)
- Tier 3: Daily REB solo (baja)

---

## 5. P/E Histórico 5 años

**Cálculo:**
```python
P/E_mes = Price_mes / EPS_del_trimestre_más_reciente a esa fecha
```

**Output:** `data/fundamentals/historical/annual_pe/ticker_pe_historical.json`
- `current_pe` - P/E actual
- `pe_history_5y` - 60 entries (60 meses)
- `stats_5y.mean`, `median`, `stdev`, `min`, `max`, `pct_5y`, `signal`
- `signal`: "expensive" (>p75) / "fair" / "cheap" (<p25)

---

## 6. Quarterly 5 años

**Fuente:** ROIC `income_statement` con `limit=20` (1 call/ticker, 160 calls total)

**Output:** `data/fundamentals/historical/quarterly/{TICKER}_quarterly.json`
- `quarters` (20 entries): revenue, net_income, eps_diluted, ebitda, etc.

---

## 7. APIs

| Fuente | Activos | Cuándo | Costo |
|--------|---------|--------|-------|
| **ROIC** | 160 stocks | post-cierre | 300 calls/min, sin rate limit |
| **Binance** | 5 crypto | siempre | gratis |
| **Twelve Data** | 17 ETF, 24 FX, 163 stocks intraday | apertura + pre-cierre + ondemand | 800/día free |
| **Twelve Data** | stocks (NO intraday) | post-cierre | incluido |

**Importante:** ROIC trae `stock-prices` 1d que puede reemplazar Twelve Data para stocks.

---

## 8. Cron Schedule

| Hora ET | Cron | Pasos |
|---------|------|-------|
| 9:57 AM | apertura | TD stocks/ETF intraday + Binance |
| 2:30 PM | pre-cierre | TD stocks/ETF intraday |
| 4:30 PM | post-cierre | 10 pasos: Binance, ROIC, FX+ETF, Daily, Weekly, Monthly, Quarterly, P/E, Snapshot, IA |

---

## 9. Lifecycle de Archivos

| Tipo | Lifecycle |
|------|-----------|
| Snapshot ephemeral | se elimina en post-cierre (mismo día) |
| Snapshot historical | 6 meses |
| IA report ephemeral | se elimina en post-cierre |
| IA report historical | 6 meses |
| Daily/Weekly/Monthly | rolling (30/52/60) |
| Quarterly 5y | se actualiza semanalmente |
| P/E 5y | se actualiza diariamente |

---

## 10. URLs RAW (GitHub)

Todas las URLs son `https://raw.githubusercontent.com/jhonnyoviedo/jolp-bot-data/main/...`

Ejemplos:
- Daily AAPL: `data/daily/stocks/AAPL.csv`
- Weekly AAPL: `data/weekly/stocks/AAPL.csv`
- Monthly AAPL: `data/monthly/stocks/AAPL.csv`
- Snapshot: `data/snapshots/historical/post_cierre_2026-08-20.csv`
- P/E 5y: `data/fundamentals/historical/annual_pe/ticker_pe_historical.json`
- IA report: `data/ia_reports/historical/post_cierre_2026-08-20/report.md` o `.json`

---

## 11. Ejemplos de uso Mavis

### Ejemplo 1: ¿AAPL está cara o barata?
```python
df = pd.read_csv(".../data/snapshots/historical/post_cierre_2026-08-20.csv")
aapl = df[df["Ticker"] == "AAPL"].iloc[0]
print(f"P/E actual: {aapl['Current_PE']}")
print(f"P/E 5y mean: {aapl['PE_5y_mean']}")
print(f"P/E 5y max: {aapl['PE_5y_max']}")
print(f"P/E 5y min: {aapl['PE_5y_min']}")
print(f"Posición %: {aapl['PE_5y_pct']}")
```

### Ejemplo 2: Setup multi-timeframe en BSX
```python
d = pd.read_csv(".../data/daily/stocks/BSX.csv")
w = pd.read_csv(".../data/weekly/stocks/BSX.csv")
if d.iloc[-1]['REB'] and w.iloc[-1]['ACC'] and w.iloc[-1]['BUY_ZONE']:
    print("STRONG BUY (daily REB + weekly ACC + weekly BUY_ZONE)")
```

### Ejemplo 3: Top movers del día
```python
df = pd.read_csv(".../data/snapshots/historical/post_cierre_2026-08-20.csv")
oversold = df[df['Oversold'] == True]
print(f"Oversold: {oversold['Ticker'].tolist()}")
```

---

## 12. Limitaciones Conocidas

- **Gmail SMTP bloqueado** en VPS Hetzner → solo Telegram
- **Twelve Data Free**: 8 credits/min, 800/día
- **P/E proxy**: solo refleja precio, no EPS (el P/E 5y sí refleja ambos)
- **Daily ETF/Crypto desde Binance/TD**, no ROIC

---

**Generado:** 20-ago-2026 | **Versión:** 3.0
