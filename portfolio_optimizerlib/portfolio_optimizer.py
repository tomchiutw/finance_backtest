# -*- coding: utf-8 -*-
"""
Created on Sat May  4 10:44:46 2024


portfolio_optimizer

@author: user
"""
import pandas as pd
import numpy as np
import math
import copy
import riskfolio as rp
import generallib.general as gg
import generallib.plot as gp
import backtestlib.performance as bp
import portfolio_optimizerlib.equity_series as pes

class PortfolioOptimizer:
    
    def __init__(self,method,interval,observed_equityseries_info,previous_steps=30,rebalance_steps=60,changable_var_dict=dict()):
        """
        
        always rebalance at the end of time_index
        previous_steps include time_index
        rebalance_steps not count in time_index 
        """
        self.method=method
        self._init_method()
        self.interval=interval
        self.equityseries_info,self.min_backtest_index,self.max_backtest_index=self._init_equityseries_info_and_backtest_index(observed_equityseries_info)
        self.previous_steps=previous_steps
        self.rebalance_steps=rebalance_steps
        self.changable_var_dict=changable_var_dict
        self.rebalanced_with_equity_value_dict=dict() # current value include equityseries, cash and method
        self.rebalanced_df=pd.DataFrame() # only include method
    
    def _init_method(self):
        if not hasattr(self,self.method):
            raise ValueError(f"no method called {self.method} in class PortfolioOptimizer") 
            
    def _init_equityseries_info_and_backtest_index(self, observed_equityseries_info):
        equityseries_info = copy.deepcopy(observed_equityseries_info)
        max_min_index = None
        min_max_index = None
        
        for info in equityseries_info:
            try:
                data = pes.EquitySeriesList.get_specific_data_in_data_info( hash_value=info['hash_value'],start_date=None,end_date=None)
                # check whether data interval 
                data = pes.EquitySeries.check_if_resampled(series=data, expected_interval=self.interval)
            except Exception as e:
                raise ValueError(f'error when processing data in data_info:{e}')
            current_min_index = data.index.min()
            current_max_index = data.index.max()
            if max_min_index is None or current_min_index > max_min_index:
                max_min_index = current_min_index
            if min_max_index is None or current_max_index < min_max_index:
                min_max_index = current_max_index
        
        return equityseries_info,max_min_index,min_max_index

    def do_method(self,idx,time_index):
        method=getattr(self,self.method)

        return method(idx,time_index)
    
    def sum_weight_equal_one_with_cash(self,weight):
        total_weight = sum(value for key,value in weight.items() if key!= 'Cash' )
        # print(f'weight_without_cash:{total_weight:.3f}')
        if 'Cash' in weight and math.isclose(total_weight, 1.0, rel_tol=1e-4):
            return weight
        else:
            weight['Cash']=1-total_weight
            # Check if the sum of the weights is close enough to 1 within a tolerance
            if not math.isclose(sum(weight.values()), 1.0, rel_tol=1e-4):
                raise ValueError(f'Sum of weight is {total_weight}, not 1')
            return weight
        

