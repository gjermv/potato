# -*- coding: utf-8 -*-

from gpx import gpxtricks
from gpx import tcxtricks
from gpx import segmentTimer
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from timeit import default_timer as timer
from datetime import timedelta,datetime

def training_analyzer(datafolder):
    trips = list()
    for file in glob.glob(datafolder):
        gpxdict = getTrainingData(file)
        trips.append(gpxdict)
    outdata = pd.DataFrame(trips)
    trainingdata_to_csv(outdata)
    return outdata

def checkForNewFiles(datafolder):
    # Next line reads the dateandtime, but skips the seconds...
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


def saveGPSFile(gps_file,gps_datafolder='C:\\python\\testdata\\gpxx4\\files\\',csv_file='C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',additional_info=None):
    print("SAVEGPSFILE")
    df = pd.read_csv(csv_file,parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df['tottime'] = pd.to_timedelta(df['tottime'])
    df['walk_time'] = pd.to_timedelta(df['walk_time'])

    trainingData = additional_info

    dateandtime = trainingData['dateandtime']
    print(dateandtime)
    
    if min(abs(df['dateandtime'] - dateandtime)) < pd.Timedelta(minutes=2):
        print("saveGPSFile Message: Timestamp already exists +/- 2 min",trainingData['dateandtime'])
        return 125
    else:
        print("saveGPSFile Message: Timestamp OK",trainingData['dateandtime'])
    

    trainingData.update(additional_info)
    trainingDF = pd.DataFrame([trainingData])
    df = pd.concat([df, trainingDF])
    trainingdata_to_csv(df)
    
    print('Successfully updated csv file')
    
    
    

def insertToGPXDatabase(originalfile,filename,activity,comment,indata):
    df = pd.read_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df['tottime'] = pd.to_timedelta(df['tottime'])
    df['walk_time'] = pd.to_timedelta(df['walk_time'])
    df['speed_00100'] = df['speed_00100'].convert_objects(convert_numeric=True)
    existing_files =  list(df['filename'])
    
    if filename in existing_files:
        return df
    
    print('**** New file',filename,' ****')
    #indata = getTrainingData(originalfile,skip=False)

    print('Tottime',indata['tottime'])
    print('Walktime',indata['walk_time'])
    print('Length',indata['length'])
    print('Avg',indata['avg_speed'])
    print('Climbing',indata['climbing'])

    gpxdict =  pd.DataFrame([indata])
    gpxdict['filename'] = filename
    gpxdict['activity'] = activity
    gpxdict['comment'] = comment
    df = pd.concat([df, gpxdict])
    
    printSomething(df,filename)
            
    df = df.sort('dateandtime')
    df.index = range(1,len(df) + 1)
    #trainingdata_to_csv(df)
    
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
           'sone5',
           'speed_00100',
           'speed_00200',
           'speed_00400',
           'speed_00800',
           'speed_01000',
           'speed_01500',
           'speed_03000',
           'speed_05000',
           'speed_10000',
           'speed_20000',
           'speed_50000',
           'segments']
    
    df = df.sort('dateandtime')
    df.index = range(1,len(df) + 1)
    df.to_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',columns=col)

def inputShortCut(txt):
    """ Shortcuts for different types of activity"""
    
    appr = {'W':'Walking','R':'Running','C':'Cycling','RS':'Rollerskiing','S':'Skiing-X' }
    if txt in appr:
        return appr[txt]
    else:
        return txt

def getTrainingData(filename,skip=False):
    """ Returns dict with summary of training data """
    extension = os.path.splitext(filename)[1]
    
    if 'gpx' in extension:
        df = gpxtricks.GPXtoDataFrame(filename)
    elif 'tcx' in extension:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    gpxdict = gpxtricks.getmainInfo(df)
    gpxdict['filename'] = os.path.basename(filename)
    
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
    
    # Add best speed data
    bt = gpxtricks.findBestTempo2(df)
    bt2 = dict()

    for itm in bt:
        bt2['speed_{:0>5}'.format(itm)] = float('{:.2f}'.format(bt[itm][0]*3.6))

    gpxdict.update(bt2)
    print(gpxdict)
    
    if not skip:
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

