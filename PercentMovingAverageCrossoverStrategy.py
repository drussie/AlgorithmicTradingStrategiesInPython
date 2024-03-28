import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

import matplotlib.pyplot as plt

class PercentageBasedSLStrategy(Strategy):
    n1 = 50  # Initial value for short moving average window
    n2 = 150  # Initial value for long moving average window
    sl_percentage = 0.05  # Initial value for stop-loss percentage

    def init(self):
        # Ensure data is a DataFrame (if necessary)
        if not isinstance(self.data, pd.DataFrame):
            self.data = pd.DataFrame(self.data)  # Assuming it's convertible

        # Handle the case where data is not convertible to a DataFrame
        # (implement your own logic if necessary)
        # else:
        #     raise ValueError("Data cannot be converted to a pandas DataFrame")

        # Calculate moving averages
        self.sma1 = self.data.Close.rolling(self.n1, min_periods=1).mean()
        self.sma2 = self.data.Close.rolling(self.n2, min_periods=1).mean()

    def next(self):
        # Entry strategy: Long when short MA crosses above long MA
        if crossover(self.sma1, self.sma2):
            if not self.position:
                self.buy()
        # Exit strategy: Close position when long MA crosses above short MA or stop-loss is hit
        elif crossover(self.sma2, self.sma1):
            if self.position:
                self.position.close()

        # Update stop-loss for each trade
        for trade in self.trades:
            if not trade.is_closed:
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

    # Optimize the strategy
    optimization_results = bt.optimize(**param_grid, maximize='Sharpe Ratio', return_heatmap=False)

    print("Optimized Parameters:", optimization_results._strategy)
    print("Optimized Sharpe Ratio:", optimization_results['Sharpe Ratio'])

    # Corrected code to access optimized parameters
    optimized_n1 = optimization_results._strategy.n1
    optimized_n2 = optimization_results._strategy.n2
    optimized_sl_percentage = optimization_results._strategy.sl_percentage

    # Rerun the backtest with optimized parameters
    bt = Backtest(data, PercentageBasedSLStrategy, cash=10_000, commission=.002, n1=optimized_n1, n2=optimized_n2, sl_percentage=optimized_sl_percentage)
    stats = bt.run()
    
    # Print all backtest statistics
    print(stats)

    # Plot the backtest results (optional)
    # bt.plot()

    # Plot the close price of the ticker (optional)
    # plt.figure(figsize=(10, 6))
    # plt.plot(data.index, data['Close'], label='Close Price')
    # plt.title(f'{ticker} Close Price')
    # plt.legend()
    # plt.show()
