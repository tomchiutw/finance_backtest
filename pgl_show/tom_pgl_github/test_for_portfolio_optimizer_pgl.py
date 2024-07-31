import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
# import self module
import portfolio_optimizer as popo



            
# portfolio_optimizer_interval
portfolio_optimizer_interval='1d'


# 1 portfolio_optimizer
perfromance_df=pd.DataFrame()
portfolio_optimizer_method_results=dict()

# test_list=[100,500]
test_list=[100]


for i in test_list:
    for year in range(2023,2024):
        backtest_start_date=datetime(year,1,1,0,0)
        backtest_end_date=datetime(year+1,12,31,0,0)
        if year==2023:
            backtest_end_date=datetime(year+1,1,10,0,0)
        
        !!!!!!!!!!!!!!!!!!!!!
        # net_values_df
        xls=f'change_here_maybe\\{year}_net_values.csv'
        !!!!!!!!!
        net_values_df=pd.read_csv(xls,index_col=0)
        # net_values_df=net_values_df.iloc[:,250:255]
        net_values_df.index = pd.to_datetime(net_values_df.index)

        strings_to_exclude = [
            '1H-HIGH-OPEN', '1H-CLOSE-LOW', '1H-S', 'L1-OLD', 'L1-NEW', 'S1',
            '8H115', '8H24', '24H115', '24H24', 'L2', 'L3'
        ]

        
        cols_to_drop = []
        for col in net_values_df.columns:
            # find first "_" from right
            last_underscore_index = col.rfind('_')
            if last_underscore_index != -1: # -1 means no find "_"
                left_part = col[:last_underscore_index]
                right_part = col[last_underscore_index + 1:]
                
                if left_part in strings_to_exclude:
                    cols_to_drop.append(col)
                    continue
                
                # exclude VOLX strategy
                if 'VOLX' in right_part:
                    cols_to_drop.append(col)
                    continue
        
        net_values_df.drop(columns=cols_to_drop, inplace=True)     
        
        
        # changable_var_dict
        changable_var_dict=dict()
        changable_var_dict['take_profit_perventage']=0.3
        changable_var_dict['days_for_take_profit_perventage']=5
        changable_var_dict['n']=i
        changable_var_dict['idx_start']=0
        changable_var_dict['days_for_rebalance_steps']=60
        portfolio_optimizer=popo.PortfolioOptimizer(method='TOP_N_EQUALLY_DIVIDE_AND_CHECK_POSITIVE_R_THEN_REBALANCE', \
                                                    interval=portfolio_optimizer_interval,previous_steps=370,rebalance_steps=1,changable_var_dict=changable_var_dict) 
        
        # 2 portfolio_optimizer.observed_df
        portfolio_optimizer.observed_df=net_values_df[backtest_start_date:backtest_end_date]
        # 3 start portfolio_optimizer_backtest
        portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_equityseries=False,show_details=True)
        
        # save
        portfolio_optimizer_method_results[year]=portfolio_optimizer_results
    

