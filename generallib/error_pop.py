# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:19:04 2024

@author: user
"""

import tkinter as tk
from tkinter import messagebox

def show_error_message(error_message):
    root = tk.Tk()
    # 将主窗口设置为最顶层
    root.attributes('-topmost', True)  # 确保窗口在最上层
    root.withdraw()  # 隐藏主窗口

    # 显示错误消息的弹出窗口
    messagebox.showerror("Error", error_message)

    # 等待用户点击后关闭
    # root.mainloop()
    root.destroy()

    
    