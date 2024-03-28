import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

class PercentageBasedSLStrategy(Strategy):
    def __init__(self, broker, data, n1, n2, sl_percentage):
        self.n1 = n1
        self.n2 = n2
        self.sl_percentage = sl_percentage
        super().__init__(broker, data)

    def init(self):
        self.sma1 = self.I(lambda close: pd.Series(close).rolling(self.n1, min_periods=1).mean(), self.data.Close)
        self.sma2 = self.I(lambda close: pd.Series(close).rolling(self.n2, min_periods=1).mean(), self.data.Close)

    def next(self):
        if crossover(self.sma1, self.sma2):
            if not self.position:
                self.buy()  # Long position
        elif crossover(self.sma2, self.sma1):
            if self.position:
                self.position.close()  # Close long position
        else:
            # No crossover, check for short opportunity
            if not self.position:
                self.sell()  # Short position
            elif self.position.size < 0:
                self.position.close()  # Close short position

        for trade in self.trades:
            if trade.is_long:
                sl_price = trade.entry_price * (1 - self.sl_percentage)
            else:
                sl_price = trade.entry_price * (1 + self.sl_percentage)
            trade.sl = sl_price

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    end_date = end_date.replace("=", "-")  # Correcting the end date input

    data = yf.download(ticker, start=start_date, end=end_date)

    param_grid = {
        'n1': range(10, 51, 10),
        'n2': range(50, 201, 50),
        'sl_percentage': [0.01, 0.02, 0.03, 0.05]
    }

    # Initialize the Backtest object with the strategy and other parameters
    bt = Backtest(data, PercentageBasedSLStrategy, cash=10_000, commission=.002, exclusive_orders=True)

    # Perform optimization on the strategy parameters
    optimization_results = bt.optimize(maximize='Sharpe Ratio', return_heatmap=False, **param_grid)

    print("Optimized Parameters:", optimization_results._strategy)
    print("Optimized Sharpe Ratio:", optimization_results['Sharpe Ratio'])

    bt.plot(title=f"{ticker} Backtest Results")
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
