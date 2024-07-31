# -*- coding: utf-8 -*-
"""
Created on Thu May 16 20:49:32 2024

@author: user
"""
import math
import sys
import os
import pandas as pd
from datetime import datetime
# import self module
import backtestlib.commodity as bc
import generallib.general as gg
import generallib.plot as gp
import backtestlib.performance as bp
import backtestlib.account as ba
import backtestlib.order as bo
import folderlib.folder as ff
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import backtestlib.marketdata as bm
import backtestlib.kline as bk
import backtestlib.backtest as bb
import backtestlib.indicator_list as bil
import get_base_dir as gbd
script_dir=gbd.get_base_dir()
import numpy as np


class Long_Index_With_Low_Percent(ff.Folder):
    
    def __init__(self,changable_var_dict,description=''):
        self.changable_var_dict=changable_var_dict
        super().__init__(self.__class__.__name__,description=description)    
        self._init_folder_dict()
        self._init_folder() # this function from folder.py
        
    def _init_folder_dict(self):
        self.folder_dict=self.get_folder_dict()
        self.folder_dict['folder_name']=self.name
        
    
        
    # below code different strategy may different  
    def get_folder_dict(self):
        
        self.folder_dict=dict()
        
        try:
            account=self.changable_var_dict['account']
            commodity=self.changable_var_dict['commodity']
            interval=self.changable_var_dict['interval']
            contract=self.changable_var_dict['contract']
            backtest_start_date=self.changable_var_dict['backtest_start_date']
            backtest_end_date=self.changable_var_dict['backtest_end_date']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
        # ---------------------
        # account
        account.deposit(1000000)
        # -----------------
        # marketdata
        commodity_contract=commodity.marketdata[contract]
        if commodity.data_source=='yfinance':
            commodity_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
        else:
            commodity_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
        # -------------------------------
        # indicator1
        indicator1_name='Low_Percent'
        indicator1_marketdata=commodity_contract
        indicator1_interval=interval
        indicator1=bil.Indicator(indicator1_name,indicator1_marketdata,indicator1_interval)
        ret_2=indicator1.data
        # ---------------------
        # tradingpanel
        tradingpanel=bt.TradingPanel(account)
        tradingpanel.append_marketdata(commodity_contract,interval)
        # ---------------------
        folder_dict={
            'account':account,'interval':interval,'tradingpanel':tradingpanel,
            'indicator1':indicator1,'marketdata':commodity_contract,
            'commodity':commodity}
        
        self.folder_dict=folder_dict
        
        return folder_dict
    
    
    
    def Long_Index_With_Low_Percent(self,time_index):
        # get param from folder_dict
        try:
            # required
            account=self.folder_dict['account']
            interval=self.folder_dict['interval']
            tradingpanel=self.folder_dict['tradingpanel']
            # non required
            commodity=self.folder_dict['commodity']
            indicator1=self.folder_dict['indicator1']
            marketdata=self.folder_dict['marketdata']
            
        except:
            raise ValueError(f'Missing variable when creating Folder')
        
        
        if time_index in indicator1.data.index and not np.isnan(indicator1.data.loc[time_index,indicator1.name]):

            loc = indicator1.data.index.get_loc(time_index)
            # OHLC
            open_price=marketdata.data[interval].loc[time_index,'Open']
            high_price=marketdata.data[interval].loc[time_index,'High']
            low_price=marketdata.data[interval].loc[time_index,'Low']
            close_price=marketdata.data[interval].loc[time_index,'Close']
            # entry_condition
            entry_condition1=indicator1.data.loc[indicator1.data.index[loc-1],indicator1.name]>-0.01
            entry_condition2=account.inventory.get_net_position_size(marketdata.symbol+"_"+marketdata.contract) \
                ==0
            # close_condition
            close_condition1=indicator1.data.loc[indicator1.data.index[loc],indicator1.name]<=-0.01
            close_condition2=account.inventory.get_net_position_size(marketdata.symbol+"_"+marketdata.contract) \
                !=0
            # entry order
            if entry_condition1 and entry_condition2:
                open_quantity=math.floor(account.balance/(commodity.contract_size*open_price+commodity.fee))
                # open_quantity=math.floor(account.cash/(commodity.margin_info['initial_margin']+commodity.fee))
                # open_quantity=1
                order_1=account.orderbook.add_order('long',commodity,marketdata.contract,'market','long',self,time_index,quantity=open_quantity,price=0)
            # close_order
            if close_condition1 and close_condition2:
                close_quantity=abs(account.inventory.get_net_position_size(marketdata.symbol+"_"+marketdata.contract))
                order_2=account.orderbook.add_order('sell',commodity,marketdata.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0)
        
# --------------------------

def folder_main(changable_var_dict,show_balance=False,show_details=False,show_pnl=False):


    # folder changable_var_dict->folder_dict(done inside folder)->return_dict(done inside backtest.py)
    long_index_folder=Long_Index_With_Low_Percent(changable_var_dict)
    # ---------------------
    # backtest_setting
    # backtest_date
    # commodity
    # interval
    # contract
    # --------------------------------------------
    folder_dict=long_index_folder.show_folder_dict()
    # ---------------------
    # main
    # backtest_date
    backtest_start_date=changable_var_dict['backtest_start_date']
    backtest_end_date=changable_var_dict['backtest_end_date']
    return_dict=bb.single_interval_backtest(backtest_start_date=backtest_start_date,
                                            backtest_end_date=backtest_end_date,
                                            folder=long_index_folder,
                                            show_balance=show_balance,
                                            show_details=show_details,
                                            show_pnl=show_pnl
                                            )
    dict_to_pickle={'input':folder_dict,
                    'output':return_dict}


    # gg.save_var_to_pickle(dict_to_pickle,'test','test')
    return dict_to_pickle