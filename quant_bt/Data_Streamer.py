import polars as pl
from time import sleep
import pandas as pd

def Polars_Streamer(file_name, length=None, sleep_time=0.001):
    df = pl.read_csv(file_name)
    if length == None:
        for i in range(len(df)):
            sleep(sleep_time)
            yield df[i]
    else:
        for i in range(length, len(df)):
            sleep(sleep_time)
            yield df[i]

def Pandas_Streamer(file_name, length=None, sleep_time=0.001):
    df = pd.read_csv(file_name)
    if length == None:
        for i in range(len(df)):
            sleep(sleep_time)
            yield df.iloc[i]
    else:
        for i in range(length, len(df)):
            sleep(sleep_time)
            yield df.iloc[i]


