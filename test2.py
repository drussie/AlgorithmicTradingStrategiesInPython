import yfinance as yf
import pandas as pd
import pandas_ta as pa
import numpy as np
import plotly.graph_objects as go
from tqdm import tqdm
from backtesting import Strategy, Backtest

def get_data(symbol: str):
    """Fetches historical market data from Yahoo Finance."""
    data = yf.download(tickers=symbol, period='1000d', interval='1d')
    # Correctly reset the index and then rename it
    data.reset_index(inplace=True)
    data = data.rename(columns={'Date': 'date'})  # Rename the 'Date' column to 'date'
    return data


def identify_rejection(data):
    """Identifies rejection signals based on specific criteria and adds them to the dataframe."""
    def rejection_criteria(row):
        bullish_rejection = (
            (min(row['Open'], row['Close']) - row['Low']) > (1.5 * abs(row['Close'] - row['Open'])) and 
            (row['High'] - max(row['Close'], row['Open'])) < (0.8 * abs(row['Close'] - row['Open'])) and 
            (abs(row['Open'] - row['Close']) > row['Open'] * 0.001)
        )
        bearish_rejection = (
            (row['High'] - max(row['Open'], row['Close'])) > (1.5 * abs(row['Open'] - row['Close'])) and 
            (min(row['Close'], row['Open']) - row['Low']) < (0.8 * abs(row['Open'] - row['Close'])) and 
            (abs(row['Open'] - row['Close']) > row['Open'] * 0.001)
        )
        if bullish_rejection:
            return 2
        elif bearish_rejection:
            return 1
        else:
            return 0
    
    data['rejection'] = data.apply(rejection_criteria, axis=1)
    return data

# Adjusting plot_with_signal to use 'date' column and address SettingWithCopyWarning

def plot_with_signal(df):
    """Plots candlestick chart with rejection signals."""
    # Clone df to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Ensure the 'date' column is of datetime type for proper plotting
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate 'pointpos'; ensure column names match your DataFrame's columns
    df['pointpos'] = df.apply(lambda row: row['High'] + 1e-4 if row['rejection'] == 1 
                              else row['Low'] - 1e-4 if row['rejection'] == 2 
                              else np.nan, axis=1)

    fig = go.Figure(data=[go.Candlestick(x=df['date'], 
                                         open=df['Open'], 
                                         high=df['High'], 
                                         low=df['Low'], 
                                         close=df['Close'])])

    # Add rejection signals
    fig.add_trace(go.Scatter(x=df['date'], y=df['pointpos'], mode="markers", 
                             marker=dict(size=8, color="MediumPurple"), name="Signal"))

    fig.update_layout(
                      autosize=False, width=1000, height=800,
                      paper_bgcolor='black', plot_bgcolor='black',
                      xaxis=dict(type='date', gridcolor='black'), yaxis=dict(gridcolor='black'))

    fig.show()



if __name__ == "__main__":
    # Execution flow
    data = get_data('NVDA')
    data = identify_rejection(data)
    # filtered_data = data[data["rejection"] != 0]  # Filtering data with rejection signals
    # plot_with_signal(filtered_data)
    plot_with_signal(data)

# Support and Resistance Functions
def support(df1, l, n1, n2): #n1 n2 before and after candle l
    if ( df1.Low[l-n1:l].min() < df1.Low[l] or
        df1.Low[l+1:l+n2+1].min() < df1.Low[l] ):
        return 0
    return 1

def resistance(df1, l, n1, n2): #n1 n2 before and after candle l
    if ( df1.High[l-n1:l].max() > df1.High[l] or
       df1.High[l+1:l+n2+1].max() > df1.High[l] ):
        return 0
    return 1

# Close to resistance and support testing
def closeResistance(l, levels, lim, df):
    if len(levels) == 0:
        return 0
    c1 = abs(df['High'][l] - min(levels, key=lambda x: abs(x - df['High'][l]))) <= lim
    c2 = abs(max(df['Open'][l], df['Close'][l]) - min(levels, key=lambda x: abs(x - df['High'][l]))) <= lim
    c3 = min(df['Open'][l], df['Close'][l]) < min(levels, key=lambda x: abs(x - df['High'][l]))
    c4 = df['Low'][l] < min(levels, key=lambda x: abs(x - df['High'][l]))
    if (c1 or c2) and c3 and c4:
        return min(levels, key=lambda x: abs(x - df['High'][l]))
    else:
        return 0

def closeSupport(l, levels, lim, df):
    if len(levels) == 0:
        return 0
    c1 = abs(df['Low'][l] - min(levels, key=lambda x: abs(x - df['Low'][l]))) <= lim
    c2 = abs(min(df['Open'][l], df['Close'][l]) - min(levels, key=lambda x: abs(x - df['Low'][l]))) <= lim
    c3 = max(df['Open'][l], df['Close'][l]) > min(levels, key=lambda x: abs(x - df['Low'][l]))
    c4 = df['High'][l] > min(levels, key=lambda x: abs(x - df['Low'][l]))
    if (c1 or c2) and c3 and c4:
        return min(levels, key=lambda x: abs(x - df['Low'][l]))
    else:
        return 0

