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
    
    def __init__(self,method,interval,observed_data_info,previous_steps=30,rebalance_steps=60,changable_var_dict=dict()):
        """
        
        always rebalance at the end of time_index
        previous_steps include time_index
        rebalance_steps not count in time_index 
        """
        self.method=method
        self._init_method()
        self.interval=interval
        self.equityseries_list=[]
        self._init_equityseries_list_and_observed_df(observed_data_info)
        self.previous_steps=previous_steps
        self.rebalance_steps=rebalance_steps
        self.changable_var_dict=changable_var_dict
        self.template_data=pd.DataFrame()
        self.current_weight=dict()
        self.rebalanced_df=pd.DataFrame()
    
    def _init_method(self):
        if not hasattr(self,self.method):
            raise ValueError(f"no method called {self.method} in class PortfolioOptimizer")    
    def _init_equityseries_list_and_observed_df(self,observed_data_info):
        """
        for backtesting different interval, we need to use pes.resample_series() to process data['data'] for data in observed_data_info first.
        Therefore, observed_data_info might change.
        After that, we add data['data'] for data in observed_data_info to observed_df, and create EquitySeries
        """
        observed_df=pd.DataFrame()
        observed_data_info_for_init=copy.deepcopy(observed_data_info) # to avoid memory overlay
        for data in observed_data_info_for_init:
            # proccess data
            series=data['data']
            series=pes.EquitySeries.resample_series(series,self.interval)
            
            # observed_df
            observed_df[data['hash_value']]=series
            # equityseries_list
            # data['data'] has already updated because we use series=data['data'] and resample_series
            self.equityseries_list.append(pes.EquitySeries(**data))
            
        observed_df.dropna(inplace=True)
        self.observed_df=observed_df

    
    def do_method(self,idx,time_index):
        self.create_template_data(time_index)
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
    
    def create_template_data(self,time_index):
        time_index_loc=self.observed_df.index.get_loc(time_index)
        start_loc = max(0, time_index_loc +1- self.previous_steps)
        self.template_data = self.observed_df.iloc[start_loc:time_index_loc+1]
        
        return self.template_data
    
    def normalized_to_base(self,df,start_balance=100000,exception=['Cash']):
        for col in df.columns:
            if col not in exception:
                df_col_loc=df.columns.get_loc(col)
                df[col]=df[col]/df.iloc[0,df_col_loc]*start_balance
        return df
    
    def keep_current_weight(self):
        if not self.current_weight:
            raise ValueError("No previous weight found. Please run do_method first.")
        return self.current_weight
    
    def update_current_weight(self, rebalanced_df, time_index):
        self.current_weight = {col: rebalanced_df.loc[time_index, col] / rebalanced_df.loc[time_index, self.method] 
                               for col in rebalanced_df.columns if col != self.method}
        return self.current_weight
