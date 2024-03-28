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
    # The strategy now uses hardcoded best parameters from optimization results
    # These should be updated manually based on optimization output
    n1 = 50  # To be updated manually after optimization
    n2 = 100  # To be updated manually after optimization

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

if __name__ == "__main__":
    # Fetch historical data from Yahoo Finance
    ticker = input("Enter the ticker symbol: ")
    data = yf.download(ticker, start="2020-01-01", end="2024-03-27")

    # Initialize the Backtest object
    bt = Backtest(data, MovingAverageCrossoverStrategy, cash=10_000, commission=.002)

    # Run optimization (Note: This is to demonstrate the process. Typically, you'd do this separately.)
    param_grid = {
        'n1': range(10, 51, 10),  # Short moving average window
        'n2': range(50, 201, 50)  # Long moving average window
    }
    optimization_results = bt.optimize(**param_grid, maximize='Sharpe Ratio', return_heatmap=False)

    # Print the best parameters and their corresponding performance metric
    print("Best Parameters:", optimization_results._strategy)
    print("Sharpe Ratio:", optimization_results['Sharpe Ratio'])

    # Manually input the optimized parameters after reading them from the output
    # Example: MovingAverageCrossoverStrategy.n1 = 50, MovingAverageCrossoverStrategy.n2 = 150

    # Since the parameters are manually updated in the strategy, directly rerun the backtest
    stats = bt.run()
    print(stats)

    # Plot the backtest result with the updated parameters
    bt.plot()

    # Additional plotting (if needed)
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close Price')
    plt.title(f'{ticker} Close Price')
    plt.legend()
    plt.show()
