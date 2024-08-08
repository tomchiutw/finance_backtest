# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 01:56:21 2024

@author: user
"""
import generallib.general as gg
import generallib.line as gl
import generallib.plot as gp
import portfolio_optimizerlib.portfolio_optimizer as popo
import pandas as pd
import csv

performance_df=pd.DataFrame()
summary_df_results=pd.DataFrame()
weight_dict_summary=dict()

xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\backtest_result\\pgl_index\\0711'
save_dict_xls=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\backtest_result\\pgl_index\\0711\\weight_dict.xlsx'
# load pickle
portfolio_optimizer_methods_results=gg.load_pickles_from_path_to_dict(xls)

for name,results in portfolio_optimizer_methods_results.items():
    # performance
    performance_df[name]=results['performance']
    # equity
    summary_df_results[name]=results['summary_df'][results['summary_df'].columns[-1]]
    # weight_dict
    weight_dict_summary[name]=results['weight_dict']

summary_df_results=popo.normalized_to_base(summary_df_results,start_balance=100000,exception=[''])
# plot
gp.plot_all_columns_together(summary_df_results,bold_list=['BASELINE'])


# save weight_dict tocsv
with pd.ExcelWriter(save_dict_xls) as writer:

    for sheet_name,weight_dict in weight_dict_summary.items():
        data=[]
        for date,sub_dict in weight_dict.items():
            for key,value in sub_dict.items():
                if value!=0:
                    data.append([date,key,value])
        df = pd.DataFrame(data, columns=['Date', 'Key', 'Value'])
        # 将DataFrame写入Excel文件的相应工作表
        df.to_excel(writer, sheet_name=sheet_name[:30], index=False)
    
# others
# gg.save_df_to_excel(performance_df, file_path=xls, file_name=performance_df.xlsx)
# file_name='equally_divide_at_beginning_2014_2024'
# results=gg.load_var_from_pickle(dir_list=['pgl_index'], file_name='EQUALLY_DIVIDE_AT_BEGINNING_2020_2024')



