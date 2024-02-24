from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from data.angel_one import Broker
import pandas as pd
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import backtrader as bt
import backtrader.feeds as btfeeds

from __init__ import BRKR, DATA
S_STRGY, _ = os.path.splitext(os.path.basename(__file__))

# Create a Stratey


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

# Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[-0]:
                # current close less than previous close

                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


data = pd.read_csv(f'{DATA}{S_STRGY}/output.csv',
                   parse_dates=['Timestamp'])
unique_symbols = data['Symbol'].unique()
for symbol in unique_symbols:
    symbol_data = data[data['Symbol'] == symbol].set_index('Timestamp')
    symbol_data.index = symbol_data.index.tz_localize(
        None)  # Remove timezone info


def download():
    # get data from angelone
    historicParam = {
        "exchange": "NSE",
        "interval": "FIVE_MINUTE",
        "fromdate": "2023-02-24 09:00",
        "todate": "2024-02-24 09:16"
    }
    obj_broker = Broker(
        S_STRGY,
        credential_file=f"../../../{BRKR}.yml",
        data_dir=DATA
    )
    candle = obj_broker.get_historical(historicParam)
    print(f"{candle=}")
    obj_broker.merge_data(candle)


def run():
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))

    datapath = os.path.join(modpath, f'{DATA}{S_STRGY}', 'ADANIENT.csv')
    print(datapath)
# Create a Data Feed
    data = btfeeds.GenericCSVData(
        dataname=datapath,
        timeframe=bt.TimeFrame.Minutes,
        # fromdate=datetime.datetime(2023, 7, 11, 0, 0, 0),
        # todaydate=datetime.datetime(2023, 8, 31, 0, 0, 0),
        # nullvalue=0.0,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        datetime=0,
        high=2,
        low=3,
        open=1,
        close=4,
        volume=5,
        openinterest=-1,
    )
# Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    cerebro.broker.setcommission(commission=0.001)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()


run()
