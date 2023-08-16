import polars as pl
import pandas as pd


def True_Range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    if isinstance(high, pd.Series):
        high = pl.from_pandas(high)
        low = pl.from_pandas(low)
        close = pl.from_pandas(close)
    else:
        high = pl.Series(high)
        low = pl.Series(low)
        close = pl.Series(close)
    df = pl.DataFrame()
    df = df.with_columns(high_low=high - low, high_close=high -
                         close.shift(1).abs(), low_close=low - close.shift(1).abs())

    df = df.with_columns(pl.max([pl.col("high_low"), pl.col(
        "high_close"), pl.col("low_close")]).alias("tr"))
    return df.select(pl.col("tr")).to_series()

# calculate average true range


def Average_True_Range(high: pd.Series, low: pd.Series, close: pd.Series, period=7) -> pd.Series:
    tr = True_Range(high, low, close)
    atr = tr.ewm_mean(alpha=1/period, adjust=False)
    return atr


def SuperTrend(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 7, multiplier: int = 2) -> (pd.Series, pd.Series):
    high = pl.from_pandas(high)
    low = pl.from_pandas(low)
    atr = Average_True_Range(high, low, close, period)
    avg = (high + low)/2
    mult = multiplier * atr
    red = avg + mult
    green = avg - mult
    return red, green


def SMA(series: pd.Series, period: int) -> pd.Series:
    return pl.from_pandas(series).rolling_mean(window_size=period).to_pandas()

df = pd.read_csv("data/tata.csv")

high = df['high']
low = df['low']
close = df['close']

atr = SuperTrend(high, low, close)

print(atr)
