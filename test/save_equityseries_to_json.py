import sys
import os
import pandas as pd
import numpy as np
import copy
from datetime import datetime
# import self module
import backtestlib.commodity as bc
from backtestlib.commodity import CommodityList
from datetime import timedelta
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
# pes.EquitySeriesList.create_default_equityseries_info(confirm_execution=True)
# test1=pes.EquitySeriesList.get_equityseries_info()
# test2=pes.EquitySeriesList.get_data_info(hash_value_to_load=[i for i in range(5)])


breakpoint()

# net values
net_values_df=pd.DataFrame()
csv_list=[2020,2021,2022,2023]
col_dict=dict()
# start process
data_info=[]
equityseries_info=[] 
for year in csv_list:    
    equityseries_name=[]
    net_values_df=pd.DataFrame()
    xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\{year}_net_values.csv'
    net_values=pd.read_csv(xls,index_col=0)
    net_values.index = pd.to_datetime(net_values.index)
    
    for col in net_values.columns:
        net_values_df[col] = net_values[col]

    # equityseries_name
    equityseries_name=net_values_df.columns.tolist()
    # strategyname
    error_name=[]
    # process equityseries_name
    for item in equityseries_name:
        changable_var_dict_for_folder=dict()
        changable_var_dict_for_folder['optimize_year']=str(year)
        # find rightest "_"
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
                    pes.EquitySeriesList.check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder)
                # save
                if not check_equityseries_exists:
                    
                    # turn to df
                    data=net_values_df[item]
                    source='pgl'
                    
                    equityseries_info_params=pes.EquitySeriesList.create_new_equityseries_params(commodity, interval, folder_name, data, source,changable_var_dict_for_folder, note='')
                else:
                    print(f'{commodity}, {interval}, {folder_name} existed in equityseries dict')
                    
            except Exception as e:
                error_name.append(item)
                raise ValueError(f'{e}')
                
            
            # update equityseries_info
            # data
            data_info.append(copy.deepcopy(equityseries_info_params))
            # info
            append_dict=copy.deepcopy(equityseries_info_params)
            del append_dict['data']
            equityseries_info.append(append_dict)


        
print(f' error_name: {len(error_name)}')

# check
check=False
if check==False:
    sys.exit("stop") 
# final save
# pes.EquitySeriesList.save_equityseries_info(equityseries_info,confirm_execution=True)
# pes.EquitySeriesList.save_data_info(data_info,confirm_execution=True)







# # portfolio_optimizer_interval
# # portfolio_optimizer_interval='1d'
# # changable_var_dict=dict()
# # changable_var_dict['n']=2
# # portfolio_optimizer=popo.PortfolioOptimizer(method='HIGH_MDD',interval=portfolio_optimizer_interval,previous_steps=10,rebalance_steps=30,changable_var_dict=changable_var_dict) 
# # portfolio_optimizer.observed_df=net_values_df[backtest_start_date:backtest_end_date]
# # results
# # portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_equityseries=False,show_details=True)




# performance
# performance_summary=dict()
# for year,col_list in col_dict.items():
#     df=pd.DataFrame()
#     for col in col_list:
#         equity_series=net_values_df.loc[datetime(year+1,1,1):datetime(year+1,6,1),col]
#         initial_value = equity_series.iloc[0]
#         final_value = equity_series.iloc[-1]
#         annual_return = (final_value - initial_value) / initial_value
#         df[col] = [annual_return]
#     performance_summary[year] = df
    
# filepath=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\backtest_result\\pgl_index\\0718\\performance_{year}.xlsx'
# with pd.ExcelWriter(filepath) as writer:
#     for year, df in performance_summary.items():
#         df.to_excel(writer, sheet_name=str(year), index=False)

