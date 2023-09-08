from indicators.ta_ import Average_True_Range
from downloaders.ao_dl import AoDl
import quantstats as qs
import os
from datetime import time
import finplot as fplt
import pandas as pd
from time import sleep

# finplot settings
fplt.background = "black"
fplt.foreground = "white"
fplt.cross_hair_color = "white"
fplt.candle_shadow_width = 2

dir_path = "../../../"
# Define  Bands parameters
window = 30
fibratio1 = 1.618
fibratio2 = 2.618
fibratio3 = 4.236

current_file_path = __file__
current_file_name_with_extension = os.path.basename(current_file_path)
strategy, _ = os.path.splitext(current_file_name_with_extension)
# get data from angelone
historicParam = {
    "exchange": "NSE",
    "interval": "FIVE_MINUTE",
    "fromdate": "2023-05-01 09:00",
    "todate": "2023-08-18 09:16"
}
# aodl = AoDl(strategy, hist_param=historicParam, dir_path=dir_path)
data = pd.read_csv(f'data/{strategy}/output.csv', parse_dates=['Timestamp'])
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
    enter_before = time(14, 20)
    exit_before = time(15, 20)

    symbol_data['sell_arrow'] = None
    symbol_data['buy_arrow'] = None
    symbol_data['returns'] = None
    SUP = RES = False
    for i in range(window, len(symbol_data)):
        if (
            position is None and
            (symbol_data.index[i].time() < enter_before)
        ):
            if not RES and (symbol_data['High'][i] >= symbol_data['top2'][i]):
                RES = True
            if not SUP and (symbol_data['Low'][i] <= symbol_data['bott2'][i]):
                SUP = True
            if (
                RES and
                (symbol_data['Close'][i] < symbol_data['top1'][i])
                    and (symbol_data['Open'][i] > symbol_data['top1'][i])):
                position = 'short'
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                symbol_data['sell_arrow'][i] = symbol_data['High'][i]
                # symbol_data.loc[i, 'sell_arrow'] = symbol_data['High'][i]
                RES = False
            elif (
                SUP and
                (symbol_data['Close'][i] > symbol_data['bott1'][i])
                    and (symbol_data['Open'][i] < symbol_data['bott1'][i])):
                position = 'long'
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                symbol_data['buy_arrow'][i] = symbol_data['Low'][i]
                # symbol_data[i, 'buy_arrow'] = symbol_data['Low'][i]
                SUP = False
        elif position == "short":
            if (
                (symbol_data.index[i].time() > exit_before) or
                ((symbol_data['Close'][i] > symbol_data['top2'][i])
                 and (symbol_data['Open'][i] <= symbol_data['top2'][i]))
                or (symbol_data['Close'][i] < symbol_data['bott1'][i])
            ):
                position = None
                buy_price = symbol_data['Close'][i]
                capital -= buy_price * quantity
                symbol_data['buy_arrow'][i] = symbol_data['Low'][i]
                # symbol_data[i, 'buy_arrow'] = symbol_data['Low'][i]
                symbol_data['returns'][i] = sell_price - buy_price
        elif position == "long":
            if (
                (symbol_data.index[i].time() > exit_before) or
                ((symbol_data['Close'][i] < symbol_data['bott2'][i])
                 and (symbol_data['Open'][i] >= symbol_data['bott2'][i]))
                or (symbol_data['Close'][i] > symbol_data['top1'][i])
            ):
                position = None
                sell_price = symbol_data['Close'][i]
                capital += sell_price * quantity
                symbol_data['sell_arrow'][i] = symbol_data['High'][i]
                # symbol_data.loc[i, 'sell_arrow'] = symbol_data['High'][i]
                symbol_data['returns'][i] = sell_price - buy_price
    print(f"Final Capital for {symbol}: {capital}")
    symbol_data.to_csv(f"data/{strategy}/{symbol}.csv")
    """
     calculate tearsheet
    """
    # convert timestamp to date
    df = symbol_data.dropna(subset=['returns'])
    df = df[['returns']]
    # Remove time zone information from the index
    df.index = df.index.tz_localize(None)
    # Convert the index to a datetime index (if not already)
    df.index = pd.to_datetime(df.index)
    # Converting to returns
    df['returns'] = df['returns'] / capital
    # extend pandas functionality with metrics, etc.
    qs.extend_pandas()
    qs.reports.metrics(df.returns, cumulative=False)  # turn off compounding
    """
        plot the trades
    """
    # open symbol.csv and read it in pandas
    symbol_data = pd.read_csv(f"data/{strategy}/{symbol}.csv")
    df = symbol_data.rename(columns={
        'Timestamp': 'time', 'Open': 'open', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Volume': 'volume'})
    df = df.astype({'time': 'datetime64[ns]'})
    # create axes
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
              color='orange', style='v', width=2, legend='sell')
    fplt.autoviewrestore()

    def save():
        fplt.screenshot(open('screenshots/' + symbol + '.png', 'wb'))
    # wait some until we're rendered
    fplt.timer_callback(save, 0.5, single_shot=True)
    # we're done
    fplt.show()
