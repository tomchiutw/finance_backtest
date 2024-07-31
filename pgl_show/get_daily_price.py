import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import copy
# import self module
import backtestlib.commodity as bc
from backtestlib.commodity import CommodityList
import generallib.general as gg
import generallib.line as gl
import generallib.plot as gp
import backtestlib.performance as bp
import backtestlib.optimizer as bop
import portfolio_optimizerlib.portfolio_optimizer as popo
import portfolio_optimizerlib.equity_series as pes
import backtestlib.account as ba
import backtestlib.order as bo
import backtestlib.tradingpanel as bt
import backtestlib.inventory as bi
import backtestlib.marketdata as bm
import backtestlib.kline as bk
import backtestlib.backtest as bb
import backtestlib.indicator_list as bil
import get_base_dir as gbd
script_dir=gbd.get_base_dir()

# commodity_prices_features
commodity_close_dict=dict()
filepath=f'C:\\Users\\user\\miniconda3\\envs\\Finance_Backtest\\finance_backtest\\pgl_show\\equity_prices_features'
for filename in os.listdir(filepath):
    underscore_index=filename.find('_')
    if underscore_index!=-1:
        commodity_name=filename[:underscore_index]
        df=pd.read_csv(os.path.join(filepath,filename),index_col=0)
        df.index=pd.to_datetime(df.index)
        commodity_close_dict[filename[:underscore_index]]=df[['BidClose']]


        
# data dict_to_dataframe
data_info_dict=pes.EquitySeriesDict.get_data_info()
for key,item in data_info_dict.items():
    df=gg.json_dict_to_dataframe(item['data'])
    del item['data']
    item['data']=df
    
# merge df
corr_summary=[]
corr_standard=0.3
i1,i2,i3,i4=0,0,0,0
for num,info in data_info_dict.items():
    temp_corr_df=pd.DataFrame()
    commodity_name = info['commodity']
    if commodity_name in commodity_close_dict:
        temp_corr_df=info['data'].copy()
        temp_corr_df['Close']=commodity_close_dict[info['commodity']]
        # corr_summary
        corr_df=gg.cor(temp_corr_df)
        corr_summary.append(corr_df.iloc[0,1])
        
        if corr_df.iloc[0,1]>=corr_standard:
            info['changable_var_dict_for_folder']['trend']='follow'
            info['changable_var_dict_for_folder']['position']='long'
            info['changable_var_dict_for_folder']['corr']=corr_df.iloc[0,1]
            i1+=1
        elif corr_df.iloc[0,1]>=0 and corr_df.iloc[0,1]<corr_standard:
            info['changable_var_dict_for_folder']['trend']='counter'
            info['changable_var_dict_for_folder']['position']='long'
            info['changable_var_dict_for_folder']['corr']=corr_df.iloc[0,1]
            i2+=1
            
        elif corr_df.iloc[0,1]>=-corr_standard and corr_df.iloc[0,1]<0:
            info['changable_var_dict_for_folder']['trend']='counter'
            info['changable_var_dict_for_folder']['position']='short'
            info['changable_var_dict_for_folder']['corr']=corr_df.iloc[0,1]
            i3+=1
        else:
            info['changable_var_dict_for_folder']['trend']='follow'
            info['changable_var_dict_for_folder']['position']='short'
            info['changable_var_dict_for_folder']['corr']=corr_df.iloc[0,1]
            i4+=1
print(f'i1:{i1/(i1+i2+i3+i4):.2f}, i2={i2/(i1+i2+i3+i4):.2f}, i3={i3/(i1+i2+i3+i4):.2f}, i4={i4/(i1+i2+i3+i4):.2f}')


# final save
# equityseries_info=pes.EquitySeriesDict.get_equityseries_info()
# temp_info=copy.deepcopy(data_info_dict)
# for item in temp_info.values():
#     del item['data']
# equityseries_info['info']=temp_info
# pes.EquitySeriesDict.save_equityseries_info(equityseries_info)
# pes.EquitySeriesDict.save_data_info(data_info_dict)
        
        
        