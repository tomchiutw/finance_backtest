# -*- coding: utf-8 -*-
"""
Created on Thu May 16 20:49:32 2024

@author: user
"""
import math
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
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


class Long_Short_SMV(ff.Folder):
    def __init__(self,changable_var_dict,description=''):
        self.changable_var_dict=changable_var_dict
        super().__init__(self.__class__.__name__,description=description)    
        self._init_folder_dict()
        self._init_folder() # this function from folder.py
        
    def _init_folder_dict(self):
        self.folder_dict=self.get_folder_dict()
        self.folder_dict['folder_name']=self.name
        
    def get_folder_dict(self):
        
        self.folder_dict=dict()
        
        try:
            commodities=self.changable_var_dict['commodities']
            contract=self.changable_var_dict['contract']
            account=self.changable_var_dict['account']
            interval=self.changable_var_dict['interval']
            backtest_start_date=self.changable_var_dict['backtest_start_date']
            backtest_end_date=self.changable_var_dict['backtest_end_date']
            short_SMA_length=self.changable_var_dict['short_SMA_length']
            long_SMA_length=self.changable_var_dict['long_SMA_length']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
        # ---------------
        indicator_var_dict={'short_SMA_length':short_SMA_length,
                            'long_SMA_length':long_SMA_length}
        # account
        account.deposit(1000000)
        # tradingpanel
        tradingpanel=bt.TradingPanel(account)
        # commodities,marketdatas and indicators and append to tradingpanel
        indicators=dict()
        for commodity in commodities:
            # adjusted_backtest_start_date=backtest_start_date - timedelta(days=indicator_var_dict['long_SMA_length'])
            adjusted_backtest_start_date=backtest_start_date
            commodity_contract=commodity.marketdata[contract]
            if commodity.data_source=='yfinance':
                commodity_contract.automatic_get_data_from_yfinance(interval,adjusted_backtest_start_date,backtest_end_date)
            else:
                commodity_contract.get_data_from_xlsx(interval,adjusted_backtest_start_date,backtest_end_date)
            # already apend marketdata , you can get marketdata from commodity.marketdata[contract].data[interval]
            tradingpanel.append_marketdata(commodity_contract,interval)
            # indicator
            indicator_name='Double_SMA'
            indicator=bil.Indicator(indicator_name,commodity_contract,interval,indicator_var_dict=indicator_var_dict)
            indicators[str(commodity_contract.symbol+"_"+commodity_contract.contract+"_"+interval+"_"+indicator_name)]=indicator
            tradingpanel.append_indicator(commodity_contract,interval,indicator_name,indicator)
        
        
        
        folder_dict=self.changable_var_dict.copy()
        folder_dict.update({
            'tradingpanel':tradingpanel,
            'indicators':indicators
            })
    
        
        self.folder_dict=folder_dict
        
        return folder_dict

    def Long_Short_SMV(self,time_index):
        # get param from folder_dict
        try:
            # required
            account=self.folder_dict['account']
            interval=self.folder_dict['interval']
            tradingpanel=self.folder_dict['tradingpanel']
            commodities=self.folder_dict['commodities']
            contract=self.folder_dict['contract']
            backtest_start_date=self.folder_dict['backtest_start_date']
            backtest_end_date=self.folder_dict['backtest_end_date']
            indicators=self.folder_dict['indicators']
        except KeyError as e:
            raise ValueError(f'Folder dict miss var: {e}')
            
            
        # portfolio_optimizer
        portfolio_optimizer=bpo.PortfolioOptimizer(method='POSIIVE_RETURN')
        for commodity in commodities:
            new_data=commodity.marketdata[contract].data[interval]['Close']
            portfolio_optimizer.append_observed_df(new_data, col_name=commodity.name)
        
        
        
        
        for commodity in commodities:
            
            marketdata=commodity.marketdata[contract]
            indicator=indicators[str(marketdata.symbol+"_"+marketdata.contract+"_"+interval+"_"+'Double_SMA')]
            
            if time_index in indicator.data.index and (indicator.data.loc[time_index].notna().all()):
                
                loc = indicator.data.index.get_loc(time_index)
                # OHLC
                open_price=marketdata.data[interval].loc[time_index,'Open']
                high_price=marketdata.data[interval].loc[time_index,'High']
                low_price=marketdata.data[interval].loc[time_index,'Low']
                close_price=marketdata.data[interval].loc[time_index,'Close']
                
                net_position=account.inventory.get_net_position_size(marketdata.symbol+"_"+marketdata.contract)
                # entry_condition
                entry_condition1=indicator.data.loc[indicator.data.index[loc-1],'short_SMA']+1000>=indicator.data.loc[indicator.data.index[loc-1],'long_SMA']
                entry_condition2=net_position<=0
                entry_condition3=indicator.data.loc[indicator.data.index[loc-1],'short_SMA']<=indicator.data.loc[indicator.data.index[loc-1],'long_SMA']
                entry_condition4=net_position>=0
                # close_condition
                close_condition1=indicator.data.loc[indicator.data.index[loc],'short_SMA']<indicator.data.loc[indicator.data.index[loc],'long_SMA']-100000
                close_condition2=net_position>0
                close_condition3=indicator.data.loc[indicator.data.index[loc],'short_SMA']>indicator.data.loc[indicator.data.index[loc],'long_SMA']
                close_condition4=net_position<0
                
                # entry order
                # long_entry
                if entry_condition1 and entry_condition2:
                    
                    open_quantity=math.floor(account.balance/len(commodities)/(commodity.contract_size*open_price+commodity.fee))
                    # open_quantity=math.floor(account.cash/(commodity.margin_info['initial_margin']+commodity.fee))
                    # open_quantity=1
                    if open_quantity!=0:
                        order_1=account.orderbook.add_order('long',commodity,marketdata.contract,'market','long',self,time_index,quantity=open_quantity,price=0,remark='long_entry')
                # short_entry
                # if entry_condition3 and entry_condition4:
                #     open_quantity=math.floor(account.balance/len(commodities)/(commodity.contract_size*open_price+commodity.fee))
                # #     # open_quantity=math.floor(account.cash/(commodity.margin_info['initial_margin']+commodity.fee))
                # #     # open_quantity=1
                #     if open_quantity!=0:
                #         order_1=account.orderbook.add_order('short',commodity,marketdata.contract,'market','short',self,time_index,quantity=open_quantity,price=0,remark='short_entry')
                
                # close_order
                # long_close
                if close_condition1 and close_condition2:
                    close_quantity=abs(net_position)
                    order_2=account.orderbook.add_order('sell',commodity,marketdata.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0,remark='long_close')
                # short_close
                if close_condition3 and close_condition4:
                    close_quantity=abs(net_position)
                    order_2=account.orderbook.add_order('buytocover',commodity,marketdata.contract,'market on closing order','long',self,time_index,quantity=close_quantity,price=0,remark='short_close')
            
# ------------------------

def folder_main(changable_var_dict,show_balance=False,show_details=False,show_pnl=False):
    # folder
    folder=Long_Short_SMV(changable_var_dict)
    # backtest setting
    # commodities
    # contract
    # account
    # interval
    # --------------
    folder_dict=folder.show_folder_dict()
    # -------------------------------
    # main
    # backtest_dates
    backtest_start_date=changable_var_dict['backtest_start_date']
    backtest_end_date=changable_var_dict['backtest_end_date']
    
    return_dict=dict()
    return_dict=bb.single_interval_backtest(backtest_start_date=backtest_start_date,
                                            backtest_end_date=backtest_end_date,
                                            folder=folder,
                                            show_balance=show_balance,
                                            show_details=show_details,
                                            show_pnl=show_pnl
                                            )
    
    dict_to_pickle={'input':folder_dict,
                    'output':return_dict}
    
    
    return dict_to_pickle




