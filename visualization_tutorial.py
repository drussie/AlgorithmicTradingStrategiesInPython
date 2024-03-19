import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Download data from Yahoo Finance
data = yf.download(tickers='NVDA', period='max', interval='1d')

print(data.head())
print(data.tail())

# Plot the data
# plt.plot(data.index, data.Close)
# plt.show()

# Slice the data and plot it
# dfpl = data[5300:]
# plt.plot(dfpl.index, dfpl.Close)
# plt.show()


# Create a candlestick chart
# fig = go.Figure(data=[go.Candlestick(x=data.index,
#                 open=data['Open'],
#                 high=data['High'],
#                 low=data['Low'],
#                 close=data['Close'],
#                 increasing_line_color='cyan', decreasing_line_color='gray'),
#                 go.Scatter(x=data.index, y=[380]*len(data), line=dict(color='blue', width=2), name='support/resistance')
#                 ])

# Create a candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close']),
                go.Scatter(x=data.index, y=[380]*len(data), line=dict(color='red', width=2), name='support/resistance'),
                go.Scatter(x=data.index, y=[499]*len(data), line=dict(color='red', width=2), name='support/resistance'),
                go.Scatter(x=data.index, y=data.High+10, mode="markers", marker=dict(size=5, color="MediumPurple"), name='Signal')
                ])


# fig.update(layout_xaxis_rangeslider_visible=False)
# fig.update_layout(paper_bgcolor="black", plot_bgcolor="black", title_text="NVDA Candlestick Chart", 
#                   title_font_color="white", title_font_size=20, title_font_family="Arial", title_x=0.5, 
#                   title_y=0.9, title_xanchor="center", title_yanchor="top", title_pad_t=20, title_pad_b=20, 
#                   title_pad_l=20, title_pad_r=20)

fig.show()

