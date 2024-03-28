class MovingAverageCrossoverStrategy(Strategy):
    # Hardcoded moving average window parameters
    n1 = 40  
    n2 = 200  

    # Stop-loss percentage parameter
    stop_loss_percentage = 0.02  # 2% stop-loss percentage

    def init(self):
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)

    def next(self):
        if crossover(self.sma1, self.sma2):
            if self.position.is_short:  # Close short position if currently short
                self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            if self.position.is_long:  # Close long position if currently long
                self.position.close()
            self.sell()

        # Set stop-loss based on current price and stop-loss percentage for both long and short positions
        if self.position:
            stop_loss_price_long = self.data.Close[-1] * (1 - self.stop_loss_percentage)
            stop_loss_price_short = self.data.Close[-1] * (1 + self.stop_loss_percentage)
            self.position.stop_loss = stop_loss_price_long if self.position.is_long else stop_loss_price_short
