# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 22:14:42 2022

@author: Felipe
"""

#%%

import pandas as pd
import numpy as np

#%%

def IVE_tve(df, col_precio, col_fecha, col_tienda, var_descr):
    
    var_descr = var_descr + [col_tienda]
    df.dropna(subset=var_descr, inplace=True)
    df = df.groupby(var_descr+[col_fecha], as_index=False).median()
    df.sort_values(col_fecha, inplace=True)
    df.loc[:, 'IVE_tve'] = df[col_precio].div(df.groupby(var_descr)[col_precio].shift(1))*100
    return df.drop(col_precio, axis=1).dropna(subset=['IVE_tve'])


#%%
def IVAR_tv(df_ive_tve, col_fecha, var_descr):
    
    var_descr = var_descr + [col_fecha]
    
    IVAR = df_ive_tve.groupby(var_descr, as_index=False).agg({'IVE_tve':['prod', 'count']})
    
    IVAR.columns = var_descr + ['IVAR_tv', 'IVAR_tv_count']
    
    IVAR.loc[:, 'IVAR_tv'] = IVAR['IVAR_tv']**(1/IVAR['IVAR_tv_count'])
    
    return IVAR.drop('IVAR_tv_count', axis=1).dropna(subset=['IVAR_tv'])

#%%
def IPRO_t(df_ivar_tv, col_fecha):
    
    IPRO_count = df_ivar_tv.groupby([col_fecha], as_index=False)['IVAR_tv'].count()
    
    IVAR_new = pd.merge(df_ivar_tv, IPRO_count, on= col_fecha)
    
    IVAR_new.loc[:, 'IPRO_tv'] = IVAR_new['IVAR_tv_x']**(1/IVAR_new['IVAR_tv_y'])
    
    IPRO = IVAR_new.groupby([col_fecha], as_index=False)['IPRO_tv'].prod()
    
    return IPRO.rename({'IPRO_tv' : 'IPRO_t'}, axis=1)