def is_below_resistance(l, level_backCandles, level, df):
    return df.loc[l-level_backCandles:l-1, 'High'].max() < level

def is_above_support(l, level_backCandles, level, df):
    return df.loc[l-level_backCandles:l-1, 'Low'].min() > level

def check_candle_signal(l, n1, n2, levelbackCandles, windowbackCandles, df):
    ss = []
    rr = []
    for subrow in range(l-levelbackCandles, l-n2+1):
        if support(df, subrow, n1, n2):
            ss.append(df.Low[subrow])
        if resistance(df, subrow, n1, n2):
            rr.append(df.High[subrow])

    ss.sort() #keep lowest support when popping a level
    for i in range(1,len(ss)):
        if(i>=len(ss)):
            break
        if abs(ss[i]-ss[i-1])/ss[i]<=0.001: # merging close distance levels
            ss.pop(i)

    rr.sort(reverse=True) # keep highest resistance when popping one
    for i in range(1,len(rr)):
        if(i>=len(rr)):
            break
        if abs(rr[i]-rr[i-1])/rr[i]<=0.001: # merging close distance levels
            rr.pop(i)

    #----------------------------------------------------------------------
    # joined levels
    rrss = rr+ss
    rrss.sort()
    for i in range(1,len(rrss)):
        if(i>=len(rrss)):
            break
        if abs(rrss[i]-rrss[i-1])/rrss[i]<=0.001: # merging close distance levels
            rrss.pop(i)
    cR = closeResistance(l, rrss, df.Close[l]*0.003, df)
    cS = closeSupport(l, rrss, df.Close[l]*0.003, df)
    #----------------------------------------------------------------------

    # cR = closeResistance(l, rr, 150e-5, df)
    # cS = closeSupport(l, ss, 150e-5, df)
    #print(rrss,df.Close*0.002)
    if (df.rejection[l] == 1 and cR and is_below_resistance(l,windowbackCandles,cR, df)):
        return 1
    elif(df.rejection[l] == 2 and cS and is_above_support(l,windowbackCandles,cS, df)):
        return 2
    else:
        return 0

# Extra function added by me    
# Define the pointpos function outside of any other definitions
def pointpos(row, xsignal):
    if row[xsignal] == 1:
        return row['High'] + 1e-4
    elif row[xsignal] == 2:
        return row['Low'] - 1e-4
    return np.nan    
    

n1 = 8
n2 = 8
levelbackCandles = 60
windowbackCandles = n2

signal = [0 for i in range(len(data))]

for row in tqdm(range(levelbackCandles+n1, len(data)-n2)):
    signal[row] = check_candle_signal(row, n1, n2, levelbackCandles, windowbackCandles, data)

data["signal"] = signal

# check this print
data[data["signal"]!=0]

data['pointpos'] = data.apply(lambda row: pointpos(row,"signal"), axis=1)
plot_with_signal(data[750:950])

# Backtesting
data.set_index("date", inplace=True)

print(data.head())
print(data.tail())

data['ATR'] = pa.atr(high=data.High, low=data.Low, close=data.Close, length=14)
data['RSI'] = pa.rsi(data.Close, length=5)

def SIGNAL():
    return data.signal

#A new strategy needs to extend Strategy class and override its two abstract methods: init() and next().
#Method init() is invoked before the strategy is run. Within it, one ideally precomputes in efficient, 
#vectorized manner whatever indicators and signals the strategy depends on.
#Method next() is then iteratively called by the Backtest instance, once for each data point (data frame row), 
#simulating the incremental availability of each new full candlestick bar.

#Note, backtesting.py cannot make decisions / trades within candlesticks — any new orders are executed on the
#next candle's open (or the current candle's close if trade_on_close=True). 
#If you find yourself wishing to trade within candlesticks (e.g. daytrading), you instead need to begin 
#with more fine-grained (e.g. hourly) data.

# Using fixed Stop loss and TP rules
# Trader fixed SL and TP

class MyCandlesStrat(Strategy):  
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        self.ratio = 2
        self.risk_perc = 0.1

    def next(self):
        super().next() 
        if self.signal1==2:
            sl1 = self.data.Close[-1] - self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.buy(sl=sl1, tp=tp1)
        elif self.signal1==1:
            sl1 = self.data.Close[-1] + self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.sell(sl=sl1, tp=tp1)
bt = Backtest(data, MyCandlesStrat, cash=100_000, commission=.02)
stat = bt.run()
print(stat)

