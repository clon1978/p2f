from lumibot.strategies.strategy import Strategy
from hr_triggers import expansion_breakout


class HitAndRun(Strategy):
    # =====Overloading lifecycle methods=============
    def initialize(self, change_threshold=-0.01):
        # Set the initial variables or constants

        # Built in Variables
        self.sleeptime = 1

        # Our custom parameters
        self.tickers = ["SPY", "GLD", "TLT", "MSFT", "TSLA", "AAPL", "INTC"]

        self.change_threshold = change_threshold
                
        self.triggers = []
        
        self.directions = []
        
        self.orders = []
        
        self.bars = {}
        
    def on_trading_iteration(self):
        # What to do each iteration (every self.sleeptime minutes)
        for ticker in self.tickers:
            
            self.directions.append (
                {
                    "symbol": ticker,
                    "up": 0,
                    "down": 0
                }
            )

            #################################################################################################
            # Evaluate the trigger indicators and trading formulas    
            #################################################################################################
            # breakout indicator
            if self.triggers[0][self.tickers.index(ticker)]["breakout"] == True:
                if self.get_last_price(ticker) > self.bars[ticker].df["high"].iloc[-1] * 9/8:
                        self.directions[self.tickers.index(ticker)]["up"] += 1
            elif self.triggers[0][self.tickers.index(ticker)]["breakdown"] == True:
                if self.get_last_price(ticker) < self.bars[ticker].df["low"].iloc[-1] * 7/8:
                        self.directions[self.tickers.index(ticker)]["down"] += 1
            
            # Calculate the quantity to trade where each asset has a 14% weight
            quantity = self.portfolio_value * 0.14 // self.triggers[0][self.tickers.index(ticker)]["price"]
            
            #################################################################################################
            # Verify if ticker has not opposite directions to create an order
            #################################################################################################
            if self.directions[self.tickers.index(ticker)]["up"] > 0 and \
                self.directions[self.tickers.index(ticker)]["down"] == 0:
                    self.orders.append (
                        self.create_order(ticker, quantity, "buy")
                    )
            elif self.directions[self.tickers.index(ticker)]["down"] > 0 and \
                self.directions[self.tickers.index(ticker)]["up"] == 0:
                    self.orders.append (
                        self.create_order(ticker, quantity, "sell")
                    )

            # Submit the orders of the day
            self.submit_orders(self.orders)
        
        # Wait until the end of the day (so we only trade once per day)
        self.await_market_to_close()

    def before_market_opens(self):
        # Cancel all orders and get the new triggers for the day
        self.cancel_orders(self.orders)
        # Get the ticker two month data
        self.bars = self.get_bars(self.tickers, 60, "day")        
        # Create the hit amd run direction table
        self.triggers.append(
            expansion_breakout(self.bars, self.tickers)
        )
            
    def on_bot_crash(self, error):
        self.log_message(error)
        self.sell_all()
        
    def on_abrupt_closing(self):
        # This is what we do when the program crashes
        self.sell_all()
