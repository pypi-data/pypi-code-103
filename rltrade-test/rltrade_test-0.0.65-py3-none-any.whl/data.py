import time
import threading
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from stockstats import StockDataFrame as Sdf
from rltrade.ibkr import IBapi, api_connect,stock_contract,future_contract


class IBKRDownloader:

    def __init__(self,start_date,end_date,ticker_list,sec_types,exchanges,demo=True,symbol_type='stock'):
        self.start_date = ''.join(start_date.split('-'))
        self.end_date = ''.join(end_date.split('-'))
        self.ticker_list = ticker_list
        self.sec_types = sec_types
        self.exchanges = exchanges
        self.start_date_dt = datetime.strptime(self.start_date,"%Y%m%d")
        self.end_date_dt = datetime.strptime(self.end_date,"%Y%m%d")
        self.date_delta =  (self.end_date_dt-self.start_date_dt)
        self.days = self.date_delta.days
        self.years = int(self.days / 365)
        self.dates = pd.date_range(start=self.start_date_dt,
                                   end =self.end_date_dt,
                                   freq='2D')
        self.dates = [''.join(str(x).split('-'))[:8] for x in self.dates]
        self.demo = demo
        self.symbol_type=symbol_type
        self.cnt = 0
            
    def download_data(self,app:IBapi,id,ticker,sec,exchange):
        def run_loop():
                app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        duration = f"{self.years} Y" if self.years > 0 else f"{self.days} D"
        if self.symbol_type == 'stock':
            cnt = stock_contract(ticker,secType=sec,exchange=exchange)
        elif self.symbol_type == 'future':
            cnt = future_contract(ticker,secType=sec,exchange=exchange)
        app.reqHistoricalData(id,cnt,self.end_date+" 15:59:00 est",
                            duration,'1 day','TRADES',0,2,False,[])
        app.nextorderId += 1
        df = app.get_df()
        df['tic'] = ticker
        df['sec'] = sec
        df['exchange'] = exchange
        app.reset_df()
        return df

    def fetch_data(self):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            print("Trying to download: ",tic)
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            try:
                temp_df = self.download_data(app,i,tic,sec,exchange)
                df = df.append(temp_df)
            except:
                print("Not able to download",tic)
                not_downloaded.append(tic)
            time.sleep(10)
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df = df.reset_index()
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d')
        df["day"] = df["date"].dt.dayofweek
        df["date"] = df["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df = df.dropna().sort_values(by=["date", "tic"]).reset_index(drop=True)
        return df
    
    def download_min_data(self,app:IBapi,id,ticker,sec,exchange,end:str):
        def run_loop():
                app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        if self.symbol_type == 'stock':
            cnt = stock_contract(ticker,secType=sec,exchange=exchange)
        elif self.symbol_type == 'future':
            cnt = future_contract(ticker,secType=sec,exchange=exchange)
        app.reqMarketDataType(1)
        app.reqHistoricalData(id,cnt ,end+" 15:59:00 est",
                            "2 D",'1 min','TRADES',0,1,False,[])
        app.nextorderId += 1
        df = app.get_df()
        df['tic'] = ticker
        df['sec'] = sec
        df['exchange'] = exchange
        app.reset_df()
        return df
    
    def fetch_min_data(self):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            print("Trying to download: ",tic)
            sec = self.sec_types[i]
            exchange  = self.exchanges[i]
            for end in self.dates[1:]:
                self.cnt += 1
                try:
                    temp_df = self.download_min_data(app,self.cnt,tic,sec,exchange,end)
                    df = df.append(temp_df)
                except:
                    print("Not able to download",tic)
                    not_downloaded.append(tic)
                time.sleep(10)
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d  %H:%M:%S')
        df['time'] = df['date'].dt.time
        df = df[(df['time']>=datetime.strptime("09:30:00","%H:%M:%S").time()) 
                & (df['time']<=datetime.strptime("15:59:00","%H:%M:%S").time())]
        df.drop('time',inplace=True,axis=1)
        return df
    
    def download_todays_min_data(self,app:IBapi,id:int,ticker,sec,exchange,end:str,duration:str):
        def run_loop():
                app.run()
        thread = threading.Thread(target=run_loop,daemon=True)
        thread.start()
        while True:
            if isinstance(app.nextorderId, int):
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        if self.symbol_type == 'stock':
            cnt = stock_contract(ticker,secType=sec,exchange=exchange)
        elif self.symbol_type == 'future':
            cnt = future_contract(ticker,secType=sec,exchange=exchange)
        # app.reqMarketDataType(1)
        app.reqHistoricalData(id,cnt ,"",
                            duration,'1 min','TRADES',0,1,True,[])
        time.sleep(5)
        app.nextorderId += 1
        df = app.get_df()
        df['tic'] = ticker
        df['sec'] = sec
        df['exchange'] = exchange
        app.reset_df()
        return df
    
    def fetch_todays_min_data(self,end,duration):
        df = pd.DataFrame()
        not_downloaded = list()
        print("connecting to server...")
        app = api_connect(demo=self.demo)
        for i,tic in enumerate(self.ticker_list):
            self.cnt +=1
            sec = self.sec_types[i]
            exchange = self.exchanges[i]
            try:
                temp_df = self.download_todays_min_data(app,self.cnt,tic,sec,exchange,end,duration)
                df = df.append(temp_df)
            except:
                print("Not able to download",tic)
                not_downloaded.append(tic)   
        app.disconnect()
        time.sleep(5)
        if len(not_downloaded) > 0:
            print("IB was not able to download this ticker",not_downloaded)
        
        df["date"] = pd.to_datetime(df['date'],format='%Y%m%d  %H:%M:%S')
        df['time'] = df['date'].dt.time
        df = df[(df['time']>=datetime.strptime("09:30:00","%H:%M:%S").time()) 
                & (df['time']<=datetime.strptime("15:59:00","%H:%M:%S").time())]
        df.drop('time',inplace=True,axis=1)
        return df
    

class FeatureEngineer:
    """Provides methods for preprocessing the stock price data
    Attributes
    ----------
        stock_indicators : boolean
             stock indicators or not
        stock_indicator_list : list
            a list of technical indicator names (modified from neofinrl_config.py)
        turbulence : boolean
            use turbulence index or not
    Methods
    -------
    create_data()
        main method to do the feature engineering
    """
    
    def __init__(self,stock_indicator_list = [],
                   additional_indicators = [],
                   cov_matrix = False,
                   mode='daily'):
        self.stock_indicator_list = stock_indicator_list
        self.additional_indicators = additional_indicators
        self.indicators = self.stock_indicator_list + self.additional_indicators
        self.cov_matrix = cov_matrix
        self.mode = mode
    
    def create_data(self,df):
        df = self.clean_data(df)
        if self.cov_matrix:
            df = self.add_cov_matrix(df)

        if 'hurst_exp' in self.additional_indicators:
            df = self.add_hurst_exponent(df)
        
        if 'half_hour_time' in self.additional_indicators and self.mode=='min':
            df = self.add_half_hour_time(df)

        if 'vix_fix_1year' in self.additional_indicators:
            df = self.add_vix_fix(df,1)
        if 'sharpe_1year' in self.additional_indicators:
            df = self.add_sharpe(df,1)
        if 'sortino_1year' in self.additional_indicators:
            df = self.add_sortino(df,1)
        if 'calamar_1year' in self.additional_indicators:
            df = self.add_clamar(df,1)
        
        if 'vix_fix_3year' in self.additional_indicators:
            df = self.add_vix_fix(df,3)
        if 'sharpe_3year' in self.additional_indicators:
            df = self.add_sharpe(df,3)
        if 'sortino_3year' in self.additional_indicators:
            df = self.add_sortino(df,3)
        if 'calamar_3year' in self.additional_indicators:
            df = self.add_clamar(df,3)
        
        if 'vix_fix_5year' in self.additional_indicators:
            df = self.add_vix_fix(df,5)
        if 'sharpe_5year' in self.additional_indicators:
            df = self.add_sharpe(df,5)
        if 'sortino_5year' in self.additional_indicators:
            df = self.add_sortino(df,5)
        if 'calamar_5year' in self.additional_indicators:
            df = self.add_clamar(df,5)

        if len(self.stock_indicator_list)>0:
            df = self.add_stock_indicators(df)

        df.loc[:,self.indicators] = df[self.indicators].replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.sort_values(["date", "tic"], ignore_index=True)
        df.index = df["date"].factorize()[0]
        return df
    
    def time_series_split(self,df, start, end, target_date_col="date"):
        df = df.copy()
        data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
        data = data.sort_values([target_date_col, "tic"], ignore_index=True)
        data.index = data[target_date_col].factorize()[0]
        return data
        
    def train_test_split(self,df,train_period,test_period):
        df = self.create_data(df)
        train = self.time_series_split(df, start = train_period[0], end = train_period[1])
        test = self.time_series_split(df, start = test_period[0], end = test_period[1])
        return train,test
    
    def clean_data(self,data):
        df = data.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.drop_duplicates(subset=['date','tic'])
        df = df.reset_index(drop=True)
        df = self.skip_missing_dates(df)
        df = self.remove_corrupt_ticker(df)
        df.index = df.date.factorize()[0]
        return df
    
    def remove_corrupt_ticker(self,df:pd.DataFrame):
        a = df.groupby('tic')['close'].apply(lambda x:sum(x==0))
        invalid_ticker = a[a>0].index.tolist()
        df = df[~df['tic'].isin(invalid_ticker)]
        df = df.reset_index(drop=True)
        print("Tickers with corrupt Data",invalid_ticker)
        print("Remaining ticker",df.tic.unique().tolist())
        return df
    
    def skip_missing_dates(self,df:pd.DataFrame):
        n_ticker = df['tic'].nunique()
        a = df.groupby('date')['tic'].count()
        invalid_dates = a[a<n_ticker].index.tolist()
        df = df[~df['date'].isin(invalid_dates)]
        df = df.reset_index(drop=True)
        return df
    
    def add_half_hour_time(self,df:pd.DataFrame):
        df['half_hour_time'] = (df.groupby('tic')['date']
                                .transform(lambda x: x.max() - x.min())
                                .dt.ceil('30Min')
                                .dt.total_seconds()
                                .div(600)
                                .astype(int))
        return df
    
    def add_cov_matrix(self,df,lookback=252):
        df=df.sort_values(['date','tic'],ignore_index=True)
        df.index = df.date.factorize()[0]

        cov_list = []
        for i in range(lookback,len(df.index.unique())):
            data_lookback = df.loc[i-lookback:i,:]
            price_lookback=data_lookback.pivot_table(index = 'date',columns = 'tic', values = 'close')
            return_lookback = price_lookback.pct_change().dropna()
            return_lookback = return_lookback.replace([np.inf, -np.inf], np.nan)
            return_lookback = return_lookback.fillna(method="ffill").fillna(method="bfill")
            covs = return_lookback.cov().values 
            cov_list.append(covs)
        
        df_cov = pd.DataFrame({'date':df.date.unique()[lookback:],'cov_list':cov_list})
        df = df.merge(df_cov, on='date',how='left')
        df = df.sort_values(['date','tic']).reset_index(drop=True)
        return df
    
    def add_hurst_exponent(self,data,max_lag=20):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['hurst_exp'] = temp['close'].rolling(max_lag*2).apply(lambda x:self.get_hurst_exponent(x.values))
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'hurst_exp']], on=["tic", "date"], how="left")
        return df

    def get_hurst_exponent(self,time_series, max_lag=20):
        """Returns the Hurst Exponent of the time series"""
        lags = range(2, max_lag)

        # variances of the lagged differences
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]

        # calculate the slope of the log plot -> the Hurst Exponent
        reg = np.polyfit(np.log(lags), np.log(tau), 1)

        return reg[0]


    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['close'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def add_stock_indicators(self,data):
        df = data.copy()
        df = df.sort_values(by=["tic", "date"])
        stock = Sdf.retype(df.copy())
        unique_ticker = stock.tic.unique()
        for indicator in self.stock_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["date"] = df[df.tic == unique_ticker[i]][
                        "date"
                    ].to_list()
                    indicator_df = indicator_df.append(
                        temp_indicator, ignore_index=True
                    )
                except Exception as e:
                    print(e)
            df = df.merge(
                indicator_df[["tic", "date", indicator]], on=["tic", "date"], how="left")
        df = df.sort_values(by=["date", "tic"])
        return df

    def add_turbulence(self,data):
        """
        add turbulence index from a precalcualted dataframe
        :param data: (df) pandas dataframe
        :return: (df) pandas dataframe
        """
        df = data.copy()
        turbulence_index = self.calculate_turbulence(df)
        df = df.merge(turbulence_index, on="date")
        df = df.sort_values(["date", "tic"]).reset_index(drop=True)
        return df

    def calculate_turbulence(self, data):
        """calculate turbulence index based on dow 30"""
        # can add other market assets
        df = data.copy()
        df_price_pivot = df.pivot(index="date", columns="tic", values="close")
        # use returns to calculate turbulence
        df_price_pivot = df_price_pivot.pct_change()

        unique_date = df.date.unique()
        # start after a year
        start = 252
        turbulence_index = [0] * start
        # turbulence_index = [0]
        count = 0
        for i in range(start, len(unique_date)):
            current_price = df_price_pivot[df_price_pivot.index == unique_date[i]]
            # use one year rolling window to calcualte covariance
            hist_price = df_price_pivot[
                (df_price_pivot.index < unique_date[i])
                & (df_price_pivot.index >= unique_date[i - 252])
            ]
            # Drop tickers which has number missing values more than the "oldest" ticker
            filtered_hist_price = hist_price.iloc[
                hist_price.isna().sum().min() :
            ].dropna(axis=1)

            cov_temp = filtered_hist_price.cov()
            current_temp = current_price[[x for x in filtered_hist_price]] - np.mean(
                filtered_hist_price, axis=0
            )
            # cov_temp = hist_price.cov()
            # current_temp=(current_price - np.mean(hist_price,axis=0))

            temp = current_temp.values.dot(np.linalg.pinv(cov_temp)).dot(
                current_temp.values.T
            )
            if temp > 0:
                count += 1
                if count > 2:
                    turbulence_temp = temp[0][0]
                else:
                    # avoid large outlier because of the calculation just begins
                    turbulence_temp = 0
            else:
                turbulence_temp = 0
            turbulence_index.append(turbulence_temp)

        turbulence_index = pd.DataFrame(
            {"date": df_price_pivot.index, "turbulence": turbulence_index}
        )
        return turbulence_index


class DayTradeFeatureEngineer:
    def __init__(self,stock_indicator_list = [],
                   additional_indicators = []):
        self.stock_indicator_list = stock_indicator_list
        self.additional_indicators = additional_indicators
        self.indicators = self.stock_indicator_list + self.additional_indicators
    
    def create_data(self,df):
        df = self.clean_data(df)

        if 'hurst_exp' in self.additional_indicators:
            df = self.add_hurst_exponent(df)

        if 'vix_fix_1000' in self.additional_indicators:
            df = self.add_vix_fix(df,1)
        if 'vix_fix_3000' in self.additional_indicators:
            df = self.add_vix_fix(df,3)
        if 'vix_fix_5000' in self.additional_indicators:
            df = self.add_vix_fix(df,5)

        if 'sharpe_1000' in self.additional_indicators:
            df = self.add_sharpe(df,1)
        if 'sharpe_3000' in self.additional_indicators:
            df = self.add_sharpe(df,3)
        if 'sharpe_5000' in self.additional_indicators:
            df = self.add_sharpe(df,5)

        if 'sortino_1000' in self.additional_indicators:
            df = self.add_sortino(df,1)
        if 'sortino_3000' in self.additional_indicators:
            df = self.add_sortino(df,3)
        if 'sortino_5000' in self.additional_indicators:
            df = self.add_sortino(df,5)
        
        if 'calamar_1000' in self.additional_indicators:
            df = self.add_clamar(df,1)
        if 'calamar_3000' in self.additional_indicators:
            df = self.add_clamar(df,3)
        if 'calamar_5000' in self.additional_indicators:
            df = self.add_clamar(df,5)
       
        if len(self.stock_indicator_list)>0:
            df = self.add_stock_indicators(df)

        df.loc[:,self.indicators] = df[self.indicators].replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.sort_values(["tic","date"], ignore_index=True)
        df = df.reset_index(drop=True)
        return df
    
    def time_series_split(self,df, start, end, target_date_col="date"):
        df = df.copy()
        temp = df[target_date_col]
        start = pd.to_datetime(start,format="%Y-%m-%d")
        end = pd.to_datetime(end,format="%Y-%m-%d")
        data = df[(temp >= start) & (temp< end)]
        data = data.reset_index(drop=True)
        return data
        
    def train_test_split(self,df,train_period,test_period):
        df = self.create_data(df)
        train = self.time_series_split(df, start = train_period[0], end = train_period[1])
        test = self.time_series_split(df, start = test_period[0], end = test_period[1])
        return train,test
    
    def clean_data(self,data):
        df = data.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method="ffill").fillna(method="bfill")
        df = df.reset_index(drop=True)
        return df
    
    def add_hurst_exponent(self,data,max_lag=20):
        df = data.copy()
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['hurst_exp'] = temp['close'].rolling(max_lag*2).apply(lambda x:self.get_hurst_exponent(x.values))
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", 'hurst_exp']], on=["tic", "date"], how="left")
        return df

    def get_hurst_exponent(self,time_series, max_lag=20):
        lags = range(2, max_lag)
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        return reg[0]

    def add_sharpe(self,data,n):
        df = data.copy()
        n = n * 1000
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{n}'] = temp['daily_return'].rolling(n,min_periods=1).mean() / temp['daily_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{n}']], on=["tic", "date"], how="left")
        return df
    
    def add_sortino(self,data,n):
        df = data.copy()
        n = n * 1000
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True) 
            temp['daily_negative_return'] = temp['daily_return'] 
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{n}'] = temp['daily_negative_return'].rolling(n,min_periods=1).mean() / temp['daily_negative_return'].rolling(n,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{n}']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,n):
        df = data.copy()
        n = n* 1000
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['close'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{n}'] = temp['daily_return'].rolling(n,min_periods=1).mean()/temp['daily_drawndown'].rolling(n,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{n}']], on=["tic", "date"], how="left")
        return df
    
    def add_vix_fix(self,data,n):
        df = data.copy()
        n = n * 1000
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{n}'] = ((temp['close'].rolling(n,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(n,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{n}']], on=["tic", "date"], how="left")
        return df


    def add_stock_indicators(self,data):
        df = data.copy()
        df = df.sort_values(by=["tic", "date"])
        stock = Sdf.retype(df.copy())
        unique_ticker = stock.tic.unique()
        for indicator in self.stock_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["date"] = df[df.tic == unique_ticker[i]][
                        "date"
                    ].to_list()
                    indicator_df = indicator_df.append(
                        temp_indicator, ignore_index=True
                    )
                except Exception as e:
                    print(e)
            df = df.merge(
                indicator_df[["tic", "date", indicator]], on=["tic", "date"], how="left")
        df = df.sort_values(by=["tic", "date"])
        return df

   