def plotLength2(dataframe,actList,period='day'):
    pdict = dict()
    pdict['day'] = [1,'D']
    pdict['week'] = [7,'W']
    pdict['month'] = [28,'MS']
    pdict['year'] = [365,'AS']
    
    timeperiod = pdict[period][1]
    wi = pdict[period][0]
    print("WI",wi,timeperiod)
    
    
    _summary = pd.DataFrame()
    fig,ax = plt.subplots()
    indexed_df = dataframe.set_index(['dateandtime'])

    df1 = pd.DataFrame()
    for i,act in enumerate(actList):
        df1[act] = pd.Series(indexed_df[indexed_df['activity'] == act]['length'],index=indexed_df.index)
        _summary[act] = df1[act].resample(timeperiod,'sum',convention='start')
        
        if i == 0:
            _summary['sum'] = _summary[act].fillna(0)
        else:
            _summary['sum'] += _summary[act].fillna(0)

        
        ax.bar(_summary.index,_summary[act], bottom=_summary['sum'] - _summary[act], width=wi,color=getActivityColor(act),lw=1,edgecolor='#bbbbbb')
    
    ax.grid(True)
    plt.show()
    print(_summary.tail(54))
    
    #===========================================================================
    # _summary[act] = df1.length.resample(timeperiod,'sum')
    # colorlist.append(getActivityColor(act))
    # 
    # ax.bar(_summary.index,_summary['Rollerskiing'],width=7,color=getActivityColor('Running'))
    # ax.bar(_summary.index,_summary['Cycling'],width=7,color=getActivityColor('Cycling'))
    # plt.show()
    # 
    # print(plt.style.available)
    #===========================================================================
    

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

def plotTrainingDiary(dataframe):
    area = []
    color = []
    x = []
    y = []
    
    times = pd.DatetimeIndex(df['dateandtime'])
    grouped = df.groupby([times.year,times.month,times.weekofyear])
    for key,val in grouped:
        if key[1] == 12 and key[2] == 1:
            m = +52 
        elif key[1] == 1 and key[2] == 53:
            m = -52
        else:
            m = 0
        week_no = (key[0]-2016)*52+key[2]+m
        print(key,week_no)
        for item in val.iterrows():
            if item[1]['activity'] not in ['Walking']:
                x.append(item[1]['dateandtime'].dayofweek)
                area.append(150)
                color.append(getActivityColor(item[1]['activity']))
                y.append(week_no)
    
    fig = plt.figure()
    ax = fig.gca()
    ax.set_yticks(np.arange(0,7,1))
    ax.set_xticks(np.arange(0-52*6,1000,52))
    ax.set_xticks(np.arange(-300,1000,1),minor=True)
    
    
    ax.set_axisbelow(True)
    ax.set_xlim(-26,52)
    ax.yaxis.grid(True)    
    ax.xaxis.grid(True,which='major',linewidth=2)  
    ax.xaxis.grid(True,which='minor')      
    plt.scatter(y,x,s=area,c=color,marker='h', lw=0.5,edgecolor='black')
    
    plt.show()
            

def plotAvgImprovement(dataframe,activity,minDist=0,maxDist=1000):
    df = dataframe[dataframe['activity']==activity]
    dfmin = df[df['length']>minDist]
    dfmax = dfmin[dfmin['length']<maxDist]
    timeX = (dfmax['dateandtime']-datetime(year=2016,month=12,day=31))
    print(timeX.dt.days)
    pf = np.polyfit(timeX.dt.days,dfmax['avg_speed'],1)
    l1 = []
    l1.append(min(dfmax['dateandtime']))
    l1.append(max(dfmax['dateandtime']))
    pg = np.poly1d(pf)
    l2 = []
    l2.append(pg(min(timeX.dt.days)))
    l2.append(pg(max(timeX.dt.days)))
    
    fig, ax = plt.subplots()
    ax.grid(True)
    ax.plot(dfmax['dateandtime'],dfmax['avg_speed'],'o',marker='o')
    ax.plot(l1,l2)
    plt.show()
       

