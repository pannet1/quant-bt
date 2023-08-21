import polars as pl
import pandas as pd
import os
import finplot as fplt



##############################################################################################################
class gtf:
    def __init__(self) -> None:
        ## dataframes
        self._htf = None
        self._itf = None
        self._ltf = None

        ## file names
        self._demand_file_name = None
        self._supply_file_name = None

##############################################################################################################
    def set_data(self, trading_purpose, symbol) -> None:
        #####################################################################
        #####
        ##### multiple timeframe analysis
        #####################################################################
        ##                      higher timeframe            intermediate        lower timeframe
        ## trading purpose      location/curve/tradig       trending            execuion timeframe
        
        ## hourly income        60/75 mins                  15 mins             5 mins
        ## dayli income         daily                       60/75 mins          15 mins
        ## weekly income        weekly                      daily               60/75/125/240 mins
        ## monthly income       monthly                     weekly              daily
        ## quarterly incom      quartely                    monthly             weekly
        ## half yearly income   half yearly                 quarterly           monthly
        ## yearly income        yearly                      half yearly         quartely
        
        ## higher timeframe         ---> used to identify supply and demand zones 
        ## intermediate timeframe   ---> used for
        ## lower timeframe          ---> used for

        if trading_purpose == "hourly" or trading_purpose == "h":
            self._hourly(symbol=symbol)
            
        elif trading_purpose == "daily" or trading_purpose == "d":
            self._daily(symbol=symbol)

        elif trading_purpose == "weekly" or trading_purpose == "w":
            self.__weekly()

        elif trading_purpose == "monthly" or trading_purpose == "m":
            self._monthly()

        elif trading_purpose == "quarterly" or trading_purpose == "q" or trading_purpose == "3m":
            self._quarterly()

        elif trading_purpose == "half yearly" or trading_purpose == "hy" or trading_purpose == "6m":
            self._half_yearly()

        elif trading_purpose == "yearly" or trading_purpose == "y" or trading_purpose == "y":
            self._yearly()

##############################################################################################################
    def _hourly(self, symbol) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "60/75 mins"
        ##### itf = "15 mins"
        ##### ltf = "5 mins"
        #####################################################################
        htf = f"data/{symbol}/{symbol}_60min.csv"
        itf = f"data/{symbol}/{symbol}_15min.csv"
        ltf = f"data/{symbol}/{symbol}_5min.csv"
        
        self._set_file_folders(htf, itf, ltf)   ## set self._htf, self_.itf, self._ltf accordingly
        self._demand_file_name = f"data/{symbol}/{symbol}_hourly_demand.csv"
        self._supply_file_name = f"data/{symbol}/{symbol}_hourly_supply.csv"
##############################################################################################################        
    def _daily(self, symbol) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "daily"
        ##### itf = "60/75 mins"
        ##### ltf = "15 mins"
        #####################################################################
        htf = f"data/{symbol}/{symbol}_daily.csv"
        itf = f"data/{symbol}/{symbol}_60min.csv"
        ltf = f"data/{symbol}/{symbol}_15min.csv"
        
        self._set_file_folders(htf, itf, ltf)   ## set self._htf, self_.itf, self._ltf accordingly
        self._demand_file_name = f"data/{symbol}/{symbol}_daily_demand.csv"
        self._supply_file_name = f"data/{symbol}/{symbol}_daily_supply.csv"
##############################################################################################################    
    def _weekly(self) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "weekly"
        ##### itf = "daily"
        ##### ltf = "60/75/125/240 mins"
        #####################################################################
        pass

##############################################################################################################
    def _monthly(self) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "monthly"
        ##### itf = "weekly"
        ##### ltf = "daily"
        #####################################################################
        pass

##############################################################################################################        
    def _quarterly(self) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "quartely"
        ##### itf = "monthly"
        ##### ltf = "weekly"
        #####################################################################
        pass

##############################################################################################################
    def _half_yearly(self) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "half yearly"
        ##### itf = "quartely"
        ##### ltf = "monthly"
        #####################################################################
        pass

##############################################################################################################
    def _yearly(self) -> None:
        #####################################################################
        #####
        ##### check if these files are present in folder data/symbol/
        ##### htf = "yearly"
        ##### itf = "half yearly"
        ##### ltf = "quartely"
        #####################################################################
        pass

