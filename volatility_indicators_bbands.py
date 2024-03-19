# Volatility Indicators
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Download the data
data = yf.download(tickers='TSLA', period='max', interval='1d')
data = pd.concat([data, ta.bbands(data['Close'], length=14)], axis=1)
data.columns = data.columns[:6].tolist() + ['BB_UPPER', 'BB_MIDDLE', 'BB_LOWER'] + data.columns[9:].tolist()

# Plot the graph
df = data[:300]
fig = go.Figure()

fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'))

fig.add_trace(go.Scatter(x=df.index, y=df['BB_UPPER'], name='BB_UPPER'))
fig.add_trace(go.Scatter(x=df.index, y=df['BB_MIDDLE'], name='BB_MIDDLE'))
fig.add_trace(go.Scatter(x=df.index, y=df['BB_LOWER'], name='BB_LOWER'))

fig.update_layout(
    xaxis=dict(rangeslider=dict(visible=False))
)

fig.show()
