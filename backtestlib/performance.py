# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 15:01:00 2024

@author: user
"""

import sys
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import math
import ffn

# for performance

def getPortfolio_Series(df, profitPercentage_Col, rf=0.02,translate=False):

    
    portfolio_df = df[[profitPercentage_Col]].apply(pd.to_numeric, errors='coerce').dropna()
    portfolio_df.index = pd.to_datetime(portfolio_df.index)

    if not isinstance(portfolio_df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex")

    portfolio_df = portfolio_df.replace([np.inf, -np.inf], np.nan).dropna()

    
    stats = portfolio_df.calc_stats()
    stats.set_riskfree_rate(rf)
    return_series = stats.stats
    
    return return_series

def getPortfolio_Df(df,series,combined_date ):
    df[combined_date]=series
    return df

    
def remove_rows_in_portfolio_df(df):
    rows_to_remove=[
    'rf',
    'three_month',
    'six_month',
    'ytd',
    'one_year',
    'three_year',
    'five_year',
    'ten_year',
    'incep',
    'best_day',
    'worst_day',
    'best_month',
    'worst_month',
    'best_year',
    'worst_year',
    'avg_drawdown',
    'avg_up_month',
    'avg_down_month',
    'win_year_perc',
    'twelve_month_win_perc',
    'daily_sortino',
    'mtd',
    'daily_mean',
    'daily_sharpe',
    'daily_vol',
    'daily_skew',
    'daily_kurt',
    'monthly_sharpe',
    'monthly_sortino',
    'monthly_mean',
    'monthly_vol',
    'monthly_skew',
    'monthly_kurt',
    'yearly_sharpe',
    'yearly_sortino',
    'yearly_mean',
    'yearly_vol',
    'yearly_skew',
    'yearly_kurt',]
    df = df.drop(index=rows_to_remove,inplace=True)
    return df

def process_portfolio_df(target_df,series_df,combined_date):
    remove_rows_in_portfolio_df(series_df)
    convert_date_format(series_df)
    convert_to_percentage(series_df)
    translate_index_to_traditional_chinese(series_df)
    getPortfolio_Df(target_df, series_df, combined_date)
    return target_df


def convert_date_format(df):
    index_names=['start','end']
    for index_name in index_names:
        # 檢查索引是否存在於 DataFrame
        if index_name in df.index:
            for col in df.columns:
                # 轉換日期格式
                df.at[index_name, col] = df.at[index_name, col].strftime("%Y%m%d")
    return df
def translate_index_to_traditional_chinese(df):
    # 英文到繁體中文的對照字典
    translation_dict = {
        'start': '開始',
        'end': '結束',
        'rf': '無風險利率',
        'total_return': '總回報',
        'cagr': '複合年增長率',
        'max_drawdown': '最大回撤',
        'calmar': '卡瑪比率',
        'mtd': '月迄今回報',
        'three_month': '三個月回報',
        'six_month': '六個月回報',
        'ytd': '年迄今回報',
        'one_year': '一年回報',
        'three_year': '三年回報',
        'five_year': '五年回報',
        'ten_year': '十年回報',
        'incep': '自成立以來回報',
        'best_day': '最佳單日',
        'worst_day': '最差單日',
        'best_month': '最佳單月',
        'worst_month': '最差單月',
        'best_year': '最佳單年',
        'worst_year': '最差單年',
        'avg_drawdown': '平均回撤',
        'avg_drawdown_days': '平均回撤天數',
        'avg_up_month': '平均上漲月份',
        'avg_down_month': '平均下跌月份',
        'win_year_perc': '年度獲勝百分比',
        'twelve_month_win_perc': '十二個月勝率'
        }


    # 翻譯索引
    df.rename(index=translation_dict, inplace=True)
    return df


def translate_index_to_traditional_chinese_month(df):
    # 英文到繁體中文的對照字典
    translation_dict = {
        'total_return': '總回報',
        'cagr': '複合年增長率',
        'max_drawdown': '最大回撤',
}


    # 翻譯索引
    df.rename(index=translation_dict, inplace=True)
    return df


def convert_to_percentage(df):
    rows =\
        [ 'rf','calmar' ,'total_return', 'cagr', 'max_drawdown', 'mtd', 'three_month', 
        'six_month', 'ytd', 'one_year', 'three_year', 'five_year', 'ten_year', 
        'incep', 'daily_mean', 'monthly_mean', 'yearly_mean', 'avg_drawdown', 
        'avg_up_month', 'avg_down_month', 'win_year_perc', 'twelve_month_win_perc',
        'best_day','worst_day','best_month','worst_month','best_year','worst_year','最大獲利','最大虧損'
        ]
    for row in rows:
        if row in df.index:
            for col in df.columns:
            # 將數值轉換為百分比並四捨五入到小數點後二位
                df.at[row, col] = round(df.at[row, col] * 100, 2)
    return df