import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf

# Simple Moving Average function
def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

# SMA Cross Strategy class
class SmaCross(Strategy):
    n1 = 60
    n2 = 90

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


# Get data from yfinance
ticker = input("Enter the ticker: ")
start = input("Enter the start date (YYYY-MM-DD): ")
end = input("Enter the end date (YYYY-MM-DD): ")
data = yf.download(ticker, start=start, end=end)

# Code for running the backtest.
# Assumes the existence of `data` variable containing backtest data.
bt = Backtest(data, SmaCross)
stats = bt.run()
print(stats)


print(stats['_trades'].to_string())

bt.plot()

# Define a range of values to test for each parameter
param_grid = {'n1': range(5, 101, 5), 'n2': range(10, 251, 5)}
# Run the optimization
res = bt.optimize(**param_grid)

# Print the best results and the parameters that lead to these results
print("Best result: ", res['Return [%]'])
print("Parameters for best result: ", res['_strategy'])

res
print('Equity curve:')
print(res['_equity_curve'])

