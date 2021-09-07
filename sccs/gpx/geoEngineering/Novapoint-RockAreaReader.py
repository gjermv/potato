# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 11:52:53 2021

@author: A485753
"""

import pandas as pd
import glob as glob
import os as os

data_folder = "C:\\python_proj\\RockAreaReader\\2021-01-28\\*.xlsx"
data_out =  "C:\\python_proj\\RockAreaReader\\output\\output 2021-01-28-v3.xlsx"
test_file = "C:\\python_proj\\RockAreaReader\\12000_O1.xlsx"


with pd.ExcelWriter(data_out) as writer:

    for file in glob.glob(data_folder):
        file_name = os.path.basename(file)
        file_name = file_name.split('.')[0]
        
        
        try:
            df = pd.read_excel(file, sheet_name='Area',header=11, index_col='Chainage')
            df = df.drop(index='Total Sum')
            df.index = df.index.astype(float)
            df['chainage'] = df.index
            
            
            df_rockcut = df[df['Rock Cut Face\n(m2)']>40]
            
            df_rockcut['chainage_diff'] = df_rockcut['chainage'].diff() 
            
            # Print all rockcuts pr roadline
            df_rockcut.to_excel(writer,sheet_name=file_name)
            
            start_list = [df_rockcut['chainage'].min()]
            stop_list =[]
            # start_list.append(list(df_rockcut[df_rockcut['chainage_diff'].shift(-1)>10]['chainage_diff'].index))
            for i in list(df_rockcut[df_rockcut['chainage_diff']>10]['chainage_diff'].index):
                start_list.append(i)
            
            for i in list(df_rockcut[df_rockcut['chainage_diff'].shift(-1)>10]['chainage_diff'].index):
                stop_list.append(i)
            stop_list.append(df_rockcut['chainage'].max())
            

            
            if len(df_rockcut)>1:
                for i in range(len(stop_list)):
                    max_height = df_rockcut.loc[start_list[i]:stop_list[i]]['Rock Cut Face\n(m2)'].max()/10
                    sum_area = df_rockcut.loc[start_list[i]:stop_list[i]]['Rock Cut Face\n(m2)'].sum()
                    print(file_name,start_list[i],stop_list[i],sum_area,max_height)
        except: 
            print("***** Error *****", file_name, )
            continue