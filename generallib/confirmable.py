import tkinter as tk
from tkinter import messagebox
import sys
from functools import wraps

def confirmable(func):
    """
    can only use in normal func or statisticmethod, not for classmethod
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if 'confirm_execution' is in kwargs and is True
        if kwargs.get('confirm_execution', False):
            # Show a confirmation dialog to ask the user whether to continue
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            result = messagebox.askyesno("Confirmation", "Do you want to run this function?")
            
            if not result:
                # If the user cancels, exit the program or stop the function
                sys.exit("Operation cancelled")
        
        # Remove 'confirm_execution' from kwargs before calling the function
        kwargs.pop('confirm_execution', None)

        return func(*args, **kwargs)

    
    return wrapper





# HINT
# @confirmable
# def my_function(msg):
#     """
#     Example function that processes data and can optionally confirm execution.
#     """
#     print(msg)
# To run the function with confirmation
# my_function('hello', confirm_execution=True)
# To run the function without confirmation
# my_function('hello')
