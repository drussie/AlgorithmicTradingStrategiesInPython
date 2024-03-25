import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import numpy as np

def get_data(symbol: str):
    data = yf.download(tickers=symbol, period='100d', interval='1d')
    data.reset_index(inplace=True, drop=True)
    return data
# Get the data
ticker = input("Enter the ticker: ")
data = get_data(ticker)

def calculate_sma(data, length: int):
    return ta.sma(data['Close'], length)

# Calculate the moving average
data['SMA'] = calculate_sma(data, 20)
data.dropna(inplace=True)

#Calculate the slope of the moving average
def calculate_slope(series, period: int = 5):
    slopes = [0 for _ in range(period-1)]
    for i in range(period-1, len(series)):
        x = np.arange(period)   # Create an array of x values
        y = series[i-period+1:i+1].values   # Get the values of the moving average for the last n periods
        slope = np.polyfit(x, y, 1)[0]  # Calculate the slope using linear regression
        percent_slope = (slope / y[0]) * 100  # Convert the slope to a percentage
        slopes.append(percent_slope)    # Append the slope to the list
    return slopes

# Calculate the slope
data['Slope'] = calculate_slope(data['SMA'])
data.reset_index(inplace=True, drop=True)

print(data[40:55])

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

fig.add_scatter(x=dfpl.index, y=dfpl['SMA'], mode="markers",
                marker=dict(size=5, color="MediumPurple"),
                name="SMA")
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

print(data)

# 3 Moving averages alignment
# Calculate the moving averages
data['SMA_9'] = calculate_sma(data, 9)
data['SMA_21'] = calculate_sma(data, 21)
data['SMA_50'] = calculate_sma(data, 50)

print(data)

def determine_trend(data):
    if data['SMA_9'] > data['SMA_21'] > data['SMA_50']:
        return 2  # Uptrend
    elif data['SMA_9'] < data['SMA_21'] < data['SMA_50']:
        return 1  # Downtrend
    else:
        return 0  # No trend

# Determine the trend and add it as a new column to the DataFrame
data['Trend'] = data.apply(determine_trend, axis=1)

print("Trend added")
print(data)

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

# Add the moving averages to the plot
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA_9'], mode='lines', name='SMA 9', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA_21'], mode='lines', name='SMA 21', line=dict(color='red')))
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA_50'], mode='lines', name='SMA 50', line=dict(color='green')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

#Candles above or below the MA curve
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
data['Category'] = check_candles(data, 5, 'SMA_21')

print(data[25:55])

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

# Add the moving averages to the plot
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['SMA_21'], mode='lines', name='SMA 21', line=dict(color='red')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

# Apply trend detection using VWAP
# Download the BTC-USD 15 min data for the last 7 days
data = yf.download(ticker, period='14d', interval='15m')
# Compute the VWAP
data.ta.vwap(append=True)

# Apply the check_candles function
data['Category'] = check_candles(data, 5, 'VWAP_D') 

print(data[data["Category"]!=0])

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

# Add the moving averages to the plot
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['VWAP_D'], mode='lines', name='VWAP', line=dict(color='red')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

print(data[:50])

# Trend confirmation using the ADX
# Calculate the ADX
data.ta.adx(append=True)

print(data)

# Define a function to generate the trend signal based on ADX
def generate_trend_signal(data, threshold=40):
    trend_signal = []
    for i in range(len(data)):
        if data['ADX'][i] > threshold:
            if data['DMP'][i] > data['DMN'][i]:
                trend_signal.append(2)  # Confirmed Uptrend
            else:
                trend_signal.append(1)  # Confirmed Downtrend
        else:
            trend_signal.append(0)  # No confirmed trend
    return trend_signal

# Apply the function to generate the trend signal column
data = data.rename(columns=lambda x: x[:-3] if x.startswith('ADX') else x)
data = data.rename(columns=lambda x: x[:-3] if x.startswith('DM') else x)

data['Trend Signal'] = generate_trend_signal(data)

print(data[data['Trend Signal']!=0])

data['Confirmed Signal'] = data.apply(lambda row: row['Category'] if row['Category'] == row['Trend Signal'] else 0, axis=1)

print(data[data['Confirmed Signal']!=0])
# print(data[(data['Category']!=data['Trend Signal']) & (data['Confirmed Signal']!=0)])

dfpl = data[:]
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

# Add the moving averages to the plot
fig.add_trace(go.Scatter(x=dfpl.index, y=dfpl['VWAP_D'], mode='lines', name='VWAP', line=dict(color='red')))

fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()