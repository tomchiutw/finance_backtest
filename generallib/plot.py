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
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.plot(df[column], color='blue',label=df[column].name if df[column].name else column)  # Plot the specified column data in blue
    plt.title(column)  # Set the title of the graph as the column name
    plt.legend(loc='best')
    plt.xlabel(df.index.name if df.index.name else 'Index')  # Set the x-axis label
    plt.ylabel(column)  # Set the y-axis label as the column name
    
    # Create a ScalarFormatter object which turns off scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)
    # Set the formatter for the y-axis
    plt.gca().yaxis.set_major_formatter(y_formatter)

    plt.grid(True)  # Enable the grid
    plt.tight_layout()  # Ensure everything fits without overlapping
    # Display the plot only if show is True
    plt.show()
    
    return plt
    
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
    
    # Adding plot details
    plt.title('Portfolio Balances')
    plt.xlabel('Date')  # Assuming the index of the DataFrame is date
    plt.ylabel('Balance')
    plt.legend(title='Equity')  # Adding a legend with a title

    # Create a ScalarFormatter object which turns off scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)
    # Set the formatter for the y-axis
    plt.gca().yaxis.set_major_formatter(y_formatter)
    
    # Optional: adds a grid for easier readability
    plt.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.7)
    
    # Show the plot
    plt.show()
            
            