def printSomething(df,filename):
    print('*** Statistic ***\n',filename)
    ex = df[df['filename']==filename]
    idx = ex.index[0]
    activity = ex['activity'].iloc[0]
    triplength = ex['length'].iloc[0]
    s_00100 = ex['speed_00100'].iloc[0]
    s_00200 = ex['speed_00200'].iloc[0]
    s_00400 = ex['speed_00400'].iloc[0]
    s_00800 = ex['speed_00800'].iloc[0]
    s_01000 = ex['speed_01000'].iloc[0]
    s_01500 = ex['speed_01500'].iloc[0]
    s_03000 = ex['speed_03000'].iloc[0]
    s_05000 = ex['speed_05000'].iloc[0]
    s_10000 = ex['speed_10000'].iloc[0]
    s_20000 = ex['speed_20000'].iloc[0]
    
    dfact = df[df['activity']==activity]
    pos0 = np.argsort(np.argsort(dfact['length'])).loc[idx]
    len0 = len(dfact)
    
    dfmin = dfact[dfact['length']>triplength*0.8 ]
    dfmax = dfmin[dfmin['length']<triplength*1.3]
    
    lenx = len(dfmax)
    pos1 = np.argsort(np.argsort(dfmax['avg_speed'])).loc[idx]
    pos2 = np.argsort(np.argsort(dfmax['climbing'])).loc[idx]
    pos_00100 = lenx-np.argsort(np.argsort(dfmax['speed_00100'])).loc[idx]
    pos_00200 = lenx-np.argsort(np.argsort(dfmax['speed_00200'])).loc[idx]
    pos_00400 = lenx-np.argsort(np.argsort(dfmax['speed_00400'])).loc[idx]
    pos_00800 = lenx-np.argsort(np.argsort(dfmax['speed_00800'])).loc[idx]
    pos_01000 = lenx-np.argsort(np.argsort(dfmax['speed_01000'])).loc[idx]
    pos_01500 = lenx-np.argsort(np.argsort(dfmax['speed_01500'])).loc[idx]
    pos_03000 = lenx-np.argsort(np.argsort(dfmax['speed_03000'])).loc[idx]
    pos_05000 = lenx-np.argsort(np.argsort(dfmax['speed_05000'])).loc[idx]
    pos_10000 = lenx-np.argsort(np.argsort(dfmax['speed_10000'])).loc[idx]
    pos_20000 = lenx-np.argsort(np.argsort(dfmax['speed_20000'])).loc[idx]
    
    avg_best = dfmax['avg_speed'].max()
    avg_avg = dfmax['avg_speed'].mean()
    
    clb_best = dfmax['climbing'].max()
    clb_avg =dfmax['climbing'].mean()
    
    print("Length {}/{}".format(len0-pos0,len0))
    print("Avg speed {}/{} - Best: {:.2f} Avg: {:.2f}".format(lenx-pos1,lenx,avg_best,avg_avg))
    print("Climbing {}/{}  - Max: {:.1f} Avg: {:.1f}".format(lenx-pos2,lenx,clb_best,clb_avg))
    txt = "Length {}/{}\n".format(len0-pos0,len0)
    txt += "{} from {:.2f} - {:.2f} kilometers\n".format(activity,triplength*0.8,triplength*1.3)
    txt +="Avg speed {}/{} - Best: {:.2f} - Avg: {:.2f}\n".format(lenx-pos1,lenx,avg_best,avg_avg)
    txt += "Climbing {}/{}  - Max: {:.1f} - Avg: {:.1f}\n\n".format(lenx-pos2,lenx,clb_best,clb_avg)

    txt += "00100m - {: >2} - {:>4.2f} km/h\n".format(pos_00100,s_00100)
    txt += "00200m - {: >2} - {:>4.2f} km/h\n".format(pos_00200,s_00200)
    txt += "00400m - {: >2} - {:>4.2f} km/h\n".format(pos_00400,s_00400)
    txt += "00800m - {: >2} - {:>4.2f} km/h\n".format(pos_00800,s_00800)
    txt += "01000m - {: >2} - {:>4.2f} km/h\n".format(pos_01000,s_01000)
    txt += "01500m - {: >2} - {:>4.2f} km/h\n".format(pos_01500,s_01500)
    txt += "03000m - {: >2} - {:>4.2f} km/h\n".format(pos_03000,s_03000)
    txt += "05000m - {: >2} - {:>4.2f} km/h\n".format(pos_05000,s_05000)
    txt += "10000m - {: >2} - {:>4.2f} km/h\n".format(pos_10000,s_10000)
    txt += "20000m - {: >2} - {:>4.2f} km/h\n".format(pos_20000,s_20000)
    return txt
    
