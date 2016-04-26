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
            activity = inputShortCut(input('activity: (C,W,R,S,...) '))
            gpxdict['activity'] = activity
            gpxdict['filename'] = filename
            
            df = pd.concat([df, gpxdict])
            printSomething(df,activity,indata['length'],filename)
            #plotAverage(df,activity,indata['length'],filename)
            
    df = df.sort('dateandtime')
    df.index = range(1,len(df) + 1)
    df.to_csv('C:\\python\\testdata\\gpxx1\\Activity_Summary2.csv',columns=['filename','dateandtime','activity','tottime','walk_time','length','avg_speed','climbing','comment','health','sone1','sone2','sone3','sone4','sone5'])
    return df
    
def trainingdata_to_csv(df):
    df.to_csv('C:\\python\\testdata\\gpxx1\\Activity_Summary2.csv',columns=['filename','dateandtime','activity','tottime','walk_time','length','avg_speed','climbing','comment','health','sone1','sone2','sone3','sone4','sone5'])

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
    gpxdict['sone1'] = ''
    gpxdict['sone2'] = ''
    gpxdict['sone3'] = ''
    gpxdict['sone4'] = ''
    gpxdict['sone5'] = ''
    return gpxdict
    
def getTCXtrainingData(filename):
    mydf = tcxtricks.TCXtoDataFrame(filename)
    #print(tcxtricks.getTCXheartzone(mydf))
    return tcxtricks.getmainInfoTCX(mydf)

def plotHeartrate(dataframe):
    times = pd.DatetimeIndex(df['dateandtime'])
    grouped = df.groupby([times.year,times.week])
     
    x=[]
    y1=[]
    y2=[]
    y3=[]
    y4=[]
    y5=[]
    y2b=[]
    y3b=[]
    y4b=[]
    y5b=[]
    
    for a,b in grouped:
        
        x.append((a[0]-2016)*52+a[1])
        
        z1 = b['sone1'].sum()/3600
        z2 = b['sone2'].sum()/3600
        z3 = b['sone3'].sum()/3600
        z4 = b['sone4'].sum()/3600
        z5 = b['sone5'].sum()/3600
        
        y1.append(z1)#.total_seconds()/3600)
        y2.append(z2)
        y3.append(z3)
        y4.append(z4)
        y5.append(z5)
        y2b.append(z1)
        y3b.append(z1+z2)
        y4b.append(z1+z2+z3)
        y5b.append(z1+z2+z3+z4)
                
    plt.bar(x,y1,width=1,color='#fef0d9')
    plt.bar(x,y2,width=1,bottom=y2b,color='#fdcc8a')
    plt.bar(x,y3,width=1,bottom=y3b,color='#fc8d59')
    plt.bar(x,y4,width=1,bottom=y4b,color='#e34a33')
    plt.bar(x,y5,width=1,bottom=y5b,color='#b30000')

    plt.show()

def plotLength(dataframe,actList,period='day'):
    p = 365
    
    times = pd.DatetimeIndex(df['dateandtime'])
    grouped = df.groupby([times.year,times.dayofyear])
    if period == 'week':
        grouped = df.groupby([times.year,times.weekofyear])
        p = 52
    if period == 'month':
        grouped = df.groupby([times.year,times.month])
        p = 12
    if period == 'year':
        grouped = df.groupby([times.year])
        p=1
    
    lenList = []
    lenBList = []
    x = []
    
    for act in actList:
        lenList.append([])
        lenBList.append([])
    
    for a,b in grouped:
        if period == 'year':
            x.append((a-2016)*p)#+a[1])
        else:
            x.append((a[0]-2016)*p+a[1])
        z = []
        for act in actList:
            z.append(b[b['activity'] == act]['length'].sum())
        
        lenList.append([])
        lenBList.append([])
        
        for i,l in enumerate(z):
            lenList[i].append(l)
            lenBList[i].append(sum(z[:i]))
    
    for i,li in enumerate(actList):
        plt.bar(x,lenList[i],bottom=lenBList[i],width=1,color=getActivityColor(li))

    plt.show()

