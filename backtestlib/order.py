# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:47:57 2024

@author: user
"""
import os 
from datetime import datetime
import backtestlib.account as ba
import backtestlib.commodity as bc
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import generallib.general as gg

class Order:    
    def __init__(self,num,account,identity,commodity,contract,order_type,direction,folder,order_time,quantity,price=0,deal_price=None,deal_time=None,status=0,remark=''):
        '''
        Parameters
            account(ba.Account): from what account
            identity(str): used for specify order name
            commodity(bc.Commodity): commodity
            contract(str): appoint contract
            order_type(str) : 'limit' or 'market' or 'stop' or 'stop-limit' or 'market on opening order' or 'market on closing order'
            direction(str): 'long' or 'short'
            folder(str): set of strategy
            order_time(datetime): order time in type of datetime
            deal_time(datetime,opt): deal time in type of datetime.The default is None
            status(int,opt): deal or not, not deal then 0, deal then 1, canceled then -1.The default is 0
            remark(str,opt): any remark, the default is ''
        '''
        # common for different ticket created from same order
        self.num=num
        self.account=account
        self.identity=identity
        self.commodity=commodity
        self.contract=contract
        self.order_type=order_type
        self.direction=direction
        self.folder=folder
        self.order_time=order_time
        self.price=price        
        self.deal_price=deal_price
        self.deal_time=deal_time
        self.status=status
        self.remark=remark
        # when order_type is 'limit', price means limit price.
        # when order_type is 'stop', price means stop trigger price.
        
        self.quantity=quantity
        self.fee=commodity.fee*quantity
        
        
    # order_deal_start
    def get_data_for_checking_order_deal(self,tradingpanel,interval):
        if bt.get_marketdata_name(self.commodity.marketdata[self.contract],interval) not in tradingpanel.marketdatas:
            raise ValueError('Data for checking order deal not existed in TradingPanel. Try to use append_marketdata()')
        elif self.order_time not in tradingpanel.marketdatas[bt.get_marketdata_name(self.commodity.marketdata[self.contract],interval)].index:
            raise ValueError('TimeIndex for checking order deal not existed in data. Check data in TradingPanel. Maybe because of order_time not in trading hours')
        else:
            return tradingpanel.marketdatas[bt.get_marketdata_name(self.commodity.marketdata[self.contract],interval)][self.order_time:]
    
    # !!!!!!!! 補一個check_order_deal_for_deal_price_and_time only open 版本!!!!!!!!!!!!!!   
    def check_order_deal_for_deal_price_and_time(self,time_index,tradingpanel,interval):
        # just process order not deal, return 2 if skip, 1 if deal, 0 if not deal
        if self.status!=0:
            return 2
        # marketdata
        marketdata_df=self.get_data_for_checking_order_deal(tradingpanel, interval)
        # if time_index not in marketdata_df then return
        if time_index not in marketdata_df.index:
            return 2
        
        # order_type
        limit_type_list=['limit']
        market_type_list=['market','stop','market on opening order','market on closing order']
        
        # direction=='long'
        if self.direction=='long':
            # limit
            if self.order_type=='limit':
                # deal in open
                if self.price>=marketdata_df.loc[time_index,'Open']:
                    deal_price=gg.ceil_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
                elif self.price>=marketdata_df.loc[time_index,'Low']:
                    deal_price=gg.ceil_to_nearest_tick(self.price,self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
            # market and market on opening order
            if self.order_type=='market' or self.order_type=='market on opening order':
                deal_price=gg.ceil_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                self.set_deal_price_time_status(deal_price,time_index)
                return 1
            # market on closing order
            if self.order_type=='market on closing order':
                deal_price=gg.ceil_to_nearest_tick(marketdata_df.loc[time_index,'Close'],self.commodity.tick_size)
                self.set_deal_price_time_status(deal_price,time_index)
                return 1
            # stop
            if self.order_type=='stop':
                if self.price<=marketdata_df.loc[time_index,'Open']:
                    deal_price=gg.ceil_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    print(f'{time_index} stop at next day open')
                    return 1
                elif self.price<=marketdata_df.loc[time_index,'High']:
                    deal_price=gg.ceil_to_nearest_tick(self.price,self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
                
        # direction=='short'
        if self.direction=='short':
            # limit
            if self.order_type=='limit':
                # deal in open
                if self.price<=marketdata_df.loc[time_index,'Open']:
                    deal_price=gg.floor_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
                elif self.price<=marketdata_df.loc[time_index,'High']:
                    deal_price=gg.floor_to_nearest_tick(self.price,self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
            # market and market on opening order
            if self.order_type=='market' or self.order_type=='market on opening order':
                deal_price=gg.floor_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                self.set_deal_price_time_status(deal_price,time_index)
                return 1
            # market on closing order
            if self.order_type=='market on closing order':
                deal_price=gg.floor_to_nearest_tick(marketdata_df.loc[time_index,'Close'],self.commodity.tick_size)
                self.set_deal_price_time_status(deal_price,time_index)
                return 1
            # stop
            if self.order_type=='stop':
                if self.price>=marketdata_df.loc[time_index,'Open']:
                    deal_price=gg.floor_to_nearest_tick(marketdata_df.loc[time_index,'Open'],self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
                elif self.price>=marketdata_df.loc[time_index,'Low']:
                    deal_price=gg.floor_to_nearest_tick(self.price,self.commodity.tick_size)
                    self.set_deal_price_time_status(deal_price,time_index)
                    return 1
        return 0
            
    def set_deal_price_time_status(self,deal_price,deal_time):
        self.deal_price=deal_price
        self.deal_time=deal_time
        self.status=1
    
    def add_ticket(self):
        if self.status==0:
            raise ValueError('Order not deal but add_ticket is triggered, sth wrong')
        # establish key ticket_name fto inventory.tickets for specific commodity.contract's first ticket
        
        ticket_dict_name= bi.get_ticket_dict_name(self) 
        if ticket_dict_name not in self.account.inventory.tickets:
            self.account.inventory.tickets[ticket_dict_name] = None
        
        
        # if same directions
        self.account.inventory.create_ticket_dict_if_not_exist(ticket_dict_name)
        ticket=bi.Ticket(self.account.inventory,order=self)
        self.account.inventory.append_ticket_to_tickets(ticket,ticket_dict_name)
        return ticket
            
    def check_order_deal_and_add_ticket(self,time_index,tradingpanel,interval):
        # for whole process
        check_order_deal=self.check_order_deal_for_deal_price_and_time(time_index,tradingpanel,interval)
        if  check_order_deal==1:
            # ticket
            ticket=self.add_ticket()
            # account
            floating_asset_name=ba.get_floating_asset_dict_name(self)
            # if order.commodity.category is in margin list, then amount would be 0 and calculate used_cash
            margin_list=['future','option','currency_pair']
            
            # ########這裡要改 ###############################
            ticket.order.account.update_account_when_order_deal_and_add_ticket(ticket)
    
        else:
            check_order_deal=0
            
        return check_order_deal
    
    

    
class OrderBook:
    def __init__(self,account):
        '''
        One account create OrderBook at __init__

        Parameters:
            account(ba.Account): what account belongs to.
        '''
        self.cumulative_order_num=0
        # ex.orderbook.orders[order.num]=order
        self.orders={}
        self.account=account
        # create OrderBook in account.py by default
    def update_used_cash(self):
        '''
        used_cash is defined in ba.Account, for order_error(), add_order(), del_order()
        First, reset used_cash to 0. Then, check cash needed for orders in orderbook.
        Only commodity.category not 'stock' or 'bond' will be counted
        Note: category(str) includes stock, index, future, bond, or currency_pair
        Return:
            OrderBook.account.used_cash
        '''
        self.account.used_cash=0
        for order in self.orders.values():
            if  order.status==0: 
                if not (order.commodity.category=='stock' or order.commodity.category=='bond'):
                    # get net position if deal
                    self.account.used_cash+=order.commodity.margin_info['initial_margin']*order.quantity
        
        return self.account.used_cash
    
    def add_order(self,identity,commodity,contract,order_type,direction,folder,order_time,quantity,price=0,deal_time=None,status=0,remark=''):

        self.update_used_cash()
        
        if self.order_error(commodity,contract, order_type, direction, folder,commodity.fee,quantity,price)==False:
            order_num=self.get_next_cumulative_order_num()
            order=Order(order_num,self.account,identity,commodity,contract,order_type,direction,folder,order_time,quantity,price,remark=remark)
            self.orders[order_num]=order
        else:
            print("Add order fail")
        # always add at open, can be deal at close or anytime
        
        self.update_used_cash()
        
        # print(self.account.cash)
        
        return order
    
        
    def del_order(self,num,show_del_order=False):
        '''
        
        Parameters:
            identity(str): Order.identity

        ValueError:
            raise ValueError('Order identity not existed') if order not in OrderBook.orders, check by order.identity
        '''
        found_order = False
    
        for order_num, order in list(self.orders.items()):  # Use list to safely mutate the dictionary
            if order.num == num:
                if show_del_order:
                    order.status = -1  # Deactivate the order (soft delete)
                else:
                    del self.orders[order_num]  # Remove the order from the dictionary (hard delete)
                self.update_used_cash()  # Assume we need to update cash usage regardless of delete type
                found_order = True
                break
        
        if not found_order:
            raise ValueError('Order identity not existed')
        
    def order_error(self,commodity,contract,order_type,direction,folder,fee,quantity,price):
        # 1 commodity is tradable error
        if commodity.is_tradable==False:
            raise ValueError("This commodity is non-tradable")
        # 2 contract is defined
        if contract not in commodity.marketdata:
           raise ValueError("Contract is not defined.")
        elif not commodity.marketdata[contract].data:
            raise ValueError("Contract has no data.")
        # 3 order type isn't defined or is market but given price
        order_type_list=['limit','market','stop','market on opening order','market on closing order']
        no_price_list=['market','market on opening order','market on closing order']
        if order_type not in order_type_list:
            raise ValueError("Order_type not allowed. Please input type in list ['limit','market','stop','market on opening order','market on closing order']")
        if order_type in no_price_list and price!=0:
            raise ValueError('order type is market. Please reorder without limit price')
        if order_type not in no_price_list and price==0:
            raise ValueError('Please reorder with limit price or stop price')
        # 4 direction isn't defined
        direction_list=['long','short']
        if direction not in direction_list:
            raise ValueError("Direction not allowed. Please input 'long' or 'short'.")
        # 5 quantity equals 0
        if quantity==0:
            raise ValueError(f"Order.quantity isnt allowed to be zero.")
        # 6 cash not enough
        # first check net position
        net_position_size=self.account.inventory.get_net_position_size(commodity.symbol+"_"+contract)
        adjusted_quantity=self.account.inventory.adjusted_quantity_for_cost_or_margin_by_net_position_size(direction,quantity,commodity.symbol+"_"+contract)
        margin_list=['future','option','currency_pair','cfd']
        if commodity.category in margin_list:
            if self.account.cash-self.account.used_cash<(commodity.margin_info['initial_margin']+fee)*adjusted_quantity and \
                (commodity.margin_info['initial_margin']+fee)*adjusted_quantity!=0:
                raise ValueError(f"Not enough cash for margin. initial margin is {commodity.margin_info['initial_margin']}, adjusted quantity is {adjusted_quantity}, fee is {fee} .You got only {self.account.cash} in cash, {self.account.used_cash} in used cash , but you need {(commodity.margin_info['initial_margin']+fee)*adjusted_quantity}")
        
        
        
        return False
    
    def get_next_cumulative_order_num(self):
        self.cumulative_order_num+=1
        return self.cumulative_order_num