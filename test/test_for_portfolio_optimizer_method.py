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




equityseries_info=pes.EquitySeriesList.get_equityseries_info()
observed_equityseries_info=equityseries_info[:5]
# observed_equityseries_info=equityseries_info[:]

# breakpoint()
# portfolio_optimizer_interval
portfolio_optimizer_interval='1d'

backtest_start_date=datetime(2023,4,7,0,0)
backtest_end_date=datetime(2024,1,1,0,0)

changable_var_dict=dict()
changable_var_dict['n']=2

portfolio_optimizer=popo.PortfolioOptimizer(method='TOP_N_EQUALLY_DIVIDE',interval=portfolio_optimizer_interval,observed_equityseries_info=observed_equityseries_info,previous_steps=5,rebalance_steps=30,changable_var_dict=changable_var_dict) 
# results
portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_details=True)






