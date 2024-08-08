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


# portfolio_optimizer_interval
portfolio_optimizer_interval='1d'

# net values
xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\test\\test_for_optimizer_method.csv'
net_values_df=pd.read_csv(xls,index_col=0)
net_values_df.index = pd.to_datetime(net_values_df.index)


backtest_start_date=datetime(2000,1,3,0,0)
backtest_end_date=datetime(2000,1,20,0,0)
changable_var_dict=dict()
changable_var_dict['n']=2

portfolio_optimizer=popo.PortfolioOptimizer(method='HIGH_MDD',interval=portfolio_optimizer_interval,previous_steps=10,rebalance_steps=30,changable_var_dict=changable_var_dict) 
portfolio_optimizer.observed_df=net_values_df[backtest_start_date:backtest_end_date]
# results
portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_equityseries=False,show_details=True)






