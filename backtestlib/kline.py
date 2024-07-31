# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 16:00:35 2024

@author: user
"""

import pandas as pd
import matplotlib
import mplfinance as mpf

def plot_kline(marketdata_df,marketdata_name,start,end):
    kwargs = dict(type='candle', volume=False, figratio=(12,8), figscale=0.6, title=marketdata_name, style='yahoo',tight_layout=False) 
    plt=mpf.plot(marketdata_df[start:end], **kwargs)
    return plt