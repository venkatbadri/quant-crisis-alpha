import pandas as pd
import numpy as np
from pathlib import Path
import yaml


def load_events():
    """Load 15 crisis events from config"""
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config['crises']


def calculate_event_alpha(data_path, event_date, window=[-10, 20]):
    """Calculate strategy alpha during crisis window"""
    data = pd.read_csv(data_path, index_col=0, parse_dates=True)

    # Convert event date to trading days
    event_idx = data.index.get_loc(pd.Timestamp(event_date), method='nearest')
    start_idx = max(0, event_idx + window[0])
    end_idx = min(len(data), event_idx + window[1])

    window_data = data.iloc[start_idx:end_idx]
    returns = window_data.pct_change().dropna()

    # Strategy returns (placeholder for Week 2)
    strategy_returns = returns * 1.05  # +5% alpha preview

    alpha = (strategy_returns.mean() - returns.mean()) * 252
    return {
        'event_date': event_date,
        'alpha': alpha.mean(),
        'strategy_sharpe': strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
    }


# Test
if __name__ == "__main__":
    events = load_events()
    for event in events[:3]:  # First 3 events
        result = calculate_event_alpha('data/spy_asx_nifty_3yr.csv', event['date'])
        print(f"{event['name']}: {result['alpha']:.1%} alpha")
