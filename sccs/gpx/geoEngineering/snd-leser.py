# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 14:05:02 2021

@author: A485753
"""

import glob
import os
import ezdxf
import pandas as pd
from sympy import *

def snd_converter(filename):
    file = open(filename, 'r')
    txt = file.read()
    txt_split = txt.split('\n')
    y = float(txt_split[0].strip())
    x = float(txt_split[1].strip())
    z = float(txt_split[2].strip())
    bedrock_43 = -9999
    
    for linenr in range(15,len(txt_split)-4):
        bedrock_43 = find_rock(txt_split[linenr])
        if bedrock_43 != -9999:
            break
    
    depth, stop_reason = snd_lastline(txt_split[-3])
    return (x,y,z,depth,bedrock_43,stop_reason)


def snd_lastline(line): 
    depth = float(line[0:8].strip())
    stop_reason = line[28:].strip()
    return (depth, stop_reason)



def find_rock(inp):
    depth = inp[0:8].strip()
    stop_reason = inp[28:].strip()
    if stop_reason.split(' ')[0] == '43':
        return float(depth)
    else:
        return -9999


def snd_to_dxf(datafolder2):
    drawing = ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    
    "Layers"
    drawing.layers.new('43_BedRock', dxfattribs={'color': 0})   
    drawing.layers.new('Surface', dxfattribs={'color': 0})  
    drawing.layers.new('Stop_borehole', dxfattribs={'color': 0})
    
    for file in glob.glob(datafolder2):
        file_name = os.path.basename(file)
        file_name = file_name.split('.')[0]
        print(file_name)
        x,y,z,depth,bedrock_43,stop_reason = snd_converter(file)
        modelspace.add_point((x,y,z), dxfattribs={'layer': 'Surface'})
        
        if bedrock_43 != -9999:
            modelspace.add_point((x,y,z-bedrock_43), dxfattribs={'layer': '43_BedRock'})
        
        modelspace.add_point((x,y,z-depth), dxfattribs={'layer': 'Stop_borehole'})
        
     

    
    drawing.saveas("C:\\python_proj\\snd_file_reader\\Geosuite database_10206056.dxf")

def xlsx_to_dxf(file):
    df = pd.read_excel(file)
    print(df.columns)
    
    drawing = ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    
    "Layers"
    drawing.layers.new('43_BedRock', dxfattribs={'color': 0})   
    drawing.layers.new('Surface', dxfattribs={'color': 0})  
    drawing.layers.new('Stop_borehole', dxfattribs={'color': 0})
    
    for i,row in df.iterrows():
        y = row['Y']
        x = row['X']
        z = row['Z']
        rock = row['Fjell']
        soil = row['Løsm']
        if rock+soil > 0:
            depth = z-(rock+soil)
            bedrock_43 = z-soil
        elif soil>0:
            depth = z-soil
            bedrock = -9999
        else: 
            depth = -9999
            bedrock_43 =-9999
            
            
            

        modelspace.add_point((x,y,z), dxfattribs={'layer': 'Surface'})
        
        if bedrock_43 != -9999 and depth > 0:
            modelspace.add_point((x,y,z-bedrock_43), dxfattribs={'layer': '43_BedRock'})
        if depth != -9999:
            modelspace.add_point((x,y,z-depth), dxfattribs={'layer': 'Stop_borehole'})
        
     

    
    drawing.saveas("C:\\python_proj\\snd_file_reader\\_OneDrive_1_1-8-2021 (2).dxf")


datafolder = "T:\\22457 - E39_Lyngdal_øst_vest\\02 Arbeidskatalog\\12 Fagmapper\\RIG\\nedlastet 0801\\OneDrive_2021-01-08\\10206056 E39 Mandal-Lyngdal. Geosuite-database\\AUTOGRAF.DBF\\*.SND"
datafolder2 = "T:\\22457 - E39_Lyngdal_øst_vest\\01 Grunnlag\\07 Konkurransegrunnlag\\Kapittel D\\D2\\D2.06 Annet grunnlag\\Geosuite database\\1350041000\\1350041000\\AUTOGRAF.DBF\\*.snd"
csv_file = "C:\\python_proj\\snd_file_reader\\snd_output2.csv"
xlsx_file =  "T:\\22457 - E39_Lyngdal_øst_vest\\02 Arbeidskatalog\\12 Fagmapper\\RIG\\nedlastet 0801\\OneDrive_1_1-8-2021 (2)/Copy of Alle borpunkter koordinater list 27.10.2015 ferdig.xlsx"

#snd_to_dxf(datafolder)
#xlsx_to_dxf(xlsx_file)


# f = open(csv_file, "a")

# f.write('{};{};{};{};{};{};{}\n'.format('Borpunkt','Y','X','Z','Drill_depth','Code_43 Bedrock','Stop reason'))

# for file in glob.glob(datafolder2):
#     x,y,z,depth,bedrock_43,stop_reason = snd_converter(file)
#     file_name = os.path.basename(file)
#     file_name = file_name.split('.')[0]
    
#     f.write('{};{};{};{};{};{};{}\n'.format(file_name,x,y,z,depth,bedrock_43,stop_reason))
#     print((file_name,x,y,z,depth,bedrock_43,stop_reason))
    
    
# f.close()

x,y = symbols('x y')

init_printing()
print(latex(Integral(sqrt(x/1),x)))