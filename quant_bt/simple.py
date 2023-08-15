import pandas as pd
from indicators.ta import Average_True_Range
from time import sleep
from plots.simple import Plot

# Define  Bands parameters
window = 20
fibratio1 = 1.618
fibratio2 = 2.618
fibratio3 = 4.236

data = pd.read_csv('output.csv', parse_dates=['Timestamp'])
unique_symbols = data['Symbol'].unique()

for symbol in unique_symbols:
    symbol_data = data[data['Symbol'] == symbol].set_index('Timestamp')
    symbol_data.index = symbol_data.index.tz_localize(
        None)  # Remove timezone info
    symbol_data['atr'] = Average_True_Range(
        symbol_data['High'], symbol_data['Low'], symbol_data['Close'], period=5)
    symbol_data['sma'] = symbol_data['Close'].rolling(20).mean()
    symbol_data['top2'] = symbol_data.sma + (symbol_data.atr * fibratio2)
    symbol_data['top1'] = symbol_data.sma + (symbol_data.atr * fibratio1)
    symbol_data['bott1'] = symbol_data.sma - (symbol_data.atr * fibratio1)
    symbol_data['bott2'] = symbol_data.sma - (symbol_data.atr * fibratio2)

    position = None
    capital = 10000  # Initial capital
    quantity = 1  # Quantity to buy/sell
    buy_price = 0
    sell_price = 0
    buy_arrow_coords = []
    sell_arrow_coords = []

    for i in range(window, len(symbol_data)):
        if ((symbol_data['Close'][i] < symbol_data['top1'][i])
                and (symbol_data['Open'][i] > symbol_data['Close'][i])):
            if position is None:
                position = 'short'
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                buy_arrow_coords.append(
                    (symbol_data.index[i], symbol_data['Low'][i]))
        elif ((symbol_data['Close'][i] > symbol_data['bott1'][i])
              and (symbol_data['Open'][i] < symbol_data['Close'][i])):
            if position is None:
                position = 'long'
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                sell_arrow_coords.append(
                    (symbol_data.index[i], symbol_data['High'][i]))
        # Close positions if necessary
        if position == "short":
            if (
                (symbol_data['Close'][i] > symbol_data['top2'][i])
                and (symbol_data['Open'][i] < symbol_data['Close'][i])
            ):
                position = None
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                buy_arrow_coords.append(
                    (symbol_data.index[i], symbol_data['Low'][i])
                )
        elif position == "long":
            if (
                (symbol_data['Close'][i] < symbol_data['bott2'][i])
                and (symbol_data['Open'][i] > symbol_data['Close'][i])
            ):
                position = None
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                sell_arrow_coords.append(
                    (symbol_data.index[i], symbol_data['High'][i]))

    print(f"Final Capital for {symbol}: {capital}")
    symbol_data.to_csv(f"{symbol}.csv")

    lst = [symbol_data['top2'], symbol_data['top1'], symbol_data['sma'],
           symbol_data['bott1'], symbol_data['bott2']]
    Plot(symbol, symbol_data[['Open', 'Close', 'High', 'Low']], lst)
    sleep(10)
