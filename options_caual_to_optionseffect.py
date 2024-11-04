
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

options=pd.read_excel(r'Drivers_no_SB_Sectors.xlsx')
options.set_index('Date',inplace=True)
options_causal =options[['Pan-European High Yield','U.S. Corporate High Yield','STXE 600 (EUR) Pr', 'VSTOXX Index','U.S. Corporate High Yield','Euro Stoxx 50 Pr','VSTOXX Index']]
options_effect=options[['ITRAXX EU 5YR TOT RET IX','ITRAXX XO 5YR TOT RET IX', 'VSTOXX Index','STXE 600 (EUR) Pr','CDX HY Basket OTR','VSTOXX Index', 'Euro Stoxx 50 Pr']]
df=pd.merge(options_causal,options_effect,on="Date")
ce_df3=df.copy()

k = 200
lag = 5
interval = 100
Data_res_all_columns = pd.DataFrame()

for f in range(options_causal.shape[1], options_causal.shape[1]+options_effect.shape[1]):
    Data_res_all_columns = pd.DataFrame()
    for col_index in range(0, options_causal.shape[1]):
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

    Data_res_all_columns.to_excel( f"{ce_df3.columns[f]}_options_real_data(options causal to options effect).xlsx")



