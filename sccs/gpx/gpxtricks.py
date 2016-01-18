# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 15:38:35 2015
@author: gjermund.vingerhagen
"""

from lxml import etree as etree
from gpx import utmconverter as utm
from gpx import algos as algos
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as dtt
from matplotlib import pyplot as plt
import time
import googlemaps


def parseGPX(filename):
    """ Reads a gpx file and returns a dataframe with the important parameters.
    'name','desc','segno','dist','lat','lng','ele','time','duration','speed' """
    
    
    f = open(filename,encoding='utf-8')
    ns = '{http://www.topografix.com/GPX/1/1}'
    xml = etree.parse(f)
    f.close()
    
    gpxinfo = list() 
    segc = -1 #Segment counter
    
    point = xml.find(ns+"trk/"+ns+"trkseg/"+ns+"trkpt")
    tmp_lat = float(point.attrib['lat'])
    tmp_lon = float(point.attrib['lon'])

#    startTime = dt.strptime(point.find(ns+'time').text,'%Y-%m-%dT%H:%M:%S.%fZ')
    startTime = dt.strptime(point.find(ns+'time').text,'%Y-%m-%dT%H:%M:%SZ')
    
    trks = xml.iterfind(ns+'trk')
    dist = 0
    for trk in trks:
        name = trk.find(ns+'name')
        if name != None:
            name = name.text
            
        else: name = "NA"
        
        desc = trk.find(ns+'desc')
        if desc != None:
            desc = desc.text
        else: desc = "NA"
    
        trksegs = trk.iterfind(ns+'trkseg')
        for trkseg in trksegs:
            segc += 1
            points = trkseg.iterfind(ns+'trkpt')
            for point in points:
                try:            
                    lat = float(point.attrib['lat'])
                    lon = float(point.attrib['lon'])       
                    ele = round(float(point.find(ns+'ele').text),2)
                    time = point.find(ns+'time').text
                    
                    dist += round(utm.haversine(tmp_lon,tmp_lat,lon,lat),2)
#                    timez = dt.strptime(time,'%Y-%m-%dT%H:%M:%S.%fZ')
                    timez = dt.strptime(time,'%Y-%m-%dT%H:%M:%SZ')
                    duration = (timez - startTime).total_seconds()
                    tmp_lat,tmp_lon = lat,lon
                    gpxinfo.append([name,desc,segc,dist,lat,lon,ele,timez,duration])
                except:
                    print("Points does not have all information needed, or namespace is wrong")
    
    gpxdf = pd.DataFrame(gpxinfo,columns=['name','desc','segno','dist','lat','lng','ele','time','duration'])
    gpxdf['speed'] = (gpxdf['dist'].shift(-1)-gpxdf['dist'])/(gpxdf['duration'].shift(-1)-gpxdf['duration'])
    gpxdf['speed'] = gpxdf['speed'].shift(1)
    
    return gpxdf

def getmainInfo(dataframe):
    print('Number of points:',len(dataframe))    
    print('Length:',max(dataframe['dist']))
    print('Lowest point:', min(dataframe['ele']))
    print('Highest point:', max(dataframe['ele']))
    
    a = (dataframe[dataframe['speed']<0.50][['duration']].index)
    print('Stop time:',dtt(seconds=sum(dataframe['duration'].diff()[a])))
    print('Walking time:',dtt(seconds=max(dataframe['duration'])-sum(dataframe['duration'].diff()[a])))
    print('Total time:',dtt(seconds=max(dataframe['duration'])))

def googleElevation(dataframe):
    lat = dataframe['lat']
    lng = dataframe['lng']
    dist = dataframe['dist']
    ele = dataframe['ele']
    
    dist1 = []
    ele1 = []
    ele2 = []
    
    gmaps = googlemaps.Client(key='AIzaSyC2F01wKnb0vmW8qxF5KvGIe2pbJgmm7HY')
    
    for i in range(0,len(lat),10):
        reverse_geocode_result = gmaps.elevation([(lat[i],lng[i])])
        tmp_ele = reverse_geocode_result[0]['elevation']
       
        print(lat[i],lng[i],dist[i],ele[i],tmp_ele)
        time.sleep(0.4)    
        dist1.append(dist[i])
        ele1.append(ele[i])
        ele2.append(tmp_ele)
    
    
    plt.plot(dist1,ele1)    
    plt.plot(dist1,ele2)
    plt.show()

def reducedElePoints(dataframe):
    dist = dataframe['dist']
    ele = dataframe['ele']
    l = []
    for i in range(len(dist)):
        l.append((dist[i],ele[i]))
    red = pd.DataFrame(algos.ramerdouglas(l,dist=5),columns=['dist','ele'])

    red['elediff'] = red['ele'].diff()
    
    print(sum(red[red['elediff']>0]['elediff']))
    print(sum(red[red['elediff']<0]['elediff']))
    print(dt.now())

def reducePoints(dataframe):
    lat = dataframe['lat']
    lng = dataframe['lng']
    l = []
    for i in range(len(lat)):
        coord = utm.from_latlon(lat[i],lng[i])
        l.append((coord[0],coord[1]))

    red = pd.DataFrame(algos.ramerdouglas(l,dist=5),columns=['lat','lng'])
    plt.plot(*zip(*l))
    plt.plot(red['lat'],red['lng'])
    plt.show()
    
    print(len(red))
    
def findStopLocations(dataframe):
    ind = dataframe[dataframe['speed']<0.50][['duration']].index
    dur = (dataframe['duration'].diff()[ind])
    lat = (dataframe['lat'][ind])
    lng = (dataframe['lng'][ind])
    
    tmp = None
    totdur = 0
    
    for i in ind:
        if tmp == None:        
            latS = lat[i]
            lngS = lng[i]
            totdur += dur[i]
            tmp = i
        
        else:
            if i - tmp == 1:
                totdur += dur[i]
            else:
                if totdur>30:
                    print("Break",i,latS,lngS,totdur)
                latS = lat[i]
                lngS = lng[i]
                totdur += dur[i]
                totdur = 0
            tmp = i
    if totdur>30:
        print("Break",latS,lngS,totdur)        

def readkommunexml(xml_file):
    kommunedict = dict()
    
    p = etree.XMLParser(remove_blank_text=True)
    et = etree.parse(xml_file,parser=p)    
    for kommune in et.iter('kommune'):
        d = dict()
        d['areal'] = kommune.find('areal')
        d['befolkning'] = kommune.find('befolkning')
        d['beskrivelse'] = kommune.find('beskrivelse')
        d['besteget'] = kommune.find('besteget')
        d['dato'] = kommune.find('dato')
        d['hoyde2'] = kommune.find('hoyde2')
        d['kommunenavn'] = kommune.find('kommunenavn')
        d['kommunenr'] = kommune.find('kommunenr')
        d['lat'] = kommune.find('lat')
        d['lng'] = kommune.find('lng')
        d['topp'] = kommune.find('topp')
        yield d




