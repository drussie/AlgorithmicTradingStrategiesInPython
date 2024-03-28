# Data handling and analysis
import pandas as pd
import numpy as np

# Fetching financial market data
import yfinance as yf

# Backtesting library
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, TrailingStrategy

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings if needed (e.g., deprecation warnings)
import warnings
warnings.filterwarnings("ignore")

class ATRMovingAverageCrossoverStrategy(TrailingStrategy):
    n1 = 20  # Initial/default value for n1, will be optimized
    n2 = 60  # Initial/default value for n2, will be optimized
    atr_period = 10  # Initial/default value for atr_period, will be optimized
    atr_multiplier = 2  # Initial/default value for atr_multiplier, will be optimized

    def init(self):
        super().init()
        # Moving averages
        self.sma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)
        
        # ATR for volatility
        self.atr = self.I(lambda high, low, close: pd.Series(high).rolling(self.atr_period).max()
                          - pd.Series(low).rolling(self.atr_period).min(), 
                          self.data.High, self.data.Low, self.data.Close)

    def next(self):
        if len(self.data.Close) < max(self.n1, self.n2, self.atr_period) + 1:
            # Not enough data yet for indicators to be reliable
            return

        for trade in self.trades:
            atr_value = self.atr[-1]
            if np.isnan(atr_value) or atr_value <= 0:
                continue  # Skip if ATR value is not valid

            if trade.is_long:
                sl_price = trade.entry_price - atr_value * self.atr_multiplier
                if sl_price <= 0:
                    continue  # Ensure SL price is positive
                trade.sl = max(trade.sl or 0, sl_price)

        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")
    data = yf.download(ticker, start, end)

    bt = Backtest(data, ATRMovingAverageCrossoverStrategy, cash=10_000, commission=.002)

    param_grid = {
        'n1': range(20, 61, 10),  # Short moving average window
        'n2': range(60, 201, 20),  # Long moving average window
        'atr_period': range(10, 21, 5),  # ATR calculation window
        'atr_multiplier': [2, 3, 4, 5]  # Multiplier for ATR-based stop-loss
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
