# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 22:28:51 2024

@author: user
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import copy
import ta
# import self module
import backtestlib.commodity as bc
from backtestlib.commodity import CommodityList
import generallib.general as gg
import generallib.line as gl
import generallib.plot as gp
import backtestlib.performance as bp
import backtestlib.optimizer as bop
import portfolio_optimizerlib.portfolio_optimizer as popo
import portfolio_optimizerlib.equity_series as pes
import backtestlib.account as ba
import backtestlib.order as bo
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import backtestlib.marketdata as bm
import backtestlib.kline as bk
import backtestlib.backtest as bb
import backtestlib.indicator_list as bil
import get_base_dir as gbd
script_dir=gbd.get_base_dir()

# get info
equityseries_info=pes.EquitySeriesDict.get_equityseries_info()
# data_info=pes.EquitySeriesDict.get_data_info(nums_to_load=[num for num in range(5)])
# nums_to_load=[info['num'] for info in equityseries_info['info'] if info['commodity']=='ETHUSD']
nums_to_load=[]
data_info=pes.EquitySeriesDict.get_data_info(nums_to_load=nums_to_load)

# changable_var_dict start
changable_var_dict=dict()
# commodity_prices_features
sma_length_list=[20,60,250]
filepath=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\equity_prices_features'
for filename in os.listdir(filepath):
    underscore_index=filename.find('_')
    if underscore_index!=-1:
        commodity_name=filename[:underscore_index]
        for item in data_info:
            if commodity_name==item['commodity'] :
                df=pd.read_csv(os.path.join(filepath,filename),index_col=0)
                df.index=pd.to_datetime(df.index)
                changable_var_dict.setdefault(f'close',dict())
                changable_var_dict['close'][commodity_name]=df[['BidClose']]
                for sma_length in sma_length_list:
                    sma_series=ta.trend.sma_indicator(df['BidClose'], window=sma_length).dropna()
                    changable_var_dict.setdefault(f'sma_{sma_length}',dict())
                    changable_var_dict[f'sma_{sma_length}'][commodity_name]=sma_series.to_frame()
                break
            
# trend,direction
changable_var_dict['trend']=dict()
changable_var_dict['direction']=dict()
changable_var_dict['corr']=dict()
# merge df
corr_summary=[]
corr_standard=0.3
i1,i2,i3,i4=0,0,0,0
for info in data_info:
    temp_corr_df=pd.DataFrame()
    commodity_name = info['commodity']
    num=info['num']
    if commodity_name in changable_var_dict['close'].keys():
        temp_corr_df=info['data'].copy()
        temp_corr_df['Close']=changable_var_dict['close'][info['commodity']]
        # corr_summary
        corr_df=gg.cor(temp_corr_df)
        corr_summary.append(corr_df.iloc[0,1])
        
        if corr_df.iloc[0,1]>=corr_standard:
            changable_var_dict['trend'][num]='follow'
            changable_var_dict['direction'][num]='long'
            changable_var_dict['corr'][num]=corr_df.iloc[0,1]
            i1+=1
        elif corr_df.iloc[0,1]>=0 and corr_df.iloc[0,1]<corr_standard:
            changable_var_dict['trend'][num]='counter'
            changable_var_dict['direction'][num]='long'
            changable_var_dict['corr'][num]=corr_df.iloc[0,1]
            i2+=1
        elif corr_df.iloc[0,1]>=-corr_standard and corr_df.iloc[0,1]<0:
            changable_var_dict['trend'][num]='counter'
            changable_var_dict['direction'][num]='short'
            changable_var_dict['corr'][num]=corr_df.iloc[0,1]
            i3+=1
        else:
            changable_var_dict['trend'][num]='follow'
            changable_var_dict['direction'][num]='short'
            changable_var_dict['corr'][num]=corr_df.iloc[0,1]
            i4+=1
print(f'i1:{i1/(i1+i2+i3+i4):.2f}, i2={i2/(i1+i2+i3+i4):.2f}, i3={i3/(i1+i2+i3+i4):.2f}, i4={i4/(i1+i2+i3+i4):.2f}')

changable_var_dict['n']=2
# changable_var_dict end






# portfolio_optimizer
# portfolio_optimizer_interval='1d'
# backtest_start_date=datetime(2024,1,2,0,0)
# backtest_end_date=datetime(2024,1,30,0,0)
# portfolio_optimizer=popo.PortfolioOptimizer(method='TOP_N_EQUALLY_DIVIDE',interval=portfolio_optimizer_interval,data_info=data_info,previous_steps=10,rebalance_steps=30,changable_var_dict=changable_var_dict)
# portfolio_backtest
# portfolio_optimizer_result=portfolio_optimizer.portfolio_backtest(backtest_start_date,backtest_end_date,start_balance=1000000,show_method=False,show_equityseries=False,show_details=True)
# gg.save_var_to_pickle(var=equityseries_info, dir_list=['pgl_index','0717'], file_name='equityseries_info')