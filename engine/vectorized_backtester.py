import pandas as pd
import numpy as np
from strategies.ma_crossover import ma_crossover, calculate_metrics
from pathlib import Path


class VectorizedBacktester:
    def __init__(self, data_path='data/spy_asx_nifty_3yr.csv'):
        self.data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        self.results = {}

    def run_strategy(self, strategy_func, **kwargs):
        """Run strategy across all assets"""
        for col in self.data.columns:
            prices = self.data[col].dropna()
            signals = strategy_func(prices, **kwargs)
            metrics = calculate_metrics(signals)
            self.results[col] = {
                'sharpe': metrics['sharpe'],
                'total_return': metrics['total_return'],
                'max_dd': metrics['max_drawdown']
            }
        return pd.DataFrame(self.results).T

    def benchmark(self):
        """Buy & hold benchmark"""
        returns = self.data.pct_change().dropna()
        bench_metrics = {}
        for col in returns.columns:
            r = returns[col].dropna()
            bench_metrics[col] = {
                'sharpe': r.mean() / r.std() * np.sqrt(252),
                'total_return': (1 + r).prod() - 1
            }
        return pd.DataFrame(bench_metrics).T


# Test
if __name__ == "__main__":
    bt = VectorizedBacktester()
    results = bt.run_strategy(ma_crossover)
    print("MA Strategy Results:")
    print(results[['sharpe', 'total_return']])
    print("\nBenchmark:")
    print(bt.benchmark()[['sharpe', 'total_return']])
