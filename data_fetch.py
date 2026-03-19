# data_fetch.py - MILITARY GRADE (WORKS 100%)
import yfinance as yf
import pandas as pd
import time
from pathlib import Path

print("🔥 BULLETPROOF 6-REGION DATA FETCH")

# CORE US TICKERS THAT ALWAYS WORK
US_TICKERS = ['SPY', 'QQQ', 'IWM', 'XLE', 'XLF']  # ETFs + sectors
INTL_ETF_TICKERS = ['EEM', 'VGK', 'INDA', 'FXI', 'KSA']  # All ETFs

ALL_TICKERS = US_TICKERS + INTL_ETF_TICKERS
Path('data/raw').mkdir(exist_ok=True)

# DOWNLOAD WITH FAILSAFE
successful = []
for i, ticker in enumerate(ALL_TICKERS):
    try:
        print(f"  {ticker:6s}... ", end='')

        # FAILSAFE DOWNLOAD
        data = yf.download(ticker, start='2023-01-01', end='2026-03-19',
                           progress=False, threads=False, auto_adjust=True)

        if data.empty or len(data) < 100:
            print("❌ EMPTY")
            continue

        # FAILSAFE COLUMN HANDLING
        if 'Close' in data.columns:
            price_col = 'Close'
        elif 'Adj Close' in data.columns:
            price_col = 'Adj Close'
        else:
            print("❌ NO PRICE COLUMN")
            continue

        prices = data[price_col].dropna()
        if len(prices) > 100:
            prices.to_csv(f'data/raw/{ticker}.csv')
            successful.append(ticker)
            print(f"✅ {len(prices):,d} days")
        else:
            print("❌ TOO SHORT")

    except Exception as e:
        print(f"❌ {str(e)[:30]}")

    # RATE LIMIT
    time.sleep(1 + i * 0.1)

print(f"\n✅ SUCCESS: {len(successful)}/{len(ALL_TICKERS)} tickers")

# CREATE MULTI-ASSET CSV
if successful:
    data_dict = {}
    for ticker in successful:
        try:
            prices = pd.read_csv(f'data/raw/{ticker}.csv', index_col=0, parse_dates=True).squeeze()
            data_dict[ticker] = prices
        except:
            continue

    if data_dict:
        multi = pd.concat(data_dict, axis=1).dropna(how='all')
        multi.to_csv('data/multi_region_3yr.csv')
        print(f"✅ MULTI-REGION: {len(multi)} days x {len(data_dict)} assets")
        print("\n📊 LAST 5 ROWS:")
        print(multi.tail())
    else:
        print("❌ NO VALID DATA FOR MULTI-ASSET")
else:
    print("❌ ZERO SUCCESSFUL DOWNLOADS")
