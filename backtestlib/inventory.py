# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 14:06:18 2024

@author: user
"""

import os 
from datetime import datetime
import backtestlib.account as ba
import backtestlib.commodity as bc
import backtestlib.tradingpanel as bt
import backtestlib.order as bo
import generallib.general as gg

class Ticket:
    def __init__(self,inventory,order):
        # ticket_num
        self.num=inventory.get_next_cumulative_ticket_num()
        # status 0=open, 1=close
        self.status=0
        # order
        self.order=order
        # come from same order but may not same 
        self.quantity=order.quantity # by default, should be revise if divided
        self.fee=order.commodity.fee*self.quantity
        self.__init__ticket_cost()
        self.unrealized_pnl=0
        
    def __init__ticket_cost(self):
        ticket_dict_name=get_ticket_dict_name(self.order)
        adjusted_quantity= \
            self.order.account.inventory.adjusted_quantity_for_cost_or_margin_by_net_position_size(self.order.direction \
                                                                             ,self.quantity,ticket_dict_name)
        margin_list=['future','option','currency_pair']
        if self.order.commodity.category in margin_list:
            self.cost=adjusted_quantity*self.order.commodity.margin_info['initial_margin']
        elif self.order.commodity.category not in margin_list:
            self.cost=adjusted_quantity*self.order.deal_price*self.order.commodity.contract_size
            

        
    def reset_quantity_fee_cost(self,quantity):
        self.quantity=quantity
        self.fee=self.order.commodity.fee*self.quantity
        self.__init__ticket_cost()
        
    def update_unrealized_pnl_at_close(self,time_index,tradingpanel,interval):
        marketdata_df=self.order.get_data_for_checking_order_deal(tradingpanel, interval)
        if time_index not in marketdata_df.index:
            # if no data in marketdata_df may because of not in trading hours
            # then unrealized_pnl equals to last unrealized_pnl 
            return
        close=marketdata_df.loc[time_index,'Close']
        if self.order.direction=='long':
            self.unrealized_pnl=self.quantity*(close-self.order.deal_price)*self.order.commodity.contract_size-self.fee
        elif self.order.direction=='short':
            self.unrealized_pnl=self.quantity*(self.order.deal_price-close)*self.order.commodity.contract_size-self.fee
        
        # account
        
        
        return self.unrealized_pnl
        
class Inventory:
    def __init__(self,account):
        # ex. inventory.tickets[ticket_dict_name][ticket.num]=ticket
        self.tickets=dict()
        self.cumulative_ticket_num=0
        self.total_unrealized_pnl=0
        self.account=account
    
    def get_net_position_size(self,ticket_dict_name):
        net_position_size=0
        if ticket_dict_name not in self.tickets:
            return net_position_size
        else:
            for ticket in self.tickets[ticket_dict_name].values():
                if ticket.order.direction=='long':
                    net_position_size+=ticket.quantity
                elif ticket.order.direction=='short':
                    net_position_size-=ticket.quantity
                    
        return net_position_size
        
    def get_next_cumulative_ticket_num(self):
        self.cumulative_ticket_num+=1
        return self.cumulative_ticket_num

    def create_ticket_dict_if_not_exist(self,ticket_dict_name):
        if ticket_dict_name not in self.tickets or self.tickets[ticket_dict_name] is None:
            self.tickets[ticket_dict_name] = {}

    def append_ticket_to_tickets(self,ticket,ticket_dict_name):
        self.create_ticket_dict_if_not_exist(ticket_dict_name)
        self.tickets[ticket_dict_name][ticket.num]=ticket
        
    def sort_tickets_by_deal_time_asc(self,ticket_dict_name):
        if ticket_dict_name in self.tickets and self.tickets[ticket_dict_name] is not None:
            sorted_tickets=sorted(self.tickets[ticket_dict_name].values(), key=lambda ticket: ticket.order.deal_time)
            sorted_tickets_dict={ticket.num: ticket for ticket in sorted_tickets}
            self.tickets[ticket_dict_name]=sorted_tickets_dict
            return sorted_tickets_dict
        else:
            return {}
        
    def get_first_ticket_num(self, ticket_dict_name):
        if ticket_dict_name in self.tickets and self.tickets[ticket_dict_name]:
            first_ticket = next(iter(self.tickets[ticket_dict_name].values()))
            return first_ticket.num
        else:
            raise ValueError("The ticket dictionary is empty or does not exist.")
            
    
    def del_ticket(self,ticket_dict_name,ticket_num):
        if ticket_dict_name in self.tickets and self.tickets[ticket_dict_name] is not None:
            del self.tickets[ticket_dict_name][ticket_num]
    
    def divide_ticket_and_del_origin_one(self,ticket,quantity_1):
        if ticket.quantity<=quantity_1:
            raise ValueError("tickey.quantity is equal or less than Quantity for divide")
        quantity_2=ticket.quantity-quantity_1
        # same order same tickeet_dict_name
        ticket_dict_name=get_ticket_dict_name(ticket.order)
        # first create new ticket, quantity=quantity_1, change quantity and fee by reset_quantity_fee_cost()
        ticket_1=Ticket(ticket.order.account.inventory,order=ticket.order)
        ticket_1.reset_quantity_fee_cost(quantity_1)
        self.append_ticket_to_tickets(ticket_1,ticket_dict_name)
        # then create new ticket, quantity=quantity_2
        ticket_2=Ticket(ticket.order.account.inventory,order=ticket.order)
        ticket_2.reset_quantity_fee_cost(quantity_2)
        self.append_ticket_to_tickets(ticket_2,ticket_dict_name)
        # del origin one
        self.del_ticket(ticket_dict_name,ticket.num)
        # sort tickeet by time again
        self.sort_tickets_by_deal_time_asc(ticket_dict_name)
    
    def get_long_short_earliest_position(self,ticket_dict_name):
        
        first_long_ticket=None
        first_short_ticket=None
        if ticket_dict_name in self.tickets and self.tickets[ticket_dict_name]:
            for ticket in self.tickets[ticket_dict_name].values():
                if first_long_ticket is not None and first_short_ticket is not None:
                    break
                # find earliest long ticket
                if ticket.order.direction=='long' and first_long_ticket is None:
                    first_long_ticket=ticket
                    continue
                # find earliest short ticket
                if ticket.order.direction=='short' and first_short_ticket is None:
                    first_short_ticket=ticket
                    continue
        if first_long_ticket is not None and first_short_ticket is not None:
            
            if first_long_ticket.order.deal_time < first_short_ticket.order.deal_time:
                return {'Open': first_long_ticket, 'Close': first_short_ticket}
            else:
                return {'Open': first_short_ticket, 'Close': first_long_ticket}
        else:
            return {}

    def add_transaction_and_reset_status_and_del_tickets(self,first_ticket_dict):
        # reset status
        first_ticket_dict['Open'].status=1
        first_ticket_dict['Close'].status=1
        # add transaction
        transaction=Transaction(first_ticket_dict['Open'].order.account.historical_transactions,first_ticket_dict['Open'],first_ticket_dict['Close'])
        first_ticket_dict['Open'].order.account.historical_transactions.append_transaction_to_historical_transactions(transaction)
        # update_account
        self.account.update_account_when_add_transaction(transaction)
        # del
        self.del_ticket(get_ticket_dict_name(first_ticket_dict['Open'].order),first_ticket_dict['Open'].num)
        self.del_ticket(get_ticket_dict_name(first_ticket_dict['Close'].order),first_ticket_dict['Close'].num)


    def first_in_first_out_by_ticket_dict_name(self,ticket_dict_name):
        # sort first
        self.sort_tickets_by_deal_time_asc(ticket_dict_name)
        first_ticket_dict= \
            self.get_long_short_earliest_position(ticket_dict_name)
        if  not first_ticket_dict:
            return
    
        if first_ticket_dict['Open'].quantity==first_ticket_dict['Close'].quantity:
            # only condition that add transacation
            self.add_transaction_and_reset_status_and_del_tickets(first_ticket_dict)
            # update account please
        elif first_ticket_dict['Open'].quantity>first_ticket_dict['Close'].quantity:
            self.divide_ticket_and_del_origin_one(first_ticket_dict['Open'],first_ticket_dict['Close'].quantity)
        elif first_ticket_dict['Open'].quantity<first_ticket_dict['Close'].quantity:
            self.divide_ticket_and_del_origin_one(first_ticket_dict['Close'],first_ticket_dict['Open'].quantity)
        # for recursion
        first_ticket_dict= \
            self.get_long_short_earliest_position(ticket_dict_name)
        if first_ticket_dict:
            self.first_in_first_out_by_ticket_dict_name(ticket_dict_name)
            
    
    def update_tickets_unrealized_pnl(self,time_index,tradingpanel,interval):
        
        total_unrealized_pnl=0
        for ticket_commodity_contract_name,ticket_commodity_contract in self.tickets.items():
            self.account.floating_assets[ticket_commodity_contract_name]=0
            for ticket in ticket_commodity_contract.values():
                ticket_unrealized_pnl=ticket.update_unrealized_pnl_at_close(time_index,tradingpanel,interval)
                if total_unrealized_pnl is not None:
                    total_unrealized_pnl+=total_unrealized_pnl
                    self.total_unrealized_pnl=total_unrealized_pnl
        return self.total_unrealized_pnl
    
    def adjusted_quantity_for_cost_or_margin_by_net_position_size(self,direction,quantity,ticket_dict_name):
        net_position_size=self.get_net_position_size(ticket_dict_name)
        # long
        if direction=='long':
            if net_position_size>=0:
                return quantity
            elif net_position_size<0:
                if quantity+net_position_size<=0:
                    return 0
                elif quantity+net_position_size>0:
                    return quantity+net_position_size
        # short
        if direction=='short':
            if net_position_size<=0:
                return quantity
            elif net_position_size>0:
                if quantity+net_position_size>=0:
                    return 0
                elif quantity+net_position_size<0:
                    return abs(quantity+net_position_size)
    
    
class Transaction:
    def __init__(self,historical_transactions,open_ticket,close_ticket):
        
        self.num=historical_transactions.get_next_cumulative_transaction_num()
        self.open_direction=open_ticket.order.direction
        self.open_ticket=open_ticket
        self.close_ticket=close_ticket
        self.open_price=open_ticket.order.deal_price
        self.close_price=close_ticket.order.deal_price
        # check quantity
        self.__init__quantity()
        self.total_fee=open_ticket.fee+close_ticket.fee
        # realized_pnl
        self.__init__realized_pnl()
    def __init__quantity(self):
        if self.open_ticket.quantity!=self.close_ticket.quantity:
            raise ValueError('Quantity not same when creating Transaction')
        else:
            self.quantity=self.open_ticket.quantity
        
    def __init__realized_pnl(self):
        
        if self.open_ticket.order.direction=='long' and  self.close_ticket.order.direction=='short':
            # quantity*(close_price-open_price)*contract_size-total_fee
            self.realized_pnl=self.quantity*(self.close_price-self.open_price)*self.open_ticket.order.commodity.contract_size-self.total_fee
        elif self.open_ticket.order.direction=='short' and  self.close_ticket.order.direction=='long':
            # quantity*(open_price-close_price)-total_fee
            self.realized_pnl=self.quantity*(self.open_price-self.close_price)*self.open_ticket.order.commodity.contract_size-self.total_fee
        else:
            raise ValueError('open and close ticket are both long or short')
            
class Historical_Transactions:
    
    def __init__(self,account):
        self.transactions={}
        self.cumulative_transaction_num=0
    def get_next_cumulative_transaction_num(self):
        self.cumulative_transaction_num+=1
        return self.cumulative_transaction_num
    def append_transaction_to_historical_transactions(self,transaction):
        self.transactions[transaction.num]=transaction
        
    
    
# func not in class    
def get_ticket_dict_name(order):
    return str(order.commodity.symbol+"_"+order.contract)
