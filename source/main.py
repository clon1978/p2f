from dateutil.relativedelta import relativedelta
from datetime import datetime

from lumibot.backtesting import BacktestingBroker, PandasDataBacktesting
from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting

from hit_and_run import HitAndRun
    
# Choose your budget and log file locations
budget = 40000

logfile = "logs/test.log"
strategy_name = "HitAndRun"

# Initialize all our classes
trader = Trader(logfile=logfile)

# Development: Minute Data
Tickers = ["SPY", "GLD", "TLT", "MSFT", "TSLA", "AAPL", "INTC"]

# Choose the time from and to which you want to backtest
backtesting_start = datetime(2020, 11, 1)
backtesting_end = datetime(2021, 12, 1)

# Run the  backtest
stats = HitAndRun.backtest(
    strategy_name,
    budget,
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
    show_plot=True,
)
