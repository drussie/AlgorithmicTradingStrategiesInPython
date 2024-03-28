# Data handling and analysis
import pandas as pd

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
    n1 = 50  # Short moving average window
    n2 = 150  # Long moving average window
    atr_period = 14  # ATR calculation window
    atr_multiplier = 1  # Multiplier for ATR-based stop-loss

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
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
        
        # Dynamically adjust stop-loss with each new candle
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or 0, self.data.Close[-1] - self.atr[-1] * self.atr_multiplier)
            else:
                trade.sl = min(trade.sl or float('inf'), self.data.Close[-1] + self.atr[-1] * self.atr_multiplier)

if __name__ == "__main__":
    ticker = input("Enter the ticker symbol: ")
    data = yf.download(ticker, start="2020-01-01", end="2024-03-27")

    bt = Backtest(data, ATRMovingAverageCrossoverStrategy, cash=10_000, commission=.002)
    stats = bt.run()
    print(stats)

    bt.plot()

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
