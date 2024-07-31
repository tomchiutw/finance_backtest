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


class F0002(ff.Folder):
    
    def __init__(self,changable_var_dict,description=''):
        self.changable_var_dict=changable_var_dict
        super().__init__(self.__class__.__name__,description=description)    
        self._init_folder_dict()
        self._init_folder() # this function from folder.py
        self.description='long sp or other index future when commidity_future last close> commodity_spot future close, can also add hedge strategy ex.vix'
        
    def _init_folder_dict(self):
        self.folder_dict=self.get_folder_dict()
        self.folder_dict['folder_name']=self.name
        
    
        
    # below code different strategy may different  
    def get_folder_dict(self):
        
        self.folder_dict=dict()
        
        try:
            account=self.changable_var_dict['account']
            index_future=self.changable_var_dict['index_future']
            commodity_future=self.changable_var_dict['commodity_future']
            commodity_spot=self.changable_var_dict['commodity_spot']
            interval=self.changable_var_dict['interval']
            contract=self.changable_var_dict['contract']
            backtest_start_date=self.changable_var_dict['backtest_start_date']
            backtest_end_date=self.changable_var_dict['backtest_end_date']
            short_entry_percentage=self.changable_var_dict['short_entry_percentage']
            short_close_percentage=self.changable_var_dict['short_close_percentage']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
            
        # ---------------------
        # account
        account.deposit(1000000)
        # -----------------
        # marketdata
        # contract ex.'c1'
        commodity_future_contract=commodity_future.marketdata[contract]
        if commodity_future.data_source=='yfinance':
            commodity_future_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
        else:
            commodity_future_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
        # spot
        commodity_spot_contract=commodity_spot.marketdata['spot']
        if commodity_spot.data_source=='yfinance':
            commodity_spot_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
        else:
            commodity_spot_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
        # index future ex. sp 500
        index_future_contract=index_future.marketdata[contract]
        if index_future.data_source=='yfinance':
            index_future_contract.automatic_get_data_from_yfinance(interval,backtest_start_date,backtest_end_date)
        else:
            index_future_contract.get_data_from_xlsx(interval,backtest_start_date,backtest_end_date)
        # -------------------------------
        # indicator
        # commodity settlement dates
        commodity_indicator_var_dict={'settlement_dates_list': commodity_future.settlement_dates}
        commodity_settlement_dates=bil.Indicator('Days_To_Next_Settlement_Dates',commodity_future_contract,interval,indicator_var_dict=commodity_indicator_var_dict)
        # index future settlement dates
        index_indicator_var_dict={'settlement_dates_list': index_future.settlement_dates}
        index_settlement_dates=bil.Indicator('Days_To_Next_Settlement_Dates',index_future_contract,interval,indicator_var_dict=index_indicator_var_dict)
        
        # ---------------------
        # tradingpanel
        tradingpanel=bt.TradingPanel(account)
        tradingpanel.append_marketdata(commodity_future_contract,interval)
        tradingpanel.append_marketdata(index_future_contract,interval)
        # ---------------------
        folder_dict=self.changable_var_dict.copy()
        folder_dict.update({
            'tradingpanel':tradingpanel,
            'commodity_settlement_dates':commodity_settlement_dates,
            'index_settlement_dates':index_settlement_dates,
            'marketdata_future':commodity_future_contract,
            'marketdata_spot':commodity_spot_contract,
            'marketdata_index_future':index_future_contract
            })
        
        self.folder_dict=folder_dict
        
        return folder_dict
    
    
    
    def F0002(self,time_index):
        # short commodity1
        try:
            # required
            account=self.folder_dict['account']
            interval=self.folder_dict['interval']
            tradingpanel=self.folder_dict['tradingpanel']
            # non required
            index_future=self.folder_dict['index_future']
            commodity_future=self.folder_dict['commodity_future']
            commodity_settlement_dates=self.folder_dict['commodity_settlement_dates']
            index_settlement_dates=self.folder_dict['index_settlement_dates']
            marketdata_future=self.folder_dict['marketdata_future']
            marketdata_spot=self.folder_dict['marketdata_spot']
            marketdata_index_future=self.folder_dict['marketdata_index_future']
            short_entry_percentage=self.folder_dict['short_entry_percentage']
            short_close_percentage=self.folder_dict['short_close_percentage']
            
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
    
