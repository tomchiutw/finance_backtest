# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 13:24:18 2024

@author: user
"""
import os
import yfinance as yf
import pandas as pd
import generallib.general as gg
import get_base_dir as gbd
from datetime import datetime, timedelta


# 應該要存在json 

class MarketData:
    
    def __init__(self,symbol,category,currency,contract,contract_size=1,exchange='',is_tradable=True,notes='',**kwargs):
        '''
        Initialize a MarketData object
        
        Parameters:
            symbol(str): 
            category(str): stock, index, future, option, bond, or currency_pair
            currency(str):
            contract(str):
            contract_size(str):
            exchange(str.optional): exchange
            is_tradable(bool,optional): whether this commodity is tradable
            notes(str,optional): 
        Keyword Arguments:
            margin_info(dict, optional): {'initial_margin':int}
        '''
        self.symbol=symbol
        self.category=category
        self.currency=currency
        self.contract=contract
        self.contract_size=contract_size
        self.exchange=exchange
        self.is_tradable=is_tradable
        self.notes=notes
        # different interval of data will save in the form of dict
        self.data={}
 
    def check_interval(self,interval):
        interval_list=['1m', '2m', '5m', '15m','30m','60m','90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if interval not in interval_list:
            raise ValueError(f'interval must be {interval_list} ')

    def download_data_from_yfinance(self,interval,start_date,end_date):
        '''
        This function is used for downloading data from yfinance and save to self.data[interval]
    
        Parameters:
            symbol(str): code of commodities
            interval(str): "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
            start_date(datetime): 
            end_date(datetime): 
        Returns:
            asset_data(dataframe): dataframe, index=Datetime or Date,columns=[Open, High, Low, Close, Adj Close, Volume}
        '''
        self.check_interval(interval)
        # download data from yf to asset_data
        print(f'downloading {self.symbol}_{interval} data...')
        
        try:
            # Method 1: Use Ticker.history() (Official recommended, more stable)
            ticker = yf.Ticker(self.symbol)
            asset_data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            # Check if download succeeded
            if asset_data.empty:
                print(f"WARNING: Ticker.history() returned empty data, trying yf.download()...")
                # Method 2: Use yf.download() (Fallback)
                asset_data = yf.download(
                    self.symbol, 
                    start=start_date, 
                    end=end_date, 
                    interval=interval,
                    progress=False
                )
            
            # Check again
            if asset_data.empty:
                raise ValueError(f"Downloaded data for {self.symbol} is empty. Please check the symbol and date range.")
            
            print(f"SUCCESS: Downloaded {len(asset_data)} rows of data")
            
            # remove timezone information
            if hasattr(asset_data.index, 'tz') and asset_data.index.tz is not None:
                asset_data.index = asset_data.index.tz_localize(None)
            
            # Ensure index is datetime type
            if not isinstance(asset_data.index, pd.DatetimeIndex):
                asset_data.index = pd.to_datetime(asset_data.index)
            
            return asset_data
            
        except Exception as e:
            error_msg = f"Failed to download {self.symbol}: {str(e)}"
            print(f"ERROR: {error_msg}")
            
            # Show suggested file path
            base_dir = gbd.get_base_dir()
            file_path = os.path.join(base_dir, 'data', self.category, self.symbol, self.contract)
            file_name = f"{self.symbol}_{self.contract}_{interval}.xlsx"
            full_path = os.path.join(file_path, file_name)
            
            print(f"\nSuggestions:")
            print(f"   1. Check your internet connection")
            print(f"   2. Verify symbol '{self.symbol}' is correct")
            print(f"   3. Try updating yfinance: pip install --upgrade yfinance")
            print(f"   4. Or manually download data and save to: {full_path}")
            
            raise ValueError(error_msg) from e
    
    def get_marketdata_saved_path_in_list(self):
        '''
        return sub_dir_name_list
        
        Returns:
            list: [data(default file name for saved market data),category,symbol,contract]
        '''
        return ['data',self.category,self.symbol,self.contract]
    
    def save_downloaded_data_from_df(self,data_df,interval,note=''):
        '''
        save data to file in type of xlsx

        Parameters:
            base_dir(str) : Base directory for path creation.
            interval(str): interval
            note(str,optional) : note after file name
        Returns:
            None
        '''
        self.check_interval(interval)
        
        base_dir=gbd.get_base_dir()
        file_name=f"{self.symbol}_{self.contract}_{interval}{note}.xlsx"
        file_path=os.path.join(base_dir,'data',self.category,self.symbol,self.contract)
        
        full_path=os.path.join(file_path,file_name)
        
        
        if os.path.exists(full_path):
            existing_df = pd.read_excel(full_path,index_col=0,engine='openpyxl')
            combined_df = data_df.combine_first(existing_df)
            gg.save_df_to_excel(combined_df,file_path,file_name)
        else:
            pass
            gg.save_df_to_excel(data_df,file_path,file_name)
        
    

    
    
    
    def get_marketdata_file_name(self,interval,note=''):
        file_name=self.symbol+"_"+self.contract+"_"+interval+note
        return file_name

    def save_data_to_parquet(self, data_df, interval, note=''):
        '''
        Save data to a Parquet file for faster I/O.

        Parameters:
            data_df (DataFrame): Data to save.
            interval (str): Data interval.
            note (str, optional): Optional note appended to the file name.
        '''
        self.check_interval(interval)
        base_dir = gbd.get_base_dir()
        file_name = f"{self.symbol}_{self.contract}_{interval}{note}.parquet"
        file_path = os.path.join(base_dir, 'data', self.category, self.symbol, self.contract)
        full_path = os.path.join(file_path, file_name)
        os.makedirs(file_path, exist_ok=True)
        if os.path.exists(full_path):
            existing_df = pd.read_parquet(full_path)
            combined_df = data_df.combine_first(existing_df)
            combined_df.to_parquet(full_path)
        else:
            data_df.to_parquet(full_path)

    def get_data_from_parquet(self, interval, start_date='', end_date='', note=''):
        '''
        Load data from a Parquet file.

        Parameters:
            interval (str): Data interval.
            start_date (datetime, optional): Filter start date.
            end_date (datetime, optional): Filter end date.
            note (str, optional): Optional note in the file name.

        Returns:
            DataFrame: Loaded market data.

        Raises:
            ValueError: If the Parquet file does not exist.
        '''
        self.check_interval(interval)
        base_dir = gbd.get_base_dir()
        file_name = f"{self.symbol}_{self.contract}_{interval}{note}.parquet"
        file_path = os.path.join(base_dir, 'data', self.category, self.symbol, self.contract)
        full_path = os.path.join(file_path, file_name)
        if not os.path.exists(full_path):
            raise ValueError(
                f"Parquet file not found: {full_path}\n"
                "Try MarketData.save_data_to_parquet() first."
            )
        df = pd.read_parquet(full_path)
        if start_date != '' and end_date != '':
            df = df[start_date:end_date]
        self.data[interval] = df
        return df

    def get_data_from_xlsx(self,interval,start_date='',end_date='',note=''):
        '''
        save xlsx data in specific interval and period to commodit.marketdata[contract].data[interval]
        and return dataframe

        Parameters:
            base_dir(str) : Base directory for path creation.
            interval(str): interval
            start_date(datetime): 
            end_date(datetime): 
            note(str,optional) : note after file name
        Returns:
            df(dataframe):
        ValueError:
            if file not exist, suggest user to use MarketData.download_data_from_yfinance(interval,start_date,end_date)
        '''
        self.check_interval(interval)
        
        base_dir=gbd.get_base_dir()
        file_name=f"{self.symbol}_{self.contract}_{interval}{note}.xlsx"
        file_path=os.path.join(base_dir,'data',self.category,self.symbol,self.contract)
        
        full_path=os.path.join(file_path,file_name)
        # check wether file exist
        if not os.path.exists(full_path):
            raise ValueError(f"file not exists: {full_path}\nTry to Use MarketData.download_data_from_yfinance(interval,start_date,end_date)")
        # get df 
        xls = pd.ExcelFile(full_path)
        df = pd.read_excel(xls,index_col=0)
        
        if start_date != '' and end_date != '':
            df=df[start_date:end_date]
        self.data[interval]=df
        
        return df
    
    def automatic_get_data_from_yfinance(self,interval,backtest_start_date,backtest_end_date,delayed_days=5,note=''):
        '''
        Automatically download data from yfinance if not exists or data range is insufficient
        
        Parameters:
            interval(str): data interval
            backtest_start_date(datetime): backtest start date
            backtest_end_date(datetime): backtest end date
            delayed_days(int): tolerance days for data range check
            note(str): optional note for file name
        '''
        self.check_interval(interval)
        
        base_dir=gbd.get_base_dir()
        file_name=f"{self.symbol}_{self.contract}_{interval}{note}.xlsx"
        file_path=os.path.join(base_dir,'data',self.category,self.symbol,self.contract)
        full_path=os.path.join(file_path,file_name)
        
        if not os.path.exists(full_path):
            print(f"File not found, downloading data...")
            data_df=self.download_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
            self.save_downloaded_data_from_df(data_df,interval)
            
        else:
            # print(f"File exists, checking data range...")
            data_df=self.get_data_from_xlsx(interval)
            data_df.index = pd.to_datetime(data_df.index)
            
            if pd.to_datetime(backtest_start_date)+timedelta(days=delayed_days) < data_df.index.min() or \
               pd.to_datetime(backtest_end_date)-timedelta(days=delayed_days) > data_df.index.max() or \
               data_df.empty:
                print(f"WARNING: Data range insufficient, re-downloading...")
                data_df=self.download_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
                self.save_downloaded_data_from_df(data_df,interval)
            else:
                # print(f"Data range is sufficient")
                pass
        
        self.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)