import csv
import pandas as pd
from omspy_brokers.angel_one import AngelOne
from toolkit.fileutils import Fileutils
from toolkit.logger import Logger
import sys
import json
from time import sleep

logging = Logger(20)


def symbols(full_path):
    universe_df = pd.read_csv(full_path)
    universe_df['disabled'] = universe_df['disabled'].astype('str')
    universe_df = universe_df[~(universe_df.disabled.str.upper() == 'Y')]
    universe_df = universe_df.drop(['disabled'], axis=1)
    return universe_df


class Broker:

    def __init__(
        self,
        strategy_name,
        data_dir,
        credential_file,
    ):
        self.strategy = strategy_name
        self.data_dir = data_dir
        self.stratergy_dir = self.data_dir + self.strategy + "/"
        self.broker = self.get_broker(credential_file)

    @staticmethod
    def get_broker(broker_yaml):
        try:
            cred = Fileutils().get_lst_fm_yml(broker_yaml)
            ao = AngelOne(**cred)
            if not ao.authenticate():
                raise Exception("Authentication failed.")
        except Exception as e:
            print(e)
            sys.exit(1)
        else:
            return ao

    def get_historical(self, param):
        def get_tkn_fm_sym(sym):
            try:
                f = open(self.data_dir + "symbols.json")
                data = json.load(f)
                token = next((item.get("token")
                              for item in data if item.get("symbol") == sym), 0)
                f.close
                return token
            except Exception as e:
                print(f"{e} occured while get_tkn_fm_sym")

        candle = {}
        df_tsym = symbols(f"{self.stratergy_dir}universe.csv")
        for symbol in df_tsym.symbol:
            historicParam = {
                "symboltoken": str(get_tkn_fm_sym(symbol)),
            }
            historicParam.update(param)
            logging.info(f"Getting historical data for {symbol}")
            resp = self.broker.obj.getCandleData(historicParam)
            print(f"{resp=}")
            if resp is not None and isinstance(resp, dict) and resp.get('data', False):
                candle[symbol] = [x for x in resp['data']]
            print("sleeping")
            sleep(.5)
        return candle

    def merge_data(self, candle):
        with open(f"{self.stratergy_dir}output.csv", 'w', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(["Symbol", "Timestamp", "Open", "High",
                                "Low", "Close", "Volume"])  # Header row

            for symbol, ohlc_list in candle.items():
                # Index 4 corresponds to Close price
                lst_close = [data[4] for data in ohlc_list]
                # Index 0 corresponds to Timestamp
                lst_dates = [data[0] for data in ohlc_list]
                # Index 1 corresponds to Open price
                lst_open = [data[1] for data in ohlc_list]
                # Index 2 corresponds to High price
                lst_high = [data[2] for data in ohlc_list]
                # Index 3 corresponds to Low price
                lst_low = [data[3] for data in ohlc_list]
                # Index 5 corresponds to Volume
                lst_volume = [data[5] for data in ohlc_list]

                for timestamp, open_price, high_price, low_price, close_price, volume in zip(lst_dates, lst_open, lst_high, lst_low, lst_close, lst_volume):
                    csvwriter.writerow(
                        [symbol, timestamp, open_price, high_price, low_price, close_price, volume])

    """
    def prepare(candle):
        for symbol, ohlc_list in candle.items():
            # Index 3 corresponds to Close price
            lst_close = [data[4] for data in ohlc_list]
            lst_dates = [data[0] for data in ohlc_list]
            print(f"Symbol: {symbol}, Close prices: {lst_close}")
        return lst_dates, lst_close
    if any(candle):
        lst_dates, lst_close = prepare(candle)
        if any(lst_dates) and any(lst_close):
            val = indicator(lst_close, period)
    plot(lst_dates, val)
    """
