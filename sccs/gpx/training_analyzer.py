# -*- coding: utf-8 -*-

from gpx import gpxtricks
from gpx import tcxtricks
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from timeit import default_timer as timer

def training_analyzer(datafolder):
    trips = list()
    for file in glob.glob(datafolder):
        gpxdict = getTrainingData(file)
        trips.append(gpxdict)
    outdata = pd.DataFrame(trips)
    trainingdata_to_csv(outdata)
    return outdata

def checkForNewFiles(datafolder):
    df = pd.read_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df['tottime'] = pd.to_timedelta(df['tottime'])
    df['walk_time'] = pd.to_timedelta(df['walk_time'])
    existing_files =  list(df['filename'])
    
    for file in glob.glob(datafolder):
        filename = os.path.basename(file)
        if filename in existing_files:
            pass
        else:
            print('**** New file',filename,' ****')
            if '.gpx' in filename or '.tcx' in filename: 
                indata = getTrainingData(file)

            else:
                print('Unknow file format: SKIP')
                continue
            
            print('Tottime',indata['tottime'])
            print('Walktime',indata['walk_time'])
            print('Length',indata['length'])
            print('Avg',indata['avg_speed'])
            print('Climbing',indata['climbing'])
            
            gpxdict =  pd.DataFrame([indata])
            activity = inputShortCut(input('activity: (C,W,R,S,...) '))
            gpxdict['activity'] = activity
            gpxdict['filename'] = filename
            
            df = pd.concat([df, gpxdict])
            printSomething(df,filename)
            
    df = df.sort('dateandtime')
    df.index = range(1,len(df) + 1)
    trainingdata_to_csv(df)
    return df
    
def trainingdata_to_csv(df):
    col = ['filename',
           'dateandtime',
           'activity',
           'tottime',
           'walk_time',
           'length',
           'avg_speed',
           'climbing',
           'comment',
           'health',
           'sone1',
           'sone2',
           'sone3',
           'sone4',
           'sone5']
    
    df.to_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',columns=col)

def inputShortCut(txt):
    """ Shortcuts for different types of activity"""
    
    appr = {'W':'Walking','R':'Running','C':'Cycling','RS':'Rollerskiing','S':'Skiing-X' }
    if txt in appr:
        return appr[txt]
    else:
        return txt

def getTrainingData(filename):
    """ Returns dict with summary of training data """
    extension = os.path.splitext(filename)[1]
    
    if 'gpx' in extension:
        df = gpxtricks.GPXtoDataFrame(filename)
    elif 'tcx' in extension:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    gpxdict = gpxtricks.getmainInfo(df)
    gpxdict['filename'] = os.path.basename(filename)
    gpxdict['activity'] = 'NA'
    
    # Remove some kommunetopp specific details.
    del gpxdict['elediff']
    del gpxdict['climbingrate']
    del gpxdict['steepness']
    del gpxdict['stop_time']
    del gpxdict['kupert_faktor']
    del gpxdict['pause_faktor']
    del gpxdict['topptur_faktor']
    
    # Add some empty columns for spreadsheet
    gpxdict['comment'] = ''
    gpxdict['health'] = ''
    gpxdict['activity'] = ''
    
    # Add hr data if any
    zonelist = ['sone1','sone2','sone3','sone4','sone5']
    hrdata = gpxtricks.heartZone(df)
    if hrdata != -1:
        for i,item in enumerate(zonelist):
            gpxdict[item] = hrdata[i]        
    else:
        for item in zonelist:
            gpxdict[item] = ''  

    gpxtricks.plotHeartZone(df, 'C:/python/image/pRect2.png')
    gpxtricks.plotElevationProfile2(df, 'C:/python/image/elevationProfile.png')
    gpxtricks.plotSpeedProfile(df, 'C:/python/image/speedProfile.png')
    gpxtricks.plotHeartrateProfile(df, 'C:/python/image/hrProfile.png')
    
    return gpxdict

  
def plotHeartrate(dataframe,period='day'):
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
        if period == 'year':
            x.append((a-2016)*p)
        else:
            x.append((a[0]-2016)*p+a[1])
        
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
    
def printSomething(da,filename):
    print('*** Statistic ***\n',filename)
    ex = da[da['filename']==filename]
    idx = ex.index[0]
    activity = ex['activity'].iloc[0]
    triplength = ex['length'].iloc[0]
    
    
    dfact = da[da['activity']==activity]
    pos0 = np.argsort(np.argsort(dfact['length'])).loc[idx]
    len0 = len(dfact)
    
    dfmin = dfact[dfact['length']>triplength*0.8 ]
    dfmax = dfmin[dfmin['length']<triplength*1.3]
    
    lenx = len(dfmax)
    pos1 = np.argsort(np.argsort(dfmax['avg_speed'])).loc[idx]
    pos2 = np.argsort(np.argsort(dfmax['climbing'])).loc[idx]
    avg_best = dfmax['avg_speed'].max()
    avg_avg =dfmax['avg_speed'].mean()
    
    clb_best = dfmax['climbing'].max()
    clb_avg =dfmax['climbing'].mean()
    
    print("Length {}/{}".format(len0-pos0+1,len0))
    print("Avg speed {}/{} - Best: {:.2f} Avg: {:.2f}".format(lenx-pos1+1,lenx,avg_best,avg_avg))
    print("Climbing {}/{}  - Max: {:.1f} Avg: {:.1f}".format(lenx-pos2+1,lenx,clb_best,clb_avg))

def getActivityColor(activity):
    if activity == "Walking":
        return '#b3e6ff'
    elif activity == "Running":
        return '#0099e6'
    elif activity == "Skiing": 
        return '#ffffb3'
    elif activity == "Skiing-X": #CrossCountry skiing / Trening
        return '#ffff66'
    elif activity == "Rollerskiing":
        return '#e6e600'
    elif activity == "Alpin": 
        return '#fdcc8a'
    elif activity == "Cycling":
        return '#66ff99'
    else:
        return  '#b30000'

   
def getTrackData(filename):
    extension = os.path.splitext(filename)[1]
    print("at -getTrackData-",extension)
    
    if 'gpx' in extension:
        df = gpxtricks.GPXtoDataFrame(filename)
    elif 'tcx' in extension:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    df_dat = gpxtricks.exportRedPoints(df)
    print(df_dat)
    return df_dat
    
def getTrackBounds(filename):
    extension = os.path.splitext(filename)[1]
    print("at -getTrackBounds-",extension)
    
    if 'gpx' in extension:
        df = gpxtricks.GPXtoDataFrame(filename)
    elif 'tcx' in extension:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    return gpxtricks.getTrackBounds(df)


if __name__ == "__main__":
    start = timer()
    df = checkForNewFiles('C:\\python\\testdata\\gpxx4\\files\\*.*')
    end = timer()
    print(end-start)
    
    plotLength(df,['Running','Rollerskiing','Skiing-X','Cycling'], period='year')
    #plotHeartrate(df,'year')
