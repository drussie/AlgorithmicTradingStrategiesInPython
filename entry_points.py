import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

def get_data(symbol: str):
    data = yf.download(tickers=symbol, period='300d', interval='1d')
    data.reset_index(inplace=True, drop=True)
    return data
# Get the data
data = get_data('TSLA')

# Calculate Bollinger Bands using pandas_ta
data.ta.bbands(length=10, std=1.5, append=True)

# Add the upper and lower bands to the DataFrame
data['Upper Band'] = data['BBU_10_1.5']
data['Lower Band'] = data['BBL_10_1.5']

def calculate_sma(data, length: int):
    return ta.sma(data['Close'], length)

# Calculate the moving average
data['SMA'] = calculate_sma(data, 20)
data.dropna(inplace=True)

print(data)

def check_candles(data, backcandles, ma_column):
    categories = [0 for _ in range(backcandles)]
    for i in range(backcandles, len(data)):
        if all(data['Close'][i-backcandles:i] > data[ma_column][i-backcandles:i]):
            categories.append(2)  # Uptrend
        elif all(data['Close'][i-backcandles:i] < data[ma_column][i-backcandles:i]):
            categories.append(1)  # Downtrend
        else:
            categories.append(0)  # No trend
    return categories

# Apply the function to the DataFrame
data['Trend'] = check_candles(data, 7, 'SMA')

print(data)

# Entry based on Bollinger Bands
# Check conditions and assign entry values
data['entry'] = 0

# Condition for entry category 2 (buy entry)
buy_entry_condition = (data['Trend'] == 2) & ((data['Open'] < data['Lower Band']) & (data['Close'] > data['Lower Band']))
data.loc[buy_entry_condition, 'entry'] = 2

# Condition for entry category 1 (sell entry)
sell_entry_condition = (data['Trend'] == 1) & ((data['Open'] > data['Upper Band']) & (data['Close'] < data['Upper Band']))
data.loc[sell_entry_condition, 'entry'] = 1

print(data[data['entry']!=0])

# Plot the data

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

# Add the moving averages to the plot
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA'], mode='lines', name='SMA', line=dict(color='red')))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['Lower Band'], mode='lines', name='Lower Band', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['Upper Band'], mode='lines', name='Upper Band', line=dict(color='blue')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

# Entry based on RSI and Bllinger Bands
def add_rsi_column(data):
    # Calculate RSI with a period of 14
    data['RSI'] = ta.rsi(data['Close'])
    return data

data = add_rsi_column(data)

def rsi_signal(data):
    data['RSI Signal'] = 0  # Initialize the signal column with 0

    # Set the signal category to 2 when the price is below the lower Bollinger Band and RSI is below 30
    data.loc[(data['Close'] < data['Lower Band']) & (data['RSI'] < 55), 'RSI Signal'] = 2

    # Set the signal category to 1 when the price is above the upper Bollinger Band and RSI is above 70
    data.loc[(data['Close'] > data['Upper Band']) & (data['RSI'] > 45), 'RSI Signal'] = 1

    return data

data = rsi_signal(data)

print(data[data["RSI Signal"]!=0])

data['entry'] = 0

# Condition for entry category 2 (buy entry)
buy_entry_condition = (data['Trend'] == 2) & (data['RSI Signal'] == 2) & (data['Low'] < data['Lower Band'])
data.loc[buy_entry_condition, 'entry'] = 2

# Condition for entry category 1 (sell entry)
sell_entry_condition = (data['Trend'] == 1) & (data['RSI Signal'] == 1) & (data['High'] > data['Upper Band'])
data.loc[sell_entry_condition, 'entry'] = 1

print(data[data['entry']!=0])

# Entry based on Rejection Candle next to Bollinger Bands
def identify_shooting_star(data):
    # Create a new column for shooting star
    data['shooting_star'] = data.apply(lambda row: 2 if (
        ( (min(row['Open'], row['Close']) - row['Low']) > (1.5 * abs(row['Close'] - row['Open']))) and 
        (row['High'] - max(row['Close'], row['Open'])) < (0.8 * abs(row['Close'] - row['Open'])) and 
        (abs(row['Open'] - row['Close']) > row['Open'] * 0.01)
    ) else 1 if (
        (row['High'] - max(row['Open'], row['Close'])) > (1.5 * abs(row['Open'] - row['Close'])) and 
        (min(row['Close'], row['Open']) - row['Low']) < (0.8 * abs(row['Open'] - row['Close'])) and 
        (abs(row['Open'] - row['Close']) > row['Open'] * 0.01)
    ) else 0, axis=1)

    return data

data = identify_shooting_star(data)
print('Shooting Star')
print(data[data['shooting_star']!=0])

