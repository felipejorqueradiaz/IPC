# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 19:53:37 2022

@author: Felipe
"""
import pandas as pd
import numpy as np
import glob
import datetime

def read_product(product_code, inicio=202001, fin= 202512, path_base = 'C:/Users/Felipe/Documents/Github/IPC'):
    path = path_base+'/data/input/'
    files = [file_name.replace('\\', '/').replace(path,'') for file_name in glob.glob(path+'*.csv')]
    print(files)
    files = [file_name for file_name in files if (int(file_name[2:5]) == product_code) and (int(file_name[6:12]) >= inicio) and (int(file_name[6:12]) <= fin)]
    meses = [int(file_name[6:12]) for file_name in files]
    files = [pd.read_csv(path+file_name, parse_dates=True) for file_name in files]
    return pd.concat(files)

def load_desc(df, product_code, path_base = 'C:/Users/Felipe/Documents/Github/IPC'):
    
    def prettyList(l):
        l = l.replace("[","")
        l = l.replace("]","")
        l = l.split("'")
        s = ""
        for e in l:
            s +=e
        return s
    
    stores = pd.read_csv(path_base+'/data/input/base/stores.csv')
    stores = stores[["id_tienda", "name"]]
    
    base = pd.read_csv(path_base+'/data/input/base/BASE_{}.csv'.format(str(product_code).zfill(3)))
    dic = pd.read_csv(path_base+'/data_dict.csv', encoding='latin-1')
    dic = dic[dic['product_code'] == product_code].drop('product_code', axis=1)
    
    
    ipc_format = [ "cdg_p",'Tienda', 'Precio_Tarjeta','Precio_Normal', "Fecha"]
    slt_format = ["id", "id_tienda", "precio", "precio_oferta", "fecha"]
    
    ipc_format_desc = dic['ipc_format']
    slt_f_desc = dic['original']
    
    base = base[slt_f_desc].copy()
    base.columns = ipc_format_desc
    if product_code == 7:
        base["Funciones"] = base["Funciones"].fillna("No posee").apply(prettyList)
    df = df[slt_format].copy()
    df.columns = ipc_format
    
    df2 = pd.merge(df, stores, left_on="Tienda", right_on="id_tienda")
    df2["Tienda"] = df2["name"]
    df2 = df2.drop(["id_tienda", "name"], axis=1)
    data = pd.merge(df2, base, left_on="cdg_p", right_on="id")
    data.rename({"cdg_p":"id_slt","catIPC":"categoria"}, axis=1, inplace=True)
    data.drop(["id"],axis=1,inplace=True)
    return data
    
    
def no_packs(df, col_model):
     return df[~df[col_model].str.contains(" \+")]

def price_to_int(df, col_precio):
    df.loc[:, col_precio] = df[col_precio].replace('[\.,]','',regex=True).replace('[\",]','',regex=True).astype(int)
    df.loc[:, col_precio] = pd.to_numeric(df[col_precio].str.extract(r'^(\d+)'))
    return df

def filtro_tiendas(df, col_tienda, *tiendas):
    return df.query('{0} in {1}'.format(col_tienda, str(tiendas)))
        
def date_utils(df, col_fecha):
    x = pd.to_datetime(df[col_fecha], utc=True)
    df[col_fecha] = x.dt.strftime('%Y-%m')
    return df