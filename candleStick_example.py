import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Download data from Yahoo Finance
df = yf.download('NVDA', start='2020-01-01', end='2024-03-10', interval='1d')
df = df[df["Volume"] != 0]

# Add technical analysis
df['EMA_9'] = ta.ema(df['Close'], length=9)
df['EMA_21'] = ta.ema(df['Close'], length=21)
df['RSI_10'] = ta.rsi(df['Close'], length=10)

print(df.head())
print(df.tail())

# Create a subplot with adjusted spacing for the RSI
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2, 
                    subplot_titles=('Price', 'RSI'), row_heights=[0.5, 0.2])

# Add the candlestick chart to the first subplot
fig.add_trace(go.Candlestick(x=df.index, 
                             open=df['Open'], 
                             high=df['High'], 
                             low=df['Low'], 
                             close=df['Close']), 
              row=1, col=1)

# Add EMA traces to the first subplot
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21'), row=1, col=1)

# Add RSI trace to the second subplot
fig.add_trace(go.Scatter(x=df.index, y=df['RSI_10'], mode='lines', name='RSI 10'), row=2, col=1)

# Update x-axis and y-axis labels
fig.update_xaxes(title_text="Date", row=2, col=1)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)

# Add RSI level lines to the second subplot
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Update layout to add more space at the bottom
fig.update_layout(
    height=1000,
    width=1000,
    showlegend=False,
    margin=dict(l=50, r=50, t=50, b=150)  # Increase bottom margin to 100 (or more if needed)
)

# fig.update(layout_xaxis_rangeslider_visible=False)
fig.show()

# print(df.ta.indicators())
# print(help(ta.atr))

