# from pandas.core.frame import DataFrame
# from lumibot.strategies.strategy import Strategy
from lumibot.entities.bars import Bars

def expansion_breakout(bars, tickers):
    """[summary]

    Args:
        bars (lumibot.Bars): contains the last 60 days of ticker data
        symbol (str): Name of the symbol to trade

    Returns:
        Dictionary: A dictionary with the trigger information of expansion breakout/down
    """
    
    expansion = []
    
    for ticker in tickers:        
        high = bars[ticker].df["high"].iloc[-1]
        low = bars[ticker].df["low"].iloc[-1]
        range = bars[ticker].df["high"].iloc[-1] - bars[ticker].df["low"].iloc[-1]
        two_month_new_high = max(bars[ticker].df["high"].to_list())
        two_month_new_low = min(bars[ticker].df["low"].to_list())
        nine_day_range = bars[ticker].df["high"].iloc[-9:] - bars[ticker].df["low"].iloc[-9:]
        nine_day_range_max = max(nine_day_range.to_list())
        
        
        expansion.append(
            {
                "symbol": ticker,
                "breakout": False,
                "breakdown": False,
                "price": bars[ticker].get_last_price()
            }
        )

        # Expansion breakout trigger
        if high > two_month_new_high and range >= nine_day_range_max:
            expansion[tickers.index(ticker)]["breakout"] = True
            
        # Expansion breakdown trigger
        elif low < two_month_new_low and range >= nine_day_range_max:
            expansion[tickers.index(ticker)]["breakdown"] = True
            
    return expansion

    