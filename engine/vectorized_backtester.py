# engine/vectorized_backtester.py - WORKS WITH YOUR CSV FORMAT
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def ma_crossover(prices, short=10, long=30, cost=0.001):
    """MA(10/30) strategy - VECTORIZED"""
    df = pd.DataFrame(index=prices.index)
    df['price'] = prices

    df['ma_short'] = df['price'].rolling(short).mean()
    df['ma_long'] = df['price'].rolling(long).mean()
    df['position'] = (df['ma_short'] > df['ma_long']).astype(int)

    df['returns'] = df['price'].pct_change()
    df['trades'] = df['position'].diff().abs()
    df['tc_cost'] = df['trades'] * cost / 2
    df['strategy_returns'] = df['position'].shift(1) * df['returns'] - df['tc_cost']

    return df.dropna()


def calculate_metrics(signals):
    """Full quant metrics"""
    strat = signals['strategy_returns'].dropna()
    bench = signals['returns'].dropna()

    return {
        'sharpe': (strat.mean() / strat.std() * np.sqrt(252)) if strat.std() > 0 else 0,
        'strategy_return': (1 + strat).prod() - 1,
        'benchmark_return': (1 + bench).prod() - 1,
        'alpha': strat.mean() - bench.mean(),
        'max_drawdown': ((1 + strat).cumprod().cummax() - (1 + strat).cumprod()).max(),
        'win_rate': (strat > 0).sum() / len(strat)
    }


def load_raw_data(raw_dir='data/raw'):
    """Load ALL your CSV files (Date,Price format)"""
    print("📂 Loading YOUR CSV files from data/raw/...")

    data_dict = {}
    raw_path = Path(raw_dir)

    for csv_file in sorted(raw_path.glob('*.csv')):
        ticker = csv_file.stem
        try:
            # YOUR FORMAT: Date,Price (index_col=0, squeeze=True)
            prices = pd.read_csv(csv_file, index_col=0, parse_dates=True).squeeze('columns')
            prices = prices.dropna()

            if len(prices) > 100:
                data_dict[ticker] = prices
                print(f"  ✅ {ticker:8s} {len(prices):4,} days")
            else:
                print(f"  ❌ {ticker:8s} too short")
        except Exception as e:
            print(f"  ❌ {ticker:8s} error: {str(e)[:40]}")

    # Multi-asset DataFrame
    multi_asset = pd.DataFrame(data_dict)
    print(f"\n✅ Multi-asset ready: {len(multi_asset)} days × {len(data_dict)} tickers")

    return multi_asset


def run_backtest(multi_asset):
    """Week 1: MA strategy on all assets"""
    print("\n🔥 VECTORIZED MA(10/30) BACKTEST...")

    results = {}
    Path('data/processed').mkdir(exist_ok=True)

    for ticker in multi_asset.columns:
        print(f"  {ticker}... ", end='')
        try:
            signals = ma_crossover(multi_asset[ticker])
            if len(signals) > 50:
                metrics = calculate_metrics(signals)
                results[ticker] = metrics

                # Equity curve
                equity = (1 + signals['strategy_returns']).cumprod()
                equity.to_csv(f'data/processed/{ticker}_equity.csv')
                print(f"Sharpe {metrics['sharpe']:.2f}")
            else:
                print("❌ short")
        except Exception as e:
            print(f"❌ {str(e)[:15]}")

    results_df = pd.DataFrame(results).T
    return results_df


def plot_results(results_df):
    """Week 1 charts - FIXED matplotlib table"""
    Path('outputs').mkdir(exist_ok=True)

    # 1. PRINT RESULTS (ALWAYS WORKS)
    display_cols = ['sharpe', 'strategy_return', 'benchmark_return', 'alpha']
    table = results_df[display_cols].round(3).sort_values('sharpe', ascending=False)

    print("\n📊 WEEK 1 RESULTS (Top 5 Sharpe):")
    print(table.head())

    # 2. BAR CHART (RELIABLE)
    plt.style.use('default')
    plt.figure(figsize=(12, 6))

    top5 = table.head(5)
    colors = plt.cm.viridis(np.linspace(0, 1, 5))

    bars = plt.bar(range(len(top5)), top5['sharpe'],
                   color=colors, alpha=0.8, edgecolor='black')
    plt.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Target Sharpe 1.0')

    plt.title('Week 1: MA(10/30) Sharpe Ratios (Multi-Region)', fontsize=16, pad=20)
    plt.xlabel('Assets')
    plt.ylabel('Sharpe Ratio')
    plt.xticks(range(len(top5)), top5.index, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/week1_sharpe_bar.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 3. CSV EXPORT (Portfolio ready)
    table.to_csv('outputs/week1_results.csv')

    print("✅ BAR CHART: outputs/week1_sharpe_bar.png")
    print("✅ CSV: outputs/week1_results.csv")
    print(f"✅ BEST: {table.index[0]} Sharpe {table['sharpe'].max():.2f}")


def main():
    print("🚀 QUANT-CRISIS-ALPHA WEEK 1 BACKTEST")

    # Load YOUR data
    multi_asset = load_raw_data()
    if multi_asset.empty:
        print("❌ No data in data/raw/*.csv")
        return

    # Run strategy
    results = run_backtest(multi_asset)

    # Charts
    plot_results(results)

    print("\n🎉 WEEK 1 COMPLETE!")
    print("📁 Check: data/processed/*.csv (equity curves)")
    print("📁 Check: outputs/week1_table.png")


if __name__ == "__main__":
    main()
