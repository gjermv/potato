# -*- coding: utf-8 -*-

import pandas as pd
import glob as glob
import os


results = pd.DataFrame([])


for path in glob.glob('C:\\python_proj\\quizmaster\\Resultat\\*.xlsx'):
    comp = os.path.basename(path).split('.')[0]
    df = pd.read_excel(path, sheet_name='Final Scores',skiprows=2)
    
    P1 = df['Total Score (points)'].max()
    P2 = P1/2
    players = df['Player'].count()
    print(P1,P2,players)

    maxScore = 50
    if players >= 10:
        maxScore = 100
    elif players >= 5:
        maxScore = players*10
        
    df[comp] = ((df['Total Score (points)']-P2)/(P1-P2)* maxScore).astype(int)
    df.loc[df[comp]<0,comp]= 0
    df = df.set_index('Player')
    print(df[comp])
    results = pd.concat([results,df[comp]],axis=1)
    #print(df[['Player',comp]])

results['Totalt'] = results.sum(axis=1)
results.sort_values('Totalt',ascending=False, inplace=True,)
results.to_excel('C:\\python_proj\\quizmaster\\Resultater 2022.xlsx')