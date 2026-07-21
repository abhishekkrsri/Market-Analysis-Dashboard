import MetaTrader5 as mt5
import pandas as pd


def fetch_data(symbol, timeframe, candles):
    """
    Fetch historical market data from MetaTrader 5.

    Parameters:
        symbol (str): Trading symbol
        timeframe: MT5 timeframe constant
        candles (int): Number of candles

    Returns:
        pandas.DataFrame
    """

    if not mt5.initialize():
        raise Exception(
            f"MT5 Initialization Failed: {mt5.last_error()}"
        )

    rates = mt5.copy_rates_from_pos(
        symbol,
        timeframe,
        0,
        candles,
    )

    mt5.shutdown()

    if rates is None or len(rates) == 0:
        raise Exception("No data received from MT5.")

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s",
    )

    return df


if __name__ == "__main__":
    df = fetch_data(
        "EURUSD",
        mt5.TIMEFRAME_H1,
        100,
    )

    print(df.head())