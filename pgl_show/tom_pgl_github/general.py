# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 19:23:07 2024

@author: user
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ffn

def plot_all_columns_together(df,show_only_balance=False,bold_list=[],exception_list=[]):
    
    plt.figure(figsize=(12, 8))  # Create a figure for the plot
    # Iterate over each column in the DataFrame
    if show_only_balance==True:
        plt.plot(df.index, df['balance'], label='balance')
    else:
        for col in df.columns:
            if col not in exception_list:
                if col in bold_list:
                    plt.plot(df.index, df[col], label=col, linewidth=4)  # Bold specified columns
                else:
                    plt.plot(df.index, df[col], label=col)  # Regular line for other columns
                    
def get_backtest_date_range(backtest_start_date,backtest_end_date,interval):
    backtest_date_range=pd.date_range(start=backtest_start_date, end=backtest_end_date, freq=change_interval_for_date_range(interval))
    if len(backtest_date_range)==0:
        raise ValueError('Wrong backtest_date_range interval')
    return backtest_date_range

def change_interval_for_date_range(interval):
    interval_mapping = {
    "1m": "T",
    "2m": "2T",
    "5m": "5T",
    "15m": "15T",
    "30m": "30T",
    "60m": "60T",
    "90m": "90T",
    "1h": "H",
    "1d": "D",
    "5d": "5D",
    "1wk": "W",
    "1mo": "M",
    "3mo": "3M"
    }
    return interval_mapping[interval]

def getPortfolio_Series(df, profitPercentage_Col, rf=0.02):

    
    portfolio_df = df[[profitPercentage_Col]].apply(pd.to_numeric, errors='coerce').dropna()
    portfolio_df.index = pd.to_datetime(portfolio_df.index)

    if not isinstance(portfolio_df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex")

    portfolio_df = portfolio_df.replace([np.inf, -np.inf], np.nan).dropna()

    
    stats = portfolio_df.calc_stats()
    stats.set_riskfree_rate(rf)
    return_series = stats.stats


    return return_series