bt.plot()

# Using the RSI for Exit Signals

class MyCandlesStrat(Strategy):
    ratio = 1.5
    risk_perc = 0.1  
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        #self.ratio
        #self.risk_perc

    def next(self):
        super().next()
        
        if len(self.trades)>0:
            if self.trades[-1].is_long and self.data.RSI[-1]>=80:
                self.trades[-1].close()
            elif self.trades[-1].is_short and self.data.RSI[-1]<=20:
                self.trades[-1].close()

        if self.signal1==2 and len(self.trades)==0:
            sl1 = self.data.Close[-1] - self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.buy(sl=sl1, tp=tp1)
        elif self.signal1==1 and len(self.trades)==0:
            sl1 = self.data.Close[-1] + self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.sell(sl=sl1, tp=tp1)
bt = Backtest(data, MyCandlesStrat, cash=100_000, commission=.05)
stat = bt.run()
print(stat)

bt.plot()

# Define a range of values to test for each parameter
param_grid = {'ratio': list(np.arange(1.5, 3.5, 0.5)), 'risk_perc': list(np.arange(0.06, 0.2, 0.02))}
# Run the optimization
res = bt.optimize(**param_grid, random_state=5)

# Print the best results and the parameters that lead to these results
print("Best result: ", res['Return [%]'])
print("Parameters for best result: ", res['_strategy'])

# ATR based Stop Loss and TP
# ATR related SL and TP
class MyCandlesStrat(Strategy): 
    atr_f = 3
    ratio_f = 2
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next() 
        if self.signal1==2:
            sl1 = self.data.Close[-1] - self.data.ATR[-1]*self.atr_f
            tp1 = self.data.Close[-1] + self.data.ATR[-1]*self.ratio_f*self.atr_f
            self.buy(sl=sl1, tp=tp1)
        elif self.signal1==1:
            sl1 = self.data.Close[-1] + self.data.ATR[-1]*self.atr_f
            tp1 = self.data.Close[-1] - self.data.ATR[-1]*self.ratio_f*self.atr_f
            self.sell(sl=sl1, tp=tp1)
bt = Backtest(data, MyCandlesStrat, cash=100_000, commission=.000)
stat = bt.run()
print(stat)

bt.plot()

# Trailing stop loss
#fixed distance Trailing SL
class MyCandlesStrat(Strategy):
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        sltr=self.data.Close[-1]*0.02

        for trade in self.trades: 
            if trade.is_long: 
                trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - sltr)
            else:
                trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + sltr) 
        
        if self.signal1==2 and len(self.trades)==0: 
            sl1 = self.data.Close[-1] - sltr
            self.buy(sl=sl1)
        elif self.signal1==1 and len(self.trades)==0: 
            sl1 = self.data.Close[-1] + sltr
            self.sell(sl=sl1)


bt = Backtest(data, MyCandlesStrat, cash=100_000, commission=.000)
stat = bt.run()
print(stat)

bt.plot()

#ATR based Trailing Stop Loss

class MyCandlesStrat(Strategy):
    atr_f = 0.6
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        self.sltr=0

    def next(self):
        super().next()
        
        for trade in self.trades: 
            if trade.is_long: 
                trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - self.sltr)
            else:
                trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + self.sltr)

        if self.signal1==2 and len(self.trades)==0: 
            self.sltr=self.data.ATR[-1]/self.atr_f
            sl1 = self.data.Close[-1] - self.data.ATR[-1]/self.atr_f
            self.buy(sl=sl1)
        elif self.signal1==1 and len(self.trades)==0: 
            self.sltr=self.data.ATR[-1]/self.atr_f
            sl1 = self.data.Close[-1] + self.data.ATR[-1]/self.atr_f
            self.sell(sl=sl1)
bt = Backtest(data, MyCandlesStrat, cash=100_000, commission=.000)
stat = bt.run()
print(stat)

# Lost siszing and trade management
class MyCandlesStrat(Strategy):
    lotsize = 1 
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        self.ratio = 1.
        self.risk_perc = 0.1

    def next(self):
        super().next() 
        if self.signal1==2 and len(self.trades)==0:
            sl1 = self.data.Close[-1] - self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio*0.8
            tp2 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio*1.2
            self.buy(sl=sl1, tp=tp1, size=self.lotsize)
            self.buy(sl=sl1, tp=tp2, size=self.lotsize)
        elif self.signal1==1 and len(self.trades)==0:
            sl1 = self.data.Close[-1] + self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio*0.8
            tp2 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio*1.2
            self.sell(sl=sl1, tp=tp1, size=self.lotsize)
            self.sell(sl=sl1, tp=tp2, size=self.lotsize)
bt = Backtest(data, MyCandlesStrat, cash=100_000, margin=1/1, commission=.05)
stat = bt.run()
print(stat)


