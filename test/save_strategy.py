import pandas as pd
from pandas.tseries.offsets import MonthEnd

for year in range(2021, 2025):
    # 讀取 Excel 文件的所有 sheet
    file_path = f"C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\tom_check_zz\\tom_check\\{year}_rebalanced.xlsx"
    sheet_dict = pd.read_excel(file_path, sheet_name=None)  # 讀取所有工作表
    
    combined_df = pd.DataFrame()  # 用於合併所有工作表的數據
    sheet_names = list(sheet_dict.keys())  # 取得所有工作表名稱
    last_sheet = sheet_names[-1]  # 取得最後一個工作表的名稱
    
    for sheet_name, df in sheet_dict.items():
        if sheet_name == last_sheet:
            continue  # 跳過最後一個工作表
        
        # 篩選出需要的三個欄位：'time_index', 'name', 'return'
        if 'time_index' in df.columns and 'name' in df.columns and 'return' in df.columns:
            filtered_df = df[['time_index', 'name', 'return']]
            
            # 將 time_index 改為下一個月的最後一天
            filtered_df['time_index'] = pd.to_datetime(filtered_df['time_index']) + MonthEnd(1)
            
            # 將篩選的數據附加到 combined_df
            combined_df = pd.concat([combined_df, filtered_df], ignore_index=True)
    
    # 將合併後的數據寫入到新的 Excel 文件中的單一工作表
    output_file_path = f"C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\tom_check_zz\\tom_check\\new\\{year}_rebalanced_combined.xlsx"
    combined_df.to_excel(output_file_path, index=False)
    
    print(f"{year} 的處理已完成，結果儲存在 {output_file_path} 中")
