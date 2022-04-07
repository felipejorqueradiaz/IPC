# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 22:18:22 2022

@author: Felipe
"""
#%% Librerias
import pandas as pd
import numpy as np
import datetime


#%% Librerias
import os
path = 'G:\Mi unidad\IPC Bienes'
path = path.replace('\\', '/')
os.chdir(path)

from ipc_main.functions.variaciones import *
from ipc_main.functions.utils import *

#%% Carga de datos
products = pd.read_csv('ipc_main/data_codes.txt', sep='\t')

#inicio = datetime.datetime.now().year*100+(datetime.datetime.now().month -1)
#fin = datetime.datetime.now().year*100+(datetime.datetime.now().month)

inicio = 202111
fin = 202205
dic = {}

codes = [1,2,3,4,5,7]
#codes = [1,2,3]
for p_code in codes:
#for p_code in products.code:
    print('Estamos en el producto: {}'.format(p_code))
    df = read_product(p_code, inicio, fin)
    df = load_desc(df, p_code)
    df = no_packs(df, 'Modelo')
    df = date_utils(df, 'Fecha')
    #df = price_to_int(df, 'Precio Normal')
    df = filtro_tiendas(df, 'Tienda', 'Falabella', 'Ripley', 'Paris')
    dic[p_code] = df
#%%

#PREPROCESAMIENTO

#%%
ipro = {}
for p_code in codes:
#for p_code in products.code:
    desc = products['descr'][p_code-1].split(',')
    x = IVE_tve(dic[p_code], 'Precio_Normal', 'Fecha', 'Tienda', desc)
    x = IVAR_tv(x, 'Fecha', desc)
    x = IPRO_t(x, 'Fecha')
    x['code'] = p_code
    ipro[p_code] = x

ipro = pd.concat(ipro.values())
p = products[['code', 'INE_name']]
ipro = pd.merge(ipro, p , how="left", on=["code"])
ipro['Fecha'] = [int(x[:4])*100+int(x[5:]) for x in ipro['Fecha']]
ipro.replace(np.inf, np.nan, inplace=True)
ipro.replace(0, np.nan, inplace=True)
ipro.fillna(method="ffill", inplace=True)
ipro.to_csv('G:/Mi unidad/IPC Bienes/ipc_main/data/output/indices.csv', index=False)