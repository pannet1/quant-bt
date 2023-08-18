from time import sleep
import pandas as pd
from datetime import time


data = pd.read_csv('output.csv', parse_dates=['Timestamp'])
unique_symbols = data['Symbol'].unique()

for symbol in unique_symbols:
    symbol_data = data[data['Symbol'] == symbol].set_index('Timestamp')
    symbol_data.index = symbol_data.index.tz_localize(
        None)  # Remove timezone info
    print(symbol_data.index.time > time(15, 10))
    # df[df.timestamp.dt.time == dt.time(15, 10)]
    sleep(10)
