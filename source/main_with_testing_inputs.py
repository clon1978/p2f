import logging
from datetime import datetime
from time import time

from lumibot.backtesting import YahooDataBacktesting
from lumibot.tools import indicators

from expansion_breakout import ExpansionBreakout

# Choose your budget and log file locations
budget = 40000

####
# 1. Backtest the strategy using different inputs
####

# Choose the time from and to which you want to backtest
backtesting_start = datetime(2018, 1, 1)
backtesting_end = datetime(2019, 1, 1)

# Keep track of the best outcomes
best_cagr = None
best_cagr_buy_after_days = None

for x in range(10):
    buy_after_days = (x * 5) + 1

    print(f"Backtesting with buy_after_days = {buy_after_days}")

    # Select our strategy
    strategy_name = "expansion_breakout"

    # Run the actual backtest
    stats = ExpansionBreakout.backtest(
        strategy_name,
        budget,
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
        buy_after_days=buy_after_days,
        buy_symbol="INTC",
        change_threshold=-0.01,
    )
    result = stats.get(strategy_name)

    if best_cagr is None or result["cagr"] > best_cagr:
        best_cagr = result["cagr"]
        best_cagr_buy_after_days = buy_after_days

print(
    f"The best CAGR is {(best_cagr * 100):.02f}%, when using buy_after_days of {best_cagr_buy_after_days}"
)

####
# 2. Trade Live
####

from lumibot.brokers import Alpaca
from lumibot.traders import Trader

# Import what you need for trading
from credentials import AlpacaConfig

# Initialize all our classes
logfile = "logs/test.log"
trader = Trader(logfile=logfile)
broker = Alpaca(AlpacaConfig)

strategy = ExpansionBreakout(
    name=strategy_name,
    budget=budget,
    broker=broker,
    buy_after_days=best_cagr_buy_after_days,
)

trader.add_strategy(strategy)
trader.run_all()
