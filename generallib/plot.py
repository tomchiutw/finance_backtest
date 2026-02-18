# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 00:00:58 2024


@author: user
"""
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# for plot


    
def plot_one_df(df,column=''):
    plt.figure(figsize=(8, 4))  # 從 (10, 6) 改為 (8, 4)
    plt.plot(df[column], color='blue',label=df[column].name if df[column].name else column)
    plt.title(column)
    plt.legend(loc='best')
    plt.xlabel(df.index.name if df.index.name else 'Index')
    plt.ylabel(column)
    
    # Create a ScalarFormatter object which turns off scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)
    # Set the formatter for the y-axis
    plt.gca().yaxis.set_major_formatter(y_formatter)

    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    return plt
    
def plot_all_columns_together(df,show_only_balance=False,bold_list=[],exception_list=[]):
    
    plt.figure(figsize=(10, 5))  # 從 (12, 8) 改為 (10, 5)
    
    if show_only_balance==True:
        plt.plot(df.index, df['balance'], label='balance')
    else:
        for col in df.columns:
            if col not in exception_list:
                if col in bold_list:
                    plt.plot(df.index, df[col], label=col, linewidth=4)
                else:
                    plt.plot(df.index, df[col], label=col)
    
    # Adding plot details
    plt.title('Portfolio Balances', fontsize=12)  # 加上字體大小控制
    plt.xlabel('Date', fontsize=10)
    plt.ylabel('Balance', fontsize=10)
    plt.legend(title='Equity', fontsize=9)  # 縮小 legend 字體
    
    # Create a ScalarFormatter object which turns off scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)
    # Set the formatter for the y-axis
    plt.gca().yaxis.set_major_formatter(y_formatter)
    
    # Optional: adds a grid for easier readability
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    plt.tight_layout()  # 加上這行，自動調整邊距
    plt.show()