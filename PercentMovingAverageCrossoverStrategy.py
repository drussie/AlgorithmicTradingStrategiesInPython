# Data handling and analysis
import pandas as pd

# Fetching financial market data
import yfinance as yf

# Backtesting library
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings if needed (e.g., deprecation warnings)
import warnings
warnings.filterwarnings("ignore")

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
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

            # Set stop-loss based on current price and stop-loss percentage
            stop_loss_price = self.data.Close[-1] * (1 - self.stop_loss_percentage)
            self.position.stop_loss = stop_loss_price

if __name__ == "__main__":
    # Fetch historical data from Yahoo Finance
    ticker = input("Enter the ticker symbol: ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")
    data = yf.download(ticker, start, end)

    # Initialize the Backtest object
    bt = Backtest(data, MovingAverageCrossoverStrategy, cash=10_000, commission=.002)

    # Run the backtest
    stats = bt.run()
    print(stats)

    # Plot the backtest result
    bt.plot()

    # Additional plotting (if needed)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