##############################################################################################################
    def _set_file_folders (self, _htf, _itf, _ltf) -> None:
        #####################################################################
        ## set
        ## higher timeframe or 
        ## location/curve/tradig
        #####################################################################
        if os.path.exists(_htf):
            self._htf = self._set_gtf_dataframe(_htf)
        else:
            exit(f"404 file not found {_htf}")

        #####################################################################
        ## set
        ## intermediate timeframe or 
        ## trending timeframe
        #####################################################################
        if os.path.exists(_itf):
            self._itf = self._set_other_df(_itf)
        else:
            exit(f"404 file not found {_itf}")

        #####################################################################
        ## set
        ## lower timeframe or 
        ## execuion timeframe
        #####################################################################
        if os.path.exists(_ltf):
            self._ltf = self._set_other_df(_ltf)
        else:
            exit(f"404 file not found {_ltf}")

##############################################################################################################
    def _set_gtf_dataframe(self, file_name) -> pl.DataFrame:
        ##################################################################
        #### date manupulation
        #### higher timeframe or location/curve/tradig
        ##################################################################
        ## read csv file
        df = pl.read_csv(file_name)
        ## convert to datetime
        df =(df.with_columns(pl.col('date').str.strptime(pl.Datetime)))
        ## convert to indian time
        df=(df.with_columns((pl.col('date').dt.convert_time_zone(time_zone="Asia/Kolkata"))))
        
        ## add index as unix_time name
        df = df.with_columns(pl.col("date").dt.epoch(time_unit="s").alias("unix_time"))
        df = df.drop("date")    ## drop date as it no longer required

        ## calculate rolling mean / simple moving average / SMA for 50 days
        df = df.with_columns(pl.col("close").rolling_mean(window_size=50).alias("sma50"))

        ## set SMA50 color
        df =( df
                .with_columns
                (
                    pl.when(pl.col("sma50").gt(pl.col("close")))
                    .then("red")
                    .otherwise("green")
                    .alias("sma50clr")
                )
            )
        ##################################################################
        ##### set dataframe for polars
        ##### used internally by this class
        ##### gtf specific setup
        ##################################################################
        df = df.drop(columns=["volume"])    ## drop column as not used any where

        ## set id2 for reference only
        df = df.with_row_count(name="id2")
        '''
        ## set current market price
        df =(
              df
              .with_columns
              (
                  pl.when(pl.col("open").gt(pl.col("close")))
                    .then(pl.col("open"))
                    .otherwise(pl.col("close"))
                    .alias("cmp")
              )
            )
        '''
        ## for gtf specific things
        df =( 
              df
                .with_columns
                (   
                    ## calculate body
                    (abs((pl.col('open') - pl.col('close'))).alias('body')),
                    ## calculate candle range
                    (pl.col('high') - pl.col('low')).alias('cdl_range')
                )
                ##  caclulate candle type
                .with_columns
                    (
                        pl.when(pl.col('open').gt(pl.col('close')))
                            .then(
                                    pl.when
                                        (
                                            pl.col('body').gt(0.5 * pl.col('cdl_range'))
                                        )
                                      .then('ERC')
                                      .otherwise('BR')
                                )
                            .otherwise(
                                        pl.when
                                            (
                                                pl.col('body').gt(0.5 * pl.col('cdl_range'))
                                            )
                                           .then('EGC')
                                           .otherwise('BG')
                                    )
                            .alias('cdl_type')
                        )
                    )
        
        ## filter exciting candles
        self.exciting_candles =(
                                 df
                                 .filter
                                 (
                                    pl.col("cdl_type").eq("ERC")
                                    .or_(pl.col("cdl_type").eq("EGC"))
                                 )
                                )
        
        ## find which is greater open or close
        ## demand zone
        df =(
             df
             .with_columns
             (
                pl.when(pl.col("open").gt(pl.col("close")))
                .then(pl.col("open"))
                .otherwise(pl.col("close"))
                .alias("body_high")
             )
            )
        
        ## find which is lower open or close
        ## demand zone
        df =(
             df
             .with_columns
             (
                pl.when(pl.col("open").lt(pl.col("close")))
                .then(pl.col("open"))
                .otherwise(pl.col("close"))
                .alias("body_low")
             )
            )
        return df
       
