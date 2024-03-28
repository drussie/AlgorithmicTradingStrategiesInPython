import pandas as pd
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings

# Suppress specific BokehDeprecationWarning
warnings.filterwarnings("ignore", category=UserWarning, message=".*BokehDeprecationWarning*")


def SMA(values, n):
    """Return simple moving average of `values`, at each step taking into account `n` previous values."""
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Default moving averages periods if not overridden
    n1 = 60
    n2 = 100

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, buy; else if sma1 crosses below sma2, sell
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

def fetch_data(ticker):
    """Fetch historical data for the given ticker symbol from yfinance."""
    return yf.download(ticker)

def run_backtest(data):
    """Run backtest using the SmaCross strategy with the provided data."""
    bt = Backtest(data, SmaCross, cash=10000, commission=.002, exclusive_orders=True)
    stats = bt.run()
    return bt, stats

# def optimize_strategy(data):
#     """Optimize strategy parameters to maximize the final equity."""
#     bt = Backtest(data, SmaCross, cash=10000, commission=.002, exclusive_orders=True)
#     result = bt.optimize(n1=range(5, 60, 5),
#                          n2=range(10, 90, 5),
#                          maximize='Equity Final [$]')
#     return result

def optimize_strategy(data):
    """Optimize strategy parameters to maximize the final equity."""
    bt = Backtest(data, SmaCross, cash=10000, commission=.002, exclusive_orders=True)
    result = bt.optimize(n1=range(5, 60, 5),
                         n2=range(10, 90, 5),
                         maximize='Equity Final [$]',
                         return_heatmap=False)  # Set to True if heatmap is desired

    # Accessing the best parameters directly from the result
    best_params = result._strategy_params
    return result, best_params


# if __name__ == "__main__":
#     ticker = input("Enter the ticker: ")
#     data = fetch_data(ticker)
#     bt, stats = run_backtest(data)
#     print(stats)
#     bt.plot()

#     # Uncomment the following lines to perform and print optimization results
#     res = optimize_strategy(data)
#     print("Best result: ", res._strategy)
#     print("Parameters for best result: ", res._strategy_params)

# if __name__ == "__main__":
#     ticker = input("Enter the ticker: ")
#     data = fetch_data(ticker)
#     bt, stats = run_backtest(data)
#     print(stats)
#     bt.plot()

#     # Running the optimization and printing the results
#     res, best_params = optimize_strategy(data)
#     print("Best result strategy: ", res._strategy)
#     print(f"Parameters for best result: n1={best_params['n1']}, n2={best_params['n2']}")


if __name__ == "__main__":
    ticker = input("Enter the ticker: ")
    data = fetch_data(ticker)
    bt, stats = run_backtest(data)
    print(stats)
    bt.plot()

    # Running the optimization and printing the results
    res = optimize_strategy(data)
    print("Best result: ", res._strategy)
    # Correctly access and print the parameters for the best result
    print(f"Parameters for best result: n1={res.params['n1']}, n2={res.params['n2']}")

