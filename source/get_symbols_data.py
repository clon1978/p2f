from download_data_alpaca import alpaca_api
from download_data_alpaca import get_barset
from lumibot.entities import Asset, Data
import pandas as pd
import os

def get_symbols_data(Tickers, start_date, end_date):
    """Connects to Alpaca API and download historical data from Tickers

    Args:
        Tickers (string): Symbols name from Tickers
        start_date (datetime): starting date of data to download
        end_date (datetime): end date of data to download
    """
    # Create data directory if it does not exist
    if not os.path.exists("data"):
        os.makedirs("data")

    for ticker in Tickers:
        if not os.path.exists(f"data/{ticker}.csv"):
            # Get minute-level training data
            downloaded_data = get_barset(
                alpaca_api,
                ticker,
                "1_minute",
                pd.Timestamp(start_date, tz="America/New_York").isoformat(),
                pd.Timestamp(end_date, tz="America/New_York").isoformat(),
            )

            downloaded_data_est = downloaded_data.tz_convert("US/Eastern")

            filename = f"data/{ticker}.csv"
            downloaded_data_est.to_csv(filename)

def get_asset_data(Tickers):
    """Create a dictionary of lumibot Assets with symbols historical data from Tickers

    Args:
        Tickers (string): Tickers of symbols

    Returns:
        lumibot Assets: returns a dictionary of lumibot stock assets from Tickers
    """
    my_data = {}
    for ticker in Tickers:
        if os.path.exists(f"data/{ticker}.csv"):
            df = pd.read_csv(f"data/{ticker}.csv")
            df = df.set_index("time")
            df.index = pd.to_datetime(df.index, utc=True)
            asset = Asset(
                symbol=ticker,
                asset_type="stock",
            )
            my_data[asset] = Data(
                asset,
                df,
                timestep="minute",
            )
    
    return my_data