##############################################################################################################    
    def _set_other_df(self, file_name) -> pl.DataFrame:
        ##################################################################
        #### date manupulation
        #### intermediate timeframe or trending timeframe
        ##################################################################
        df = pl.read_csv(file_name)  ## read csv file
        ## convert to datetime
        df =(df.with_columns(pl.col('date').str.strptime(pl.Datetime)))
        ## convert to indian time
        df=(df.with_columns((pl.col('date').dt.convert_time_zone(time_zone="Asia/Kolkata"))))

        ## add index as unix_time name
        df = df.with_columns(pl.col("date").dt.epoch(time_unit="s").alias("unix_time"))
        df = df.drop("date")    ## drop date as it no longer required

        ## set id2 for reference only
        df = df.with_row_count(name="id2")
        
        return df
##############################################################################################################    
    def demand_zone(self, cmp_idx):
        cmp_row = self._htf.filter(pl.col("unix_time").eq(cmp_idx))     ## filter row wher imp_idx is present
        cmp = cmp_row.item(0, "close")                                    ## current market price at close
        cmp_idx_temp = cmp_row.item(0, "id2")                           ## index as integer
        ##################################################################
        ####
        #### legout candle must be GREEN EXCITING CANDLE
        ##################################################################
        legout_candles = (self.exciting_candles
                          .select(["unix_time", "close", "cdl_type", "id2"])
                          .filter
                          (
                            pl.col("unix_time").le(cmp_idx).and_(pl.col("close").le(cmp))
                            .and_(pl.col("cdl_type").eq("EGC"))
                          )
                        )
        ## legout index
        last_legout_rows = legout_candles.tail(6)                        ## last 5 rows of legout_candles
        if len(last_legout_rows) <=0:                                    ## if legout_canldes is empty 
            return                                                       ## then exit loop
        else:

            legout_unix_time = last_legout_rows.item(0, "unix_time")     ## legout index as unix timestamp
            legout_id = last_legout_rows.item(0, "id2")                  ## legout index as interger

        ##################################################################
        ####
        #### legin candles
        ##################################################################
        legin_candles = (self.exciting_candles.filter(pl.col("unix_time").lt(legout_unix_time)))  ## filter legin candles befor legout index
        last_legin_row = legin_candles.tail(1)
        if len(last_legin_row) <=0:                                     ## if legin_candles is empty 
            return                                                      ## then exit loop
        else:                                                           ## otherwise
            legin_idx = last_legin_row.item(0, "unix_time")             ## legin index as unix timestamp
            lg_in = last_legin_row.item(0, "id2")                       ## legin index as integer
        
        length = legout_id - lg_in                                         ## used to slice dataframe between legin and legout
        if length <= 1:                                                 ## if there are no candles between legin and legout
            return                                                      ## exit loop
        
        ## if there are one or more candles between legin and legout
        sliced_df = self._htf.slice(lg_in, length=length)
        
        ## proximal line
        ## normal base candles
        proximal_value = sliced_df["body_high"].top_k(1).to_list()[0]
        proximal_row = sliced_df.filter(pl.col("body_high").eq(proximal_value))
        proximal_idx = proximal_row["unix_time"].to_list()[0]           ## highest body of all base candles
        ## distal line
        ## normal base candles
        distal_value = sliced_df["low"].bottom_k(1).to_list()[0]
        distal_row = sliced_df.filter(pl.col("low").eq(distal_value))
        distal_idx = distal_row["unix_time"].to_list()[0]                ## lowest wick/low of all base candles

        ##################################################################
        ####
        #### slice dataframe between current market price and lenght of datframe
        #### checking for tested or not
        ##################################################################
        length2 = len(self._htf) - cmp_idx_temp
        if length2 <=1:
            return
        else:
            sdf = self._htf.slice(cmp_idx_temp, length=length2)
            sdf = sdf.filter(pl.col("low").le(proximal_value))
            tested = len(sdf)
        ##################################################################
        ##
        ## set which pattern is found
        ##################################################################
        if self._htf.item(lg_in, "cdl_type") == "ERC":
            legin_ptrn = "D"
        else:
            legin_ptrn = "R"
        
        # pattern name
        pattern = f"{legin_ptrn}BR"

        yield cmp_idx, cmp, proximal_idx, proximal_value, distal_idx, distal_value, pattern, tested, legin_idx, legout_unix_time, lg_in, legout_id
    