# !!! =============================================================================
    def TOP_N_EQUALLY_DIVIDE(self,idx,time_index):
        
        '''
        when save json, use TOP_N_EQUALLY_DIVIDE_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        
        try:
            n=self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        # process r
        r_dict=dict()
        strategy_list=[info['hash_value'] for info in self.equityseries_info]
        for hash_value in strategy_list:
            end_date=time_index
            start_date=end_date-gg.get_date_offset(self.interval)*(self.previous_steps-1)
            data=pes.EquitySeriesList.get_specific_data_in_data_info(hash_value, start_date=start_date, end_date=end_date)

            r=(data.iloc[-1]-data.iloc[0])/data.iloc[0]
            r_dict[hash_value]=r
        
        # check n 
        if len(r_dict)<n:
            raise ValueError(f'top n :{n} is larger than len(r_dict):{len(r_dict)}')
        top_n_strategy_list = sorted(r_dict, key=r_dict.get, reverse=True)[:n]
        
        weight={name:1/len(top_n_strategy_list) for name in top_n_strategy_list}
        
        weight=self.sum_weight_equal_one_with_cash(weight)
        
        
        return weight
        
        
        
        
        
# !!! =============================================================================

    def portfolio_backtest(self, backtest_start_date, backtest_end_date, start_balance=1000000, show_method=False, show_details=False):
        # check backtest_start_date, backtest_end_date validity
        if backtest_start_date < self.min_backtest_index or backtest_start_date > self.max_backtest_index:
            raise ValueError(f"backtest_start_date {backtest_start_date} is out of the valid range ({self.min_backtest_index} to {self.max_backtest_index}).")
        if backtest_end_date < self.min_backtest_index or backtest_end_date > self.max_backtest_index:
            raise ValueError(f"backtest_end_date {backtest_end_date} is out of the valid range ({self.min_backtest_index} to {self.max_backtest_index}).")
        
        # backtest_date_range
        backtest_date_range=gg.get_backtest_date_range(backtest_start_date,backtest_end_date,interval=self.interval)
        
        # check previous_steps
        if len(backtest_date_range)<self.previous_steps:
            raise ValueError(f"previous_steps is {self.previous_steps}, which is larger than length of backtest_date_range: {len(backtest_date_range)}")
        
        # rebalanced_df
        self.rebalanced_df = self.rebalanced_df.assign(**{self.method: 0})
        weight_history=dict()
        rebalanced_with_equity_value_dict_history=dict()
        
        
        # start backtest
        for idx,time_index in enumerate(backtest_date_range):
    
            # skip if data not enough for previous_steps, we start rebalance at time_index when data number is exactly previous_steps 
            if idx<self.previous_steps-1:
                continue
            # set idx_count in first rebalance time
            if idx==self.previous_steps-1:
                idx_count=idx
                self.rebalanced_df.loc[time_index,self.method]=start_balance
                
            # update every time_index equity
            # update rebalanced_with_equity_value_dict and rebalanced_df
            if idx>self.previous_steps-1: #skip the first row idx==portfolio_optimizer.previous_steps-1 after start
                self.rebalanced_df.loc[time_index]=np.nan
                
                for key in self.rebalanced_with_equity_value_dict.keys():
                    # skip self.method, process at the end
                    if key==self.method:
                        continue
                    # do if key==cash because cash remain same
                    if key=='Cash':
                        continue
                    
                    # start process simple return and update equity
                    simple_return=0
                    # get previous, current value
                    try:
                        end_date=time_index
                        start_date=end_date-gg.get_date_offset(self.interval)
                        data=pes.EquitySeriesList.get_specific_data_in_data_info(hash_value=key, start_date=start_date, end_date=end_date)
                        # value
                        previous_value=data.iloc[0]
                        current_value=data.iloc[1]
                    except Exception as e :
                        raise ValueError(f'no time_index {time_index} in {key} or cant get {key} data:{e}')
                    if previous_value!=0 and not pd.isna(previous_value):
                        simple_return=float((current_value-previous_value)/previous_value)
                    
                    # update equity
                    self.rebalanced_with_equity_value_dict[key]= \
                        self.rebalanced_with_equity_value_dict[key]*(1+simple_return)
                   
                # update self.rebalanced_with_equity_value_dict[self.method]
                self.rebalanced_with_equity_value_dict[self.method]= \
                    sum(value for key,value in self.rebalanced_with_equity_value_dict.items() if key!=self.method)
                
                # update rebalanced_df
                self.rebalanced_df.loc[time_index,self.method]=self.rebalanced_with_equity_value_dict[self.method]

                            
            # do if need rebalance, first time do when idx==previous_steps
            if (idx-idx_count>=self.rebalance_steps or idx==self.previous_steps-1):
                # idx,time_index check
                # do_method, append weight_history
                weight=self.do_method(idx,time_index)
                
                # update rebalanced_with_equity_value_dict and rebalanced_df
                self.rebalanced_with_equity_value_dict=dict()
                for key, weight_value in weight.items():         
                    self.rebalanced_with_equity_value_dict[key]=weight_value*self.rebalanced_df.loc[time_index,self.method]
                # update method
                self.rebalanced_with_equity_value_dict[self.method]= \
                    sum(value for key,value in self.rebalanced_with_equity_value_dict.items() if key!=self.method)
                self.rebalanced_df.loc[time_index,self.method]=self.rebalanced_with_equity_value_dict[self.method]
                # breakpoint()
                # show_details
                if show_details:
                    weight_history[time_index]=weight
                # update idx_count
                idx_count=idx
                
            # show_details
            if show_details:
                rebalanced_with_equity_value_dict_history[time_index]=copy.deepcopy(self.rebalanced_with_equity_value_dict)
                
            
        # plot
        if show_method:
            gp.plot_all_columns_together(self.rebalanced_df,bold_list=[self.method],exception_list=[])
    
        
        # append portfolio_backtest_results
        portfolio_backtest_results=dict()
        portfolio_backtest_results['rebalanced_with_equity_value_dict_history']=rebalanced_with_equity_value_dict_history
        portfolio_backtest_results['rebalanced_df']=self.rebalanced_df
        portfolio_backtest_results['performance']=bp.getPortfolio_Series(df=self.rebalanced_df,profitPercentage_Col=self.method,rf=0.02,translate=False)
        portfolio_backtest_results['weight_history']=weight_history
        
        return portfolio_backtest_results           
        

        
    