def time_series_split(df, start, end, target_date_col="date"):
    """
    split the dataset into training or testing using date
    :param data: (df) pandas dataframe, start, end
    :return: (df) pandas dataframe
    """
    df = df.copy()
    data = df[(df[target_date_col] >= start) & (df[target_date_col] < end)]
    data = data.sort_values([target_date_col, "tic"], ignore_index=True)
    data.index = data[target_date_col].factorize()[0]
    return data


class YahooDownloader:
    """Provides methods for retrieving daily stock data from
    Yahoo Finance API
    Attributes
    ----------
        start_date : str
            start date of the data 
        end_date : str
            end date of the data 
        ticker_list : list
            a list of stock tickers
    Methods
    -------
    fetch_data()
        Fetches data from yahoo API
    """

    def __init__(self, start_date: str, end_date: str, ticker_list: list):

        self.start_date = start_date
        self.end_date = end_date
        self.ticker_list = ticker_list

    def fetch_data(self) -> pd.DataFrame:
        """Fetches data from Yahoo API
        Parameters
        ----------
        Returns
        -------
        `pd.DataFrame`
            7 columns: A date, open, high, low, close, volume and tick symbol
            for the specified stock ticker
        """
        # Download and save the data in a pandas DataFrame:
        data_df = pd.DataFrame()
        not_downloaded = list()
        for tic in self.ticker_list:
            print(tic)
            try:
                temp_df = yf.download(tic, start=self.start_date, end=self.end_date)
                temp_df["tic"] = tic
                data_df = data_df.append(temp_df)
            except:
                not_downloaded.append(tic)
        # reset the index, we want to use numbers as index instead of dates
        data_df = data_df.reset_index()
        if len(not_downloaded) > 0:
            print("Yahoo was not able to download this ticker",not_downloaded)
        try:
            # convert the column names to standardized names
            data_df.columns = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "adjcp",
                "volume",
                "tic",
            ]
            # use adjusted close price instead of close price
            data_df["close"] = data_df["adjcp"]
            # drop the adjusted close price column
            data_df = data_df.drop(labels="adjcp", axis=1)
        except NotImplementedError:
            print("the features are not supported currently")
        # create day of the week column (monday = 0)
        data_df["day"] = data_df["date"].dt.dayofweek
        # convert date to standard string format, easy to filter
        data_df["date"] = data_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)
        print("Shape of DataFrame: ", data_df.shape)

        data_df = data_df.sort_values(by=["date", "tic"]).reset_index(drop=True)

        return data_df