import pandas as pd


def calculate_returns(df):
    """
    Calculate the percentage return for each candle.
    Formula:
        Return (%) = ((Close - Open) / Open) * 100
    """
    result = df.copy()

    result["return"] = (
        (result["close"] - result["open"])
        / result["open"]
    ) * 100

    return result


def candle_statistics(df):
    """
    Calculate basic candle statistics.
    """
    total = len(df)

    bullish = (df["close"] > df["open"]).sum()
    bearish = (df["close"] < df["open"]).sum()
    neutral = (df["close"] == df["open"]).sum()

    return {
        "Total Candles": int(total),
        "Bullish Candles": int(bullish),
        "Bearish Candles": int(bearish),
        "Neutral Candles": int(neutral),

        "Bullish Probability (%)": round((bullish / total) * 100, 2) if total else 0,
"Bearish Probability (%)": round((bearish / total) * 100, 2) if total else 0,
"Neutral Probability (%)": round((neutral / total) * 100, 2) if total else 0,
    }


def return_statistics(df):
    """
    Calculate return-based statistics.
    """
    return {
        "Average Return (%)": round(df["return"].mean(), 6),
        "Median Return (%)": round(df["return"].median(), 6),
        "Maximum Return (%)": round(df["return"].max(), 6),
        "Minimum Return (%)": round(df["return"].min(), 6),
        "Volatility (Std Dev)": round(df["return"].std(), 6),
    }


def excursion_statistics(df):
    """
    Add Maximum Favorable Excursion (MFE)
    and Maximum Adverse Excursion (MAE)
    columns to the DataFrame.
    """
    result = df.copy()

    result["MFE (%)"] = (
        (result["high"] - result["open"])
        / result["open"]
    ) * 100

    result["MAE (%)"] = (
        (result["low"] - result["open"])
        / result["open"]
    ) * 100

    return result


def breakout_statistics(df):
    """
    Calculate previous candle breakout statistics.
    """
    result = df.copy()

    previous_high = result["high"].shift(1)
    previous_low = result["low"].shift(1)

    high_breakout = (result["high"] > previous_high).sum()
    low_breakout = (result["low"] < previous_low).sum()

    total = max(len(result) - 1, 1)

    return {
        "High Breakouts": int(high_breakout),
        "Low Breakouts": int(low_breakout),
        "High Breakout Probability (%)": round((high_breakout / total) * 100, 2),
        "Low Breakout Probability (%)": round((low_breakout / total) * 100, 2),
    }
    
def false_breakout_statistics(df):
    """
    Calculate false breakout statistics.

    A false high breakout occurs when:
    - Current high breaks the previous high
    - Current candle closes below the previous high

    A false low breakout occurs when:
    - Current low breaks the previous low
    - Current candle closes above the previous low
    """

    result = df.copy()

    previous_high = result["high"].shift(1)
    previous_low = result["low"].shift(1)

    # High breakout
    high_breakout = result["high"] > previous_high

    false_high_breakout = (
        (result["high"] > previous_high)
        & (result["close"] < previous_high)
    )

    # Low breakout
    low_breakout = result["low"] < previous_low

    false_low_breakout = (
        (result["low"] < previous_low)
        & (result["close"] > previous_low)
    )

    total_high = high_breakout.sum()
    total_low = low_breakout.sum()

    false_high = false_high_breakout.sum()
    false_low = false_low_breakout.sum()

    return {
        "High Breakouts": int(total_high),
        "False High Breakouts": int(false_high),
        "False High Breakout (%)":
            round((false_high / total_high) * 100, 2)
            if total_high > 0 else 0,

        "Low Breakouts": int(total_low),
        "False Low Breakouts": int(false_low),
        "False Low Breakout (%)":
            round((false_low / total_low) * 100, 2)
            if total_low > 0 else 0,
    }
    
    
def time_window_analysis(df):
    """
    Analyze recurring time windows across the historical dataset.

    Groups candles by their time of day and computes
    statistical measures for each recurring window.
    """

    result = df.copy()

    # Extract recurring time window (HH:MM)
    result["Time Window"] = result["time"].dt.strftime("%H:%M")

    analysis = (
        result.groupby("Time Window")
        .agg(
            Occurrences=("return", "count"),
            Bullish_Candles=("return", lambda x: (x > 0).sum()),
            Bearish_Candles=("return", lambda x: (x < 0).sum()),
            Average_Return=("return", "mean"),
            Median_Return=("return", "median"),
            Volatility=("return", "std"),
            Average_MFE=("MFE (%)", "mean"),
            Average_MAE=("MAE (%)", "mean"),
        )
        .reset_index()
    )

    analysis["Bullish Probability (%)"] = (
        analysis["Bullish_Candles"]
        / analysis["Occurrences"]
        * 100
    ).round(2)

    analysis["Bearish Probability (%)"] = (
        analysis["Bearish_Candles"]
        / analysis["Occurrences"]
        * 100
    ).round(2)

    analysis = analysis.round(
        {
            "Average_Return": 6,
            "Median_Return": 6,
            "Volatility": 6,
            "Average_MFE": 6,
            "Average_MAE": 6,
        }
    )

    return analysis
def best_time_windows(time_window_df):
    """
    Find the best-performing recurring time windows.
    """

    return {
        "Most Bullish": (
            time_window_df.sort_values(
                "Bullish Probability (%)",
                ascending=False,
            ).head(10)
        ),

        "Most Bearish": (
            time_window_df.sort_values(
                "Bearish Probability (%)",
                ascending=False,
            ).head(10)
        ),

        "Highest Average Return": (
            time_window_df.sort_values(
                "Average_Return",
                ascending=False,
            ).head(10)
        ),

        "Highest Volatility": (
            time_window_df.sort_values(
                "Volatility",
                ascending=False,
            ).head(10)
        ),
    }