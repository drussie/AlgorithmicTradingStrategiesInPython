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
    n1 = 40  # Initial value for short moving average window
    n2 = 200  # Initial value for long moving average window
    sl_percentage = 0.01  # Initial value for stop-loss percentage

    def init(self):
        # Calculate moving averages
        self.sma1 = self.I(lambda close: pd.Series(close).rolling(self.n1, min_periods=1).mean(), self.data.Close)
        self.sma2 = self.I(lambda close: pd.Series(close).rolling(self.n2, min_periods=1).mean(), self.data.Close)

    def next(self):
        if crossover(self.sma1, self.sma2):
            if not self.position:
                self.buy()
        elif crossover(self.sma2, self.sma1):
            if self.position:
                self.position.close()

        for trade in self.trades:
            sl_price = trade.entry_price * (1 - self.sl_percentage) if trade.is_long else trade.entry_price * (1 + self.sl_percentage)
            trade.sl = sl_price

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    
    data = yf.download(ticker, start=start_date, end=end_date)

    bt = Backtest(data, PercentageBasedSLStrategy, cash=10_000, commission=.002)

    param_grid = {
        'n1': range(10, 51, 10),  # Range for short moving average window
        'n2': range(50, 201, 50),  # Range for long moving average window
        'sl_percentage': [0.01, 0.02, 0.03, 0.05]  # Range for stop-loss percentage
    }

    optimization_results = bt.optimize(**param_grid, maximize='Sharpe Ratio', return_heatmap=False)

    print("Optimized Parameters:", optimization_results._strategy)
    print("Optimized Sharpe Ratio:", optimization_results['Sharpe Ratio'])

    bt.plot()

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
