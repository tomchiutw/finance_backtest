# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:07:16 2024

@author: user
"""
import os
import yfinance as yf
import pandas as pd
import generallib.general as gg
import backtestlib.marketdata as bm
import get_base_dir as gbd


class Commodity:
        def __init__(self,name,symbol,category,currency,tick_size,contract_size,fee,data_source,contract_list=['default'],exchange='',is_tradable=True,notes='',**kwargs):
             '''
             Initialize a Commodity object
             
             Parameters:
                 symbol(str): 
                 category(str): stock,cfd, index, future, bond, or option or currency_pair
                 currency(str): 
                 contract size(float):
                 exchange(str,optional): exchange
                 is_tradable(bool,optional): whether this commodity is tradable
                 notes(str,optional): 
             Keyword Arguments:
                 margin_info(dict, optional):
                     ex. margin_info['initial_margin']=12580
                     
            Notes:
                for importing marketdata, first append contract as keyword for dict of marketdata
             '''
             self.name=name
             self.symbol=symbol
             self.category=category
             self.currency=currency
             self.tick_size=tick_size
             self.contract_size=contract_size
             self.fee=fee
             self.contract_list=contract_list
             self.exchange=exchange
             self.is_tradable=is_tradable
             self.notes=notes
             self.data_source=data_source
             
             self.marketdata=dict()
             self.kwargs=kwargs
             # append dict of marketdara by function after knowing marketdata.contract
             self.init_marketdata()
             # check if this commodity needs margin_info 
             self.init_margin_list_error()
             # settlement dates
             self.init_settlement_dates()
             
        def append_commodity_contract_list(self,contract_list):
            for contract in contract_list:
                self.contract_list.append(contract)
                self.append_marketdata_contract_dict(contract)
        
        def append_marketdata_contract_dict(self,contract='default'):
            '''
            append keyword in dict of marketdata
            
            Parameters:
                contract(str,optional): set 'default' if not specified, maybe appoint 'spot', 'c1','202406'

            '''
            self.marketdata[contract]=bm.MarketData(self.symbol,self.category,self.currency,contract)
        def init_marketdata(self):
            '''
            do in __init__. do append_marketdata_contract_dict(self,contract='default'), which append 'default'
            '''
            for contract in self.contract_list:
                self.append_marketdata_contract_dict(contract)
            # print(f'Already append {self.symbol}.marketdata{self.contract_list} as default contract')
            
        def init_margin_list_error(self):
            '''
            ValueError:
                do in __init__. raise 'Please enter margin_info in type of dict' if commodity.category is 
            in margin_list and existence of input of kwargs('margin_info')
            '''
            # ask for margin_info if needed
            margin_list=['future','option','currency_pair','cfd']
            if self.category.lower() in margin_list:
                margin_info=self.kwargs.get('margin_info')
                self.margin_info=margin_info
                # if category should provide margin_info
                if self.margin_info is None:
                    raise ValueError('Please enter margin_info in type of dict')
                     
        def init_settlement_dates(self):
            margin_list=['future','option','currency_pair','cfd']
            if self.category.lower() in margin_list:
                self.ignore_settlement_dates=self.kwargs.get('ignore_settlement_dates')
                # --------
                if self.ignore_settlement_dates is None:
                    raise ValueError('Please add input ignore_settlement_dates in commdity.py')
                elif self.ignore_settlement_dates==True:
                    return
                elif self.ignore_settlement_dates==False:
                    base_dir=gbd.get_base_dir()
                    file_path=os.path.join(base_dir,'data',self.category,self.symbol,'settlement_dates.xlsx')
                    if os.path.exists(file_path):
                        df = pd.read_excel(file_path, parse_dates=[0])
                        self.settlement_dates = df.iloc[:, 0].dt.date.tolist()
                    else:
                        raise FileNotFoundError(f"The file {file_path} does not exist.")
                else:
                    raise ValueError('wrong ignore_settlement_dates type. Please enter True or False')
                # ------------
            else:
                return
                     

class CommodityList:
    # 應該要搬到json
    # Index
    VIX_INDEX={
                'name':'VIX_INDEX',
                'symbol':'^VIX',
                'category':'index',
                'currency':'usd',
                'tick_size':0.05,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':False,
                'data_source':'yfinance'
    }
    SP500_INDEX={
        'name':'SP500_INDEX',
        'symbol':'^GSPC',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    DOW_JONES_INDEX={
        'name':'DOW_JONES_INDEX',
        'symbol':'^DJI',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    NASDAQ_INDEX={
        'name':'NASDAQ_INDEX',
        'symbol':'^IXIC',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    NYSE_COMPOSITE_INDEX={
        'name':'NYSE_COMPOSITE_INDEX',
        'symbol':'^NYA',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    NYSE_AMEX_INDEX={
        'name':'NYSE_AMEX_INDEX',
        'symbol':'^XAX',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    CBOE_UK100_INDEX={
        'name':'CBOE_UK100_INDEX',
        'symbol':'^BUK100P',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    RUSSELL_2000_INDEX={
        'name':'RUSSELL_2000_INDEX',
        'symbol':'^RUT',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    FTSE_100_INDEX={
        'name':'FTSE_100_INDEX',
        'symbol':'^FTSE',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    DAX_INDEX={
        'name':'DAX_INDEX',
        'symbol':'^GDAXI',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    CAC_40_INDEX={
        'name':'CAC_40_INDEX',
        'symbol':'^FCHI',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }
    
    ESTX_50_INDEX={
        'name':'ESTX_50_INDEX',
        'symbol':'^STOXX50E',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    EURONEXT_100_INDEX={
        'name':'EURONEXT_100_INDEX',
        'symbol':'^N100',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    BEL_20_INDEX={
        'name':'BEL_20_INDEX',
        'symbol':'^BFX',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    MOEX_RUSSIA_INDEX={
        'name':'MOEX_RUSSIA_INDEX',
        'symbol':'IMOEX.ME',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    NIKKEI_225_INDEX={
        'name':'NIKKEI_225_INDEX',
        'symbol':'^N225',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    HANG_SENG_INDEX={
        'name':'HANG_SENG_INDEX',
        'symbol':'^HSI',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    SSE_COMPOSITE_INDEX={
        'name':'SSE_COMPOSITE_INDEX',
        'symbol':'000001.SS',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    SHENZHEN_INDEX={
        'name':'SHENZHEN_INDEX',
        'symbol':'399001.SZ',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    STI_INDEX={
        'name':'STI_INDEX',
        'symbol':'^STI',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    SP_ASX_200_INDEX={
        'name':'SP_ASX_200_INDEX',
        'symbol':'^AXJO',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    ALL_ORDINARIES_INDEX={
        'name':'ALL_ORDINARIES_INDEX',
        'symbol':'^AORD',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    SENSEX_INDEX={
        'name':'SENSEX_INDEX',
        'symbol':'^BSESN',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    IDX_COMPOSITE_INDEX={
        'name':'IDX_COMPOSITE_INDEX',
        'symbol':'^JKSE',
        'category':'index',
        'currency':'usd',
        'tick_size':0.001,
        'contract_size':1,
        'fee':0,
        'contract_list':['spot'],
        'is_tradable':False,
        'data_source':'yfinance'
    }

    # Future
    SP_FUTURE={
                'name':'SP_FUTURE',
                'symbol':'ES=F',
                'category':'future',
                'currency':'usd',
                'tick_size':0.25,
                'contract_size':50,
                'fee':5,
                'contract_list':['c1'],
                'is_tradable':True,
                'margin_info':{'initial_margin':12980,'maintenance_margin':11800},
                'ignore_settlement_dates':False,
                'data_source':'yfinance'
    }

    GOLD_FUTURE={
        
                'name':'GOLD_FUTURE',
                'symbol':'GC=F',
                'category':'future',
                'currency':'usd',
                'tick_size':0.1,
                'contract_size':100,
                'fee':5,
                'contract_list':['c1'],
                'is_tradable':True,
                'margin_info':{'initial_margin':12100,'maintenance_margin':11800},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
        
   } 
    VIX_FUTURE={
                'name':'VIX_FUTURE',
                'symbol':'VIX_FUTURE',
                'category':'future',
                'currency':'usd',
                'tick_size':0.05,
                'contract_size':1000,
                'fee':5,
                'contract_list':['c1','c2'],
                'is_tradable':True,
                'margin_info':{'initial_margin':6094,'maintenance_margin':5540},
                'ignore_settlement_dates':False,
                'data_source':'investing'
    }
    # currency_pair
    USDJPY={
                'name':'USDJPY',
                'symbol':'JPY=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    
    EURUSD={
                'name':'EURUSD',
                'symbol':'EURUSD=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    GBPUSD={
                'name':'GBPUSD',
                'symbol':'GBPUSD=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    AUDUSD={
                'name':'AUDUSD',
                'symbol':'AUDUSD=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    NZDUSD={
                'name':'NZDUSD',
                'symbol':'NZDUSD=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    CNYUSD={
                'name':'CNYUSD',
                'symbol':'CNY=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    SGDUSD={
                'name':'SGDUSD',
                'symbol':'SGD=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    INRUSD={
                'name':'INRUSD',
                'symbol':'INR=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    MXNUSD={
                'name':'MXNUSD',
                'symbol':'MXN=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    PHPUSD={
                'name':'PHPUSD',
                'symbol':'PHP=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    IDRUSD={
                'name':'IDRUSD',
                'symbol':'IDR=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    THBUSD={
                'name':'THBUSD',
                'symbol':'THB=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    MYRUSD={
                'name':'MYRUSD',
                'symbol':'MYR=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    ZARUSD={
                'name':'ZARUSD',
                'symbol':'ZAR=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    RUBUSD={
                'name':'RUBUSD',
                'symbol':'RUB=X',
                'category':'currency_pair',
                'currency':'usd',
                'tick_size':0.001,
                'contract_size':1,
                'fee':0,
                'contract_list':['spot'],
                'is_tradable':True,
                'margin_info':{'initial_margin':0,'maintenance_margin':0},
                'ignore_settlement_dates':True,
                'data_source':'yfinance'
    }
    
    
    ########### pgl ####################
    
    
    
    
    ########### pgl ####################
    
    @classmethod
    def commodities_lists_name(cls, category_list=[]):
    
        commodities = [getattr(cls, attr) for attr in dir(cls) if not attr.startswith("__") and not callable(getattr(cls, attr))]
        if category_list!=[]:
            filtered_commodities = []
            for category in category_list:
                filtered_commodities.extend([commodity['name'] for commodity in commodities if commodity['category'] == category])
            commodities = filtered_commodities
        else:
            commodities=[commodity['name'] for commodity in commodities]
            
        return commodities
        
    @classmethod
    def list_commodities(cls, category_list=None,exception_list=None,transfer_to_commodity_type=True):
        if exception_list is None:
            exception_list = []
        commodities = [getattr(cls, attr) for attr in dir(cls) if not attr.startswith("__") and not callable(getattr(cls, attr)) and attr not in exception_list]
        if category_list:
            filtered_commodities = []
            for category in category_list:
                filtered_commodities.extend([commodity for commodity in commodities if commodity['category'] == category])
            commodities = filtered_commodities
        
        if transfer_to_commodity_type:
            commodities=[create_commodity(commodity) for commodity in commodities]
        
        return commodities
    
    @classmethod
    def get_commodities(cls,commodities_list,transfer_to_commodity_type=True):
        for commodity in commodities_list:
            if not hasattr(cls,commodity):
                raise ValueError(f'{commodity} not exist')
        commodities=[getattr(cls, attr) for attr in commodities_list if hasattr(cls,attr)]
        
        if transfer_to_commodity_type:
            commodities=[create_commodity(commodity) for commodity in commodities]
    
        return commodities
# -------------------------
# first create commidty details in CommodityList, and use create_commodity() in main function
def create_commodity(config):
    # Assuming you have a Commodity class which matches these parameters exactly
    return Commodity(**config)

