# -*- coding: utf-8 -*-
"""
Created on Fri May 24 13:27:03 2024

@author: user
"""

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
import folderlib.F0002 as f


# performance_summary
performance_summary=pd.DataFrame()
# balance_summary
balance_summary=pd.DataFrame()
# backtest_result
backtest_result=dict()
# ---------------------------
# entry_percentage
short_entry_percentage=0.05
short_close_percentage=0.05
# create main account
accounts=ba.AccountManager()
# ---------------------------
# backtest_period
start_year=2018
end_year=2024
n_steps=1
# backtest_loop
for year in range(start_year,end_year,n_steps):
    # commodity_list
    # commodity_list=bc.CommodityList.list_commodities(category='currency_pair',exception_list=['RUBUSD','IDRUSD','SGXUSD','ZARUSD'])
    # commodity_list=bc.CommodityList.get_commodities(['VIX_FUTURE'])
    # commodity
    commodity_future=bc.create_commodity(bc.CommodityList.VIX_FUTURE)
    commodity_spot=bc.create_commodity(bc.CommodityList.VIX_INDEX)
    index_future=bc.create_commodity(bc.CommodityList.SP_FUTURE)
    print(f'{index_future.name} in {year} start')
    # backtest_period
    backtest_start_date=datetime(year,1,1,0,0)
    backtest_end_date=datetime(year,12,31,0,0)
    # --------------------------
    # folder_setting start
    # account
    account_name = f'{index_future.name}_account'
    if account_name not in accounts.accounts:
        accounts.create_new_account(name=account_name)
    else:
        accounts.accounts[account_name].reset()
    account = accounts.accounts[account_name]
    # interval
    interval='1d'
    # contract
    contract='c1'
    
    changable_var_dict={'account':account,
                        'backtest_start_date':backtest_start_date,
                        'backtest_end_date':backtest_end_date,
                        'index_future':index_future,
                        'commodity_future':commodity_future,
                        'commodity_spot':commodity_spot,
                        'interval': interval,
                        'contract':contract,
                        'short_entry_percentage':short_entry_percentage,
                        'short_close_percentage':short_close_percentage}
    # folder_setting end
    # ----------------------------
    backtest_result[year]= f.folder_main(changable_var_dict,show_balance=True,show_details=False,show_pnl=False)
    
    # performance_summary
    balance_summary[year]=backtest_result[year]['output']['account_details']['balance']
    performance_summary[year]=backtest_result[year]['output']['performance']
    print(f'{index_future.name} in {year} success')
    


