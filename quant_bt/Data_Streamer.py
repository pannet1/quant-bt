import polars as pl
import pandas as pd
from time import sleep

class Data_Streamer:
    def __init__(self) -> None:
        self.pl_df = pl.DataFrame()
        self.pd_df = pd.DataFrame()

    def Csv_Streamer(self, file_name, to_pandas = False, sleep_time = 0.1) -> pl.DataFrame:
        """
        params : file_name  -> csv file name
        params : to_pandas  -> 
                            dafault false -> retruns polars datframe \n
                            if set to True -> return pandas datframe
        params : sleep_time -> return values after this much time
                            -> default value is 0.1 
        """
        df = pl.read_csv(file_name)
        length = df.height

        ## read csv file one row at a time
        reader =  pl.read_csv_batched(file_name, batch_size=1)
        if to_pandas is True:
            for i in range(length):
                sleep(sleep_time)
                values = reader.next_batches(n=1)
                for vals in values:
                    ## return pandas datframe
                    yield vals.to_pandas()
        else:
            for i in range(length):
                sleep(sleep_time)
                values = reader.next_batches(n=1)
                for vals in values:
                    ## return polars datframe
                    yield vals

    def SMA(self, window:int) -> None:
        sma_col = f"sma{window}"
        self.pl_df =(
                      self.pl_df
                      .with_columns
                      (
                        pl.col("close").rolling_mean(window_size=window).alias(sma_col)
                      )
                    )
    def True_Range(self) -> None:
        high_low = pl.col("high") - pl.col("low")
        high_close = abs(pl.col("high") - pl.col("close").shift(1))
        low_close = abs(pl.col("low") - pl.col("close").shift(1))

        self.pl_df = self.pl_df.with_columns(high_low=high_low, high_close=high_close, low_close=low_close)
        self.pl_df = (
                        self.pl_df
                        .with_columns
                        (
                            pl.max([pl.col("high_low"), pl.col("high_close"), pl.col("low_close")]).alias("tr")
                        )
                     )

    def Average_True_Range(self, period:int =7) -> None:
        self.True_Range()
        self.pl_df = self.pl_df.with_columns(pl.col("tr").ewm_mean(alpha=1/period, adjust=False).alias("atr"))

    def SuperTrend(self, period:int =7, multiplier:int =2) -> None:
        self.Average_True_Range(period=period)
        self.pl_df= (
                        self.pl_df
                        .with_columns
                        (
                            ((pl.col("high") + pl.col("low"))/2).alias("avg")
                        )
                        .with_columns
                        (
                            ((pl.col("avg") + multiplier)).alias("red"),
                            ((pl.col("avg") - multiplier)).alias("green")
                        )
                    )

    def Main_Loop(self, file_name:str) -> None:
        temp_df = self.Csv_Streamer(file_name=file_name, sleep_time=0)  ## get streaming data here
        for df in temp_df:                                              ## this used as above function yields data
            df = df.drop(["date", "volume"])                            ## drop columns if you want
            self.pl_df = pl.concat([self.pl_df, df], how="diagonal")    ## concat old dataframe with new streading data
            
            ## call functions which u need
            #self.SuperTrend()
            self.SMA(20)
            self.SMA(50)

            print(self.pl_df)
