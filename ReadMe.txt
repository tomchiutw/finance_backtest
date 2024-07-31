
folder:

1. account、interval、tradingpanel必要的
2. 建立folder時，其他的要自己先設立好
3. 1和2都在class folder.name那裏先建立好，哪些可變(commodity、marketdata)



class Long_Index_With_Low_Percent(bf.Folder):
    
    def __init__(self,changable_var_dict,description=''):
        self.changable_var_dict=changable_var_dict
        super().__init__(self.__class__.__name__,description=description)    
        self._init_folder_dict(self.get_folder_dict())
        self._init_folder() # this function from folder.py
        
    def _init_folder_dict(self,folder_dict):
        self.kwargs=folder_dict

    接下來不同
	
    def get_folder_dict(self)
    def Long_Index_With_Low_Percent(self,time_index)

changable_var_dict->folder_dict->return_dict

-----------------
3. 安裝套件
4. forrexconnect
5. 測試
----------------
分線壓後，先做日線
1. for loop(year,month)
2. for loop(commodity_list)
3. optimizer
4. long_with 的資金管理