
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
import generallib.line as gl
import backtestlib.performance as bp
import backtestlib.account as ba
import backtestlib.order as bo
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import backtestlib.marketdata as bm
import backtestlib.kline as bk
import backtestlib.backtest as bb
import backtestlib.indicator_list as bil
import backtestlib.optimizer as bop
import get_base_dir as gbd
script_dir=gbd.get_base_dir()
# folderlib
import folderlib.folder as ff
import folderlib.F0001 as f


# performance_summary
performance_summary=pd.DataFrame()
# balance_summary
balance_summary=pd.DataFrame()
# backtest_result
backtest_results=dict()
optimize_results=dict()
# ---------------------------
# entry_percentage
sid=0.05
short_entry_percentage=sid
short_close_percentage=sid
short_close_percentage_2=0.03
spread=0
lid=0.15
long_entry_percentage=lid
long_close_percentage=lid
long_stop_percentage=lid
settlement=1
# leverage
leverage=0.2
# liability
liability_percentage=0
# create main account
accounts=ba.AccountManager()
# ---------------------------
is_optimizer=False
# backtest_period
start_year=2006
end_year=2024
# backtest_loop
n_steps=18

for year in range(start_year,end_year,n_steps):
    
    
    # commodity_list
    # commodity_list=bc.CommodityList.list_commodities(category='currency_pair',exception_list=['RUBUSD','IDRUSD','SGXUSD','ZARUSD'])
    # commodity_list=bc.CommodityList.get_commodities(['VIX_FUTURE'])
    # commodity
    commodity_future=bc.create_commodity(bc.CommodityList.VIX_FUTURE)
    commodity_spot=bc.create_commodity(bc.CommodityList.VIX_INDEX)
    print(f'{commodity_future.name} in {year} start')
    # backtest_period
    backtest_start_date=datetime(year,1,1,0,0)
    backtest_end_date=datetime(year+n_steps,1,1,0,0)
    # --------------------------
    # folder_setting start
    # account
    account_name = f'{commodity_future.name}_account'
    if account_name not in accounts.accounts:
        accounts.create_new_account(name=account_name)
    else:
        accounts.accounts[account_name].reset()
    account = accounts.accounts[account_name]
    # interval
    interval='1d'
    # contract
    contract='c1'
    
    # ----
    changable_var_dict={'account':account,
                        'backtest_start_date':backtest_start_date,
                        'backtest_end_date':backtest_end_date,
                        'commodity_future':commodity_future,
                        'commodity_spot':commodity_spot,
                        'interval': interval,
                        'contract':contract,
                        'short_entry_percentage':short_entry_percentage,
                        'short_close_percentage':short_close_percentage,
                        'short_close_percentage_2':short_close_percentage_2,
                        'spread':spread,
                        'long_entry_percentage':long_entry_percentage,
                        'long_close_percentage':long_close_percentage,
                        'long_stop_percentage':long_stop_percentage,
                        'settlement':settlement,
                        'leverage':leverage,
                        'liability_percentage':liability_percentage
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
            'short_entry_percentage': [0.03,0.05,0.07],
            'short_close_percentage': [0.03,0.05,0.07],
        }
        method='MAX_RETURN'
        optimizer=bop.Optimizer(params, method, changable_var_dict,f.folder_main)
        optimize_results[year]=optimizer.optimize(show_balance=False,show_details=False,show_pnl=False)
        changable_var_dict['account'].reset()
        # optimizer end
    # ---------------------
        
    # folder_setting end
    # ----------------------------
    backtest_results[year]= f.folder_main(changable_var_dict,show_balance=True,show_details=False,show_pnl=False)
    
    
    
    # performance_summary
    balance_summary[year]=backtest_results[year]['output']['account_details']['balance']
    performance_summary[year]=backtest_results[year]['output']['performance']
    print(f'{commodity_future.name} in {year} success')
    
# save
# performance_optimize=gg.load_var_from_pickle('F0001_VIXFUTURE', 'performance_summary')

# others
# gl.line_notify('success')
