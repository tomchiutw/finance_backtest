# -*- coding: utf-8 -*-
"""
Created on Sat May 18 00:39:01 2024

@author: user
"""


import generallib.general as gg
import generallib.plot as gp

test={}



# performance_summary=gg.load_var_from_pickle('F0001_VIXFUTURE','performance_summary')
# backtest_results=gg.load_var_from_pickle('F0001_VIXFUTURE','backtest_results')
# optimize_results=gg.load_var_from_pickle('F0001_VIXFUTURE','optimize_results')
# for year in backtest_results.values():
#     gp.plot_all_columns_together(year['output']['account_details'],show_only_balance=True)

test=gg.load_var_from_pickle(dir_list=['pgl_index','0717'],file_name='equtyseries_corr_trend')