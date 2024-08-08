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
# folderlib
import folderlib.folder as ff
import folderlib.Long_Short_SMA as f


backtest_start_date=datetime(2015,1,1,0,0)
backtest_end_date=datetime(2024,1,1,0,0)
# portfolio_optimizer_interval
portfolio_optimizer_interval='1d'
# interval
interval='1d'
# contract
contract='spot'
# portfolio_optimizer
changable_var_dict=dict()
changable_var_dict['n']=10
# changable_var_dict['n']=5
portfolio_optimizer=popo.PortfolioOptimizer(method='TOP_N_EQUALLY_DIVIDE',interval=portfolio_optimizer_interval,previous_steps=360,rebalance_steps=20,changable_var_dict=changable_var_dict) 
# equityseries_list
equityseries_list=list()


# 1 create equity_series 
main_index_list=['ALL_ORDINARIES_INDEX','BEL_20_INDEX','CAC_40_INDEX','DAX_INDEX', 
                  'HANG_SENG_INDEX','IDX_COMPOSITE_INDEX','NIKKEI_225_INDEX','RUSSELL_2000_INDEX',
                  'SENSEX_INDEX','SHENZHEN_INDEX','SP500_INDEX','STI_INDEX']
# main_index_list=['SP500_INDEX','HANG_SENG_INDEX','NIKKEI_225_INDEX']
# commodities=bc.CommodityList.get_commodities(main_index_list,transfer_to_commodity_type=True)
commodities=bc.CommodityList.list_commodities(category_list=['currency_pair','index'],exception_list=['VIX_INDEX'])
for commodity in commodities:
    commodity_contract=commodity.marketdata[contract]
    if commodity.data_source=='yfinance':
        commodity_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
    else:
        commodity_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
     
    marketdata=commodity.marketdata[contract]
    marketdata_df=marketdata.data[interval]
    new_data=marketdata_df['Close'].to_frame()
    
    # create equityseries
    portfolio_optimizer.append_observed_df(new_data,col_name=commodity.symbol)



# 3 start portfolio_optimizer_backtest
portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=1000000,show_method=True,show_equityseries=False,show_details=False)



# save
# gg.save_var_to_pickle(portfolio_optimizer_results, dir_list=['all_index'], file_name='equally_divide_at_beginning_2014_2024')

# others
# corr=gg.cor(portfolio_optimizer_results['summary_df'])
# gp.plot_all_columns_together(portfolio_optimizer_results['summary_df'],bold_list=[portfolio_optimizer.method])