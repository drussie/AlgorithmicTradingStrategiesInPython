import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
import pandas_ta as ta
import multiprocessing

# Fetches historical market data
def fetch_data(symbol, start, end, interval='1d'):
    data = yf.download(tickers=symbol, start=start, end=end, interval=interval)
    data.reset_index(inplace=True)
    return data

# Trading strategy based on Williams %R
class WilliamsRStrategy(Strategy):
    # Define 'length' as a class variable for optimization
    length = 2
    
    def init(self):
        # Use 'self.length' to access the parameter
        def willr(high, low, close):
            hh = pd.Series(high).rolling(window=self.length).max()
            ll = pd.Series(low).rolling(window=self.length).min()
            will_r = -100 * ((hh - pd.Series(close)) / (hh - ll))
            return will_r.bfill().values

        self.williams_r = self.I(willr, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        if self.williams_r[-1] < -80:
            self.buy()
        elif self.williams_r[-1] > -20 and self.position.is_long:
            self.position.close()




# Backtest the strategy
def run_backtest(data):
    bt = Backtest(data, WilliamsRStrategy, cash=10_000, commission=.000)
    output = bt.run()
    print(output)
    bt.plot()


# Plot Williams %R
def plot_williams_r(data):
    """Plot the Williams %R indicator."""
    williams_r = ta.willr(data['High'], data['Low'], data['Close'], length=14)
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, williams_r, label="Williams %R")  # Use data.index instead of data['Date']
    plt.axhline(y=-20, color='r', linestyle='--', label="Overbought")
    plt.axhline(y=-80, color='g', linestyle='--', label="Oversold")
    plt.title("Williams %R Indicator")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    multiprocessing.set_start_method('fork')
    symbol = input("Enter the ticker symbol: ")
    start = input("Enter the start date (YYYY-MM-DD): ")
    end = input("Enter the end date (YYYY-MM-DD): ")

    data = fetch_data(symbol, start, end)
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    data.dropna(inplace=True)

    bt = Backtest(data, WilliamsRStrategy, cash=10_000, commission=.002)
    
    # Define the parameter grid over which to optimize
    params = {'length': range(2, 60)}  # For example, optimizing the length from 10 to 19

    # Optimize the strategy
    result = bt.optimize(**params, maximize='Equity Final [$]', return_heatmap=True)
    print(result)
    
    # Plot the optimized strategy
    bt.plot()


