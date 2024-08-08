# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:41:12 2024

@author: user
"""

import sys
import os
import pandas as pd
import numpy as np
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
import generallib.error_pop as ep


# for backtest
def single_interval_backtest(backtest_start_date,backtest_end_date,folder,show_balance=False,show_details=False,show_pnl=False):
    '''
    before backtest, user must set basic information in order in the main py:
        backtest_range->folder
        
    folder.folder_dict must include interval,account,tradingpanel

    '''
    orderbook_dict=dict()
    inventory_dict=dict()
    historical_transactions_dict=dict()
    pnl_details=pd.DataFrame()
    
    interval=folder.folder_dict['interval']
    account=folder.folder_dict['account']
    tradingpanel=folder.folder_dict['tradingpanel']
    
    
    do_count=False
    margin_error_break=False
    # start backtest
    backtest_date_range=gg.get_backtest_date_range(backtest_start_date,backtest_end_date,interval)
    
    for time_index in backtest_date_range:
        
        
        #  to prevent none of data in marketdata include in backtest_date_range
        do_count=True
        
        # folder, include entry,close condition and order
        getattr(folder,folder.name)(time_index)
        
        # update order and ticket in specific most tiny interval
        for order in account.orderbook.orders.values():
            # skip if order dealed before
            if order.status!=0:
                continue
            check_order_deal=order.check_order_deal_and_add_ticket(time_index,tradingpanel,interval)
            # check_order_deal is 1 if new order dealed and new ticket added, else 2 or 0
            if check_order_deal==0:
                continue
            # updata ticket to transactions only if new transaction should be added, checked by check_order_deal
            ticket_dict_name=bi.get_ticket_dict_name(order)
            account.inventory.first_in_first_out_by_ticket_dict_name(ticket_dict_name)
        
        
        # update only once in one time_index
        # update inventory market value at close
        total_unrealized_pnl=account.inventory.update_tickets_unrealized_pnl(time_index,tradingpanel,interval)
        margin_error_break=account.update_account()
        # update dict or df for showing in tradingpanl
        if show_details==True:
            orderbook_dict=tradingpanel.update_orderbook_details(time_index,account.orderbook.orders.values())
            inventory_dict=tradingpanel.update_inventory_details(time_index,account.inventory.tickets.values())
            historical_transactions_dict=tradingpanel.update_historical_transactions_details(time_index,account.historical_transactions.transactions.values())
        if show_pnl:
            pnl_details=tradingpanel.update_pnl_details(time_index)
            
        account_details=tradingpanel.update_account_details(time_index)
    
        # margin
        if margin_error_break==False:
            print(f'{time_index}: margin_error_break')
            break
    # none of data in marketdata include in backtest_date_range
    if do_count==False:
        raise ValueError('none of data in marketdata include in backtest_date_range. Please get more data for marketdata.')
    
    # plot and performance
    if show_balance:
        plt_balance=gp.plot_all_columns_together(account_details,show_only_balance=True)
    if show_pnl:
        plt_balance=gp.plot_all_columns_together(pnl_details,show_only_balance=False)
    performance_series=bp.getPortfolio_Series(account_details,'balance',0.02,translate=False)

    # return dict
    return_dict={
        'account_class':account,
        'account_details':account_details,
        'orderbook':orderbook_dict,
        'inventory':inventory_dict,
        'historical_transactions':historical_transactions_dict,
        'pnl':pnl_details,
        'performance':performance_series
        }
    
    # end backtest
    # print('backtest success')
    
    return return_dict
    
def single_interval_backtest_used_in_folder(time_index,account,tradingpanel,interval):
    for order in account.orderbook.orders.values():
        # skip if order dealed before
        if order.status!=0:
            continue
        check_order_deal=order.check_order_deal_and_add_ticket(time_index,tradingpanel,interval)
        # check_order_deal is 1 if new order dealed and new ticket added, else 2 or 0
        if check_order_deal==0:
            continue
        # updata ticket to transactions only if new transaction should be added, checked by check_order_deal
        ticket_dict_name=bi.get_ticket_dict_name(order)
        account.inventory.first_in_first_out_by_ticket_dict_name(ticket_dict_name)
    
    

    