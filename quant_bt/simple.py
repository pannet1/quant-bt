import pandas as pd
from indicators.ta import Average_True_Range
from time import sleep
# from plots.simple import Plot
import finplot as fplt

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

    symbol_data['sell_arrow'] = None
    symbol_data['buy_arrow'] = None
    for i in range(window, len(symbol_data)):
        if ((symbol_data['Close'][i] < symbol_data['top1'][i])
                and (symbol_data['Open'][i] > symbol_data['top1'][i])):
            if position is None:
                position = 'short'
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                symbol_data['sell_arrow'][i] = symbol_data['High'][i]
        elif ((symbol_data['Close'][i] > symbol_data['bott1'][i])
              and (symbol_data['Open'][i] < symbol_data['bott1'][i])):
            if position is None:
                position = 'long'
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                symbol_data['buy_arrow'][i] = symbol_data['Low'][i]
        # Close positions if necessary
        if position == "short":
            if (
                ((symbol_data['Close'][i] > symbol_data['top2'][i])
                 and (symbol_data['Open'][i] <= symbol_data['top2'][i]))
                or (symbol_data['Close'][i] < symbol_data['bott1'][i])
            ):
                position = None
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                symbol_data['buy_arrow'][i] = symbol_data['Low'][i]
        elif position == "long":
            if (
                ((symbol_data['Close'][i] < symbol_data['bott2'][i])
                 and (symbol_data['Open'][i] >= symbol_data['bott2'][i]))
                or (symbol_data['Close'][i] > symbol_data['top1'][i])
            ):
                position = None
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                symbol_data['sell_arrow'][i] = symbol_data['High'][i]

    print(f"Final Capital for {symbol}: {capital}")
    symbol_data.to_csv(f"{symbol}.csv")
    # open symbol.csv and read it in pandas
    symbol_data = pd.read_csv(f"{symbol}.csv")
    df = symbol_data.rename(columns={
                            'Timestamp': 'time', 'Open': 'open', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Volume': 'volume'})
    df = df.astype({'time': 'datetime64[ns]'})

# create two axes
    ax = fplt.create_plot(symbol)

# plot candle sticks
    candles = df[['time', 'open', 'close', 'high', 'low']]
    fplt.candlestick_ochl(candles, ax=ax)
    fplt.plot(df['time'], df['top2'], ax=ax, legend='UPPER2')
    fplt.plot(df['time'], df['top1'], ax=ax, legend='UPPER1')
    fplt.plot(df['time'], df['sma'], ax=ax, legend='MA')
    fplt.plot(df['time'], df['bott1'], ax=ax, legend='LOWER1')
    fplt.plot(df['time'], df['bott2'], ax=ax, legend='LOWER2')
    fplt.plot(df['time'], df['buy_arrow'], ax=ax,
              color='#4a5', style='^', width=2, legend='buy')
    fplt.plot(df['time'], df['sell_arrow'], ax=ax,
              color='red', style='v', width=2, legend='sell')

    fplt.autoviewrestore()

    # we're done
    fplt.show()
    """
    lst = [symbol_data['top2'], symbol_data['top1'], symbol_data['sma'],
           symbol_data['bott1'], symbol_data['bott2']]
    Plot(symbol, symbol_data[['Open', 'Close', 'High', 'Low']], lst)
    """
    sleep(10)
