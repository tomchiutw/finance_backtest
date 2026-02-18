import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# import self module
import generallib.general as gg
import generallib.line as gl
import portfolio_optimizerlib.portfolio_optimizer as popo
import portfolio_optimizerlib.equity_series as pes
import get_base_dir as gbd
script_dir=gbd.get_base_dir()





# equityseries_info=pes.EquitySeriesList.get_equityseries_info()
# commodity_list=[]
# folder_list=[]
# for info in equityseries_info:
#     if info['commodity'] not in commodity_list:
#         commodity_list.append(info['commodity'] )
#     if info['folder_name'] not in folder_list:
#         folder_list.append(info['folder_name'] )

# commodity_to_exclude=['DOGEUSD']
# folder_to_exclude=[]
equity_price_file=f"C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\equity_prices_features\\{commodity}_daily_prices_features"
price_data=pd.read_csv(equity_price_file)
# Set the 'Date' column as the index
price_data['Date'] = pd.to_datetime(price_data['Date'])
price_data.set_index('Date', inplace=True)
price_data.index = pd.to_datetime(price_data.index)
# Convert the data into DataFrame
data = net_values_df[item]