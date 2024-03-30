import yfinance as yf
import pandas_ta as pa
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Import test data
def get_data(symbol: str):
    data = yf.download(tickers=symbol, period='300d', interval='1d')
    data.reset_index(inplace=True)
    return data
# Get the data
data = get_data('BTC-USD')

import plotly.graph_objects as go
dfpl=data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl['Open'],
                    high=dfpl['High'],
                    low=dfpl['Low'],
                    close=dfpl['Close'])])

fig.update_layout(
    autosize=False,
    width=1000,
    height=800, 
    paper_bgcolor='black',
    plot_bgcolor='black')
fig.update_xaxes(gridcolor='black')
fig.update_yaxes(gridcolor='black')

fig.show()

# Signals function
def identify_rejection(data):
    # Create a new column for rejection signal
    data['rejection'] = data.apply(lambda row: 2 if (
        ( (min(row['Open'], row['Close']) - row['Low']) > (1.5 * abs(row['Close'] - row['Open']))) and 
        (row['High'] - max(row['Close'], row['Open'])) < (0.8 * abs(row['Close'] - row['Open'])) and 
        (abs(row['Open'] - row['Close']) > row['Open'] * 0.001)
    ) else 1 if (
        (row['High'] - max(row['Open'], row['Close'])) > (1.5 * abs(row['Open'] - row['Close'])) and 
        (min(row['Close'], row['Open']) - row['Low']) < (0.8 * abs(row['Open'] - row['Close'])) and 
        (abs(row['Open'] - row['Close']) > row['Open'] * 0.001)
    ) else 0, axis=1)

    return data

def pointpos(x, xsignal):
    if x[xsignal]==1:
        return x['High']+1e-4
    elif x[xsignal]==2:
        return x['Low']-1e-4
    else:
        return np.nan

def plot_with_signal(dfpl):

    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl['Open'],
                    high=dfpl['High'],
                    low=dfpl['Low'],
                    close=dfpl['Close'])])

    fig.update_layout(
        autosize=False,
        width=1000,
        height=800, 
        paper_bgcolor='black',
        plot_bgcolor='black')
    fig.update_xaxes(gridcolor='black')
    fig.update_yaxes(gridcolor='black')
    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=8, color="MediumPurple"),
                    name="Signal")
    fig.show()

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

# Defining and testing signal functions
def check_candle_signal(l, n1, n2, levelbackCandles, windowbackCandles, df):
    df=identify_rejection(df)
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

#check_candle_signal(l=len(data)-1, n1=10, n2=10, levelbackCandles=200, windowbackCandles=11, df=data)

n1=5 
n2=5 
levelbackCandles=100 
windowbackCandles=5

signal = [0 for i in range(0, levelbackCandles + n1 + 1)] #fill 0 signals for first rows

for i in range(0, len(data) - 1 - levelbackCandles - n1):
    df = data[i + n1 + 1:i + levelbackCandles + n1 + 1 + 1].copy()
    df.reset_index(inplace=True)

    # Validate the return value of check_candle_signal before appending
    result = check_candle_signal(l=len(df)-1,
                                    n1=n1,
                                    n2=n2,
                                    levelbackCandles=levelbackCandles,
                                    windowbackCandles=windowbackCandles,
                                    df=df)
    signal.append(result)
data["signal"] = signal

# might be a print command 
data.signal.value_counts()

data['pointpos'] = data.apply(lambda row: pointpos(row,"signal"), axis=1)
plot_with_signal(data[:])

# Connect to the market and execute trades
from apscheduler.schedulers.blocking import BlockingScheduler
from oandapyV20 import API
import oandapyV20.endpoints.orders as orders
from oandapyV20.contrib.requests import MarketOrderRequest
from oanda_candles import Pair, Gran, CandleClient
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails

# from config import access_token, accountID
access_token='f5b337d19e6b1ef7bea5a897941e1bfa-b6a2d2ffb8e7061e67d72279c3aecfee'
accountID = 10100128766677001
def get_candles(n):
    #access_token='XXXXXXX'#you need token here generated from OANDA account
    client = CandleClient(access_token, real=False)
    collector = client.get_collector(Pair.BTC_USD, Gran.D1)
    candles = collector.grab(n)
    return candles

candles = get_candles(300)
# for candle in candles:
#     print(float(str(candle.bid.o))>1)


def trading_job():
    candles = get_candles(300)
    dfstream = pd.DataFrame(columns=['Open','Close','High','Low'])
    
    i=0
    for candle in candles:
        dfstream.loc[i, ['Open']] = float(str(candle.bid.o))
        dfstream.loc[i, ['Close']] = float(str(candle.bid.c))
        dfstream.loc[i, ['High']] = float(str(candle.bid.h))
        dfstream.loc[i, ['Low']] = float(str(candle.bid.l))
        i=i+1

    dfstream['Open'] = dfstream['Open'].astype(float)
    dfstream['Close'] = dfstream['Close'].astype(float)
    dfstream['High'] = dfstream['High'].astype(float)
    dfstream['Low'] = dfstream['Low'].astype(float)

    signal = check_candle_signal(l=len(dfstream)-1, n1=6, n2=6, levelbackCandles=200, windowbackCandles=7, df=dfstream)
    
    # EXECUTING ORDERS
    accountID = "10100128766677001" #your account ID here
    client = API(access_token)
         
    SLTPRatio = 2.
    
    SLBuy = dfstream['Low'].iloc[-1]
    SLSell = dfstream['High'].iloc[-1]

    TPBuy = dfstream['Close'].iloc[-1]+(dfstream['Close'].iloc[-1]-SLBuy)*SLTPRatio
    TPSell = dfstream['Close'].iloc[-1]-(dfstream['Close'].iloc[-1]-SLSell)*SLTPRatio
    
    print(dfstream.iloc[:-1,:])
    print(TPBuy, "  ", SLBuy, "  ", TPSell, "  ", SLSell)
    #signal = 2
    #Sell
    if signal == 1:
        mo = MarketOrderRequest(instrument="BTC_USD", units=-1, takeProfitOnFill=TakeProfitDetails(price=TPSell).data, stopLossOnFill=StopLossDetails(price=SLSell).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)
    #Buy
    elif signal == 2:
        mo = MarketOrderRequest(instrument="BTC_USD", units=1, takeProfitOnFill=TakeProfitDetails(price=TPBuy).data, stopLossOnFill=StopLossDetails(price=SLBuy).data)
        r = orders.OrderCreate(accountID, data=mo.data)
        rv = client.request(r)
        print(rv)

        # Executing  orders automatically with a schedular
        #trading_job()

scheduler = BlockingScheduler()
scheduler.add_job(trading_job, 'cron', hour='23', minute='55', start_date='2023-10-20 23:55:00', timezone='America/Chicago')
scheduler.start()