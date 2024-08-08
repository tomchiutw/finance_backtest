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
import folderlib.Long_Short_SMA as lss
# account
accounts=ba.AccountManager()

# backtest_period
backtest_start_date=datetime(2004,9,1,0,0)
backtest_end_date=datetime(2025,4,1,0,0)

# folder setting start
# commodity
commodities=bc.CommodityList.get_commodities(['SP_FUTURE'])
# interval
interval='1d'
# contract
contract='c1'

for commodity in commodities:
    # marketdata
    commodity_contract=commodity.marketdata[contract]
    indicator_var_dict={'settlement_dates_list':commodity.settlement_dates}
    if commodity.data_source=='yfinance':
        commodity_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
    else:
        commodity_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
    # indicator
    indicator_name='Days_To_Next_Settlement_Dates'
    indicator=bil.Indicator(indicator_name,commodity_contract,interval,indicator_var_dict=indicator_var_dict)
    
    
    
    
    
    
    
    