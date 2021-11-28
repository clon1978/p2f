from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.backtesting import PandasDataBacktesting
from lumibot.entities import Asset, Data
from lumibot.strategies import Strategy
import pandas as pd

from expansion_breakout import ExpansionBreakout
from technical_analysis import TechnicalAnalysis

from dateutil.relativedelta import relativedelta
from datetime import datetime

df = None

today = datetime.now()
end = datetime.now()
start = end - relativedelta(years=15)

ticker = 'INTC'
# Copy this string by right clicking on Yahoo's "Download" link
url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={int(start.timestamp())}&period2={int(end.timestamp())}&interval=1d&events=history"
# Download the csv
    
# Choose your budget and log file locations
budget = 40000

####
# 1. Backtest the strategy using different inputs
####

# Choose the time from and to which you want to backtest
backtesting_start = datetime(2018, 1, 1)
backtesting_end = datetime(2019, 1, 1)
strategy_name = "ExpansionBreakout"

df = pd.read_csv(url)
df = df.set_index("time")
df.index = pd.to_datetime(df.index)

asset = Asset(
    symbol="INTC",
    asset_type="stock",
)

pandas_data = {}
pandas_data[asset] = Data(
    asset,
    df,
    timestep="minute"
)

# Run the  backtest
stats = ExpansionBreakout.backtest(
    strategy_name,
    budget,
    PandasDataBacktesting,
    backtesting_start,
    backtesting_end,
    pandas_data=pandas_data,
)
result = stats.get(strategy_name)

####
# 2. Trade Live
####

from lumibot.brokers import Alpaca
from lumibot.traders import Trader

# Import what you need for trading
from credentials import AlpacaConfig

# Initialize all our classes
logfile = "logs/output.log"
trader = Trader(logfile=logfile)
broker = Alpaca(AlpacaConfig)

strategy = ExpansionBreakout(
    name=strategy_name,
    budget=budget,
    broker=broker,
)

trader.add_strategy(strategy)
trader.run_all()
