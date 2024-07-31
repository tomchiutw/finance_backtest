# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 17:07:08 2024

@author: user
"""


class Folder:
    def __init__(self,name,description=''):
        self.name=name
        self.description=description
        self.folder_dict=dict()
    
        
    def _init_folder(self):
        self.check_folder_dict()
        if hasattr(self,self.name):
            pass
        else:
            raise ValueError(f"No strategy found for the folder: {self.name}. Please create in folder.py")
            
    def check_folder_dict(self):
        # List of required keyword arguments
        required_keys = ['account', 'interval', 'tradingpanel']

        # Check if all required keys are in self.folder_dict
        if not all(key in self.folder_dict for key in required_keys):
            missing_keys = [key for key in required_keys if key not in self.folder_dict]
            raise ValueError(f"Missing required keyword arguments: {', '.join(missing_keys)}")

    def show_folder_dict(self):
        return self.folder_dict
          
        
        
class FolderList:
    def __init__(self):
        '''
        Folders categoried to 2 types in dict, 'long' and 'short' 
        '''
        self.folders={'long':[],'short':[]}
        
    def append_folder_to_folderlist(self,direction,folder):
        '''
        Append folder to folderlist

        Parameters:
            direction(str): 'long' or 'short', for dict in FolderList.folders key
            flolder(Folder): 
        ------
        ValueError:
            raise error if folder existed

        '''
        if any(f.name==folder.name for f in self.folders[direction]):
            raise ValueError('Folder existed')
        else:
            self.folders[direction].append(folder)