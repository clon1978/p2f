import datetime
import time

import alpaca_trade_api as tradeapi
import pandas as pd
from credentials import AlpacaConfig

"""
    This function will download the historical data for the given stock symbol 
    and write it to a csv file in the data folder.
"""

# Initialize API
alpaca_api = tradeapi.REST(AlpacaConfig.API_KEY, AlpacaConfig.API_SECRET, AlpacaConfig.ENDPOINT)


def get_barset(api, symbol, timeframe, start, end, limit=None):
    """
    gets historical bar data for the given stock symbol
    and time params.
    outputs a dataframe open, high, low, close columns and
    a UTC timezone aware index.
    """

    conversion = {"day": "D", "minute": "Min"}
    mult, freq = timeframe.split("_")
    limit = 1000 if limit is None else mult * limit
    alpaca_format_str = mult + conversion[freq]
    df_ret = None
    curr_end = end
    cnt = 0
    last_curr_end = None
    while True:
        cnt += 1
        barset = api.get_barset(
            symbol, alpaca_format_str, limit=limit, start=start, end=curr_end
        )
        df = barset[symbol].df.tz_convert("utc")

        if df_ret is None:
            df_ret = df
        elif str(df.index[0]) < str(df_ret.index[0]):
            df_ret = df.append(df_ret)

        if start is None or (str(df_ret.index[0]) <= start):
            break
        else:
            curr_end = (
                datetime.datetime.fromisoformat(str(df_ret.index[0])).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                + "-04:00"
            )

        # Sometimes the beginning date we put in is not a trading date,
        # this makes sure that we end when we're close enough
        # (it's just returning the same thing over and over)
        if curr_end == last_curr_end:
            break
        else:
            last_curr_end = curr_end

        # Sleep so that we don't trigger rate limiting
        if cnt >= 50:
            time.sleep(10)
            cnt = 0

    df_ret = df_ret[~df_ret.index.duplicated(keep="first")]
    if start is not None:
        df_ret = df_ret.loc[df_ret.index >= start]

    return df_ret[df_ret.close > 0]
