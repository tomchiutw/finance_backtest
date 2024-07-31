# -*- coding: utf-8 -*-
"""
Created on Wed May 15 18:52:18 2024

@author: user
"""

import os

def get_base_dir():
    current_file=os.path.abspath(__file__)
    base_dir=os.path.dirname(current_file)+'\\'
    
    return base_dir