# !!! =============================================================================

    # !!! weight must include all self.template_data.columns
    # !!! beware of same variable name in changable_var_dict
    def TOP_N_EQUALLY_DIVIDE_AND_FILTERED_BY_MDD_AND_R(self,idx,time_index):
        '''
        
        changable_var_dict=dict()
        changable_var_dict['n']=100
        changable_var_dict['acceptable_mdd']=-0.2
        changable_var_dict['acceptable_r']=0

        '''
        try:
            n=self.changable_var_dict['n']
            acceptable_mdd=self.changable_var_dict['acceptable_mdd']
            acceptable_r=self.changable_var_dict['acceptable_r']

        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
                   
        # process r
        r_dict=dict()
        strategy_list=self.template_data.columns
        self.template_data=self.template_data.dropna()
        
        for col in strategy_list:
            col_index=self.template_data.columns.get_loc(col)
            r=(self.template_data.iloc[-1,col_index]-self.template_data.iloc[0,col_index])/self.template_data.iloc[0,col_index]
            r_dict[col]=r

        # check n 
        if len(r_dict)<n:
            raise ValueError(f'top n :{n} is larger than len(r_dict):{len(r_dict)}')
        sorted_r_dict_in_list = sorted(r_dict.items(), key=lambda item: item[1], reverse=True)
        # cols_to_append
        cols_to_append=[]
        for index,item in enumerate(sorted_r_dict_in_list):
            key,value=item
            # value<=acceptable_r
            if value<=acceptable_r:
                break
            # mdd
            mdd_df=self.observed_df.loc[:time_index,key].to_frame()
            performance_temp=bp.getPortfolio_Series(df=mdd_df,profitPercentage_Col=key,rf=0.02,translate=False)
            mdd=performance_temp.loc['max_drawdown',key]
            if mdd>acceptable_mdd and value>acceptable_r :
                cols_to_append.append(key)
                # print(f'{index}, {key}, r: {value:.2f}, mdd:{mdd:.2f}')
            
            if len(cols_to_append)==n:
                break
                
        
        weight={name:1/n if name in cols_to_append else 0 for name in r_dict}
        
        weight=self.sum_weight_equal_one_with_cash(weight)
        
        return weight    
        
        
    def DO_METHOD_AND_TAKE_PROFIT(self,idx,time_index):
        '''
        changable_var_dict['idx_start'] set 0 at main.py
        ex.
        # for take profit method
        changable_var_dict['take_profit_percentage']=0.3
        changable_var_dict['days_for_take_profit_percentage']=5
        changable_var_dict['idx_start']=0
        changable_var_dict['days_for_rebalance_steps']=60
        changable_var_dict['first_step_method']='TOP_N_SHARPE_RATIO_EQUALLY_DIVIDE'
        '''
        try:
            take_profit_percentage=self.changable_var_dict['take_profit_percentage']
            days_for_take_profit_percentage=self.changable_var_dict['days_for_take_profit_percentage']
            days_for_rebalance_steps=self.changable_var_dict['days_for_rebalance_steps']
            idx_start=self.changable_var_dict['idx_start']
            first_step_method=self.changable_var_dict['first_step_method']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        # check first_step_method
        if not hasattr(self,first_step_method):
            raise ValueError
        # idx
        if idx_start==0:
            idx_start=idx
            self.changable_var_dict['idx_start']=idx_start
            print(f'start: {idx_start} {time_index}')
        idx_count=idx-idx_start
        
        # if idx_count % days_for_rebalance_steps == 0:
        if idx_count % days_for_rebalance_steps == 0:
            print(f'{idx_count} need rebalance')
            first_step_method_function=getattr(self,first_step_method)
            weight=first_step_method_function(idx,time_index)
            return weight
        
            
        # if r>take_profit_percentage, do everyday
        rebalance_needed = False 
        cols_to_zero = []
        if idx_count>=days_for_take_profit_percentage:
            # print(f'{idx_count} r check')
            rebalanced_df_list=[col for col in self.rebalanced_df.columns if not (self.rebalanced_df.loc[time_index,col]==0 \
                                or col==self.method or col=='Cash')]  
            for col in rebalanced_df_list:
                col_index = self.rebalanced_df.columns.get_loc(col)
                initial_value = self.rebalanced_df.iloc[-days_for_take_profit_percentage-1, col_index]
                # get previous value and prevent 0
                for i in range(-days_for_take_profit_percentage-1, -1):
                    previous_value = self.rebalanced_df.iloc[i, col_index]
                    if previous_value != 0:
                        break
                r = (self.rebalanced_df.iloc[-1, col_index] - previous_value) / previous_value
                # breakpoint()
                if r >= take_profit_percentage:
                    cols_to_zero.append(col)
                    rebalance_needed = True
                    print(f'{idx_count},{time_index}, {col}, {r:.2f}, rebalanced')
                    
        if rebalance_needed:
            weight = self.current_weight
            for col in cols_to_zero:
                weight[col] = 0
            weight = self.sum_weight_equal_one_with_cash(weight)
            
            return weight
            
        # if just need return last weight
        weight=self.current_weight
        weight=self.sum_weight_equal_one_with_cash(weight)
        return weight
        
    def DO_METHOD_AND_STOP_LOSS(self, idx, time_index):
        '''
        changable_var_dict['idx_start'] set 0 at main.py
        ex.
        # for stop loss method
        changable_var_dict['stop_loss_percentage'] = 0.1
        changable_var_dict['days_for_stop_loss'] = 5
        changable_var_dict['idx_start'] = 0
        changable_var_dict['days_for_rebalance_steps'] = 60
        changable_var_dict['first_step_method'] = 'TOP_N_SHARPE_RATIO_EQUALLY_DIVIDE'
        '''
        try:
            stop_loss_percentage = self.changable_var_dict['stop_loss_percentage']
            days_for_stop_loss = self.changable_var_dict['days_for_stop_loss']
            days_for_rebalance_steps = self.changable_var_dict['days_for_rebalance_steps']
            idx_start = self.changable_var_dict['idx_start']
            first_step_method = self.changable_var_dict['first_step_method']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        # check first_step_method
        if not hasattr(self, first_step_method):
            raise ValueError(f"No method called {first_step_method} in class PortfolioOptimizer")
        
        # idx
        if idx_start == 0:
            idx_start = idx
            self.changable_var_dict['idx_start'] = idx_start
            print(f'start: {idx_start} {time_index}')
        idx_count = idx - idx_start
        
        # if idx_count % days_for_rebalance_steps == 0:
        if idx_count % days_for_rebalance_steps == 0:
            print(f'{idx_count} need rebalance')
            first_step_method_function = getattr(self, first_step_method)
            weight = first_step_method_function(idx, time_index)
            return weight
        
        # if r < -stop_loss_percentage, do everyday
        rebalance_needed = False 
        cols_to_zero = []
        if idx_count >= days_for_stop_loss:
            # print(f'{idx_count} r check')
            rebalanced_df_list = [col for col in self.rebalanced_df.columns if not (self.rebalanced_df.loc[time_index, col] == 0 or col == self.method or col == 'Cash')]
            for col in rebalanced_df_list:
                col_index = self.rebalanced_df.columns.get_loc(col)
                initial_value = self.rebalanced_df.iloc[-days_for_stop_loss - 1, col_index]
                
                for i in range(-days_for_stop_loss - 1, -1):
                    previous_value = self.rebalanced_df.iloc[i, col_index]
                    if previous_value != 0:
                        break
                r = (self.rebalanced_df.iloc[-1, col_index] - previous_value) / previous_value
                # breakpoint()
                if r <= -stop_loss_percentage:
                    cols_to_zero.append(col)
                    rebalance_needed = True
                    print(f'{idx_count},{time_index}, {col}, {r:.2f}, rebalanced')
                    
        if rebalance_needed:
            weight = self.current_weight
            for col in cols_to_zero:
                weight[col] = 0
            # breakpoint()
            weight = self.sum_weight_equal_one_with_cash(weight)
            
            return weight
            
        # if just need return last weight
        weight = self.current_weight
        weight = self.sum_weight_equal_one_with_cash(weight)
        return weight

        
    def EQUALLY_DIVIDE(self,idx,time_index):
        '''
        when save pickle, use EQUALLY_DIVIDE_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        strategy_list=self.template_data.columns
        weight={name:1/(len(strategy_list)) for name in strategy_list}
        

        
        weight=self.sum_weight_equal_one_with_cash(weight)
        
        return weight
    
    def POSITIVE_RETURN(self,idx,time_index):
        '''
        when save pickle, use POSITIVE_RETURN_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        weight=dict()
        r_dict=dict()
        strategy_list=self.template_data.columns
        self.template_data=self.template_data.dropna()
        
        try:
            n=self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
            
        for col in strategy_list:
            col_index=self.template_data.columns.get_loc(col)
            r=(self.template_data.iloc[-1,col_index]-self.template_data.iloc[0,col_index])/self.template_data.iloc[0,col_index]
            if r>0:
                r_dict[col]=r
            else:
                r_dict[col]=0

        top_n_strategy_list = sorted(r_dict, key=r_dict.get, reverse=True)[:n]
        sorted_r_dict = {key: r_dict[key] for key in top_n_strategy_list}

        
        sum_r=sum(sorted_r_dict.values())
        

        if sum_r!=0:
            weight={name:r_dict[name]/sum_r if name in top_n_strategy_list else 0 for name in r_dict}
        else:
            weight={name:1/len(strategy_list) for name in r_dict}
        
        weight=self.sum_weight_equal_one_with_cash(weight)
        
        return weight
    
    def TOP_N_EQUALLY_DIVIDE(self,idx,time_index):
        
        '''
        when save pickle, use TOP_N_EQUALLY_DIVIDE_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        
        try:
            n=self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        # process r
        r_dict=dict()
        strategy_list=self.template_data.columns
        self.template_data=self.template_data.dropna()
        for col in strategy_list:
            col_index=self.template_data.columns.get_loc(col)
            r=(self.template_data.iloc[-1,col_index]-self.template_data.iloc[0,col_index])/self.template_data.iloc[0,col_index]
            r_dict[col]=r
        # check n 
        if len(r_dict)<n:
            raise ValueError(f'top n :{n} is larger than len(r_dict):{len(r_dict)}')
        top_n_strategy_list = sorted(r_dict, key=r_dict.get, reverse=True)[:n]
        sorted_r_dict = dict(sorted(r_dict.items(), key=lambda item: item[1], reverse=True))
        

        weight={name:1/(len(top_n_strategy_list)) if name in top_n_strategy_list else 0 for name in r_dict}
        
        weight=self.sum_weight_equal_one_with_cash(weight)
        return weight
    
    
    
    def HIGH_VOL(self,idx,time_index):
        '''
        when save pickle, use HIGH_VOL_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        weight=dict()
        vol_dict=dict()
        strategy_list=self.template_data.columns
        self.template_data=self.template_data.dropna()
        
        try:
            n=self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        
        for col in strategy_list:
            col_index = self.template_data.columns.get_loc(col)
            returns = self.template_data.iloc[:, col_index].pct_change().dropna()
        
            # Calculate the volatility as the standard deviation of returns
            vol = returns.std()
            vol_dict[col] = vol

        
        top_n_strategy_list = sorted(vol_dict, key=vol_dict.get, reverse=True)[:n]
        sorted_vol_dict = {key: vol_dict[key] for key in top_n_strategy_list}


        sum_vol = sum(sorted_vol_dict.values())
        
        if sum_vol != 0:
            weight = {name: vol_dict[name] / sum_vol if name in top_n_strategy_list else 0 for name in vol_dict}
        else:
            weight = {name: 1 / len(strategy_list) for name in vol_dict}

        # Ensuring the sum of weights equals one
        weight=self.sum_weight_equal_one_with_cash(weight)
        return weight
        
    def LOW_VOL(self,idx,time_index):
        '''
        when save pickle, use LOW_VOL_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        weight=dict()
        vol_dict=dict()
        strategy_list=self.template_data.columns
        self.template_data=self.template_data.dropna()
        
        try:
            n=self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        
        for col in strategy_list:
            col_index = self.template_data.columns.get_loc(col)
            returns = self.template_data.iloc[:, col_index].pct_change().dropna()
        
            # Calculate the volatility as the standard deviation of returns
            vol = returns.std()
            vol_dict[col] = vol

        
        top_n_strategy_list = sorted(vol_dict, key=vol_dict.get)[:n]
        sorted_vol_dict = {key: vol_dict[key] for key in top_n_strategy_list}

        sum_vol = sum(sorted_vol_dict.values())
        
        if sum_vol != 0:
            weight = {name: vol_dict[name] / sum_vol if name in top_n_strategy_list else 0 for name in vol_dict}
        else:
            weight = {name: 1 / len(strategy_list) for name in vol_dict}

        # Ensuring the sum of weights equals one
        weight=self.sum_weight_equal_one_with_cash(weight)
        return weight

    def HIGH_MDD(self,idx,time_index):
        '''
        when save pickle, use HIGH_MDD_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        weight = dict()
        mdd_dict = dict()
        strategy_list = self.template_data.columns
        self.template_data = self.template_data.dropna()
        
        performance_df=pd.DataFrame()
        
        try:
            n = self.changable_var_dict['n']
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
        
        
        
        for col in strategy_list:
            col_index = self.template_data.columns.get_loc(col)
            performance_df[col]=bp.getPortfolio_Series(df=self.template_data,profitPercentage_Col=col,rf=0.02,translate=False)

                
        mdd_series=performance_df.loc['max_drawdown']
        mdd_dict=mdd_series.to_dict()
        
        mdd_dict = {key: abs(1/value) if value!=0 else 10 for key, value in mdd_dict.items()}
        
        
        # Select top n strategies with the highest max drawdown
        top_n_strategy_list = sorted(mdd_dict, key=mdd_dict.get, reverse=True)[:n]
        sorted_mdd_dict = {key: mdd_dict[key] for key in top_n_strategy_list}
 
    
        sum_mdd = sum(sorted_mdd_dict.values())
    
        if sum_mdd != 0:
            weight = {name: mdd_dict[name] / sum_mdd if name in top_n_strategy_list else 0 for name in mdd_dict}
        else:
            weight = {name: 1 / len(strategy_list) for name in mdd_dict}
        
        # Ensuring the sum of weights equals one
        print(weight)
        weight = self.sum_weight_equal_one_with_cash(weight)
        
        return weight
    
    
    
    def TOP_N_SHARPE_RATIO_EQUALLY_DIVIDE(self,idx,time_index):
        '''
        when save pickle, use TOP_N_SHARPE_RATIO_EQUALLY_DIVIDE_{n}_{previous_steps}_{rebalance_steps}_time
        '''
        weight = dict()
        sharpe_dict = dict()
        strategy_list = self.template_data.columns
        self.template_data = self.template_data.dropna()
    
        try:
            n = self.changable_var_dict['n']
            risk_free_rate = self.changable_var_dict.get('risk_free_rate', 0)  
        except KeyError as e:
            raise ValueError(f'Missing variable when creating PortfolioOptimizer: {e}')
    
        for col in strategy_list:
            col_index = self.template_data.columns.get_loc(col)
            returns = self.template_data.iloc[:, col_index].pct_change().dropna()
            mean_return = returns.mean()
            std_return = returns.std()
            
            if std_return != 0:
                sharpe_ratio = (mean_return - risk_free_rate) / std_return
            else:
                sharpe_ratio = 0
    
            sharpe_dict[col] = sharpe_ratio
            
            
    
        top_n_strategy_list = sorted(sharpe_dict, key=sharpe_dict.get, reverse=True)[:n]
        sorted_sharpe_dict = {key: sharpe_dict[key] for key in top_n_strategy_list}    
    
        weight={name:1/len(top_n_strategy_list) if name in top_n_strategy_list else 0 for name in sharpe_dict }
    
        weight = self.sum_weight_equal_one_with_cash(weight)
    
        return weight
    
    
    
