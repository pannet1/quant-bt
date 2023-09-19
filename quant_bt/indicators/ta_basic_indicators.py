import polars as pl
import pandas as pd


def Con_Ser(series) -> pl.Series:
    if isinstance(series, pd.Series):
        return pl.from_pandas(series)
    else:
        return series

def SMA(series, period) -> pd.Series:
    """ Simple moving average - rolling mean in pandas lingo. Also known as 'MA'.
        The simple moving average (SMA) is the most basic of the moving averages used for trading. """
    return Con_Ser(series).rolling_mean(window_size=period)

def SMM(series, period) -> pd.Series:
    """ Simple moving median, an alternative to moving average. SMA, when used to estimate the underlying trend in a time series,
        is susceptible to rare events such as rapid shocks or other anomalies. A more robust estimate of the trend is the simple moving median over n time periods. """
    return Con_Ser(series).rolling_median(period)

def SSMA(series, period, adjust:bool = True) -> pd.Series:
    """ Smoothed simple moving average."""
    return Con_Ser(series).ewm_mean(alpha=1/period, ignore_nulls=False, min_periods=0, adjust=adjust)


def EMA(series, period, adjust:bool = True) -> pd.Series:
    """ Exponential Weighted Moving Average """
    return Con_Ser(series).ewm_mean(span=period, adjust=adjust)


def DEMA(series, period, adjust:bool = True) -> pd.Series:
    """ Double Exponential Moving Average"""
    df = pl.DataFrame()
    df =(
            df
            .with_columns(ema = EMA(series, period)) 
            .with_columns(dema = (2 * pl.col("ema")) - (pl.col("ema").ewm_mean(span=period, adjust=adjust)))
        )
    return df.select("dema")

def TEMA(series, period, adjust:bool = True) -> pd.Series:
    """ Triple exponential moving average """
    df = pl.DataFrame()
    df =(
            df
            .with_columns(ema1 = EMA(series, period))
            .with_columns(ema2 = EMA(pl.col("ema1"), period))
            .with_columns(ema3 = EMA(pl.col("ema2"), period))
            .with_columns(tema = (3 * pl.col("ema1")) - (3 * pl.col("ema2")) + pl.col("ema3"))
        )
    return df.select("tema")

def TRIX(series, period:int=18) -> pd.Series:
    """ The Triangular Moving Average (TRIMA) [also known as TMA] """
    df = pl.DataFrame()
    df =(
            df
            .with_columns(sma = SMA(series, period))
            .with_columns(trix = pl.col("sma").rolling_sum(window_size=period)/period)
    )
    return df.select("trix")