# ----------------------------------------------------
        close_percentage=0.1
        if  time_index in index_settlement_dates.data.index and not np.isnan(index_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']) and \
                time_index in marketdata_spot.data[interval].index and time_index in marketdata_future.data[interval].index and time_index in marketdata_index_future.data[interval].index:
            pass
            
            index_settlement_dates_loc=index_settlement_dates.data.index.get_loc(time_index)
            commodity_settlement_dates_loc=commodity_settlement_dates.data.index.get_loc(time_index)
            marketdata_future_loc=marketdata_future.data[interval].index.get_loc(time_index)
            marketdata_spot_loc=marketdata_spot.data[interval].index.get_loc(time_index)
            marketdata_index_future_loc=marketdata_index_future.data[interval].index.get_loc(time_index)
            
            # OHLC
            open_price=marketdata_index_future.data[interval].loc[time_index,'Open']
            high_price=marketdata_index_future.data[interval].loc[time_index,'High']
            low_price=marketdata_index_future.data[interval].loc[time_index,'Low']
            close_price=marketdata_index_future.data[interval].loc[time_index,'Close']

            
            net_position=account.inventory.get_net_position_size(marketdata_index_future.symbol+"_"+marketdata_future.contract)
            last_commodity_future_close=marketdata_future.data[interval].loc[marketdata_future.data[interval].index[marketdata_future_loc-1],'Close']
            last_commodity_spot_close=marketdata_spot.data[interval].loc[marketdata_spot.data[interval].index[marketdata_spot_loc-1],'Close']
            spot_close=marketdata_spot.data[interval].loc[time_index,'Close']
            future_close=marketdata_future.data[interval].loc[time_index,'Close']
            # ------------------------------
            # entry_condition
            entry_condition1=net_position==0
            entry_condition2=index_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']>=2
            entry_condition3=last_commodity_spot_close<=last_commodity_future_close*(1+close_percentage)
           
           
            # long_entry order
            if entry_condition1 and entry_condition2 and entry_condition3:
                open_quantity=math.floor(account.balance/(index_future.contract_size*open_price+commodity_future.fee))
                if open_quantity!=0:
                    order_1=account.orderbook.add_order('long',index_future,marketdata_index_future.contract,'market','long',self,time_index,quantity=open_quantity,price=0,remark='long_entry')
           
           
            # ---------------------------------------------
            bb.single_interval_backtest_used_in_folder(time_index,account,tradingpanel,interval)
            # ---------------------------------------------------
           
            net_position=account.inventory.get_net_position_size(marketdata_index_future.symbol+"_"+marketdata_future.contract)
            # close_condition
            close_condition1=net_position>0
            close_condition2=index_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']<=2
            close_condition3=spot_close>=future_close*(1+close_percentage)
           
            # long_close_order
            if close_condition1:
                close_quantity=abs(net_position)    
                if close_condition2:
                    order_2=account.orderbook.add_order('sell',index_future,marketdata_index_future.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0,remark='long_close_settle')
                elif close_condition3:
                    order_2=account.orderbook.add_order('sell',index_future,marketdata_index_future.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0,remark='long_close')
             # -----------------------------------
# --------------------------

def folder_main(changable_var_dict,show_balance=False,show_details=False,show_pnl=False):


    # folder changable_var_dict->folder_dict(done inside folder)->return_dict(done inside backtest.py)
    folder=F0002(changable_var_dict)
    folder_dict=folder.show_folder_dict()
    # ---------------------
    # main
    # backtest_date
    backtest_start_date=changable_var_dict['backtest_start_date']
    backtest_end_date=changable_var_dict['backtest_end_date']
    return_dict=bb.single_interval_backtest(backtest_start_date=backtest_start_date,
                                            backtest_end_date=backtest_end_date,
                                            folder=folder,
                                            show_balance=show_balance,
                                            show_details=show_details,
                                            show_pnl=show_pnl
                                            )
    dict_to_pickle={'input':folder_dict,
                    'output':return_dict}

    # gg.save_var_to_pickle(dict_to_pickle,'test','test')
    return dict_to_pickle