def plotDuration(dataframe,actList,period='day'):
    p = 365
    
    times = pd.DatetimeIndex(df['dateandtime'])
    grouped = df.groupby([times.year,times.dayofyear])
    if period == 'week':
        grouped = df.groupby([times.year,times.weekofyear])
        p = 52
    if period == 'month':
        grouped = df.groupby([times.year,times.month])
        p = 12
    if period == 'year':
        grouped = df.groupby([times.year])
        p=1
    
    lenList = []
    lenBList = []
    x = []
    
    for act in actList:
        lenList.append([])
        lenBList.append([])
    
    for a,b in grouped:
        if period == 'year':
            x.append((a-2016))
        else:
            x.append((a[0]-2016)*p+a[1])
        z = []
        for act in actList:
            z.append(b[b['activity'] == act]['walk_time'].sum())
        
        lenList.append([])
        lenBList.append([])
        
        totsec = 0
        for i,l in enumerate(z):
            lenList[i].append(l.total_seconds()/3600)
            lenBList[i].append(totsec)
            totsec += l.total_seconds()/3600
            
    for i,li in enumerate(actList):

        plt.bar(x,lenList[i],bottom=lenBList[i],width=1,color=getActivityColor(li))


    plt.show()

def getActivityColor(activity):
    print('ActColor',activity)
    if activity == "Walking":
        return '#b3e6ff'
    elif activity == "Running":
        return '#0099e6'
    elif activity == "Rollerskiing":
        return '#ffff99'
    elif activity == "Skiing":
        return '#e6e600'
    elif activity == "Cycling":
        return '#66ff99'
    else:
        return  '#66ff99'
def plotAverage(da,activity,triplength,filename=None):
    
    fig, ax = plt.subplots()
    
    dfact = da[da['activity']==activity].sort('length')
    dfact.index = range(len(dfact))
    
    dfmin = dfact[dfact['length']>triplength*0.75]
    dfmax = dfmin[dfact['length']<triplength*1.25]
    
    df =dfmax.sort('avg_speed',ascending=False)
    df.index = range(len(df))
    
    ax.bar(df.index,df['avg_speed'],width=1,color='yellow')
    
    if filename!= None:
        df2 = df[df['filename']==filename]
        ax.bar(df2.index,df2['avg_speed'],width=1,color='red')
    
    ax.set_xticks(df.index + 0.5)
    ax.set_xticklabels(df['filename'],rotation=90)
    plt.show()
    

def printSomething(da,activity,triplength,filename):
    print("printsomthing input data",len(da),type(activity),triplength)
    
    dfact = da[da['activity']==activity].sort('length')
    
    dfact.index = range(len(dfact))
    ind = dfact[dfact['filename']== filename].index
    if len(ind>0):
        print('Length',len(dfact)-ind[0],'/',len(dfact))

             
    dfmin = dfact[dfact['length']>triplength*0.8]
    dfmax = dfmin[dfact['length']<triplength*1.2]
    
    df = dfmax.sort('avg_speed')
    df.index = range(len(df))
    
    ind = df[df['filename']== filename].index
    
    if len(ind>0):
        print('Average',len(df)-ind[0],'/',len(df))
    
    df =df.sort('climbing')
    df.index = range(len(df))
    
    ind = df[df['filename']== filename].index
    if len(ind>0):
        print('Climbing',len(df)-ind[0],'/',len(df))
    
    return df
       
df = checkForNewFiles('C:\\python\\testdata\\gpxx4\\*.*')
plotLength(df, ['Running','Walking','Rollerskiing','Skiing'],'month')
plotDuration(df, ['Running','Rollerskiing','Skiing','Cycling'],'month')
plotHeartrate(df)