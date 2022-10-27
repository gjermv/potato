# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 08:41:19 2022

@author: gjermund.vingerhagen
"""

import pandas

def change_name(name):
    if name == 'Holtskog Nicolai (A485785)':
        return 'Test'
    else:
        return name


def lookUpAV_Oppdrag(x):

    df = AV_Aktivitet.copy()
    aktivitet = x.Aktivitet
    oppdrag = x.Oppdrag
    
    df.loc[(df['AFRY_akt'] == aktivitet) & (df['AFRY_oppdrag'] == oppdrag) , 'tmp'] = 'OK'
    
    if len(df[df['tmp']== 'OK']) > 1: 
        print('Oppdrag: Sjekk for feil!!')

    return df[df['tmp']== 'OK'].iloc[0]['OppdragsID']


def lookUpAV_Aktivitet(x):
    
    df = AV_Aktivitet.copy()
    aktivitet = x.Aktivitet
    oppdrag = x.Oppdrag
    
    df.loc[(df['AFRY_akt'] == aktivitet) & (df['AFRY_oppdrag'] == oppdrag) , 'tmp'] = 'OK'
    
    if len(df[df['tmp']== 'OK']) > 1: 
        print('Oppdrag: Sjekk for feil!!')

    return df[df['tmp']== 'OK'].iloc[0]['Aktivitet og navn']

"""ParseTo5"""
folder = "C:\\python_proj\\parseToReport5\\Files\\"
timeliste_AFRY = "UK-Timeliste-AFRY-637592-07 2022-10-10"
filename =  folder + timeliste_AFRY + ".xlsx"

file_Export = folder + "Export-" + timeliste_AFRY + ".xlsx"

file_report5 =  "C:\\python_proj\\parseToReport5\\Files\\Report5_637592-2022-09-12.xlsx"


df_AFRY = pandas.read_excel(filename,skiprows=8)
AV_Konsulent = pandas.read_excel(file_report5,skiprows=1,sheet_name="Konsulenter",usecols='B:K')
AV_Aktivitet = pandas.read_excel(file_report5,skiprows=1,sheet_name="Aktiviteter",usecols='B:G')


# Fra AFRY til AV-format
df_AFRY['AV_oppdrag'] = df_AFRY.apply(lookUpAV_Oppdrag, axis=1)
df_AFRY['AV_aktivitet'] = df_AFRY.apply(lookUpAV_Aktivitet, axis=1)
df_AFRY[['Ansatt_Navn','Ansatt_nr']] = df_AFRY['Ansatt'].str.split('(', expand=True)
df_AFRY[['Ansatt_Etternavn','Ansatt_Fornavn']] = df_AFRY['Ansatt_Navn'].str.split(' ',1,expand=True)
df_AFRY['Ansatt_Etternavn'] = df_AFRY['Ansatt_Etternavn'].str.strip()
df_AFRY['Ansatt_Fornavn'] = df_AFRY['Ansatt_Fornavn'].str.strip()


# Random endringer 
df_AFRY['Ansatt_Fornavn'] = df_AFRY['Ansatt_Fornavn'].str.replace('Nicolai' , 'Nikolai')


df_AFRY['AV_Navn'] = df_AFRY['AV_oppdrag'] + ': ' + df_AFRY['Ansatt_Fornavn']+ ' ' + df_AFRY['Ansatt_Etternavn']

df_AFRY[['Dato', 'AV_Navn','AV_aktivitet', 'Notat.1', 'Antall']].to_excel(file_Export)
print(file_Export + ' - Generert')





