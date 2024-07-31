# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 04:34:38 2024

@author: user
"""

import requests


def line_notify(msg):
    token = 'XW8RtAJJp4qAOqrDCbdWLW1JKJRBSeKNC0lHRqf1qZr'  
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': msg,
    }
    
    requests.post(url, headers=headers, data=data)