# !!! =============================================================================

    def portfolio_backtest(self,backtest_start_date,backtest_end_date,start_balance=1000000,show_method=False,show_equityseries=False,show_details=False):
        pass
        
        # 1 start
        template_data_dict=dict()
        weight_dict=dict()
        # trim backtest_date_range first value to first time_index of self.obderved_df
        backtest_date_range=gg.get_backtest_date_range(backtest_start_date,backtest_end_date,interval=self.interval)
        first_observed_index = self.observed_df.index[0]
        start_date = max(backtest_date_range[0], first_observed_index)
        backtest_date_range=gg.get_backtest_date_range(start_date,backtest_end_date,interval=self.interval)
        # 2 set rebalanced_df
        # check length of portfolio_optimizer.observed_df first
        if len(self.observed_df)<self.previous_steps:
            raise ValueError(f"previous_steps is {self.previous_steps}, which is larger than length of observed_df {len(self.observed_df)}")
        rebalanced_df=pd.DataFrame(columns=list(self.observed_df.columns)+['Cash',self.method])  
        # 3 start backtest
        for idx,time_index in enumerate(backtest_date_range):
    
            # skip if data not enough for previous_steps, we start rebalance at time_index when data number exactly is previous_steps 
            if idx<self.previous_steps-1:
                continue
            # set idx_count in first rebalance time
            if idx==self.previous_steps-1:
                idx_count=idx
                rebalanced_df.loc[time_index,self.method]=start_balance
                rebalanced_df.loc[time_index,'Cash']=start_balance
            
            # 4 update every time_index equity
            if idx>self.previous_steps-1 and \
                time_index in self.observed_df.index: #skip the first row idx==portfolio_optimizer.previous_steps-1 after start
            
                rebalanced_df.loc[time_index,self.method]=np.nan
            
                for col in list(self.observed_df.columns)+['Cash']:
                    # loc
                    rebalanced_df_col_loc= rebalanced_df.columns.get_loc(col)
                    rebalanced_df_row_loc= rebalanced_df.index.get_loc(time_index)
                    # do if col==cash
                    if col=='Cash':
                        rebalanced_df.iloc[rebalanced_df_row_loc,rebalanced_df_col_loc]= \
                            rebalanced_df.iloc[rebalanced_df_row_loc-1,rebalanced_df_col_loc]
                        continue
                    if rebalanced_df.iloc[rebalanced_df_row_loc-1,rebalanced_df_col_loc]==0:
                        rebalanced_df.iloc[rebalanced_df_row_loc,rebalanced_df_col_loc]= 0
                        continue
                    # process only equityseries, no cash
                    try:
                        observed_df_row_loc= self.observed_df.index.get_loc(time_index)
                        observed_df_col_loc= self.observed_df.columns.get_loc(col)
                    except:
                        raise ValueError(f'no {col} in observed_df')
                    

                    # 5 start process simple return and update equity
                    simple_return=0
                    if len(self.observed_df)>1:
                        # get previous, current value
                        try:
                            previous_value=self.observed_df.iloc[observed_df_row_loc-1,rebalanced_df_col_loc]
                            current_value=self.observed_df.iloc[observed_df_row_loc,rebalanced_df_col_loc]
                        except:
                            raise ValueError(f'no time_index {time_index} in self.observed_df')
                        if previous_value!=0 and not pd.isna(previous_value):
                            simple_return=float((current_value-previous_value)/previous_value)
                        
                        # update equity
                        rebalanced_df.iloc[rebalanced_df_row_loc,rebalanced_df_col_loc]= \
                        rebalanced_df.iloc[rebalanced_df_row_loc-1,rebalanced_df_col_loc]*(1+simple_return) 
                    else:
                        raise ValueError(f'length of self.observed_df is {len(self.observed_df)}, not enough for calculating simple return')
                # 6 sum all col to portfolio_optimizer.method, and update cash
                rebalanced_df.loc[time_index,self.method]=rebalanced_df.loc[time_index].sum()
                # update rebalanced_df
                self.rebalanced_df=rebalanced_df
        
            # 7 do if need rebalance, first time do when idx==previous_steps
            if (idx-idx_count>=self.rebalance_steps or idx==self.previous_steps-1) \
                and time_index in self.observed_df.index:
                # idx,time_index check
                # do_method, append weight_dict and template_data_dict
                weight=self.do_method(idx,time_index)
                if show_details:
                    weight_dict[time_index]=weight
                    template_data_dict[time_index]=self.template_data
      
                for col, weight_value in weight.items():
                    rebalanced_df.loc[time_index, col] = weight_value*rebalanced_df.loc[time_index, self.method]

                # update idx_count
                idx_count=idx
                
            # update current_weigh 
            self.update_current_weight(rebalanced_df, time_index)
            self.rebalanced_df=rebalanced_df

        
        # 8 create summary_df
        summary_df=self.observed_df.copy()
        summary_df[self.method]=rebalanced_df[self.method]
        summary_df.dropna(inplace=True)
        self.normalized_to_base(summary_df,start_balance=start_balance,exception=['Cash'])
        
        # 9 plot
        if show_method and show_equityseries :
            gp.plot_all_columns_together(summary_df,bold_list=[self.method])
        if show_method and not show_equityseries:
            gp.plot_all_columns_together(summary_df,bold_list=[self.method],exception_list=[col for col in summary_df.columns if col!=self.method ])
    
        # 10 append portfolio_backtest_results
        portfolio_backtest_results=dict()
        portfolio_backtest_results['summary_df']=summary_df
        portfolio_backtest_results['template_data_dict']=template_data_dict
        portfolio_backtest_results['weight_dict']=weight_dict
        portfolio_backtest_results['rebalanced_df']=rebalanced_df
        portfolio_backtest_results['performance']=bp.getPortfolio_Series(df=summary_df,profitPercentage_Col=self.method,rf=0.02,translate=False)
        
        
        return portfolio_backtest_results

# --------------------------
def normalized_to_base(df,start_balance=1000000,exception=['Cash']):
    df.dropna(inplace=True)
    for col in df.columns:
        if col not in exception:
            df_col_loc=df.columns.get_loc(col)
            df[col]=df[col]/df.iloc[0,df_col_loc]*start_balance
    return df