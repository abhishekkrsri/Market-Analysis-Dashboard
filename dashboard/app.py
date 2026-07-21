import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import MetaTrader5 as mt5
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.fetch_data import fetch_data
from src.analysis import (
    calculate_returns,
    candle_statistics,
    return_statistics,
    excursion_statistics,
    breakout_statistics,
    false_breakout_statistics,
    time_window_analysis,
    best_time_windows,
)

def format_statistics_table(stats):
    df = pd.DataFrame(
        stats.items(),
        columns=["Metric", "Value"],
    )

    def format_value(value):
        if isinstance(value, float):
            if abs(value) < 1:
                return f"{value:.4f}"
            return f"{value:,.2f}"
        return value

    df["Value"] = df["Value"].apply(format_value)

    return df

st.set_page_config(
    page_title="Market Analysis Dashboard",
    page_icon="📈",
    layout="wide",
)



st.divider()

# ==========================
# Sidebar
# ==========================

st.sidebar.title("⚙️ Dashboard Controls")

st.sidebar.markdown(
    "Configure the market data and analysis parameters."
)

st.sidebar.divider()

st.sidebar.subheader("📈 Market Selection")
symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
)

timeframe_name = st.sidebar.selectbox(
    "Select Timeframe",
    ["M1", "M5", "M15", "H1", "H4", "D1"],
)

st.sidebar.subheader("📅 Analysis Period")
analysis_range = st.sidebar.selectbox(
    "📅 Analysis Time Range",
    [
        "Last Day",
        "Last Week",
        "Last Month",
        "Last 3 Months",
        "Last 6 Months",
        "Last Year",
        "All Available",
    ],
    index=2,    # Default: Last Month
)
# Convert analysis range to approximate candle count 
range_to_days = {
    "Last Day": 1,
    "Last Week": 7,
    "Last Month": 30,
    "Last 3 Months": 90,
    "Last 6 Months": 180,
    "Last Year": 365,
    "All Available": 1000,  # We'll improve this later
}

days = range_to_days[analysis_range]
st.sidebar.divider()

st.sidebar.success(
    f"""
**Current Selection**

• Symbol: **{symbol}**

• Timeframe: **{timeframe_name}**

• Period: **{analysis_range}**
"""
)


st.sidebar.divider()

st.sidebar.info(
    """
### 📌 Dashboard Information

**Developer**

Abhishek Kumar Srivastava

**Technologies**

- Python
- Streamlit
- Plotly
- Pandas
- MetaTrader 5  
- NumPy

**Assignment**

Market Analysis Dashboard
"""
)
with st.sidebar.expander("ℹ️ About This Dashboard"):
    st.write(
        """
This dashboard analyzes historical market data from MetaTrader 5.

It includes:
- Candlestick Analysis
- Return Statistics
- Breakout Analysis
- False Breakout Detection
- Time Window Analysis
- Interactive Visualizations
"""
    )

timeframes = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}
# Candles per day for each timeframe
candles_per_day = {
    "M1": 1440,
    "M5": 288,
    "M15": 96,
    "H1": 24,
    "H4": 6,
    "D1": 1,
}

if analysis_range == "All Available":
    candles = 50000
else:
    candles = (
        range_to_days[analysis_range]
        * candles_per_day[timeframe_name]
    )
    st.markdown(
    f"""
# 📈 Market Analysis Dashboard

### Interactive Financial Analytics using MetaTrader 5

**Current Analysis**

- **Symbol:** {symbol}
- **Timeframe:** {timeframe_name}
- **Analysis Period:** {analysis_range}
"""
)

st.divider()

# ==========================
# Fetch Data
# ==========================

