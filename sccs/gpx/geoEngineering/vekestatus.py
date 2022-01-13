# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 22:22:57 2020

@author: A485753
"""

import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path

excel_tilbud = "C:\\Users\\A485753\\OneDrive - AFRY\\Documents\\Prosjekter lokalt\\sl\\tilbud\\Tilbuds og oppdragsoversikt GEO.xlsx"
to_render=dict()
df_tilbud = pd.read_excel(excel_tilbud, sheet_name="Tilbudsforespørsler")
df_utsendt = pd.read_excel(excel_tilbud, sheet_name="Utsendte tilbud",skiprows=4)
print(df_utsendt.columns)


to_render['tilbudsforesporsler_html'] = df_tilbud.loc[df_tilbud['Registrert'] == 'Uke 51'][['Prosjekt','Oppdragsgiver','Tilbudsansvarlig GEO']].to_html()
to_render['utsendtetilbud_html'] = df_utsendt.loc[df_utsendt['Utsendt'] == 'Uke 50'][['Prosjektnavn','Oppdragsgiver','Tilbudsansvarlig AFRY','Tilbudssum']].to_html()


to_render['okonomigraf'] = 'Test'
# for a, b in df_tilbud.groupby(by="Registrert"):
#     if a == "Uke 51":
#         b.to_html("C:\\Users\\A485753\\OneDrive - AFRY\\Documents\\Prosjekter lokalt\\sl\\tilbud\\Tilbuds og oppdragsoversikt GEO.html")


my_dir = os.path.dirname(__file__)
template_dir = os.path.join(my_dir, 'veke_template')
myloader = FileSystemLoader(template_dir)
env = Environment(loader=myloader)

template = env.get_template('template_veke.html')

txt = template.render(to_render)
file = open('C:\\Users\\A485753\\OneDrive - AFRY\\Documents\\Prosjekter lokalt\\sl\\tilbud\\vekemail.html','w',encoding='utf-8')
file.write(txt)
file.close()