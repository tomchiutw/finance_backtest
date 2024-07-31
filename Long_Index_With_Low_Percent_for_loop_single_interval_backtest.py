# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 15:45:38 2024

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:41:12 2024

@author: user
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
# import self module
import backtestlib.commodity as bc
from backtestlib.commodity import CommodityList
import generallib.general as gg
import generallib.plot as gp
import backtestlib.performance as bp
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
# folderlib
import folderlib.folder as ff
import folderlib.Long_Index_With_Low_Percent as liwp

# commodity_list
commodity_list=bc.CommodityList.list_commodities(category='currency_pair',exception_list=['RUBUSD','IDRUSD','SGXUSD','ZARUSD'])
# commodity_list=bc.CommodityList.get_commodities(['EURUSD','USDJPY'])
# performance_summary
performance_summary=pd.DataFrame()
# balance_summary
balance_summary=pd.DataFrame()
# backtest_result
backtest_result=dict()
# commodity_loop
# create main account
accounts=ba.AccountManager()
for commodity in commodity_list:
    
    # backtest_period
    backtest_start_date=datetime(2021,1,1,0,0)
    backtest_end_date=datetime(2022,1,1,0,0)
    
    # --------------------------
    # folder_setting start
    print(f'{commodity.name} start')
    # account
    accounts.create_new_account(name=f'{commodity.name}_account')
    account=accounts.accounts[f'{commodity.name}_account']
    # interval
    interval='1d'
    # contract
    contract='c1'
    
    changable_var_dict={'account':account,
                        'backtest_start_date':backtest_start_date,
                        'backtest_end_date':backtest_end_date,
                        'commodity':commodity,
                        'interval': interval,
                        'contract':contract}
    # folder_setting end
    # ----------------------------
    backtest_result[commodity.name]= liwp.folder_main(changable_var_dict)
    
    # performance_summary
    balance_summary[commodity.name]=backtest_result[commodity.name]['output']['account_details']['balance']
    performance_summary[commodity.name]=backtest_result[commodity.name]['output']['performance']
    print(f'{commodity.name} success')
    
# update main account
balance_summary['balance']=balance_summary.sum(axis=1)/len(commodity_list)
performance_summary['balance']=bp.getPortfolio_Series(balance_summary,'balance',0.02,translate=False)
gp.plot_all_columns_together(balance_summary,show_only_balance=False,bold_list=['balance'])

