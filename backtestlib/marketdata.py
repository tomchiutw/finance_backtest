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
        This function is used for downloading data fromo yfinance and save to self.data[interval]
    
        Parameters:
            symbol(str): code of commodities
            interval(str): “1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo”
            start_date(datetime): 
            end_date(datetime): 
        Returns:
            asset_data(dataframe): dataframe, index=Datetime or Date,columns=[Open, High, Low, Close, Adj Close, Volume}
        '''
        self.check_interval(interval)
        # download data from yf to asset_data
        print(f'downloading {self.symbol}_{interval} data...')
        asset_data = yf.download(self.symbol, start=start_date, end=end_date, interval=interval)
        # remove timezone information
        if asset_data.index.name=='Datetime' and asset_data.index.tz is not None:
            asset_data.index = asset_data.index.tz_localize(None)

        
        return asset_data
    
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
        
        self.check_interval(interval)
        
        base_dir=gbd.get_base_dir()
        file_name=f"{self.symbol}_{self.contract}_{interval}{note}.xlsx"
        file_path=os.path.join(base_dir,'data',self.category,self.symbol,self.contract)
        full_path=os.path.join(file_path,file_name)
        
        if not os.path.exists(full_path):
            data_df=self.download_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
            self.save_downloaded_data_from_df(data_df,interval)
            
        else:
            data_df=self.get_data_from_xlsx(interval)
            data_df.index = pd.to_datetime(data_df.index)
            if pd.to_datetime(backtest_start_date)+timedelta(days=delayed_days) < data_df.index.min() or pd.to_datetime(backtest_end_date)-timedelta(days=delayed_days)> data_df.index.max() \
                or data_df.empty:
                data_df=self.download_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
                self.save_downloaded_data_from_df(data_df,interval)
            
        
        self.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)

        
    