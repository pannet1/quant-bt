import polars as pl
import pandas as pd

def SMA(series: pd.Series, period: int) -> pd.Series:
    if isinstance(series, pd.Series):
        return pl.from_pandas(series).rolling_mean(window_size=period).to_pandas()
    elif isinstance(series, pl.Series):
        return series.rolling_mean(window_size=period)

##############################################################################################################
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

    df =(
            df
            .with_columns
            (
                high_low = high - low,
                high_close = (high - close.shift(1)).abs(),
                low_close = (low - close.shift(1)).abs()
            )
        )
    df = (
            df
            .with_columns
            (
                ## calculate max between high_low, high_close, low_close
                pl.max([pl.col("high_low"), pl.col("high_close"), pl.col("low_close")]).alias("tr")
            )
        )
    return df.select(pl.col("tr")).to_series()

##############################################################################################################
def Average_True_Range(high: pd.Series, low: pd.Series, close: pd.Series, period:int= 7, kind:str = None) -> pd.Series:
    if isinstance(high, pd.Series):
        high = pl.from_pandas(high)
        low = pl.from_pandas(low)
        close = pl.from_pandas(close)
    else:
        high = pl.Series(high)
        low = pl.Series(low)
        close = pl.Series(close)
    df = pl.DataFrame()

    df =(
            df
            .with_columns
            (
                high_low = high - low,
                high_close = (high - close.shift(1)).abs(),
                low_close = (low - close.shift(1)).abs()
            )
        )
    df = (
            df
            .with_columns
            (
                ## calculate max between high_low, high_close, low_close
                pl.max([pl.col("high_low"), pl.col("high_close"), pl.col("low_close")]).alias("tr")
            )
         )
    if kind == None or kind == "RMA":
        df= ( df
                .with_columns
                (   ## calculate average true range as RMA
                    pl.col("tr").ewm_mean(alpha=1/period, adjust=True, min_periods=period).alias("atr")
                )
            )
    elif kind == "SMA":
        df= ( df
                .with_columns
                (   ## calculate average true range as SMA
                    #(pl.col("tr").rolling_sum(window_size=period)/period).alias("atr_sma")
                    (pl.col("tr").rolling_sum(window_size=period)/period).alias("atr")
                )
            )
    return df.select("atr").to_series()

##############################################################################################################
def SuperTrend(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 7, multiplier: int = 3) -> pd.Series:
    if isinstance(high, pd.Series):
        high = pl.from_pandas(high)
        low = pl.from_pandas(low)
        close = pl.from_pandas(close)
    else:
        high = pl.Series(high)
        low = pl.Series(low)
        close = pl.Series(close)
    
    df = pl.DataFrame()
    atr = Average_True_Range(high, low, close, period)
    df =(
            df
            .with_columns
            (
                high = high,
                low = low,
                close = close,
                atr = atr
            )
            .with_columns
            (
                ((pl.col("high") + pl.col("low"))/2).alias("average")
            )
            .with_columns
            (
                ## basic upper band
                (pl.col("average") + (multiplier * pl.col("atr"))).alias("BUB"),
                ## basic lower band
                (pl.col("average") - (multiplier * pl.col("atr"))).alias("BLB")
            )
            .with_columns
            (
                ## final upper band
                pl.when
                    (
                        pl.col("BUB").lt(pl.col("BUB").shift(-1))
                        .or_(pl.col("close").shift(-1).gt(pl.col("BUB").shift(-1)))
                    )
                .then(pl.col("BUB"))
                .otherwise(pl.col("BUB").shift(-1))
                .alias("FUB"),
                
                ## final lower band
                pl.when
                    (
                        pl.col("BLB").gt(pl.col("BLB").shift(-1))
                        .or_(pl.col("close").shift(-1).lt(pl.col("BLB").shift(-1)))
                    )
                .then(pl.col("BLB"))
                .otherwise(pl.col("BLB").shift(-1))
                .alias("FLB")
            )
            .with_columns
            (
                ## supertrend
                pl.when
                    (
                        pl.col("close").le(pl.col("FUB"))
                    )
                .then(pl.col("FUB"))
                .otherwise(pl.col("FLB"))
                .alias("SuperTrend")
            )
        )
    return df.select("SuperTrend").to_series()
##############################################################################################################
