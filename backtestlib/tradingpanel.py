# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 00:00:58 2024


@author: user
"""
import pandas as pd
import os
import backtestlib.marketdata as bm 
import backtestlib.inventory as bi

class TradingPanel:
    '''
    one tradingpanel access one account
    '''
    def __init__(self,account):
        self.account=account
        # time_index update df
        self.marketdatas=dict()
        self.indicators=dict()
        # account balance, cash, floating assets 
        self.account_details=pd.DataFrame()
        self.pnl_details=pd.DataFrame()
        
        # time_index update dict
        self.orderbook_details=dict()
        self.inventory_details=dict()
        self.historical_transactions_details=dict()
        
        
        # 
    
    def update_orderbook_details(self,time_index,orders):
        
        index=[]
        data=[]
        for order in orders:
            try:
                other_data={
                    'identity':order.identity,
                    'account': order.account.name,
                    'commodity': order.commodity.symbol,
                    'contract': order.contract,
                    'order_type': order.order_type,
                    'direction': order.direction,
                    'folder': order.folder.name,
                    'order_time': order.order_time,
                    'fee': order.fee,
                    'price': order.price,
                    'quantity': order.quantity,
                    'deal_price': order.deal_price,
                    'deal_time': order.deal_time,
                    'status': order.status,
                    'remark': order.remark
                } 
                data.append(other_data)
                index.append(order.num)
            except AttributeError as e:
                raise ValueError(f"Error processing order: {e}")
        orderbook_details_df=pd.DataFrame(data,index=index)
        self.orderbook_details[time_index]= orderbook_details_df
       
        return self.orderbook_details 
    
    def update_inventory_details(self,time_index,tickets):
        index=[]
        data=[]
        for ticket_commodity_contract in tickets:
            for ticket in ticket_commodity_contract.values():
                try:
                    other_data={
                        # common
                        'account':  ticket.order.account.name,
                        'commodity':  ticket.order.commodity.symbol,
                        'contract':  ticket.order.contract,
                        'status': ticket.status,
                        'direction':  ticket.order.direction,
                        'folder':  ticket.order.folder.name,
                        # fee and quantity aren't common
                        'fee':  ticket.fee,
                        'quantity': ticket.quantity,
                        'price': ticket.order.deal_price,
                        'time': ticket.order.deal_time,
                        'unrealized_pnl': ticket.unrealized_pnl,
                        'remark': ticket.order.remark
                        # close
                    } 
                    data.append(other_data)
                    index.append(ticket.num)
                except AttributeError as e:
                    raise ValueError(f"Error processing order: {e}")
        inventory_details_df=pd.DataFrame(data,index=index)
        self.inventory_details[time_index]= inventory_details_df
       
        return self.inventory_details 
    
    def update_historical_transactions_details(self,time_index,transactions):
        index=[]
        data=[]
        for transaction in transactions:
            try:
                other_data={
                    # common
                    'account':  transaction.open_ticket.order.account.name,
                    'commodity':  transaction.open_ticket.order.commodity.symbol,
                    'contract':  transaction.open_ticket.order.contract,
                    'open_direction': transaction.open_direction,
                    'quantity': transaction.quantity,
                    'open_time': transaction.open_ticket.order.deal_time,
                    'close_time': transaction.close_ticket.order.deal_time,
                    'open_price': transaction.open_price,
                    'close_price': transaction.close_price,
                    'total_fee':  transaction.total_fee,
                    'realized_pnl': transaction.realized_pnl,
                    'folder':  transaction.open_ticket.order.folder.name,
                    'entry_remark': transaction.open_ticket.order.remark,
                    'close_remark': transaction.close_ticket.order.remark
                } 
                data.append(other_data)
                index.append(transaction.num)
            except AttributeError as e:
                raise ValueError(f"Error processing transaction: {e}")
        historical_transactions_details_df=pd.DataFrame(data,index=index)
        self.historical_transactions_details[time_index]= historical_transactions_details_df
       
        return self.historical_transactions_details
    
    def update_account_details(self, time_index):
        try:
            # Initialize data dictionary with balance and cash
            data = {
                'balance': self.account.balance,
                'cash': self.account.cash,
            }
            
            # Update data with floating assets
            # Here we assume self.account.floating_assets is a dictionary
            if hasattr(self.account, 'floating_assets'):
                data.update(self.account.floating_assets)
    
        except AttributeError as e:
            raise ValueError(f"Error processing account: {e}")
        
        # Convert the data dictionary to a DataFrame with a single row
        new_row = pd.DataFrame([data], index=[time_index])
        
        # Append this new row to the DataFrame of account details
        # We use ignore_index=False to preserve the specified index
        self.account_details = pd.concat([self.account_details, new_row])
       
        return self.account_details
    
    def update_pnl_details(self,time_index):
        
        data=dict()
        
        ticket_name_list_inventory=[ticket_name for ticket_name in self.account.inventory.tickets]
        ticket_name_list_transactions=[bi.get_ticket_dict_name(transaction.close_ticket.order) \
                                       for transaction in self.account.historical_transactions.transactions.values()]
        ticket_name_list=list(set(ticket_name_list_inventory+ticket_name_list_transactions))
        
        
        for ticket_name in ticket_name_list:
            sum_value=0
            # add unrealized pnl
            for ticket in self.account.inventory.tickets.get(ticket_name,{}).values():
                sum_value+=ticket.unrealized_pnl
            # add realized pnl
            for transaction in self.account.historical_transactions.transactions.values():
                if bi.get_ticket_dict_name(transaction.close_ticket.order)==ticket_name:
                    sum_value+=transaction.realized_pnl
            
            
            # get data 
            data[ticket_name]=sum_value
        
          # add to self.pnl_details
        
        # Convert the data dictionary to a DataFrame with a single row
        new_row = pd.DataFrame([data], index=[time_index])
        
        # Append this new row to the DataFrame of account details
        # We use ignore_index=False to preserve the specified index
        self.pnl_details = pd.concat([self.pnl_details, new_row])
        
        return self.pnl_details
        
    def append_marketdata(self,marketdata,interval):
        marketdata_name=get_marketdata_name(marketdata, interval)
        self.marketdatas[marketdata_name]=marketdata.data[interval]
    
    
    def return_marketdata_column_list(self,marketdata,interval,indicator_name):
        df=marketdata.data[interval]
        columns_list = df.columns.tolist()
        return columns_list

    def append_indicator(self,marketdata,interval,indicator_name,indicator_df):
        self.indicators[get_marketdata_name(marketdata,interval)+'_'+indicator_name]=indicator_df
    def get_indicator(self,marketdata,interval,indicator_name):
        if get_marketdata_name(marketdata,interval)+'_'+indicator_name in self.indicators:
            return self.indicators[get_marketdata_name(marketdata,interval)+'_'+indicator_name]
        else:
            raise ValueError("Indicator not existed")
    
def get_marketdata_name(marketdata,interval):
    return str(marketdata.symbol+"_"+marketdata.contract+"_"+interval)   
    
