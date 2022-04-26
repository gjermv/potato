# -*- coding: utf-8 -*-

import glob, os
import pandas as pd

# Excel file with information, see example for how to set up.    
VL_spreadSheet = 'C:\\GeoArkiv\\05 Parsell 2 geosuite\\2021-11-08 GeoSuiteTverrsnitt\\P2_1_VL Oversikt-Ansett 99m.xlsx'  
VL_sheetName = 'TS02 4230-7210'         

# Forlder for Individual dwg drawings from Profile tool in GeoSuite presentation
geoSuiteDWGFolder = 'C:\\GeoArkiv\\05 Parsell 2 geosuite\\P2_2_VL'


def createAttachment(filename, CenterLine, Elevation):
    """ Create AutoCad commands to XREF a file into the specified location 
    Adds a Rectangle around the added XREF. """
    
    # Set width of rectangle. 
    recWidth = 100
    upperL = CenterLine-recWidth
    lowerR = CenterLine+recWidth
    
    myStr = """-ATTACH
{0}
A
{1},-{2}
1
1
0
REC
{3},3000
{4},-3000
""".format(filename, CenterLine, Elevation,upperL,lowerR)
    return myStr


def layoutPan(Profile, CenterLine):

    myStr = """Profile {0} ---------
-PAN
C
0,0
-{1},0
--------
""".format(Profile,CenterLine)
    return myStr

def createLayouts(total_layouts):
    
    new_layouts = 1
    if total_layouts//2 == 1:
        new_layouts = total_layouts//2 + 1
    else:
        new_layouts = total_layouts//2
    
    drawing_name = '0'
    myStr = ''
    for i in range(new_layouts): 
        myStr = myStr  + """-LAYOUT
C
Template
{}{}
""".format(drawing_name,i+10)

    f_out2 = open("C:\\GeoArkiv\\05 Parsell 2 geosuite\\Script_export\\{}-Script_2.txt".format(VL_sheetName), "w")
    f_out2.write(myStr)
    f_out2.close()
    
df = pd.read_excel(VL_spreadSheet, sheet_name= VL_sheetName)

f_out1 = open("C:\\GeoArkiv\\05 Parsell 2 geosuite\\Script_export\\{}-Script_new1.txt".format(VL_sheetName), "w")
f_out3 = open("C:\\GeoArkiv\\05 Parsell 2 geosuite\\Script_export\\{}-Script_new3.txt".format(VL_sheetName), "w")

for filename in glob.glob('{0}\\VL*.dwg'.format(geoSuiteDWGFolder)):
    
    
    fileProfileName = os.path.basename(filename)
    fileProfilePos = int(fileProfileName.split(' ')[1].replace('.dwg',''))
    
    df_file = df[df['Profile']==fileProfilePos]     
    if len(df_file)>1:
        print(fileProfileName,'Error Multiple Options')
    elif len(df_file)<1:
        print(fileProfileName,'No info found')
  
    else:
        cLine = df_file.iloc[0].VLCenterLine
        eLine = df_file.iloc[0].VLElevation
        
        f_out1.write(createAttachment(filename,cLine,eLine))
        f_out3.write(layoutPan(fileProfilePos,cLine))
#     
#         
#       
f_out1.close()
f_out3.close()
print('File1 and 3 updated')  
# 
createLayouts(len(df))
print('File2 update')   



# for filename in glob.glob('{0}\\*.dwg'.format(geoSuiteDWGFolder)):
#     fileNameShort = os.path.basename(filename).replace('.dwg','')
    
    
#     df_file = df[df['DrawingName']==fileNameShort]
#     if len(df_file == 1):
#         newName = filename.replace(fileNameShort,"VL2_1 " +  str(df_file.iloc[0].Profile))
#         print(newName)
#         os.replace(filename,newName)

        
    
    
    