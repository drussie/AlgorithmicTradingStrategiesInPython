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
    n1 = 20  # Initial/default value for n1
    n2 = 60  # Initial/default value for n2
    atr_period = 10  # Initial/default value for atr_period
    atr_multiplier = 2  # Initial/default value for atr_multiplier

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
        
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()
        
        for trade in self.trades:
            atr_value = self.atr[-1]
            if not np.isnan(atr_value) and atr_value > 0:
                if trade.is_long:
                    trade.sl = max(trade.sl or 0, trade.entry_price - atr_value * self.atr_multiplier)
                else:
                    trade.sl = min(trade.sl or float('inf'), trade.entry_price + atr_value * self.atr_multiplier)

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")
    data = yf.download(ticker, start, end)

    bt = Backtest(data, ATRMovingAverageCrossoverStrategy, cash=10_000, commission=.002)

    # For the purpose of demonstration, directly using previously obtained optimized parameters
    ATRMovingAverageCrossoverStrategy.n1 = 20
    ATRMovingAverageCrossoverStrategy.n2 = 60
    ATRMovingAverageCrossoverStrategy.atr_period = 10
    ATRMovingAverageCrossoverStrategy.atr_multiplier = 2

    # Rerun the backtest with the optimized parameters to get detailed stats
    stats = bt.run()
    print(stats)

    bt.plot()

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
