# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 10:37:04 2024
test_1
@author: TomChiu
"""
import sys
import os
import numpy as np
import pandas as pd
import math
import get_base_dir as gbd
import pickle
import json
import datetime
import uuid

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        Convert specific data types to JSON-serializable types.
        """
        if isinstance(obj, bytes):
            # Convert bytes to string
            return str(obj, encoding='utf-8')
        if isinstance(obj, pd.Series):
            # Convert Series to a dictionary to retain both data and index
            return {'data': obj.tolist(), 'index': obj.index.tolist()}
        if isinstance(obj, pd.DataFrame):
            # Convert DataFrame to a dictionary with 'split' orientation to retain columns and index
            return obj.to_dict(orient='split')
        if isinstance(obj, (datetime.datetime, datetime.date)):
            # Convert datetime or date to a formatted string
            return obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(obj, datetime.datetime) else obj.strftime('%Y-%m-%d')
        
        # Default method for other types
        return json.JSONEncoder.default(self, obj)

def append_path_include_module():
    '''
    This function is used for appending module in same directory
    
    Parameters:
        None
    Returns:
        None 
    ValueError:
        If the script's directory cannot be determined, typically due to the script being executed
        in an environment where `__file__` is not defined
    '''
    try:
        script_dir = get_script_dir()
    except NameError:
        raise ValueError("__file__ is undefined")
    if not script_dir:
        raise ValueError("Fail to get directory")
        
    if script_dir not in sys.path:
        sys.path.append(script_dir)
        

def get_script_dir():
    """
    return main directory

    Returns:
        script_dir(str): dierctory location
    """
    script_dir = gbd.get_base_dir()
    return script_dir
    


def save_df_to_excel(df,file_path,file_name):
    """
    save dataframe to path comimg from get_file_path_for_saving()

    Parameters:
        df(pd.DataFrame): target_df to save
        base_dir(str,opt): Base directory for path creation. If None, script_dir from get_script_dir() is used.
        sub_dir_name_list(list) : list of dir,top directoty would be script_dir from get_script_dir(),
            should be displaced in descent sequence
       file_name(str): file name
       file_type (type): file name

    example:
        save_df_to_excel(df,sub_dir_name_list,file_name,file_type):
            sub_dir_name_list=['sp500',a1]
            file_name='sp500'
            file_typr='xlsx'
          

    """
    os.makedirs(file_path,exist_ok=True)

    df.to_excel(os.path.join(file_path,file_name),engine='openpyxl')
    
def check_if_name_include_in_df_index(df,index_name):
    if index_name in df.index:
        return True
    else:
        return False
    
def ceil_to_nearest_tick(price,tick_size):
    multiple=1/tick_size
    return math.ceil(price * multiple) / multiple

def floor_to_nearest_tick(price,tick_size):
    multiple=1/tick_size
    return math.floor(price * multiple) / multiple

def change_interval_for_date_range(interval):
    interval_mapping = {
    "1m": "T",
    "2m": "2T",
    "5m": "5T",
    "15m": "15T",
    "30m": "30T",
    "60m": "60T",
    "90m": "90T",
    "1h": "H",
    "1d": "D",
    "5d": "5D",
    "1wk": "W",
    "1mo": "M",
    "3mo": "3M"
    }
    return interval_mapping[interval]

def get_backtest_date_range(backtest_start_date,backtest_end_date,interval):
    backtest_date_range=pd.date_range(start=backtest_start_date, end=backtest_end_date, freq=change_interval_for_date_range(interval))
    if len(backtest_date_range)==0:
        raise ValueError('Wrong backtest_date_range interval')
    return backtest_date_range
    
