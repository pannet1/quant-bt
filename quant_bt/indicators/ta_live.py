import polars as pl
from streamer import Streamer
import time

##########################################################################################################################
class Ta:
    def __init__(self):
        self.df_tmp = pl.DataFrame()
        #self.df = pl.DataFrame()
    ##########################################################################################################################
    def Pre_Calculations(self, df:pl.DataFrame, drop_date:bool = False):
        df =(
                df
                .with_columns
                (
                    pl.col('date').str.strptime(pl.Datetime).dt.convert_time_zone(time_zone="Asia/Kolkata")
                )
                .with_columns
                (
                    pl.col('date').dt.epoch(time_unit="s").alias("unix")
                )
            )
        if drop_date:
            df = df.drop('date')
        return df
    ##########################################################################################################################
    def SMA(self, df, window, live=False):
        if not live:
            pre_calc = self.Pre_Calculations(df=df)         ## precalculate something
            return self._SMA(df=pre_calc, window=window)
        
        ## for live trading only
        pre_calc = self.Pre_Calculations(df=df)
        self.df_tmp = pl.concat([self.df_tmp, pre_calc])    ## precalculate something
        if self.df_tmp.height < window:
            return None                                     ## return None if self.df_tmp.height < window
        ## else
        tmp = self.df_tmp.slice(-window)
        sma = self._SMA(df=tmp, window=window)
        ## concat to main df
        self.df = pl.concat([self.df, sma.slice(-1)])
        return self.df
    ##########################################################################################################################
    def _SMA(self, df, window):
        sma_name = f"sma{window}"
        df = df.with_columns(pl.col('close').rolling_mean(window).alias(sma_name))
        return df
    
    ##########################################################################################################################
    def RSI(self, df, window:int = 14, live=False):
        if not live:
            pre_calc = self.Pre_Calculations(df=df)         ## precalculate something
            return self._RSI(df=pre_calc, window=window)
        
        ## for live trading only
        pre_calc = self.Pre_Calculations(df=df)
        self.df_tmp = pl.concat([self.df_tmp, pre_calc])    ## precalculate something
        if self.df_tmp.height < window:
            return None                                     ## return None if self.df_tmp.height < window
        ## else
        tmp = self.df_tmp.slice(-window)
        rsi = self._RSI(df=tmp, window=window)
        '''
        ## concat to main df
        self.df = pl.concat([self.df, rsi.slice(-1)])
        return self.df
        '''
        return rsi.slice(-1)
    ##########################################################################################################################
    def _RSI(self, df, window:int=14):
        ## for live trading only
        cols = ['gain', 'loss', 'avg_gain', 'diff', 'avg_loss', 'rsi']
        for col in cols:
            if col in df.columns:
                df = df.drop(col)
        
        df =(
                df
                .with_columns(pl.col("close").diff(n=1).alias("diff"))
                .with_columns(
                    pl.when(pl.col('diff').gt(0))
                    .then(pl.col("diff"))
                    .otherwise(0)
                    .alias("gain")
                )
                .with_columns(
                    pl.when(pl.col('diff').lt(0))
                    .then(pl.col("diff").abs())
                    .otherwise(0)
                    .alias("loss")
                )
                .with_columns
                (
                    pl.col("gain").rolling_mean(window_size=window).alias("avg_gain")
                )
                .with_columns
                (
                    pl.col("loss").rolling_mean(window_size=window).alias("avg_loss")
                )
                .with_columns(
                (
                    (100 * pl.col("avg_gain")) / (pl.col("avg_gain") + pl.col("avg_loss"))).alias("rsi")
                )
            )
        df = df.drop(['gain', 'loss', 'avg_gain', 'diff', 'avg_loss'])
        return df
    
    ##########################################################################################################################
    def ATR(self, df, window):
        '''
        calculate true range
        '''
        ## for live trading only
        if 'tr' in df.columns:
            df = df.drop('tr')
        
        df = (
                    df
                    .with_columns
                    (
                        high_low = (pl.col('high') - pl.col('low')),
                        high_close = (pl.col('high') - pl.col('close').shift(n=1)).abs(),
                        low_close =  (pl.col('low') - pl.col('close').shift(n=1)).abs()
                    )
        )
        
        df =(
                    df
                    .with_columns
                    (
                        pl.max_horizontal("high_low", "high_close", "low_close").alias('tr')
                    )
        )

        df = df.with_columns(pl.col('tr').ewm_mean(alpha=1/window, adjust=False).alias('atr'))
        return df

    ##########################################################################################################################
    def ADX(self, df, window, live=False):
        if not live:
            pre_calc = self.Pre_Calculations(df=df)         ## precalculate something
            return self._ADX(df=pre_calc, window=window)
        
  
        pre_calc = self.Pre_Calculations(df=df)
        self.df_tmp = pl.concat([self.df_tmp, pre_calc])    ## precalculate something
        if self.df_tmp.height < window+1:
            return None                                     ## return None if self.df_tmp.height < window
        ## else
        tmp = self.df_tmp.slice(-(window+1))
        adx = self._ADX(df=tmp, window=window)
        '''
        ## concat to main df
        self.df = pl.concat([self.df, adx.slice(-1)])
        return self.df
        '''
        return adx.slice(-1)
    ##########################################################################################################################
    def _ADX(self, df, window):
        '''
        average directional index
        '''
        df = self.ATR(df=df, window=window)
        
        df = (
                    df
                    .with_columns
                    (
                        (pl.col('high').shift(1).alias('p_high')),
                        (pl.col('low').shift(1).alias('p_low'))
                    )
                )
        ## positive directional movement
        df = (
                    df
                    .with_columns
                    (
                        pl.when((pl.col('high') - pl.col('p_high')) > (pl.col('p_low') - pl.col('low')) )
                            .then(pl.col('high') - pl.col('p_high'))
                            .otherwise(pl.lit(0))
                            .alias('pos_dm')
                    )
                )
        ## negative directional movement
        df = (
                    df
                    .with_columns
                    (
                        pl.when(((pl.col('p_low') - pl.col('low')) > pl.col('high') - pl.col('p_high')) )
                            .then(pl.col('p_low') - pl.col('low'))
                            .otherwise(pl.lit(0))
                            .alias('neg_dm')
                    )
                )
        ## smoothed +md and -ve dm
        df = (
                    df
                    .with_columns
                    (
                        ((pl.col('pos_dm').ewm_mean(alpha=1/window, adjust=False) * 100 / (pl.col('tr'))).alias('pos_dm')),
                        ((pl.col('neg_dm').ewm_mean(alpha=1/window, adjust=False) * 100 / (pl.col('tr'))).alias('neg_dm'))
                    )
                )
        ## Directional Movement Index
        df = (
                    df
                    .with_columns
                    (
                        ((pl.col('pos_dm') - pl.col('neg_dm')) * 100 / (pl.col('pos_dm') + pl.col('neg_dm'))).abs().alias('dxi')
                    )
                )
        
        ## ADX
        df = (
                df
                .with_columns
                (
                    pl.col('dxi').rolling_mean(window).alias('adx')
                )
            )
        df = df.drop(['pos_dm', 'neg_dm', 'dxi', 'p_high', 'p_low', 'low_close', 'high_low', 'high_close', 'tr', 'atr'])
        return df
    
    ##########################################################################################################################
    def CROSS_OVER_Golden_Death(self, df, short_window:int=50, long_window:int=200, live=False):
        if not live:
            pre_calc = self.Pre_Calculations(df=df)         ## precalculate something
            return self._CROSS_OVER_Golden_Death(df=tmp, short_window=short_window, long_window=long_window)
  
        pre_calc = self.Pre_Calculations(df=df)
        self.df_tmp = pl.concat([self.df_tmp, pre_calc])    ## precalculate something
        if self.df_tmp.height < long_window+1:
            return None                                     ## return None if self.df_tmp.height < window
        ## else
        tmp = self.df_tmp.slice(-(long_window + 1))
        cross_over = self._CROSS_OVER_Golden_Death(df=tmp, short_window=short_window, long_window=long_window)
        '''
        ## concat to main df
        self.df = pl.concat([self.df, cross_over.slice(-1)])
        return self.df
        '''
        return cross_over.slice(-1)
    ##########################################################################################################################
    def _CROSS_OVER_Golden_Death(self,df, short_window, long_window):
        '''
        golden cross over and death cross over
        '''
        s_sma = f"sma_{short_window}"
        l_sma = f"sma_{long_window}"
        s_sma1 = f"{s_sma}_p"
        l_sma1 = f"{l_sma}_p"

        ## calculate simple moving averages
        df = (
                    df
                    .with_columns
                    (
                        ## sma short_window
                        pl.col('close').rolling_mean(window_size=short_window).alias(s_sma),
                        ## sma long_window
                        pl.col('close').rolling_mean(window_size=long_window).alias(l_sma)
                    )
                )
        ## shift sma50 and sma200
        df = (
                    df
                    .with_columns
                    (
                        pl.col(s_sma).shift(1).alias(s_sma1),
                        pl.col(l_sma).shift(1).alias(l_sma1)                    
                    )
                )

        ## calulate golden and death cross overs
        df = (
                    df
                    .with_columns
                    (
                        pl.when((pl.col(s_sma) < pl.col(l_sma)) & (pl.col(s_sma1) >= pl.col(l_sma)))
                        .then(True)
                        .alias('gco'),

                        pl.when((pl.col(s_sma) > pl.col(l_sma)) & (pl.col(s_sma1) <= pl.col(l_sma)))
                        .then(True)
                        .alias('dco')
                    )
                )
        df = df.drop([s_sma, l_sma, s_sma1, l_sma1])
        '''
        GCO = df.select(['unix', 'close', 'GCO']).filter(pl.col('GCO').eq(True))
        GCO = GCO.with_columns(pl.col('unix').dt.epoch(time_unit="s").alias("unix"))

        DCO = df.select(['unix', 'close', 'DCO']).filter(pl.col('DCO').eq(True))
        DCO = DCO.with_columns(pl.col('unix').dt.epoch(time_unit="s").alias("unix"))
        '''
        return df
    ##########################################################################################################################
    
    


