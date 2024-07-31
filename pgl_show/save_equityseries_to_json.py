import sys
import os
import pandas as pd
import numpy as np
import copy
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


# save_default equityseries_info and test
pes.EquitySeriesDict.create_default_equityseries_info()
# test1=pes.EquitySeriesDict.get_equityseries_info()
# test2=pes.EquitySeriesDict.get_data_info(nums_to_load=[])



    
    

# net values
net_values_df=pd.DataFrame()
csv_list=[2020,2021,2022,2023]
col_dict=dict()
for year in csv_list:    
    xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\{year}_net_values.csv'
    net_values=pd.read_csv(xls,index_col=0)
    net_values.index = pd.to_datetime(net_values.index)
    
    col_dict[year]=net_values.columns.tolist()
    existing_columns = net_values_df.columns.tolist()
    for col in net_values.columns:
        # If the column is not already in net_values_df, add it
        if col not in existing_columns:
            net_values_df[col] = net_values[col]

common_elements = set(col_dict[2020]).intersection(col_dict[2021], col_dict[2022], col_dict[2023])
common_equityseries_for_test=[]
# equityseries_name
equityseries_name=net_values_df.columns.tolist()

# check
# check=False
# if check==False:
#     sys.exit("stop")

# start process
data_info=[]
equityseries_dict=pes.EquitySeriesDict()
# strategyname
error_name=[]
for item in equityseries_name:
    temp_dict=dict()
    changable_var_dict_for_folder=dict()
    # 找到最后一个下划线的位置
    last_underscore_index = item.rfind('_')
    if last_underscore_index != -1:
        try:
            folder_name = item[:last_underscore_index]
            commodity_var = item[last_underscore_index + 1:]
            interval='1d'
            if '.' in commodity_var:
                commodity, n = commodity_var.split('.')
                changable_var_dict_for_folder['n']=n
            else:
                commodity=commodity_var
            check_equityseries_exists= \
                pes.EquitySeriesDict.check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder)
            # save
            if not check_equityseries_exists:
                temp_dict['num']=equityseries_dict.get_next_num()
                equityseries_dict.equityseries_info['total_equityseries_num']=temp_dict['num']
                temp_dict['commodity']=commodity
                temp_dict['interval']='1d'
                temp_dict['folder_name']=folder_name
                # turn to df
                temp_dict['data']=net_values_df[[item]]
                temp_dict['source']='pgl'
                temp_dict['changable_var_dict_for_folder']=changable_var_dict_for_folder
                temp_dict['note']=''
            else:
                print(f'{commodity}, {interval}, {folder_name} existed in equityseries dict')
                common_equityseries_for_test.append(f'{commodity}, {interval}, {folder_name}')
                
        except Exception as e:
            error_name.append(item)
            raise ValueError(f'{e}')
            
        
    # update equityseries_info_dict[]
    # info
    append_dict=copy.deepcopy(temp_dict)
    del append_dict['data']
    equityseries_dict.equityseries_info['info'].append(append_dict)
    # data
    data_info.append(copy.deepcopy(temp_dict))

print(f' error_name: {len(error_name)}')

# final save
pes.EquitySeriesDict.save_equityseries_info(equityseries_dict.equityseries_info)
pes.EquitySeriesDict.save_data_info(data_info)







# # portfolio_optimizer_interval
# # portfolio_optimizer_interval='1d'
# # changable_var_dict=dict()
# # changable_var_dict['n']=2
# # portfolio_optimizer=popo.PortfolioOptimizer(method='HIGH_MDD',interval=portfolio_optimizer_interval,previous_steps=10,rebalance_steps=30,changable_var_dict=changable_var_dict) 
# # portfolio_optimizer.observed_df=net_values_df[backtest_start_date:backtest_end_date]
# # results
# # portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_equityseries=False,show_details=True)






