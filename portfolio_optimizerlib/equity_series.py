import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import generallib.general as gg
import generallib.hash as gh
import get_base_dir as gbd
import ijson, json
from generallib.confirmable import confirmable
import configlib.config as cc

class EquitySeries:
    def __init__(self, hash_value, commodity, interval, folder_name, data, source, changable_var_dict_for_folder=dict(), note=''):
        '''
        Parameters:
            strategy_name(str)
            data(series)
            
            self.interval means interval of this equityseries.data, not folder interval
        '''
        self.hash_value = hash_value
        self.commodity = commodity
        self.interval = interval
        self.folder_name = folder_name
        self.data = data
        self.changable_var_dict_for_folder = changable_var_dict_for_folder
        self.source = source
        self.note = note
        
    @staticmethod
    def resample_series(series, portfolio_optimizer_interval):
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

    @staticmethod
    def create_EquitySeries(config):
        return EquitySeries(**config)

class EquitySeriesList:
    '''
    if edit json, must create New EquitySeriesDict first.
    else you can just get_equityseries_info(), get_data_info()
    all var in str type
    
    equityseries_info and data_info are all in list type
    '''
    def __init__(self):
        self.equityseries_info = self.get_equityseries_info()

    @staticmethod
    def get_equityseries_info(hash_value_to_load=[]):
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path = full_dir_path + '\\equityseries_info.json'
            equityseries_info = []
            # Using ijson to parse large JSON file
            with open(full_file_path, 'r') as file:
                objects = ijson.items(file, 'item')
                if not hash_value_to_load:
                    for obj in objects:
                        try:
                            equityseries_info.append(obj)
                        except Exception as e:
                            raise ValueError(f'cant get equityseries_info: {e}')
                else: 
                    for hash_value in hash_value_to_load:
                        for obj in objects:
                            if obj['hash_value'] == hash_value:
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
    
    @staticmethod
    def get_data_info(hash_value_to_load=[], backtest_start_date=None, backtest_end_date=None):
        """
        Load data_info from JSON files and filter based on hash_value and date range.
    
        Parameters:
            hash_value_to_load (list): List of hash values to load. If empty, load all.
            backtest_start_date (datetime): The start date for filtering data.
            backtest_end_date (datetime): The end date for filtering data.
    
        Returns:
            list: A list of data_info objects with the requested hash values and date range.
        """
        script_dir = gbd.get_base_dir()
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries', 'data_info')
        
        data_info = []
        
        if not hash_value_to_load:
            # Load all JSON files if no specific hash values are provided
            for root, _, files in os.walk(full_dir_path):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            obj = json.load(f)
                            obj['data'] = gg.json_dict_to_series(obj['data'])
                            obj['data'].index = pd.to_datetime(obj['data'].index)
                            gg.check_date_range(backtest_start_date, backtest_end_date, obj['data'])
                            if backtest_start_date and backtest_end_date:
                                obj['data'] = obj['data'].loc[backtest_start_date:backtest_end_date]
                            data_info.append(obj)
        else:
            # Load specific hash values
            for hash_value in hash_value_to_load:
                file_path = gh.find_file_by_hash_value(full_dir_path, hash_value, levels=cc.DEFAULT_DATA_INFO_LEVELS)
                if file_path:
                    with open(file_path, 'r') as f:
                        obj = json.load(f)
                        obj['data'] = gg.json_dict_to_series(obj['data'])
                        obj['data'].index = pd.to_datetime(obj['data'].index)
                        gg.check_date_range(backtest_start_date, backtest_end_date, obj['data'])
                        if backtest_start_date and backtest_end_date:
                            obj['data'] = obj['data'].loc[backtest_start_date:backtest_end_date]
                        data_info.append(obj)
                else:
                    raise ValueError(f"Can't find {hash_value} in data_info")
    
        return data_info

    @confirmable
    @staticmethod
    def save_equityseries_info(data, mode='a'):
        """
        Save equity series info to a JSON file.
        
        :param data: Data to be saved.
        :param mode: File mode ('w', 'a', or 'a+'). Default is 'a'.
        :use **kwargs=confirm_execution=True to confirm before execution.
        """
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path = os.path.join(full_dir_path, 'equityseries_info.json')
            return EquitySeriesList.save_json_data(data, full_file_path, mode)
        except Exception as e:
            raise ValueError(f'Error when saving equityseries_info.json: {e}')
        
    @confirmable
    @staticmethod
    def save_data_info(data):
        """
        Save data info to a JSON file.
        
        :use **kwargs=confirm_execution=True to confirm before execution.
        """
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries','data_info')
        
        try:
            # Use the hash_value from data to determine the folder path
            hash_value = data['hash_value']
            path_list = gh.generate_folder_path_list_by_hash_value(hash_value)
            full_file_path = os.path.join(full_dir_path, *path_list, f'{hash_value}.json')
            
            # Save the data
            return EquitySeriesList.save_json_data(data, full_file_path, mode='w')
            
        except Exception as e:
            raise ValueError(f'Error when saving data_info.json: {e}')

    
    
    @staticmethod
    def save_json_data(data, filename, mode='w'):
        """
        Save data to a JSON file using the specified mode.
        
        :param data: Data to be saved.
        :param filename: Path to the JSON file.
        :param mode: File mode ('w' or 'a+'). Default is 'a+'.
        """
        if mode not in ['w', 'a+']:
            raise ValueError("Invalid mode. Choose 'w' or 'a+'.")
        if mode == 'w':
            # Overwrite mode
            return gg.save_to_json_overwrite(data, filename)
        elif mode == 'a+':
            # Append and read mode
            return EquitySeriesList.append_to_json(data, filename)
    
    @staticmethod
    def append_to_json(data, filename):
        """
        Append data to a JSON file in 'a+' mode, without overwriting the closing bracket.
        """
        if not os.path.exists(filename):
            raise ValueError(f"The file {filename} does not exist.")
        
        try:
            with open(filename, 'a+', encoding='utf-8') as json_file:
                # seek
                json_file.seek(0, os.SEEK_END)
                pos = json_file.tell() 
                
                # Move back to skip any trailing whitespace or newline characters
                while pos > 0:
                    json_file.seek(pos)
                    last_char = json_file.read(1)
                    if last_char.strip():  # Check if the last_char is not a whitespace or newline
                        break
                    pos -= 1
    
                if last_char == ']':
                    # Move back to overwrite the closing bracket
                    json_file.seek(pos)
                    json_file.truncate()  # Remove the last character ']', effectively deleting it
    
                    if pos > 1:  # Check if there is more than just an empty array
                        # Add a comma before the new data if the list is not empty
                        json_file.write(',\n')
                    
                    # Write the new data
                    formatted_data = json.dumps(data, ensure_ascii=False, indent=4)
                    json_file.write(formatted_data)
                    
                    # Write the closing bracket back
                    json_file.write('\n]')
                else:
                    raise ValueError(f"The file {filename} does not have a valid JSON list structure.")
    
        except Exception as e:
            print(f"Error when appending data to JSON: {e}")
    


    @staticmethod
    @confirmable
    def create_default_equityseries_info():
        """
        use **kwargs=confirm_execution=True to confirm before execution.
        """
        default_list = []
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path = full_dir_path + '\\equityseries_info.json'
            return gg.save_to_json_overwrite(default_list, full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving default equityseries_info.json: {e}')

    @staticmethod
    def check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        Check if an EquitySeries exists with the same commodity, interval, folder_name, and changable_var_dict_for_folder.
        """
        equityseries_info = EquitySeriesList.get_equityseries_info()
        for value in equityseries_info:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return True
        return False
    
    @staticmethod
    def get_equityseries_hash_value(commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        Return the hash_value of the equityseries if the commodity, interval, folder_name and changable_var_dict_for_folder match.
        """
        equityseries_info = EquitySeriesList.get_equityseries_info()
        for value in equityseries_info:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return value['hash_value']
        return None
        
    @staticmethod
    def create_new_equityseries_params(commodity, interval, folder_name, data, source, changable_var_dict_for_folder=dict(), note=''):
        """
        Create a new set of parameters for an EquitySeries and return it as a dictionary.
        """
        if EquitySeriesList.check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder):
            raise ValueError("This EquitySeries has already been created")
        
        params = {
            'hash_value': gh.generate_random_hash(),
            'commodity': commodity,
            'interval': interval,
            'folder_name': folder_name,
            'data': data,
            'changable_var_dict_for_folder': changable_var_dict_for_folder,
            'source': source,
            'note': note
        }
   
        return params
