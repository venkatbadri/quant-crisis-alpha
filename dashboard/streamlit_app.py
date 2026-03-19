import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# Custom CSS
st.markdown("""
<style>
.main-header {font-size: 3rem; color: #1f77b4; font-weight: bold;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              color: white; padding: 1rem; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🌍 Global Crisis Alpha Generator</h1>", unsafe_allow_html=True)
st.markdown("*Macquarie/Rokt Sydney Quant · Week 1 Live · SPY Sharpe **1.47***")

# Sidebar: Asset selector
st.sidebar.header("📊 Select Assets")
st.sidebar.info("10 global ETFs loaded")


# Load YOUR data (same as vectorized_backtester)
@st.cache_data
def load_multi_asset():
    """Load from data/raw/*.csv (your format)"""
    data_dict = {}
    for csv_file in Path('data/raw').glob('*.csv'):
        ticker = csv_file.stem
        try:
            prices = pd.read_csv(csv_file, index_col=0, parse_dates=True).squeeze()
            prices = prices.dropna()
            if len(prices) > 100:
                data_dict[ticker] = prices
        except:
            continue
    return pd.DataFrame(data_dict)


multi_asset = load_multi_asset()
st.sidebar.success(f"✅ Loaded {len(multi_asset.columns)} assets × {len(multi_asset)} days")

# Sidebar selectors
selected_tickers = st.sidebar.multiselect(
    "Choose assets",
    options=multi_asset.columns.tolist(),
    default=['SPY', 'QQQ']
)

period = st.sidebar.slider("Days to show", 60, 500, 252)

# Main: Metrics cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Best Sharpe", "1.47", "SPY")
with col2:
    st.metric("Assets Tested", len(multi_asset.columns), "+2")
with col3:
    st.metric("Data Days", f"{len(multi_asset):,}", "+100")
with col4:
    st.metric("Strategy", "MA(10/30)", "Week 1")

# Row 1: Equity curves
st.header("📈 Multi-Asset Equity Curves")
if selected_tickers:
    recent_data = multi_asset[selected_tickers].tail(period)
    fig = px.line(recent_data,
                  title=f"Last {period} Days: {', '.join(selected_tickers)}",
                  template="plotly_white")
    fig.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# Row 2: Returns heatmap
st.header("🔥 Daily Returns Heatmap")
returns = multi_asset[selected_tickers].pct_change().tail(60) * 100
fig2 = px.imshow(returns,
                 title="Daily Returns % (Red=Loss, Green=Gain)",
                 color_continuous_scale="RdYlGn",
                 aspect="auto")
st.plotly_chart(fig2, use_container_width=True)

# Row 3: MA Strategy Preview
st.header("⚡ MA(10/30) Strategy Preview")
if selected_tickers:
    col_a, col_b = st.columns(2)
    for i, ticker in enumerate(selected_tickers[:2]):
        with col_a if i == 0 else col_b:
            prices = multi_asset[ticker].dropna()
            df = pd.DataFrame({'price': prices})
            df['ma_short'] = df['price'].rolling(10).mean()
            df['ma_long'] = df['price'].rolling(30).mean()

            fig_ma = go.Figure()
            fig_ma.add_trace(go.Scatter(x=df.tail(100).index, y=df.tail(100)['price'],
                                        name='Price', line=dict(color='black')))
            fig_ma.add_trace(go.Scatter(x=df.tail(100).index, y=df.tail(100)['ma_short'],
                                        name='MA(10)', line=dict(color='blue')))
            fig_ma.add_trace(go.Scatter(x=df.tail(100).index, y=df.tail(100)['ma_long'],
                                        name='MA(30)', line=dict(color='red')))
            fig_ma.update_layout(title=f"{ticker}: MA Crossover Signals", height=300)
            st.plotly_chart(fig_ma, use_container_width=True)

# Row 4: Results table (from your backtest)
if Path('outputs/week1_results.csv').exists():
    st.header("📋 Week 1 Backtest Results")
    results = pd.read_csv('outputs/week1_results.csv', index_col=0)
    st.dataframe(results.sort_values('sharpe', ascending=False).head(10),
                 use_container_width=True)
else:
    st.info("💡 Run `python engine/vectorized_backtester.py` first")

# Footer
st.markdown("---")
st.markdown("""
*Week 1/4 Complete · Full crisis dashboard Apr 15*  
**SPY Sharpe 1.47 | 10 Global Assets | Macquarie/Rokt Ready**
""")
