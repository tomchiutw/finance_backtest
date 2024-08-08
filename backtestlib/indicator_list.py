# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 18:28:58 2024

@author: user
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import ta
# import self module
import backtestlib.commodity as bc
import generallib.general as gg
import generallib.plot as gp
import backtestlib.performance as bp
import backtestlib.account as ba
import backtestlib.order as bo
import folderlib.folder as ff
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import backtestlib.marketdata as bm
import backtestlib.kline as bk


class Indicator:
    def __init__(self,name,marketdata,interval,indicator_var_dict=dict()):
        self.name=name
        self.marketdata=marketdata
        self.interval=interval
        self.data=pd.DataFrame()
        self.indicator_var_dict=indicator_var_dict
        self.__init__attr()
    
    def __init__attr(self):
        if hasattr(self,self.name):
            getattr(self,self.name)()
        else:
            raise ValueError(f"No method found for the indicator: {self.name}. Please create in indicator_list.py")
            
    # indicator_list
    def Days_To_Next_Settlement_Dates(self):
        marketdata = self.marketdata
        interval = self.interval
        settlement_dates_list = self.indicator_var_dict['settlement_dates_list']
        settlement_dates = pd.to_datetime(settlement_dates_list).date
    
        self.data['Days_To_Next_Settlement_Dates'] = np.nan
        
        if marketdata.data[interval].index[0].date()+ pd.Timedelta(days=60) < settlement_dates.min() or marketdata.data[interval].index[-1].date() > settlement_dates.max():
            raise ValueError(f'Please update settlement dates of {self.marketdata.symbol}')
        
        
        for i in range(len(settlement_dates)-1):
            start = settlement_dates[i]+ pd.Timedelta(days=1)
            end = settlement_dates[i+1] 
            
            trading_days = marketdata.data[interval].loc[start:end].index
            

            if len(trading_days) == 0:
                continue
            # if marketdata.data[interval].index[-1], then append first
            if trading_days[-1] == marketdata.data[interval].index[-1]:
                append_trading_days = pd.date_range(start=trading_days[-1], end=end, freq='B')
                trading_days = trading_days.append(append_trading_days[1:])
                
            
            last_date = None
            days_to_end = 0
            for idx in sorted(trading_days, key=lambda x: x.date(), reverse=True):
                current_date = idx.date()
                if last_date is None or current_date != last_date:
                    last_date = current_date
                    self.data.loc[idx, 'Days_To_Next_Settlement_Dates'] = days_to_end
                    days_to_end += 1
            
            
            # if marketdata.data[interval].index[-1], then drop append
            if 'append_trading_days' in locals():
                self.data = self.data.drop(append_trading_days[1:])
        self.data = self.data.sort_index()  # 确保数据按索引排序


        
        
    
    def High_Percent(self):
        
        marketdata=self.marketdata
        interval=self.interval
        
        df=marketdata.data[interval]
        for i in range(len(df)):
            # time_index in i 
            time_index=df.index[i]
            # other time_index located by loc
            loc = df.index.get_loc(time_index)
            time_index_previous_list=[j for j in range(1)]
            for p in time_index_previous_list:
                if loc-p<=0:
                    self.data.loc[time_index,'High_Percent']=np.nan
                else:
                    # value
                    high_value=df.loc[time_index,'High']
                    close_value_p1=df.loc[df.index[loc-1],'Close']
                    # indicator
                    self.data.loc[time_index,'High_Percent']=(high_value-close_value_p1)/close_value_p1 
                    
    def Low_Percent(self):
        
        marketdata=self.marketdata
        interval=self.interval
        
        df=marketdata.data[interval]
        for i in range(len(df)):
            # time_index in i 
            time_index=df.index[i]
            # other time_index located by loc
            loc = df.index.get_loc(time_index)
            time_index_previous_list=[i for i in range(1)]
            for p in time_index_previous_list:
                if loc-p<=0:
                    self.data.loc[time_index,self.name]=np.nan
                else:
                    # value
                    low_value=df.loc[time_index,'Low']
                    close_value_p1=df.loc[df.index[loc-1],'Close']
                    # indicator
                    self.data.loc[time_index,'Low_Percent']=(low_value-close_value_p1)/close_value_p1
    
    def SMA(self):
        pass
        
        
    
    def Double_SMA(self):
        
        try:
            short_SMA_length=self.indicator_var_dict['short_SMA_length']
            long_SMA_length=self.indicator_var_dict['long_SMA_length']
        except KeyError as e:
            raise ValueError(f'Missing in indicator_var_dict:{e}')
        
        # error
        if short_SMA_length<1:
            raise ValueError(f'error: short_SMA_length<1')
        elif long_SMA_length<1:
            raise ValueError(f'error: long_SMA_length<1')
        elif short_SMA_length>=long_SMA_length:
            raise ValueError(f'error: short_SMA_length>=long_SMA_length')
            
        marketdata_df=self.marketdata.data[self.interval]
        
        
        if 'Close' not in marketdata_df.columns:
            raise ValueError("Missing 'Close' column in marketdata dataframe")


        self.data['short_SMA'] = ta.trend.sma_indicator(marketdata_df['Close'], window=short_SMA_length)
        self.data['long_SMA'] = ta.trend.sma_indicator(marketdata_df['Close'], window=long_SMA_length)
        
        # if 'Close' in marketdata_df:
        #     self.indicator_var_dict
        
      
    