'''
Created on 7 Apr 2016

@author: gjermund.vingerhagen
'''

from lxml import etree as etree
import utmconverter as utm
import algos as algos
import gpxtricks
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as dtt
from matplotlib import pyplot as plt
import time
import googlemaps
import glob 
import json
import numpy as np


def TCXtoDataFrame(filename):
    f = open(filename,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    TCXlist = list()
    stime = xml.iter(ns+"Time")
    segno = 0
    name =  xml.find(ns+"Activities/"+ns+"Activity/"+ns+"Id").text
    desc = xml.find(ns+"Activities/"+ns+"Activity").attrib['Sport']
    
    for item in stime:
        startTime = gpxtricks.gpxtimeToStr(item.text)
        break
    
    
    for lap in xml.iter(ns+"Lap"):
        segno += 1
        for trkPoint in lap.iter(ns+"Trackpoint"):
            trkpoint = dict()
            trkpoint['name'] = name
            trkpoint['desc'] = desc
            trkpoint['segno'] = segno
            trkpoint['time'] = trkPoint.find(ns+"Time").text
            trkpoint['duration'] = (gpxtricks.gpxtimeToStr(trkpoint['time'])-startTime).total_seconds()
            
            try:
                trkpoint['lat'] = trkPoint.find(ns+"Position/"+ns+"LatitudeDegrees").text
                trkpoint['lon'] = trkPoint.find(ns+"Position/"+ns+"LongitudeDegrees").text
                trkpoint['ele'] = trkPoint.find(ns+"AltitudeMeters").text
                trkpoint['dist'] = trkPoint.find(ns+"DistanceMeters").text
            except:
                trkpoint['lat'] = np.NAN
                trkpoint['lon'] = np.NAN
                trkpoint['ele'] = np.NAN
                trkpoint['dist'] = np.NAN
                
            try:
                trkpoint['heartrate']= int(trkPoint.find(ns+"HeartRateBpm/"+ns+"Value").text)
            except:
                trkpoint['heartrate']= np.NAN
            
            TCXlist.append(trkpoint)
    
    df = pd.DataFrame(TCXlist)
    
    df['time'] = pd.to_datetime(df['time'])
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    df['ele'] = df['ele'].astype(float)
    df['dist'] = df['dist'].astype(float)
    
    df['speed'] = (df['dist'].shift(-1)-df['dist'])/(df['duration'].shift(-1)-df['duration'])
    df['speed'] = df['speed'].shift(1)
    
    return df
    
def getTCXheartzone(dataframe):
    df = dataframe
    df['timediff'] = df['time'].diff()
    
    df1 = df[(df['heartrate']<135) & (df['heartrate']>=0)]
    df2 = df[(df['heartrate']<155) & (df['heartrate']>=135)]
    df3 = df[(df['heartrate']<165) & (df['heartrate']>=155)]
    df4 = df[(df['heartrate']<175) & (df['heartrate']>=165)]
    df5 = df[df['heartrate']>=175]
    
    hr5zone = sum(df5['timediff'].dt.seconds[1:])
    hr4zone = sum(df4['timediff'].dt.seconds[1:])
    hr3zone = sum(df3['timediff'].dt.seconds[1:])
    hr2zone = sum(df2['timediff'].dt.seconds[1:])
    hr1zone = sum(df1['timediff'].dt.seconds[1:])

    return (hr1zone,hr2zone,hr3zone,hr4zone,hr5zone)

def getmainInfoTCX(dataframe):
    length = max(dataframe['dist'])
    tottime = dataframe['time'].max()-dataframe['time'].min()
    dateandtime = dataframe['time'][0] 
    climbing = gpxtricks.getClimbingHeightGPS(dataframe)
    
    stopframe = (dataframe[dataframe['speed']<0.4167][['duration']].index)
    stoptime = sum(dataframe['duration'].diff()[stopframe])
    walktime = tottime.total_seconds() - stoptime

    info = dict()
    info['length'] = round(length/1000,2) #km 
    info['dateandtime'] = dateandtime
    info['tottime'] = tottime
    info['walk_time'] = dtt(seconds=walktime)
    info['avg_speed'] = length/walktime*3.6
    info['climbing'] = round(climbing,1)
    info['activity'] = ''
    info['health'] = ''
    info['comment'] = ''
    info['sone1'],info['sone2'],info['sone3'],info['sone4'],info['sone5'] = getTCXheartzone(dataframe)
    return info

def findNamespace(file):
    str = file.read(1000)
    file.seek(0)
    ind1 = str.find('xmlns=')+7
    ind2 = str[ind1+1:].find('"')
    s = '{'+str[ind1:ind1+ind2+1]+'}'
    return s


