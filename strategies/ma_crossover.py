import pandas as pd
import numpy as np
from pathlib import Path


def ma_crossover(prices: pd.Series, short_window=10, long_window=30):
    """Vectorized MA crossover strategy"""
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices

    signals['ma_short'] = prices.rolling(window=short_window).mean()
    signals['ma_long'] = prices.rolling(window=long_window).mean()

    # 1 = long, 0 = cash
    signals['position'] = (signals['ma_short'] > signals['ma_long']).astype(int)
    signals['returns'] = prices.pct_change()
    signals['strategy_returns'] = signals['position'].shift(1) * signals['returns']

    return signals.dropna()


def calculate_metrics(signals: pd.DataFrame):
    """Industry standard metrics"""
    strat = signals['strategy_returns'].dropna()

    metrics = {
        'sharpe': strat.mean() / strat.std() * np.sqrt(252),
        'total_return': (1 + strat).prod() - 1,
        'max_drawdown': (signals['strategy_returns'].cumsum().cummax() -
                         signals['strategy_returns'].cumsum()).max(),
        'win_rate': (strat > 0).mean()
    }
    return metrics