try:
    df = fetch_data(
        symbol=symbol,
        timeframe=timeframes[timeframe_name],
        candles=candles,
    )

    if df.empty:
        st.error("No market data available.")
        st.stop()

    df = calculate_returns(df)
    df = excursion_statistics(df)

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.info(
        "Please ensure MetaTrader 5 is running and you are logged into your trading account."
    )
    st.stop()
 

    if df.empty:
        st.error("No market data available.")
        st.stop()

    df = calculate_returns(df)
    df = excursion_statistics(df)

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.info(
        "Please ensure MetaTrader 5 is running and you are logged into your trading account."
    )
    st.stop()

# ==========================
# Statistics
# ==========================

candle_stats = candle_statistics(df)
return_stats = return_statistics(df)
breakout_stats = breakout_statistics(df)
false_breakout_stats = false_breakout_statistics(df)
time_window_stats = time_window_analysis(df)
best_windows = best_time_windows(time_window_stats)
# ==========================
# Market Insights
# ==========================

# Market Bias
if candle_stats["Bullish Probability (%)"] > candle_stats["Bearish Probability (%)"]:
    market_bias = "📈 Bullish"
elif candle_stats["Bullish Probability (%)"] < candle_stats["Bearish Probability (%)"]:
    market_bias = "📉 Bearish"
else:
    market_bias = "⚖️ Neutral"

# Best Trading Time
best_trading_time = (
    best_windows["Highest Average Return"]
    .iloc[0]["Time Window"]
)

# Most Volatile Time
most_volatile_time = (
    best_windows["Highest Volatility"]
    .iloc[0]["Time Window"]
)

# False Breakout Risk
false_breakout_rate = max(
    false_breakout_stats["False High Breakout (%)"],
    false_breakout_stats["False Low Breakout (%)"],
)

if false_breakout_rate >= 60:
    breakout_risk = "🔴 High"
elif false_breakout_rate >= 40:
    breakout_risk = "🟡 Moderate"
else:
    breakout_risk = "🟢 Low"

# ==========================
# KPI Cards
# ==========================

# ==========================
# Key Performance Indicators
# ==========================

st.markdown("## 📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric(
            label="📈 Bullish Probability",
            value=f"{candle_stats['Bullish Probability (%)']:.2f}%"
        )
        st.caption("Probability of bullish candles")

with col2:
    with st.container(border=True):
        st.metric(
            label="📉 Bearish Probability",
            value=f"{candle_stats['Bearish Probability (%)']:.2f}%"
        )
        st.caption("Probability of bearish candles")

with col3:
    with st.container(border=True):
        st.metric(
            label="📊 Market Volatility",
            value=f"{return_stats['Volatility (Std Dev)']:.6f}"
        )
        st.caption("Standard deviation of returns")

with col4:
    with st.container(border=True):
        st.metric(
            label="🚀 High Breakout Rate",
            value=f"{breakout_stats['High Breakout Probability (%)']:.2f}%"
        )
        st.caption("Historical breakout probability")
        

st.subheader("📊 Market Insights")

col1, col2 = st.columns(2)

with col1:
    st.info(
        f"""
**Market Bias:** {market_bias}

**Best Trading Time:** {best_trading_time}
"""
    )

with col2:
    st.info(
        f"""
**Highest Volatility:** {most_volatile_time}

**False Breakout Risk:** {breakout_risk}
"""
    )

# ==========================
# Statistics Display
# ==========================

st.divider()
st.subheader("📊 Candle Statistics")
st.caption("Summary of bullish, bearish and neutral candle behaviour.")

st.dataframe(
    format_statistics_table(candle_stats),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("📈 Return Statistics")
st.caption("Statistical measures of historical price returns.")


st.dataframe(
    format_statistics_table(return_stats),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("🚀 Breakout Statistics")
st.caption("Analysis of previous candle high and low breakouts.")

st.dataframe(
    format_statistics_table(breakout_stats),
    use_container_width=True,
    hide_index=True,
)
# ==========================
# Time Window Analysis
# ==========================

st.divider()
st.subheader("🕒 Time Window Analysis")
st.caption("Recurring market behaviour grouped by time of day.")

st.markdown(
    """
    Analyze recurring market behavior for each time window
    across the entire historical dataset.
    """
)

st.dataframe(
    time_window_stats,
    use_container_width=True,
    hide_index=True,
)
# ==========================
# Best Trading Time Windows
# ==========================

st.divider()
st.subheader("🏆 Best Trading Time Windows")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🟢 Most Bullish",
        "🔴 Most Bearish",
        "📈 Highest Return",
        "⚡ Highest Volatility",
    ]
)