def getActivityColor(activity):
    actdict = dict()
    actdict['Walking'] = '#b3e6ff'
    actdict['Running'] = '#0099e6'
    actdict['Skiing'] = '#ffffb3'
    actdict['Skiing-X'] = '#ffff66'
    actdict['Rollerskiing'] = '#e6e600'
    actdict['Alpin'] = '#fdcc8a'
    actdict['Cycling'] = '#66ff99'
    
    if activity in actdict:
        return actdict[activity]
    else:
        return '#b30000'

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

def getSegmentResults(filename,originalfile,activity):
    
    return segmentTimer.getSegmentResults(filename,originalfile,activity)

def sufferScoreCalculator(dataframe,period='month'):
    koff = [0,12/3600,24/3600,45/3600,100/3600,130/3600]
    dataframe['sufferscore'] = (dataframe['sone1']*koff[1]+dataframe['sone2']*koff[2]+dataframe['sone3']*koff[3]+dataframe['sone4']*koff[4]+dataframe['sone5']*koff[5])#/(dataframe['sone1']+dataframe['sone2']+dataframe['sone3']+dataframe['sone4']+dataframe['sone5'])*100
    times = pd.DatetimeIndex(dataframe['dateandtime'])
    
    pdict = dict()
    pdict['day'] = [1,'D']
    pdict['week'] = [7,'W']
    pdict['month'] = [28,'MS']
    pdict['year'] = [365,'AS']
    
    timeperiod = pdict[period][1]
    wi = pdict[period][0]
    
    
    fig,ax = plt.subplots()
    indexed_df = dataframe.set_index(['dateandtime'])

    _summary = pd.Series(indexed_df['sufferscore'],index=indexed_df.index).resample(timeperiod,'sum')
    _summary1 = pd.Series(indexed_df['sufferscore'],index=indexed_df.index).resample(timeperiod,lambda x: len(x)-x.isnull().sum())
    _summ3 = pd.DataFrame()
    _summ3['suff'] = _summary/_summary1
    ax.bar(_summ3.index,_summ3['suff'],width=wi)
    plt.show()
    
    dataframe['sec'] = dataframe['walk_time'].dt.seconds
    print(dataframe[df['sufferscore']>df['sufferscore'].max()-111][['filename','sufferscore','sec']].sort('sufferscore',ascending=False).head(30))
    
    dataframe.to_csv('C:\\python\\testdata\\gpxx4\\sufferScoreExport.csv')

def toPointCloud(datafolder,outputfile):
    i = 0
    for filename in glob.glob(datafolder):
        
        if os.path.isfile(filename):
            f = open(outputfile,'a')
        else: 
            f = open(outputfile,'w')
        
        print(filename)
        extension = os.path.splitext(filename)[1]
    
        if 'gpx' in extension:
            df = gpxtricks.GPXtoDataFrame(filename)
        elif 'tcx' in extension:
            df = gpxtricks.TCXtoDataFrame(filename) 
        
        for row in df.iterrows():
            if row[1].lat >10:  
                s = '{};{};{}\n'.format(i,row[1].lat,row[1].lon)
                i += 1
                f.write(s)
        
        f.close()
        

if __name__ == "__main__":

    #saveGPSFile('C:\\Users\\gjermund.vingerhagen\\Downloads\\activity_1441272743.gpx')
    start = timer()
    #toPointCloud('C:\\python\\testdata\\gpxx4\\files\\2015*.*','C:\\python\\testdata\\gpxx4\\pCloud2.csv')
    df = checkForNewFiles('C:\\python\\testdata\\gpxx4\\files\\*.*')
    end = timer()
    print(end-start)
    plotLength2(df,['Running','Rollerskiing','Skiing-X','Cycling'], period='month')

    plotAvgImprovement(df,'Rollerskiing',minDist=5,maxDist=60)
    plotTrainingDiary(df)
    #plotDuration(df,['Running','Rollerskiing','Skiing-X','Cycling'], period='month')
    #plotAverage(df,'Cycling',20)
    #plotHeartrate(df,'month')
