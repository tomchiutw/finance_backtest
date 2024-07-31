# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 23:57:53 2023

@author: user
"""
import sys
import warnings
import backtestlib.order as bo
import backtestlib.inventory as bi
# 忽略所有警告
warnings.filterwarnings("ignore")


class Account:
    def __init__(self,account_manager,currency='USD',name='1st_account'):
        '''
        Notes:
            create OrderBook as default.
            used_cash is for checking OrderBook.add_order

        '''
        self.account_manager=account_manager
        self.currency = currency
        self.name=name
        self.balance = 0                  
        self.cash=0
        self.used_cash=0
        self.floating_assets={}
        self.margin=0
        self.orderbook=bo.OrderBook(self)
        self.inventory=bi.Inventory(self)
        self.historical_transactions=bi.Historical_Transactions(self)
        
    def reset(self):
        '''
        Reset the account to its initial state.
        '''
        self.balance = 0
        self.cash = 0
        self.used_cash = 0
        self.floating_assets = {}
        self.margin = 0
        self.orderbook = bo.OrderBook(self)
        self.inventory = bi.Inventory(self)  
        self.historical_transactions = bi.Historical_Transactions(self)
        
    def deposit(self, amount):
        '''
        deposit in cash

        Parameters:
            amount(int): number for deposit
        '''
        self.cash += amount

    # def update_used_cash

    def withdraw(self, amount):
        '''
        withdraw in cash

        Parameters:
            amount(int): number for deposit
        ValueError:
            raise error if cash isn't enough
        '''
        if amount <= self.cash:
            self.cash -= amount
        else:
            raise ValueError("Cash isn't enough. Try to use Account.deposit()")
            
    def transfer_cash_to_floating_asset(self,floating_asset_name,amount):
        '''
        transfer cash to specific floating asset to record equity

        Parameters:
            floating_asset_name(str) : name of floating asset
            amount(int) : transfered amount
        ValueError:
            raise error if cash isn't enough

        '''
        if amount <= self.cash:
            self.cash -= amount
            self.floating_assets[floating_asset_name]+=amount
        else:
            raise ValueError(f'Cash isnt enough. You got only {self.cash} in cash, but try to transfer {amount}. Try to use Account.deposit()')
            
    def create_floating_asset_if_not_exist(self, floating_asset_name):
        '''
        create specific floating asset for recording equity

        Parameters
            floating_asset_name(str) : name of floating asset
            amount(int): primary amount
        '''
        if floating_asset_name not in self.floating_assets:
            self.floating_assets[floating_asset_name] = 0

        
    def transfer_floating_asset_to_cash(self,floating_asset_name,amount):
        
        if floating_asset_name in self.floating_assets:
            self.cash +=amount
            self.floating_assets[floating_asset_name]-=amount
        else:
            raise ValueError(f"Floating asset '{floating_asset_name}' not found")


    def update_balance_from_floating_assets_cash(self):
        '''
        update balance by summing all floating asstes and cash

        '''
        self.balance=sum(self.floating_assets.values())+ self.cash
    
    def update_account(self):
        # update floating_assets by tickets
        
        value_for_check_margin=0
        for ticket_commodity_contract_name,ticket_commodity_contract in self.inventory.tickets.items():
            self.floating_assets[ticket_commodity_contract_name]=0
            for ticket in ticket_commodity_contract.values():
                value=ticket.cost+ ticket.unrealized_pnl
                self.floating_assets[ticket_commodity_contract_name]+=value
                # check if ticket_commodity_contract.value < maintenance_margin
                margin_list=['future','option','currency_pair']
                if ticket.order.commodity.category in margin_list:
                    value_for_check_margin+=ticket.order.commodity.margin_info['maintenance_margin']*ticket.quantity
                    
        
        if sum(self.floating_assets.values())+ self.cash<value_for_check_margin:
            print(f" Maintenance Margin is {value_for_check_margin}. You got only {sum(self.floating_assets.values())+ self.cash} in balance.You need more cash")
            self.update_balance_from_floating_assets_cash()
            return False
        # check if cash<0 
        
        # update balance
        self.update_balance_from_floating_assets_cash()
        
        return True
        
    def update_account_when_order_deal_and_add_ticket(self,ticket):
        floating_asset_name=get_floating_asset_dict_name(ticket.order)
        self.create_floating_asset_if_not_exist(floating_asset_name)
        self.transfer_cash_to_floating_asset(floating_asset_name,ticket.cost)
        
    def update_account_when_add_transaction(self,transaction):
        pass
        # del open_ticket, close_ticket 's cost in transaction
        floating_asset_name=get_floating_asset_dict_name(transaction.open_ticket.order)
        amount=transaction.open_ticket.cost+transaction.close_ticket.cost+transaction.realized_pnl
        self.transfer_floating_asset_to_cash(floating_asset_name,amount)
        
class AccountManager:
    
    def __init__(self):
        self.accounts = {}    
        self.init_account()
        
    def init_account(self):
        '''
        do in __init__. do create_new_account()
        '''
        self.create_new_account()
        # print("Already create new account(currency='USD',name='1st_account') by default")
        
    def create_new_account(self,currency='USD',name='1st_account'):
        '''
        create new account
        
        Parameters:
            currency(str,opt): The default is 'USD'
            name(str,opt): The default is '1st_account'
    
        '''
        if name in self.accounts:
            raise ValueError ('Account is existed')
        else:
            new_account=Account(self,currency,name)
            self.accounts[name]=new_account

# func not in class    
def get_floating_asset_dict_name(order):
    return str(order.commodity.symbol+"_"+order.contract) 
        
    

