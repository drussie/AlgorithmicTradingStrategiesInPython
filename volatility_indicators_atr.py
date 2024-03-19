import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Download the data
data = yf.download(tickers='NVDA', period='max', interval='1d')
data['ATR'] = ta.atr(data.High, data.Low, data.Close, length=14)

df = data[:500]
print(df.tail())

fig = make_subplots(rows=2, cols=1, subplot_titles=['Price', 'ATR'], shared_xaxes=True)

fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'), row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df['ATR'], name='ATR'), row=2, col=1)

fig.update_layout(
    xaxis=dict(rangeslider=dict(visible=False))
)

fig.show()
