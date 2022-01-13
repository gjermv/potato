import pandas as pd

# df = pd.read_excel('C:\\prosjekter_lokalt\\e10\\BoQ\\RD8347-TUNNEL_BoQ_211220.xlsx',sheet_name='BoQ-2021-12-21')
df = pd.read_excel('C:\\prosjekter_lokalt\\e10\\BoQ\\2022-01-07 Tunnel-volume_lining.xlsx',sheet_name='BOQ 2022-01-07')
#df_struct = pd.read_excel('C:\\prosjekter_lokalt\\e10\\BoQ\\E10_WBS.xlsx',sheet_name='WBS')
df_process = pd.read_excel('C:\\prosjekter_lokalt\\e10\\BoQ\\E10_SVV_R761.xlsx',sheet_name='ProcessCode')


dfMelt = df.melt('WBS',var_name='Process',value_name='Quantity').reset_index(drop=True)
dfMelt['Process'] = dfMelt['Process'].astype(float)
dfMelt['WBS'] = dfMelt['WBS'].astype(float)

dfMelt2 = pd.merge(dfMelt, df_process, how='left', left_on='Process',right_on = 'ProcessCode')
#dfMelt3 = pd.merge(dfMelt2, df_struct, how='left', left_on='WBS', right_on = 'WBS_Total')




dfMelt2[['WBS', 'Element','Process', 'Unit', 'Quantity','Description']].to_excel('C:\\prosjekter_lokalt\\e10\\BoQ\\Export_Tunnel-General.xlsx')
