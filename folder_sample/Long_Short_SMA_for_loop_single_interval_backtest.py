import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
# import self module
import backtestlib.commodity as bc
from backtestlib.commodity import CommodityList
import generallib.general as gg
import generallib.line as gl
import generallib.plot as gp
import backtestlib.performance as bp
import backtestlib.optimizer as bop
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
import folderlib.Long_Short_SMA as f



# performance_summary
performance_summary=pd.DataFrame()
# balance_summary
balance_summary=pd.DataFrame()
# backtest_result
backtest_results=dict()
optimize_results=dict()
# indicator
short_SMA_length=5
long_SMA_length=20
# account
accounts=ba.AccountManager()
# ---------------------------
is_optimizer=True
# backtest_period
start_year=2020
end_year=2024
# backtest_loop
n_steps=1

for year in range(start_year,end_year,n_steps):
    # backtest_period
    backtest_start_date=datetime(year,1,1,0,0)
    backtest_end_date=datetime(year+1,1,1,0,0)
    print(f'{year} start')
    # folder setting start
    # commodity
    # commodities=bc.CommodityList.list_commodities(category='currency_pair')
    commodities=bc.CommodityList.list_commodities(category_list='currency_pair',exception_list=['RUBUSD','IDRUSD','SGXUSD','ZARUSD'])
    # commodities=[bc.create_commodity(bc.CommodityList.)]
    # commodities=bc.CommodityList.get_commodities(['SP_FUTURE','USDJPY'])
    # create account
    # account
    account_name = '1st_account'
   
    if account_name not in accounts.accounts:
        accounts.create_new_account(name=account_name)
    else:
        accounts.accounts[account_name].reset()
    account = accounts.accounts[account_name]
    # interval
    interval='1d'
    # contract
    contract='c1'

    # changable_var_dict
    changable_var_dict={'commodities':commodities,
                        'contract':contract,
                        'account':account,
                        'interval':interval,
                        'backtest_start_date':backtest_start_date,
                        'backtest_end_date':backtest_end_date,
                        'short_SMA_length':short_SMA_length,
                        'long_SMA_length':long_SMA_length
                        }
    # ----------------------------
    if is_optimizer:
        # optimizer
        # input next year params from optimizer
        if year > start_year and optimize_results:
                best_params = optimize_results[year - 1]['method_result']
                changable_var_dict.update(best_params)
                print(f'{year}: {best_params}')
        
        params = {
            'long_SMA_length': [10,20,60]
        }
        method='MAX_RETURN'
        optimizer=bop.Optimizer(params, method, changable_var_dict,f.folder_main)
        optimize_results[year]=optimizer.optimize(show_balance=False,show_details=False,show_pnl=False)
        changable_var_dict['account'].reset()
        # optimizer end
        # ---------------------
        
    backtest_results[year]= f.folder_main(changable_var_dict,show_balance=True,show_details=False,show_pnl=True)
    # performance_summary
    balance_summary[year]=backtest_results[year]['output']['account_details']['balance']
    performance_summary[year]=backtest_results[year]['output']['performance']
    
    print(f'{year} end')


# gl.line_notify('finance_backtest end')