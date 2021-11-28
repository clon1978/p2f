from pandas.core.frame import DataFrame
from lumibot.strategies.strategy import Strategy


class ExpansionBreakout(Strategy):
    # =====Overloading lifecycle methods=============
    def initialize(self, buy_after_days=60, change_threshold=-0.01, buy_symbol="INTC", df={}, breakout=False, breakdown=False):
        # Set the initial variables or constants

        # Built in Variables
        self.sleeptime = 1

        # Our custom parameters
        self.buy_symbol = buy_symbol
        self.change_threshold = change_threshold
        self.buy_after_days = buy_after_days
        self.df = df
        self.breakout = breakout
        self.breakdown = breakdown

        # Variables for making the strategy work
        self.counter = self.buy_after_days
        self.previous_price = None

    def on_trading_iteration(self):
        # What to do each iteration (every self.sleeptime minutes)

        current_price = self.get_last_price(self.buy_symbol)
        previous_price = self.previous_price
        current_high = self.df["high"].iloc[self.buy_after_days]
        two_month_new_high = self.df["high"].iloc[self.buy_after_days-60:self.buy_after_days]
        current_low = self.df["low"].iloc[self.buy_after_days]
        two_month_new_low = self.df["low"].iloc[self.buy_after_days-60:self.buy_after_days]
        current_range = self.df["high"].iloc[self.buy_after_days] - self.df["low"].iloc[self.buy_after_days]
        nine_day_range = self.df["high"].iloc[self.buy_after_days-9:self.buy_after_days] - self.df["low"].iloc[self.buy_after_days-9:self.buy_after_days]

        price_change = 0
        if previous_price is not None:
            price_change = (current_price / previous_price) - 1

        # Expansion breakout stop
        if price_change < self.change_threshold and self.breakout == True:
            self.breakout = False
            self.sell_all()
            self.counter = 0
        
        # Expansion breakdown stop
        elif price_change > self.change_threshold and self.breakdown == True:
            self.breakdown = False
            self.sell_all()
            self.counter = 0

        # Expansion breakout trigger
        elif self.counter == self.buy_after_days and \
        current_high >= two_month_new_high.max() and \
        current_range >= nine_day_range.max() and \
        current_price >= previous_price + current_high * 1/8:
            self.breakout = True
            quantity = self.portfolio_value // current_price
            buy_order = self.create_order(self.buy_symbol, quantity, "buy")
            self.submit_order(buy_order)
        
        # Expansion breakdown trigger
        elif self.counter == self.buy_after_days and \
        current_low <= two_month_new_low.max() and \
        current_range >= nine_day_range.max() and \
        current_price <= previous_price - current_low * 1/8:
            self.breakdown = True
            quantity = self.portfolio_value // current_price
            sell_order = self.create_order(self.buy_symbol, quantity, "sell")
            self.submit_order(sell_order)
        
        # Get the last price that our symbol traded at and save it
        self.previous_price = current_price

        # Increment our counter
        self.counter = self.counter + 1

        # Wait until the end of the day (so we only trade once per day)
        self.await_market_to_close()

    def trace_stats(self, context, snapshot_before):
        symbol = self.buy_symbol

        my_position = self.get_tracked_position(symbol)
        qty_owned = 0
        if my_position is not None:
            qty_owned = my_position.quantity

        row = {
            f"current_price_{symbol}": context["current_price"],
            f"previous_price_{symbol}": context["previous_price"],
            "counter": self.counter,
            f"{symbol}_owned": qty_owned,
        }

        return row

    def on_abrupt_closing(self):
        # This is what we do when the program crashes
        self.sell_all()