def get_first_in_first_out_list(list_1,list_2):
    if not list_1 or not list_2:
        # print('finish')
        return
    
    if list_1[0]>list_2[0]:
        list_1[0]-=list_2[0]
        list_2.pop(0)
   
    elif list_1[0]<list_2[0]:
        list_2[0]-=list_1[0]
        list_1.pop(0) 
        
    else:
        list_1.pop(0)
        list_2.pop(0)
        
    # print(f'{list_1},{list_2}')
    if list_1 and list_2:
        get_first_in_first_out_list(list_1,list_2)
    else:
        pass
        # print('finish')
        
def save_var_to_pickle(var, dir_list, file_name):
    script_dir = gbd.get_base_dir()
    
    # Create the full directory path by joining all elements in the dir_list
    full_dir_path = os.path.join(script_dir, 'backtest_result', *dir_list)
    
    # Create the directory if it does not exist
    os.makedirs(full_dir_path, exist_ok=True)
    
    # Create the full file path
    full_path = os.path.join(full_dir_path, file_name + '.pkl')
    
    # Save the variable to the pickle file
    with open(full_path, 'wb') as file:
        pickle.dump(var, file)
        
def load_var_from_pickle(dir_list, file_name):
    script_dir = gbd.get_base_dir()
    
    # Create the full directory path by joining all elements in the dir_list
    full_dir_path = os.path.join(script_dir, 'backtest_result', *dir_list)
    
    # Construct the full path to the pickle file
    full_path = os.path.join(full_dir_path, file_name + '.pkl')
    
    # Check if the file exists
    if os.path.exists(full_path):
        # Open the file and load the variable
        with open(full_path, 'rb') as file:
            var = pickle.load(file)
        
        return var
    else:
        raise FileNotFoundError(f"The file {full_path} does not exist.")

def load_pickles_from_path_to_dict(directory_path):
    """

    """
    results = {}

    for filename in os.listdir(directory_path):
        if filename.endswith('.pkl'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'rb') as f:
                key_name = os.path.splitext(filename)[0]  
                results[key_name] = pickle.load(f)

    return results

def cor(df):
    col_list=df.columns
    corr_matrix = df[col_list].corr()
             
    return corr_matrix

def save_to_json(data, filename):
    """

    """

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    
    try:
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4,cls=MyEncoder)
    except Exception as e:
        print(f"error when save data  to json: {e}")
        
def load_from_json(filename):
    """
    Load data from a JSON file.
    If the JSON file contains a dictionary with the format including 'columns', 'data', and 'index',
    it will automatically convert it to a DataFrame.
    If the JSON file contains a dictionary with 'index' and 'data' but no 'columns',
    it will automatically convert it to a Series.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # If data is a dictionary with 'columns', 'data', and 'index', convert to DataFrame
        if isinstance(data, dict):
            if 'columns' in data and 'data' in data and 'index' in data:
                data = json_dict_to_dataframe(data)
            # If data is a dictionary with 'index' and 'data', convert to Series
            elif 'data' in data and 'index' in data and 'columns' not in data:
                data = json_dict_to_series(data)
        
        return data
    
    except Exception as e:
        raise ValueError(f"Error occurred while reading the data: {e}")
        
    
def json_dict_to_dataframe(data_dict):
    """
    Convert a specific format dictionary to a DataFrame.
    The dictionary needs to contain 'columns', 'data', and 'index' keys.
    """
    if not isinstance(data_dict, dict):
        raise ValueError("Input data is not a dictionary")
                
    columns = data_dict.get('columns', [])
    data = data_dict.get('data', [])
    index = data_dict.get('index', [])

    df = pd.DataFrame(data, columns=columns, index=index)

    return df

def json_dict_to_series(data_dict):
    """
    Convert a specific format dictionary to a Series.
    The dictionary needs to contain 'index' and 'data' keys.
    """
    if not isinstance(data_dict, dict):
        raise ValueError("Input data is not a dictionary")
    
    data = data_dict.get('data', [])
    index = data_dict.get('index', [])

    series = pd.Series(data, index=index)

    return series


def generate_random_hash():
    return uuid.uuid4().hex