##############################################################################################################
    def demand_to_csv(self) -> None:
        demand_dict={
                        "cmp_idx" : list(),
                        "cmp" : list(),
                        "proximal_idx" : list(),
                        "proximal_value" : list(),
                        "distal_idx" : list(),
                        "distal_value" : list(),
                        "pattern" : list(),
                        "legin_idx" : list(),
                        "legout_unix_time" : list(),
                        "tested" : list()
                    }
        ## run through higher timeframe all at once
        unix_time_stamps = self._htf.select(pl.col("unix_time")).to_series()

        for i in range(len(unix_time_stamps)-1, 0, -1):
            cmp_idx = unix_time_stamps[i]
            dem = self.demand_zone(cmp_idx)
            for d in dem:
                if d is not None:
                    demand_dict["cmp_idx"].append(d[0])
                    demand_dict["cmp"].append(d[1])
                    demand_dict["proximal_idx"].append(d[2])
                    demand_dict["proximal_value"].append(d[3])
                    demand_dict["distal_idx"].append(d[4])
                    demand_dict["distal_value"].append(d[5])
                    demand_dict["pattern"].append(d[6])
                    demand_dict["tested"].append(d[7])
                    demand_dict["legin_idx"].append(d[8])
                    demand_dict["legout_unix_time"].append(d[9])
        
        x = pl.DataFrame(demand_dict)   ## write dictonary to dataframe
        ## find duplicate items and keep first only
        x = x.unique(subset=["legin_idx", "legout_unix_time"], keep="first", maintain_order=True)
        
        x = x.filter(pl.col("tested") <=1)  ## filter non tested deman zones only

        x.write_csv(self._demand_file_name, has_header=True) ## write to csv file
##############################################################################################################
    
##############################################################################################################
    def get_df(self) -> pd.DataFrame:
        df = self._htf.drop(["id2", "cdl_range", "cdl_type", "body_high" ,"body"])
        df = df.to_pandas()
        df = df.set_index("unix_time")
        return df
    
##############################################################################################################
    def gtf_show(self):

        self.demand_to_csv()    ## create demand zone csv
        #self.supply_to_csv()    ## create supply zone csv
        df_htf = self.get_df()      ## set higher timeframe dataframe

        ##################################################################    
        #### configure color schemes 
        #### must set befor create_plot otherwise dont work
        ##################################################################
        fplt.background = "black"
        fplt.foreground = "white"
        fplt.cross_hair_color = "white"
        fplt.candle_shadow_width = 2
        
        ax= fplt.create_plot("CandleStcks --> prices", init_zoom_periods=50)

        ################################################################################
        ## candlesticks chart in ax
        ################################################################################
        price = df_htf['open close high low'.split()]
        price_plot = fplt.candlestick_ochl(price, ax=0)
        # update default color hex colors for each color
        price_plot.colors.update(dict(bull_body="black", bull_shadow="green", bull_frame="green",
                                bear_body="black", bear_shadow="red", bear_frame="red"))
        ################################################################################
        #### read demand zone csv
        ################################################################################
        df2 = pd.read_csv(self._demand_file_name)
        for idx in range(len(df2)):
            distal_idx= df2["distal_idx"][idx]
            distal_value=  df2["distal_value"][idx]
            legin_idx = df2["legin_idx"][idx]
            legout_unix_time = df2["legout_unix_time"][idx]

            # legin
            fplt.add_text((legin_idx, df_htf['low'][legin_idx]), s="legin", color="white")
            # legout
            fplt.add_text((legout_unix_time, df_htf['high'][legout_unix_time]), s="legout", color="white")
            ## distal line
            fplt.add_line((distal_idx, distal_value), (df_htf.index[len(df_htf)-1], distal_value), color="blue", style="....", width=2)

        fplt.plot(df_htf["sma50"], legend="sma50", width=2)
        '''
        ### SMA50 line colored
        for i in range(len(df_htf)):
            j = i +1
            if j == len(df_htf):
                break
            else:
                fplt.add_line((df_htf.index[i], df_htf['sma50'][df_htf.index[i]]), (df_htf.index[j], df_htf["sma50"][df_htf.index[j]]), color=df_htf["sma50clr"][df_htf.index[j]], width=2)
        '''
        fplt.show()

##############################################################################################################

g = gtf()
g.set_data("daily", "tata")

g.gtf_show()


