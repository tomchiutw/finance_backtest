import os
import pdb
import sys
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import generallib.general as gg
import get_base_dir as gbd
import ijson
from generallib.confirmable import confirmable

class EquitySeries:
    def __init__(self,hash_value,commodity,interval,folder_name,data,source,changable_var_dict_for_folder=dict(),note=''):
        '''
        Parameters:
            strategy_name(str)
            data(series)
            
            self.interval means interval of this equityseries.data, not folder interval
        '''
        self.hash_value=hash
        self.commodity=commodity
        self.interval=interval
        self.folder_name=folder_name
        self.data=data
        self.changable_var_dict_for_folder=changable_var_dict_for_folder
        self.source=source
        self.note=note
        
        
    @classmethod
    def resample_series(cls, series, portfolio_optimizer_interval):
        """
        Used when creating portfolio_optimizer.
        Resample the given time series to the specified interval and fill missing values.
        """
        # Drop NaN values
        series.dropna(inplace=True)
    
        # Ensure the series is not empty after dropping NaN
        if series.empty:
            raise ValueError("The series is empty after dropping NaN values.")
    
        # Resample the series to the desired frequency
        try:
            resample_frequency = gg.change_interval_for_date_range(portfolio_optimizer_interval)
            series = series.resample(resample_frequency).asfreq()
        except Exception as e:
            raise ValueError(f"Error during resampling: {e}")
    
        # Forward fill missing values
        series = series.ffill()
    
        return series

    @classmethod
    def create_EquitySeries(cls,config):
        return EquitySeries(**config)

class EquitySeriesList:
    '''
    if edit json, must create New EquitySeriesDict first.
    else you can just get_equityseries_info(), get_data_info()
    all var in str type
    
    equityseries_info and data_info are all in list type
    '''
    def __init__(self):
        self.equityseries_info=self.__class__.get_equityseries_info()

    
    
    @classmethod
    def get_equityseries_info(cls,hash_value_to_load=[]):
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\equityseries_info.json'
            equityseries_info=[]
            # Using ijson to parse large JSON file
            with open(full_file_path, 'r') as file:
                objects = ijson.items(file,'item')
                if not hash_value_to_load:
                    for obj in objects:
                        try:
                            equityseries_info.append(obj)
                        except Exception as e:
                            raise ValueError(f'cant get equityseries_info: {e}')
                else: 
                    for hash_value in hash_value_to_load:
                        for obj in objects:
                            
                            if obj['hash_value']==hash_value:
                                try:
                                    equityseries_info.append(obj)
                                    break
                                except Exception as e:
                                    raise ValueError(f'cant get {hash_value} in equityseries: {e}')  
                        else:
                            # not found hash_value
                            raise ValueError(f'cant find {hash_value} in equityseries') 
                                
            return equityseries_info
        except Exception as e:
            raise ValueError(f'error when loading equityseries_info.json: {e}')
    
    @classmethod
    def get_data_info(cls, hash_value_to_load=[]):
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path = full_dir_path + '\\data_info.json'
            
            data_info = []
            # Using ijson to parse large JSON file
            with open(full_file_path, 'r') as file:
                objects = ijson.items(file, 'item')
                
                if not hash_value_to_load:
                    for obj in objects:
                        try:
                            obj['data'] = gg.json_dict_to_series(obj['data'])
                            # Convert index to datetime
                            obj['data'].index = pd.to_datetime(obj['data'].index)
                            data_info.append(obj)
                        except Exception as e:
                            raise ValueError(f"Can't get data_info: {e}")
                else:
                    # Load specific hash values
                    for hash_value in hash_value_to_load:
                        found = False
                        for obj in objects:
                            if obj['hash_value'] == hash_value:
                                try:
                                    obj['data'] = gg.json_dict_to_series(obj['data'])
                                    # Convert index to datetime
                                    obj['data'].index = pd.to_datetime(obj['data'].index)
                                    data_info.append(obj)
                                    found = True
                                    break
                                except Exception as e:
                                    raise ValueError(f"Can't get {hash_value} in data_info: {e}")
                        if not found:
                            # Raise an error if the hash_value is not found
                            raise ValueError(f"Can't find {hash_value} in data_info")
            
            return data_info
        except Exception as e:
            raise ValueError(f"Error when loading data_info.json: {e}")


    @confirmable
    @classmethod
    def save_equityseries_info(cls,data):
        """
        use **kwargs=confirm_execution=True to cinfirm before do
        """            
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\equityseries_info.json'
            return gg.save_to_json(data, full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving equityseries_info.json: {e}')
    
    @confirmable
    @classmethod
    def save_data_info(cls,data):
        """
        use **kwargs=confirm_execution=True to cinfirm before do
        """        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\data_info.json'
            return gg.save_to_json(data, full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving data_info.json: {e}')
    
    @classmethod
    @confirmable
    def create_default_equityseries_info(cls):
        """
        use **kwargs=confirm_execution=True to cinfirm before do
        """
        default_list=[]
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\equityseries_info.json'
            return gg.save_to_json(default_list , full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving default equityseries_info.json: {e}')

            
    @classmethod
    def check_equityseries_exists(cls, commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        not ok if commodity, interval, folder_name and changable_var_dict_for_folder same
        """
        equityseries_info = cls.get_equityseries_info()
        for value in equityseries_info:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return True
        return False
    
    @classmethod
    def get_equityseries_hash_value(cls, commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        Return the hash_value of the equityseries if the commodity, interval, folder_name and changable_var_dict_for_folder match.
        """
        equityseries_info = cls.get_equityseries_info()
        for value in equityseries_info:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return value['hash_value']
        return None
        
    @classmethod
    def create_new_equityseries_params(cls, commodity, interval, folder_name, data, source, changable_var_dict_for_folder=dict(), note=''):
        """

        """
        if cls.check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder):
            raise ValueError("This EquitySeries has already been created")
        

        params={
            'hash_value': gg.generate_random_hash() ,
            'commodity': commodity,
            'interval': interval,
            'folder_name': folder_name,
            'data':data,
            'changable_var_dict_for_folder': changable_var_dict_for_folder,
            'source': source,
            'note': note
        }
   
        return params         


    # !!!
    # append EquitySeries to equity_info

# -------------------------

        