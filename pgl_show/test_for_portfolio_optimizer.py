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


# 1 portfolio_optimizer
perfromance_df=pd.DataFrame()
portfolio_optimizer_method_results=dict()

# test_list=[100,500]
test_list=[100]


for i in test_list:
    for year in range(2021,2025):
        backtest_start_date=datetime(year-1,1,1,0,0)
        backtest_end_date=datetime(year,12,31,0,0)
        if year==2024:
            backtest_end_date=datetime(year,6,1,0,0)
        
        # net_values_df
        xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\{year-1}_net_values.csv'
        net_values_df=pd.read_csv(xls,index_col=0)
        # net_values_df=net_values_df.iloc[:,250:255]
        net_values_df.index = pd.to_datetime(net_values_df.index)

        strings_to_exclude = [
            '1H-HIGH-OPEN', '1H-CLOSE-LOW', '1H-S', 'L1-OLD', 'L1-NEW', 'S1',
            '8H115', '8H24', '24H115', '24H24', 'L2', 'L3','Booling_S'
        ]
        # strings_to_exclude =[]
        
        cols_to_drop=[]
        
        for col in net_values_df.columns:
            # 找到最右边的 '_'
            last_underscore_index = col.rfind('_')
            if last_underscore_index != -1:
                left_part = col[:last_underscore_index]
                right_part = col[last_underscore_index + 1:]
                
                # 检查左边部分是否与列表中的字符串完全相同
                if left_part in strings_to_exclude:
                    cols_to_drop.append(col)
                    continue
                
                # 检查右边部分是否包含 'VOLX'
                if 'VOLX' in right_part:
                    cols_to_drop.append(col)
                    continue

        # 删除指定的列
        net_values_df.drop(columns=cols_to_drop, inplace=True)     
        
        
        
        changable_var_dict=dict()
        changable_var_dict['n']=100
        changable_var_dict['acceptable_mdd']=-0.3
        changable_var_dict['acceptable_r']=0
        changable_var_dict['stop_loss_percentage'] = 0.3
        changable_var_dict['days_for_stop_loss'] = 5
        changable_var_dict['idx_start'] = 0
        changable_var_dict['days_for_rebalance_steps'] = 60
        changable_var_dict['first_step_method'] = 'TOP_N_EQUALLY_DIVIDE_AND_FILTERED_BY_MDD_AND_R'
        # for 
        portfolio_optimizer=popo.PortfolioOptimizer(method='DO_METHOD_AND_STOP_LOSS', \
                                                    interval=portfolio_optimizer_interval,previous_steps=370,rebalance_steps=1,changable_var_dict=changable_var_dict) 

        # 2 portfolio_optimizer.observed_df
        # portfolio_optimizer.observed_df=net_values_df[backtest_start_date:backtest_end_date]
        # !!!!!!!!
        portfolio_optimizer.observed_df=net_values_df[:backtest_end_date]
        # !!!!!!!!
        # 3 start portfolio_optimizer_backtest
        portfolio_optimizer_results=portfolio_optimizer.portfolio_backtest(backtest_start_date, backtest_end_date,start_balance=100000,show_method=True,show_equityseries=False,show_details=True)
 
        # save
        # file_name=f'{portfolio_optimizer.method}_{i}_{portfolio_optimizer.previous_steps}_{portfolio_optimizer.rebalance_steps}_{year}'
        file_name=f'{portfolio_optimizer.method}_{i}_{portfolio_optimizer.previous_steps}_{portfolio_optimizer.rebalance_steps}_{year}'
        # portfolio_optimizer_method_results[file_name]=portfolio_optimizer_results
        gg.save_var_to_pickle(portfolio_optimizer_results, dir_list=['pgl_index','strategy_5111'], file_name=file_name)
        perfromance_df[year]=portfolio_optimizer_results['performance']
        
        # others
        # gp.plot_all_columns_together(portfolio_optimizer_results['summary_df'],bold_list=[portfolio_optimizer.method])
        gl.line_notify(f'{year},{file_name} success')
    

