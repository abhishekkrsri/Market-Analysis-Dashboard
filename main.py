from src.fetch_data import fetch_data
from src.analysis import (
    calculate_returns,
    candle_statistics,
    return_statistics,
    excursion_statistics,
    breakout_statistics,
)
import MetaTrader5 as mt5


def main():
    # Fetch historical market data
    df = fetch_data(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_H1,
        candles=100
    )

    # Calculate returns and excursions
    df = calculate_returns(df)
    df = excursion_statistics(df)

    # Candle Statistics
    stats = candle_statistics(df)

    print("\n=== Candle Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Return Statistics
    return_stats = return_statistics(df)

    print("\n=== Return Statistics ===")
    for key, value in return_stats.items():
        print(f"{key}: {value}")

    # Breakout Statistics
    breakout_stats = breakout_statistics(df)

    print("\n=== Breakout Statistics ===")
    for key, value in breakout_stats.items():
        print(f"{key}: {value}")

    # First 5 Rows
    print("\n=== First 5 Rows ===")
    print(
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
        ].head()
    )


if __name__ == "__main__":
    main()