import os
import pdb
import sys
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import generallib.general as gg
import get_base_dir as gbd
import ijson

class EquitySeries:
    def __init__(self,num,commodity,interval,folder_name,data,source,changable_var_dict_for_folder=dict(),note=''):
        '''
        Parameters:
            strategy_name(str)
            data(dataframe)
        
        '''
        self.num=num
        self.commodity=commodity
        self.interval=interval
        self.folder_name=folder_name
        self.data=data
        self.changable_var_dict_for_folder=changable_var_dict_for_folder
        self.source=source
        self.note=note
        

    
        
    def resample_series(self,portfolio_backtest_start_date,portfolio_backtest_end_date,portfolio_optimizer_interval):
        self.data.dropna(inplace=True)
        self.data=self.data.resample(gg.change_interval_for_date_range(portfolio_optimizer_interval)).asfreq()
        self.data = self.data.ffill()
        
        return self.data

    @classmethod
    def create_EquitySeries(cls,config):
        return EquitySeries(**config)

class EquitySeriesDict:
    '''
    if edit json, must create New EquitySeriesDict first.
    else you can just get_equityseries_info(), get_data_info()
    all var in str type
    '''
    def __init__(self):
        self.equityseries_info=self.__class__.get_equityseries_info()
        self.total_equityseries_num=self.equityseries_info['total_equityseries_num']
    
    def get_next_num(self):
        self.total_equityseries_num+=1
        return self.total_equityseries_num

    
    
    
    @classmethod
    def get_equityseries_info(cls):
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\equityseries_info.json'
            return gg.load_from_json(full_file_path)
        except Exception as e:
            raise ValueError(f'error when loading equityseries_info.json: {e}')
    
    @classmethod
    def get_data_info(cls,nums_to_load=[]):
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path = full_dir_path + '\\data_info.json'
            
            data_info = []
            # Using ijson to parse large JSON file
            with open(full_file_path, 'r') as file:

                objects = ijson.items(file,'item')
                
                for obj in objects:
                    if not nums_to_load or obj['num'] in nums_to_load:
                        obj['data'] = gg.json_dict_to_dataframe(obj['data'])
                        data_info.append(obj)
                    
            return data_info
        except Exception as e:
            raise ValueError(f'error when loading data_info.json: {e}')
    
    # @classmethod
    # def get_data_info(cls):
        
    #     script_dir = gbd.get_base_dir()
    #     # Create the full directory path by joining all elements in the dir_list
    #     full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
    #     try:
    #         full_file_path=full_dir_path+'\\data_info.json'
    #         # trasnfer data dict to df
    #         data_info=gg.load_from_json(full_file_path)
    #         for item in data_info:
    #             data_df=gg.json_dict_to_dataframe(item['data'])
    #             del item['data']
    #             item['data']=data_df
    #         return data_info
    #     except Exception as e:
    #         raise ValueError(f'error when loading data_info.json: {e}')   
            
    @classmethod
    def save_equityseries_info(cls,data):
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\equityseries_info.json'
            return gg.save_to_json(data, full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving equityseries_info.json: {e}')
            
    @classmethod
    def save_data_info(cls,data):
        
        script_dir = gbd.get_base_dir()
        # Create the full directory path by joining all elements in the dir_list
        full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
        try:
            full_file_path=full_dir_path+'\\data_info.json'
            return gg.save_to_json(data, full_file_path)
        except Exception as e:
            raise ValueError(f'error when saving data_info.json: {e}')
    
    @classmethod
    def create_default_equityseries_info(cls):
        
        # Show a confirmation dialog to ask the user whether to continue
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        result = messagebox.askyesno("Confirmation", "Are you sure you want to create the default equityseries_info.json file?")

        if result:
            default_dict=dict()
            default_dict['total_equityseries_num']=0
            default_dict['info']=[]
            
            script_dir = gbd.get_base_dir()
            # Create the full directory path by joining all elements in the dir_list
            full_dir_path = os.path.join(script_dir, 'backtest_result', 'saved_equityseries')
            try:
                full_file_path=full_dir_path+'\\equityseries_info.json'
                return gg.save_to_json(default_dict , full_file_path)
            except Exception as e:
                raise ValueError(f'error when saving default equityseries_info.json: {e}')
        else:
            sys.exit("Operation cancelled")
            
    @classmethod
    def check_equityseries_exists(cls, commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        not ok if commodity, interval, folder_name and changable_var_dict_for_folder same
        """
        equityseries_info = cls.get_equityseries_info()
        for value in equityseries_info['info']:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return True
        return False
    
    @classmethod
    def get_equityseries_num(cls, commodity, interval, folder_name, changable_var_dict_for_folder):
        """
        Return the num of the equityseries if the commodity, interval, folder_name and changable_var_dict_for_folder match.
        """
        equityseries_info = cls.get_equityseries_info()
        for value in equityseries_info['info']:
            if (value['commodity'] == commodity and
                value['interval'] == interval and
                value['folder_name'] == folder_name and
                value['changable_var_dict_for_folder'] == changable_var_dict_for_folder):
                return value['num']
        return None
        
    @classmethod
    def create_new_equityseries(cls, num, commodity, interval, folder_name, data, source, changable_var_dict_for_folder=dict(), note=''):
        """

        """
        if cls.check_equityseries_exists(commodity, interval, folder_name, changable_var_dict_for_folder):
            raise ValueError("This EquitySeries has already been created")
        
        # Update equityseries_info
        equityseries_info = cls.get_equityseries_info()
        next_num = cls().get_next_num()
        equityseries_info['info'][next_num] = {
            'commodity': commodity,
            'interval': interval,
            'folder_name': folder_name,
            'changable_var_dict_for_folder': changable_var_dict_for_folder,
            'source': source,
            'note': note
        }

        
        return EquitySeries(num, commodity, interval, folder_name, data, source, changable_var_dict_for_folder, note)           
# -------------------------

        