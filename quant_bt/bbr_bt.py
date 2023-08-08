from toolkit.logger import Logger
import numpy as np
import pandas as pd
import pendulum
from backtesting import Strategy, Backtest


class BbrBt(Strategy):
    fibratio1 = 1.618
    fibratio2 = 2.618
    fibratio3 = 4.236

    def init(self):
        self.period = 20
        self.sma = np.convolve(self.data.Close, np.ones(
            self.period)/self.period, mode='valid')
        self.atr = np.mean(np.abs(np.diff(self.data.Close)))
        self.r1 = self.atr * self.fibratio1
        self.r2 = self.atr * self.fibratio2
        self.r3 = self.atr * self.fibratio3
        self.dir = 0
        self.logging = Logger(10)

    def next(self):
        top3 = self.sma[-1] + self.r3
        top2 = self.sma[-1] + self.r2
        top1 = self.sma[-1] + self.r1
        bott1 = self.sma[-1] - self.r1
        bott2 = self.sma[-1] - self.r2
        bott3 = self.sma[-1] - self.r3

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

    # Create a Backtest instance for the symbol's data
    backtests[symbol] = Backtest(
        symbol_data, BbrBt, commission=0.001)

    # Run the backtest
    results = backtests[symbol].run()

    # Print performance metrics
    print(f"Performance metrics for {symbol}")
    print(results)

    # Plot the equity curve for the symbol
    backtests[symbol].plot()
