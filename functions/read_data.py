# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 12:41:15 2022

@author: Felipe
"""

import pandas as pd
import glob


def read_product(product_code, inicio=202001, fin= 202512):
    path = 'G:/Mi unidad/IPC Bienes/ipc_main/data/input/'
    files = [file_name.replace('\\', '/').replace(path,'') for file_name in glob.glob(path+'*.csv')]
    files = [file_name for file_name in files if (int(file_name[2:5]) == product_code) and (int(file_name[6:12]) >= inicio) and (int(file_name[6:12]) <= fin)]
    meses = [int(file_name[6:12]) for file_name in files]
    files = [pd.read_csv(path+file_name) for file_name in files]
    print(meses)
    for i in range(len(files)):
        df = files[i]
        df.loc[:, 'Fecha'] = meses[i]
        files[i] = df
    return pd.concat(files)