from toolkit.logger import Logger
from indicators.ta import Average_True_Range
import numpy as np
import pandas as pd
import pendulum
from backtesting import Strategy, Backtest
from backtesting.test import SMA


fibratio1 = 1.618
fibratio2 = 2.618
fibratio3 = 4.236


class BbrBt(Strategy):

    def init(self):
        self.logging = Logger(10)
        self.atr = self.data['atr'].round(2)
        self.sma = self.data['sma'].round(2)
        self.r1 = self.data['r1'].round(2)
        self.r2 = self.data['r2'].round(2)
        self.r3 = self.data['r3'].round(2)

    def next(self):
        top2 = self.sma[-1] + self.r2[-1]
        top1 = self.sma[-1] + self.r1[-1]
        bott1 = self.sma[-1] - self.r1[-1]
        bott2 = self.sma[-1] - self.r2[-1]

        """
        try:
            ts = self.data.Timestamp[-1]
            ts_b4 = pendulum.parse(ts, strict=False)
            if ts_b4.hour == 15 and ts_b4.minute >= 15:
                if self.position:
                    self.position.close()
        except Exception as e:
            self.logging.debug(f" {e} while parsing timestamp {ts_b4}")
        """
        self.logging.info(f"{top2}>{top1}>{bott1}>{bott2}")
        if self.position.is_long:
            if (
                (self.data.Close[-1] < bott2)
                and (self.data.Open[-1] > self.data.Close[-1])
            ):
                # buy stop is hit
                self.position.close()
                self.logging.info(
                    f"sell: SL {self.data.Timestamp[-1]} {self.position.is_long}")
            elif (self.data.Close[-1] > top1):
                # buy target is hit
                self.position.close()
                self.logging.info(
                    f"sell: TP {self.data.Timestamp[-1]} {self.position.is_long}")
        elif self.position.is_short:
            if (
                (self.data.Close[-1] > top2)
                and (self.data.Open[-1] < self.data.Close[-1])
            ):
                self.logging.info(
                    f"cover: SL {self.data.Timestamp[-1]} {self.position.is_short}")
                self.position.close()
            elif (self.data.Close[-1] < bott1):
                self.position.close()
                self.logging.info(
                    f"cover: TP {self.data.Timestamp[-1]} {self.position.is_short}")
        else:
            if (
                (self.data.Close[-1] > bott1)
                and (self.data.Open[-1] < self.data.Close[-1])
            ):
                self.buy()  # Go long
                self.logging.info(
                    f"BUY: {self.data.Timestamp[-1]} {self.position.is_long}")
            elif (
                (self.data.Close[-1] < top1)
                and (self.data.Open[-1] > self.data.Close[-1])
            ):
                self.sell()  # Go short
                self.logging.info(
                    f"SELL: {self.data.Timestamp[-1]} {self.position.is_short}")


data = pd.read_csv('output.csv', parse_dates=['Timestamp'])


backtests = {}
# Iterate over unique symbols and perform backtesting and plotting for each
for symbol in data['Symbol'].unique():
    symbol_data = data[data['Symbol'] == symbol].set_index('Timestamp')
    symbol_data['Timestamp'] = symbol_data.index
    symbol_data['atr'] = Average_True_Range(
        symbol_data['High'], symbol_data['Low'], symbol_data['Close'], period=5)
    symbol_data['sma'] = symbol_data.Close.rolling(20).mean()
    symbol_data['r1'] = symbol_data.atr * fibratio1
    symbol_data['r2'] = symbol_data.atr * fibratio2
    symbol_data['r3'] = symbol_data.atr * fibratio3

    # Create a Backtest instance for the symbol's data
    backtests[symbol] = Backtest(
        symbol_data, BbrBt, commission=0)

    # Run the backtest
    results = backtests[symbol].run()

    # Print performance metrics
    print(f"Performance metrics for {symbol}")
    print(results)

    # Plot the equity curve for the symbol
    backtests[symbol].plot()