with tab1:
    st.dataframe(
        best_windows["Most Bullish"],
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.dataframe(
        best_windows["Most Bearish"],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.dataframe(
        best_windows["Highest Average Return"],
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    st.dataframe(
        best_windows["Highest Volatility"],
        use_container_width=True,
        hide_index=True,
    )
# ==========================
# False Breakout Statistics
# ==========================

st.divider()
st.subheader("❌ False Breakout Statistics")

st.markdown(
    """
    Analyze how often price breaks the previous candle's
    high or low and then reverses, creating a false breakout.
    """
)

st.dataframe(
    pd.DataFrame(
        false_breakout_stats.items(),
        columns=["Metric", "Value"],
    ),
    use_container_width=True,
    hide_index=True,
)
st.divider()

st.header("📊 Market Visualizations")

st.caption(
    "Interactive visualizations for price action, return distribution, and market excursion analysis."
)
# ==========================
# Candlestick Chart
# ==========================

st.header("📈 Candlestick Chart")

fig = go.Figure(
    data=[
        go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=symbol,
        )
    ]
)

fig.update_layout(
    title=f"{symbol} Candlestick Chart",
    xaxis_title="Time",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    height=600,
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Historical OHLC candlestick chart for the selected symbol and timeframe.")

# ==========================
# Return Distribution
# ==========================

st.header("📊 Return Distribution")

fig_return = px.histogram(
    df,
    x="return",
    nbins=30,
    title="Distribution of Candle Returns",
)

fig_return.update_layout(
    xaxis_title="Return (%)",
    yaxis_title="Frequency",
    height=450,
)

with st.container(border=True):
    st.plotly_chart(fig_return, use_container_width=True)
    st.caption("Histogram showing the distribution of historical candle returns.")

# ==========================
# MFE vs MAE Scatter Plot
# ==========================

st.header("📌 MFE vs MAE")

fig_scatter = px.scatter(
    df,
    x="MAE (%)",
    y="MFE (%)",
    title="Maximum Favorable vs Maximum Adverse Excursion",
    labels={
        "MAE (%)": "MAE (%)",
        "MFE (%)": "MFE (%)",
    },
)

fig_scatter.update_layout(height=500)

with st.container(border=True):
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("Relationship between Maximum Favorable Excursion (MFE) and Maximum Adverse Excursion (MAE).")

# ==========================
# Market Data
# ==========================

st.header("📝 Market Data")

st.dataframe(
    df[
        [
            "time",
            "open",
            "high",
            "low",
            "close",
            "return",
            "MFE (%)",
            "MAE (%)",
        ]
    ],
    use_container_width=True,
)
st.caption("Latest processed historical market data used in the analysis.")

# ==========================
# Download CSV
# ==========================

csv = df.to_csv(index=False).encode("utf-8")

st.divider()

st.subheader("📥 Export Analysis")

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name=f"{symbol}_{timeframe_name}_analysis.csv",
    mime="text/csv",
    use_container_width=True,
)
st.divider()

st.divider()

st.markdown(
    """
<div style="text-align:center; color:gray; font-size:14px;">

**Market Analysis Dashboard**

Developed by **Abhishek Kumar Srivastava**

Software Engineer Internship Assignment

Python • Streamlit • Plotly • Pandas • MetaTrader 5 • NumPy

</div>
""",
    unsafe_allow_html=True,
)