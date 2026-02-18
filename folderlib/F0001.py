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


class F0001(ff.Folder):
    
    def __init__(self,changable_var_dict,description=''):
        self.changable_var_dict=changable_var_dict
        super().__init__(self.__class__.__name__,description=description)    
        self._init_folder_dict()
        self._init_folder() # this function from folder.py
        self.description='input short entry percentage and short close percentage, when spot<future then short. no trade withni 1 days before settlement dates.'
        
    def _init_folder_dict(self):
        self.folder_dict=self.get_folder_dict()
        self.folder_dict['folder_name']=self.name
        
    
        
    # below code different strategy may different  
    def get_folder_dict(self):
        
        self.folder_dict=dict()
        
        try:
            account=self.changable_var_dict['account']
            commodity_future=self.changable_var_dict['commodity_future']
            commodity_spot=self.changable_var_dict['commodity_spot']
            interval=self.changable_var_dict['interval']
            contract=self.changable_var_dict['contract']
            backtest_start_date=self.changable_var_dict['backtest_start_date']
            backtest_end_date=self.changable_var_dict['backtest_end_date']
            short_entry_percentage=self.changable_var_dict['short_entry_percentage']
            short_close_percentage=self.changable_var_dict['short_close_percentage']
            short_close_percentage_2=self.changable_var_dict['short_close_percentage_2']
            spread=self.changable_var_dict['spread']
            long_entry_percentage=self.changable_var_dict['long_entry_percentage']
            long_close_percentage=self.changable_var_dict['long_close_percentage']
            long_stop_percentage=self.changable_var_dict['long_stop_percentage']
            settlement=self.changable_var_dict['settlement']
            leverage=self.changable_var_dict['leverage']
            liability_percentage=self.changable_var_dict['liability_percentage']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
            
        # ---------------------
        # account
        account.deposit(1000000)
        liability=1000000*liability_percentage
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
        # -------------------------------
        # indicator
        indicator_high_percent=bil.Indicator('High_Percent',commodity_future_contract,interval)
        indicator_var_dict={'settlement_dates_list': commodity_future.settlement_dates}
        indicator_settlement_dates=bil.Indicator('Days_To_Next_Settlement_Dates',commodity_future_contract,interval,indicator_var_dict=indicator_var_dict)
        # settlement_dates
        
        # ---------------------
        # tradingpanel
        tradingpanel=bt.TradingPanel(account)
        tradingpanel.append_marketdata(commodity_future_contract,interval)
        # ---------------------
        folder_dict=self.changable_var_dict.copy()
        folder_dict.update({
            'tradingpanel':tradingpanel,
            'indicator_high_percent':indicator_high_percent,
            'indicator_settlement_dates':indicator_settlement_dates,
            'marketdata_future':commodity_future_contract,
            'marketdata_spot':commodity_spot_contract,
            'liability':liability
            })
        
        self.folder_dict=folder_dict
        
        return folder_dict
    
    
    
    def F0001(self,time_index):
        # short commodity1
        try:
            # required
            account=self.folder_dict['account']
            interval=self.folder_dict['interval']
            tradingpanel=self.folder_dict['tradingpanel']
            # non required
            commodity_future=self.folder_dict['commodity_future']
            indicator_high_percent=self.folder_dict['indicator_high_percent']
            indicator_settlement_dates=self.folder_dict['indicator_settlement_dates']
            marketdata_future=self.folder_dict['marketdata_future']
            marketdata_spot=self.folder_dict['marketdata_spot']
            short_entry_percentage=self.folder_dict['short_entry_percentage']
            short_close_percentage=self.folder_dict['short_close_percentage']
            short_close_percentage_2=self.folder_dict['short_close_percentage_2']
            spread=self.folder_dict['spread']
            long_entry_percentage=self.folder_dict['long_entry_percentage']
            long_close_percentage=self.folder_dict['long_close_percentage']
            long_stop_percentage=self.folder_dict['long_stop_percentage']
            settlement=self.folder_dict['settlement']
            leverage=self.folder_dict['leverage']
            liability=self.folder_dict['liability']
            
        except KeyError as e:
            raise ValueError(f'Missing variable when creating Folder: {e}')
        
     
        
        
        
        if time_index in indicator_high_percent.data.index and not np.isnan(indicator_high_percent.data.loc[time_index,'High_Percent']) and \
            time_index in indicator_settlement_dates.data.index and not np.isnan(indicator_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']) and \
                time_index in marketdata_spot.data[interval].index and time_index in marketdata_future.data[interval].index:

            # -----
            # bb.single_interval_backtest_used_in_folder(time_index,account,tradingpanel,interval)
            # -----
            
            indicator_settlement_dates_loc=indicator_settlement_dates.data.index.get_loc(time_index)
            indicator_high_percent_loc = indicator_high_percent.data.index.get_loc(time_index)
            marketdata_future_loc=marketdata_future.data[interval].index.get_loc(time_index)
            marketdata_spot_loc=marketdata_spot.data[interval].index.get_loc(time_index)
            
            # OHLC
            open_price=marketdata_future.data[interval].loc[time_index,'Open']
            high_price=marketdata_future.data[interval].loc[time_index,'High']
            low_price=marketdata_future.data[interval].loc[time_index,'Low']
            close_price=marketdata_future.data[interval].loc[time_index,'Close']
            spot_close=marketdata_spot.data[interval].loc[time_index,'Close']
            
            net_position=account.inventory.get_net_position_size(marketdata_future.symbol+"_"+marketdata_future.contract)
            last_future_close=marketdata_future.data[interval].loc[marketdata_future.data[interval].index[marketdata_future_loc-1],'Close']
            last_future_low=marketdata_future.data[interval].loc[marketdata_future.data[interval].index[marketdata_future_loc-1],'Low']
            last_future_open=marketdata_future.data[interval].loc[marketdata_future.data[interval].index[marketdata_future_loc-1],'Open']
            last_spot_close=marketdata_spot.data[interval].loc[marketdata_spot.data[interval].index[marketdata_spot_loc-1],'Close']
            # new
            last_spot_high=marketdata_spot.data[interval].loc[marketdata_spot.data[interval].index[marketdata_spot_loc-1],'High']
            spot_close_2nd=marketdata_spot.data[interval].loc[marketdata_spot.data[interval].index[marketdata_spot_loc-2],'Close']
            
            # entry_condition
            entry_condition1=indicator_high_percent.data.loc[indicator_high_percent.data.index[indicator_high_percent_loc-1],'High_Percent']<short_entry_percentage
            entry_condition2=open_price<last_future_close*(1+short_close_percentage)
            entry_condition3=net_position==0
            entry_condition4=indicator_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']>settlement
            entry_condition5=last_spot_close<last_future_close*(1+spread)
            entry_condition6=last_spot_close>last_future_close*(1+long_entry_percentage)
            entry_condition7=last_future_close*(1-long_stop_percentage)<open_price
    



            # del_condition
            del_condition1=any(order.order_type=='stop' for order in account.orderbook.orders.values())
            
            
            # del stop order
            if del_condition1:
                stop_order_nums=[order.num for order in account.orderbook.orders.values() if order.order_type=='stop' and order.status!=1]
                for num in stop_order_nums:
                    account.orderbook.del_order(num,show_del_order=False)
            # short_entry order
            if entry_condition1 and entry_condition2 and entry_condition3 and entry_condition4 and entry_condition5  \
                :
                open_quantity=math.floor(leverage*(account.balance+liability)/(commodity_future.contract_size*open_price+commodity_future.fee))
                if open_quantity!=0:
                    order_1=account.orderbook.add_order('short',commodity_future,marketdata_future.contract,'market','short',self,time_index,quantity=open_quantity,price=0,remark='short_entry')
            
            # long_entry order
            # if entry_condition3 and entry_condition4 and entry_condition6:
            #     open_quantity=math.floor(leverage*(account.balance+liability)/(commodity_future.contract_size*open_price+commodity_future.fee))
            #     if open_quantity!=0:
            #         order_1=account.orderbook.add_order('long',commodity_future,marketdata_future.contract,'market','long',self,time_index,quantity=open_quantity,price=0,remark='long_entry')
            # ---------------------------------------------
            bb.single_interval_backtest_used_in_folder(time_index,account,tradingpanel,interval)
            # ---------------------------------------------------
            
            net_position=account.inventory.get_net_position_size(marketdata_future.symbol+"_"+marketdata_future.contract)
            # close_condition
            close_condition1=net_position<0
            close_condition2=indicator_settlement_dates.data.loc[time_index,'Days_To_Next_Settlement_Dates']<=settlement+1
            close_condition3=net_position>0
            close_condition4=spot_close<=close_price*(1+long_close_percentage)
            close_condition5=last_future_close*(1-long_stop_percentage)>low_price
            
            
            # short_close_order
            if close_condition1:
                if not close_condition2:
                    close_quantity = abs(net_position)
                    stop_price = last_future_close * (1 + short_close_percentage)
                    remark = f'short_close_stop|date:{time_index.strftime("%Y-%m-%d")}|entry:{last_future_close:.2f}|pct:{short_close_percentage:.4f}|stop:{stop_price:.2f}'
                    order_2 = account.orderbook.add_order(
                        'buytocover',
                        commodity_future,
                        marketdata_future.contract,
                        'stop',
                        'long',
                        self,
                        time_index,
                        quantity=close_quantity,
                        price=stop_price,
                        remark=remark
                    )
                elif close_condition2:
                    now_high_price = marketdata_future.data[interval].loc[time_index,'High']
                    stop_price = last_future_close * (1 + short_close_percentage)
                    # sth unreasonable that we use todays future high, but needs to use here due to programme limitaion.
                    if now_high_price >= stop_price:
                        close_quantity = abs(net_position)
                        remark = f'short_close_stop|date:{time_index.strftime("%Y-%m-%d")}|entry:{last_future_close:.2f}|pct:{short_close_percentage:.4f}|stop:{stop_price:.2f}|settlement'
                        order_2 = account.orderbook.add_order(
                            'buytocover',
                            commodity_future,
                            marketdata_future.contract,
                            'stop',
                            'long',
                            self,
                            time_index,
                            quantity=close_quantity,
                            price=stop_price,
                            remark=remark
                        ) 
                    else:
                        close_quantity = abs(net_position)
                        remark = f'short_close_settle|date:{time_index.strftime("%Y-%m-%d")}|close:{close_price:.2f}'
                        order_2 = account.orderbook.add_order(
                            'buytocover',
                            commodity_future,
                            marketdata_future.contract,
                            'market on closing order',
                            'long',
                            self,
                            time_index,
                            quantity=close_quantity,
                            price=0,
                            remark=remark
                        )
            # long_close_order
            # if close_condition3:
            #     if not close_condition2:
            #         if close_condition4 :
            #             close_quantity=abs(net_position)
            #             order_2=account.orderbook.add_order('sell',commodity_future,marketdata_future.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0,remark='long_close')
            #     elif close_condition2:
            #         close_quantity=abs(net_position)
            #         order_2=account.orderbook.add_order('sell',commodity_future,marketdata_future.contract,'market on closing order','short',self,time_index,quantity=close_quantity,price=0,remark='long_close_settle')
# --------------------------

def folder_main(changable_var_dict,show_balance=False,show_details=False,show_pnl=False):


    # folder changable_var_dict->folder_dict(done inside folder)->return_dict(done inside backtest.py)
    folder=F0001(changable_var_dict)
    # --------------------------------------------
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