# -*- coding: utf-8 -*-
"""options(data_driver causal to options effect)

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q0RWmmSWKnRptYoSxn1DObRV42fGIY5h

note in this code i am having driver excel as casual which is 127 indicator and 14 sp 500 stock as effect how they are effected by world indicators
"""
# load the libraries

import pandas as pd
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
import os
# read the data from the excel file names are self explainatory 

daily=pd.read_excel(r'daily.xlsx')
data_driver=pd.read_excel(r'data_drivers_2008_full_cutcolumns.xlsx')
sp500=pd.read_excel(r'constituents_SPX_2008.xlsx')
options=pd.read_excel(r'Drivers_no_SB_Sectors.xlsx')
# preprocess the data 

daily = daily.fillna(method='ffill')
data_driver = data_driver.fillna(method='ffill')
data_driver['Date'] = pd.to_datetime(data_driver['Date'], format='%Y%m%d')
sp500 = sp500.fillna(method='ffill')
sp500['Date'] = pd.to_datetime(sp500['Date'], format='%Y%m%d')
options['Date'] = pd.to_datetime(options['Date'], format='%Y%m%d')
daily = daily.fillna(method='ffill')
columns_to_drop = ['Unnamed: 0', 'Datetime', ]
daily = daily.drop(columns=columns_to_drop)

# set the date as index for the data to make it easy to merge and compare 

daily.set_index('Date', inplace=True)
data_driver.set_index('Date', inplace=True)
sp500.set_index('Date', inplace=True)
options.set_index('Date',inplace=True)


columns_with_negatives1 = data_driver.columns[data_driver.lt(0).any()]
columns_with_negatives2 = sp500.columns[sp500.lt(0).any()]
data_driver = data_driver.drop(columns=columns_with_negatives1)
sp500 = sp500.drop(columns=columns_with_negatives2)
options_effect=options[['ITRAXX EU 5YR TOT RET IX','ITRAXX XO 5YR TOT RET IX', 'VSTOXX Index','STXE 600 (EUR) Pr','CDX HY Basket OTR','VSTOXX Index', 'Euro Stoxx 50 Pr']]
data_driver=((np.log(data_driver)).diff()).dropna()
df = pd.merge(data_driver, options_effect, on='Date')

# copy the data to new data frame to avoid any changes in the original data and remove the errors 
ce_df3=df.copy()

# set the values for the lag and interval and k
k = 200
lag = 5
interval = 100

# loop over the data to get the values of the pca and the eigen values as per the algorithm discussed in the paper  and store them in the excel file  

for f in range(data_driver.shape[1]+3, data_driver.shape[1] +options_effect.shape[1]):
    Data_res_all_columns = pd.DataFrame()
    for col_index in range(0, data_driver.shape[1]):
        Data_res = pd.DataFrame()
        for i in range(k, ce_df3.shape[0]):
            Data_k = ce_df3.iloc[i - interval:i, :]
            Data_k = (Data_k - Data_k.mean()) / Data_k.std()
            Date_ref = ce_df3.index[i]
            V_values = []
            for j in range(lag + 1):
                X = Data_k.iloc[:, col_index].values.reshape(-1, 1)
                Y = Data_k.iloc[:, f].values.reshape(-1, 1)
                Data_pca = pd.DataFrame(np.column_stack((X, Y)))

                Data_pca[1] = Data_pca[1].shift(periods=j)
                Data_pca = Data_pca.replace([np.inf, -np.inf], np.nan)
                Data_pca = Data_pca.fillna(0)

                pca = PCA(n_components=2)
                pca.fit(Data_pca)
                eigenvalues = pca.explained_variance_
                eigenvalue_ratio = eigenvalues[0] / (eigenvalues[0] + eigenvalues[1])
                V_values.append(eigenvalue_ratio)

            std_V_values = np.std(V_values)
            col_name = ce_df3.columns[col_index]
            Data_r = pd.DataFrame([[std_V_values]], index=[Date_ref], columns=[col_name])

            Data_res = pd.concat([Data_res, Data_r])

        Data_res_all_columns = pd.concat([Data_res_all_columns, Data_res], axis=1)

    Data_res_all_columns.to_excel(f"{ce_df3.columns[f]}_options_real_data(options causal to data_drivers).xlsx")



