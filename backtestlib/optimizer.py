import itertools
import pandas as pd



class Optimizer:
    
    def __init__(self,params,method,changable_var_dict,folder_main):
        """
        param must be dict
        ex. {'var1':[1,2,3],'var2':[10,20,30,40]}

        """
        
        self.params=params
        self.method=method
        self.changable_var_dict=changable_var_dict
        self.folder_main=folder_main
        self.results=list()
        self.performances=pd.DataFrame()
        self._init_method()
        self._init_combinations()
        
    def _init_method(self):
        if not hasattr(self,self.method):
            raise ValueError(f"no method called {self.method} in class Optimizer")
            
    def _init_combinations(self):
        self.combinations=params_combinations(self.params)
    
    
    def update_dict(self,params):
   
        for key, value in params.items():
            if key in self.changable_var_dict:
                self.changable_var_dict[key] = value
                
        
        return self.changable_var_dict
        
    
    def optimize(self,show_balance=False,show_details=False,show_pnl=False):
    
        for idx,params in enumerate(self.combinations):
            self.update_dict(params)
            self.changable_var_dict['account'].reset()
            backtest_result=self.folder_main(self.changable_var_dict,show_balance=show_balance,show_details=show_details,show_pnl=show_pnl)
            self.results.append({
                'params':params,
                'backtest_result':backtest_result})
            self.performances[idx]=backtest_result['output']['performance']['balance']
        
        optimize_results=dict()
        optimize_results['results']=self.results
        optimize_results['performances']=self.performances
        if hasattr(self,self.method):
            optimize_results['method_result']=getattr(self,self.method)()
        else:
            raise ValueError(f"No method found for the indicator: {self.name}. Please create in folder_list.py")
        
        
        
        
        return optimize_results
        
    
    def MAX_RETURN(self):
        if self.performances.empty:
            raise ValueError("No performances data available. Run optimize() first.")
        
        # Find the row with the maximum total_return
        return_value= self.performances.loc['total_return'].max()
        return_column = self.performances.columns[self.performances.loc['total_return'] == return_value][0]
        return_params=self.results[return_column]['params']
        
        return return_params

    def MAX_MDD(self):
        if self.performances.empty:
            raise ValueError("No performances data available. Run optimize() first.")
        
        # Find the row with the maximum total_return
        return_value= self.performances.loc['max_drawdown'].max()
        return_column = self.performances.columns[self.performances.loc['max_drawdown'] == return_value][0]
        return_params=self.results[return_column]['params']
        
        return return_params


def params_combinations(params):
    
    keys, values = zip(*params.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    return combinations

def update_dict(changable_var_dict,params):

    for key, value in params.items():
        if key in changable_var_dict:
            changable_var_dict[key] = value
            
    
    return changable_var_dict


# main func example
# optimize_results=dict()
# ----------------------------
# optimizer start

# if is_optimizer:
#     # optimizer
#     # input next year params from optimizer
#     if year > start_year and optimize_results:
#             best_params = optimize_results[year - 1]['method_result']
#             changable_var_dict.update(best_params)
#             print(f'{year}: {best_params}')
    
#     params = {
#         'long_SMA_length': [10,20,60]
#     }
#     method='MAX_RETURN'
#     optimizer=bop.Optimizer(params, method, changable_var_dict,f.folder_main)
#     optimize_results[year]=optimizer.optimize(show_balance=False,show_details=False,show_pnl=False)

# optimizer end
# ---------------------




    # optimizer end
    # ---------------------

