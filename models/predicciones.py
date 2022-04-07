# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 20:11:43 2022

@author: Felipe
"""


import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
#%% Indices

indices = pd.read_csv('G:/Mi unidad/IPC Bienes/ipc_main/data/output/indices.csv')

#%% IPC
ipc = pd.read_csv('G:/Mi unidad/IPC Bienes/ipc_main/ipc-csv.csv',
                  encoding = 'latin-1',
                  skiprows=0,
                  header=3,
                  sep=';')

ipc2 = pd.read_csv('G:/Mi unidad/IPC Bienes/ipc_main/ipc-1318.csv',
                  encoding = 'latin-1', sep=';',decimal=',')
ipc2.columns = list(ipc.columns)
ipc = pd.concat([ipc, ipc2], ignore_index=True)
#%%
ipc = ipc[['Año', 'Mes', 'GLOSA', 'Índice', 'Variación Mensual  ( % )']]
ipc['Fecha'] = ipc['Año']*100+ipc['Mes']

#mas_fecha = 3
#max_fecha = ipc['Fecha'].max()

#ipc.drop(['Año'], axis=1, inplace=True) 
ipc.rename(columns={'GLOSA': 'INE_name',
                    'Variación Mensual  ( % )':'Var_ine'}, inplace=True)
#%% IPC historico

ipc_hist = {}

años = 7

for prod in indices['INE_name'].unique():
    temp = ipc[ipc['INE_name']==prod]
    temp = temp.append({'Fecha':202203, 'INE_name':prod},
                       ignore_index=True)
    temp = temp.sort_values(by='Fecha')
    for i in range(años):
        code = 't-{}'.format(12*(i+1))
        temp[code] = temp['Var_ine'].shift(12*(i+1))
    ipc_hist[prod] = temp
    
ipc_h = pd.concat(ipc_hist.values(), ignore_index=True)
#%%
df = pd.merge(indices, ipc_h , how="left", on=["Fecha", 'INE_name'])
df['IPRO_diff'] = df.groupby(['INE_name'])['IPRO_t'].diff()

#%%
def rezago(df, n_meses):
    keys = ['IPRO_diff']
    for i in range(n_meses):
        key = 'Error_t{}'.format(i+1)
        df[key] = df['Var_ine'].shift(i+1) - df['IPRO_diff'].shift(i+1)
        keys.append(key)
    return df.dropna(subset=keys)

rezago_meses = 3
df = rezago(df, rezago_meses)

#%%
class Producto:
    
    def __init__(self, x, y, x_pred):
        self.X = x
        self.y = y
        self.X_pred = x_pred
        
    def split(self, test_prop):
        train_len = int(np.round(len(self.y)*(1-test_prop)))
        
        self.X_train = self.X[:train_len]
        self.y_train = self.y[:train_len]
        
        self.X_test = self.X[train_len:]
        self.y_test = self.y[train_len:]
        
    def fit_lr(self):
        reg = LinearRegression(normalize=False).fit(self.X_train, self.y_train)
        self.reg = reg
        #print('R2 train: {}'.format(np.round(reg.score(self.X_train, self.y_train), 4)))
        #print('R2 test: {}'.format(np.round(reg.score(self.X_test, self.y_test), 4)))
    
    def predict(self):
        return self.reg.predict(self.X_pred)

#%%
prod_dict = {}
for prod in df.INE_name.unique():
     X = df[(df['INE_name'] == prod) & (df['Var_ine'].notna())].iloc[:,-rezago_meses-1-años:]
     y = df[(df['INE_name'] == prod) & (df['Var_ine'].notna())]['Var_ine']
     X_pred = df[(df['INE_name'] == prod) & (~df['Var_ine'].notna())].iloc[:,-rezago_meses-1-años:]
     
     prod_dict[prod] = Producto(X, y, X_pred)
     print('Producto: {}'.format(prod))
     prod_dict[prod].split(0.20)
     prod_dict[prod].fit_lr()
     lin = prod_dict[prod].predict()
     regr = RandomForestRegressor(max_depth=5, random_state=0)
     regr.fit(X, y)
     rf = regr.predict(X_pred)
     print('\tLineal: {}\n\tRandom Forest: {}\n\tBruto: {}'.format(lin, rf, X_pred['IPRO_diff'].values))
