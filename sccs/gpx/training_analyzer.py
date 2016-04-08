# -*- coding: utf-8 -*-

from gpx import gpxtricks
from gpx import tcxtricks
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


def training_analyzer(datafolder):
    trips = list()
    for file in glob.glob(datafolder):
        gpxdict =  getGPXtrainingData(file)
        trips.append(gpxdict)
        #gpxdict['mov_type'] = input()
    outdata = pd.DataFrame(trips)
    trainingdata_to_csv(outdata)
    return outdata

def checkForNewFiles(datafolder):
    df = pd.read_csv('C:\\python\\testdata\\gpxx1\\Activity_Summary2.csv',parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df['tottime'] = pd.to_timedelta(df['tottime'])
    df['walk_time'] = pd.to_timedelta(df['walk_time'])
    existing_files =  list(df['filename'])
    
    for file in glob.glob(datafolder):
        filename = os.path.basename(file)
        if filename in existing_files:
            print('OK',filename)
        else:
            print('**** New file',filename,' ****')
            indata = dict()
            
            if 'gpx' in filename:
                indata = getGPXtrainingData(file)
            elif 'tcx' in filename:
                indata = getTCXtrainingData(file)
            else:
                print('Unknow file format: SKIP')
                continue
            
            print('Tottime',indata['tottime'])
            print('Walktime',indata['walk_time'])
            print('Length',indata['length'])
            print('Avg',indata['avg_speed'])
            
            gpxdict =  pd.DataFrame([indata])
            gpxdict['activity'] = inputShortCut(input('activity: (C,W,R,S,...) '))
            gpxdict['filename'] = filename
            df = pd.concat([df, gpxdict])
            
            
    df = df.sort('dateandtime')
    df.index = range(1,len(df) + 1)
    df.to_csv('C:\\python\\testdata\\gpxx1\\Activity_Summary2.csv',columns=['filename','dateandtime','activity','tottime','walk_time','length','avg_speed','climbing','comment','health'])
    return df
    
def trainingdata_to_csv(df):
    df.to_csv('C:\\python\\testdata\\gpxx1\\Activity_Summary2.csv',columns=['filename','dateandtime','activity','tottime','walk_time','length','avg_speed','climbing','comment','health'])

def inputShortCut(txt):
    if txt == 'C':
        return 'Cycling'
    elif txt == 'W':
        return 'Walking'
    elif txt == 'R':
        return 'Running'
    elif txt == 'S':
        return 'Skiing'
    else:
        return txt
    
def getGPXtrainingData(filename):
    df = gpxtricks.parseGPX(filename)
    gpxdict = gpxtricks.getmainInfo(df)
    gpxdict['filename'] = os.path.basename(filename)
    gpxdict['activity'] = 'NA'
    del gpxdict['elediff']
    del gpxdict['climbingrate']
    del gpxdict['steepness']
    del gpxdict['stop_time']
    del gpxdict['kupert_faktor']
    del gpxdict['pause_faktor']
    del gpxdict['topptur_faktor']
    gpxdict['comment'] = ''
    gpxdict['health'] = ''
    gpxdict['activity'] = ''
    return gpxdict
    
    
def getTCXtrainingData(filename):
    mydf =tcxtricks.TCXtoDataFrame(filename)
    #print(tcxtricks.getTCXheartzone(mydf))
    return tcxtricks.getmainInfoTCX(mydf)
        
df = checkForNewFiles('C:\\python\\testdata\\gpxx4\\*.*')
 
times = pd.DatetimeIndex(df['dateandtime'])
grouped = df.groupby([times.year,times.month])
 
x=[]
y=[]

for a,b in grouped:
    x.append((a[0]-2011)*12+a[1])
    z = b[b['activity']=='Skiing']['walk_time'].sum()
    y.append(z.total_seconds()/3600)
 
plt.bar(x,y,width=1)
plt.show()


