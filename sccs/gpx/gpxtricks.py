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
    ns = findNamespace(f)
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

def findNamespace(file):
    str = file.read(1000)
    file.seek(0)
    ind1 = str.find('xmlns=')+7
    ind2 = str[ind1+1:].find('"')
    print(ind1,ind2)
    s = '{'+str[ind1:ind1+ind2+1]+'}'
    print(s)
    return s

def getmainInfo(dataframe):
    length = max(dataframe['dist'])
    tottime = max(dataframe['duration'])
    dateandtime = dataframe['time'][0] 
    
    stopframe = (dataframe[dataframe['speed']<0.50][['duration']].index)
    stoptime = sum(dataframe['duration'].diff()[stopframe])
    walktime = tottime - stoptime
    average_speed = length/walktime
    pausefaktor = stoptime/tottime
    ele_min = min(dataframe['ele'])
    ele_max = max(dataframe['ele'])
    elediff = ele_max-ele_min
    climbing = reducedElePoints(dataframe)
    steepness = climbing/(length/2)
    climbingrate = climbing/(walktime/2)
    kupert_faktor = climbing/elediff
    topptur_faktor = elediff/ele_max
    
    info = dict()
    info['length'] = round(length/1000,2) #km 
    info['dateandtime'] = dateandtime
    info['tottime'] = dtt(seconds=tottime)
    info['stop_time'] = dtt(seconds=stoptime)
    info['walk_time'] = dtt(seconds=walktime)
    info['pause_faktor'] = round(pausefaktor*100,1)
    info['avg_speed'] = round(average_speed*3.6,2)
    
    info['elediff'] = round(elediff,1)
    info['climbing'] = round(climbing,1)
    info['steepness'] = round(steepness*1000,1)
    info['climbingrate'] = round(climbingrate*60,1)
    info['kupert_faktor'] = round(kupert_faktor,2)
    info['topptur_faktor'] = round(topptur_faktor*100,1)
    return info

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
    red = pd.DataFrame(algos.ramerdouglas(l,dist=7.5),columns=['dist','ele'])

    red['elediff'] = red['ele'].diff()
    
    print(sum(red[red['elediff']>0]['elediff']))
    print(sum(red[red['elediff']<0]['elediff']))
    
    print(dt.now())
    
    return sum(red[red['elediff']>0]['elediff'])

def reducePoints(dataframe):
    lat = dataframe['lat']
    lng = dataframe['lng']
    l = []
    for i in range(len(lat)):
        coord = utm.from_latlon(lat[i],lng[i])
        l.append((coord[0],coord[1]))

    red = pd.DataFrame(algos.ramerdouglas(l,dist=5),columns=['lat','lng'])
    #plt.plot(*zip(*l))
    #plt.plot(red['lat'],red['lng'])
    #plt.show()
    pos = zip(lat,lng)
    return pos
    
def findStopLocations(dataframe):
    stopLoc = []
    
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
                    
                    stopLoc.append([latS,lngS,totdur])
                latS = lat[i]
                lngS = lng[i]
                totdur += dur[i]
                totdur = 0
            tmp = i

              
    return stopLoc

def exportStopLoc(dataframe):
    stopLoc = findStopLocations(dataframe)
    s = ''
    for loc in stopLoc:
        s += "toppMarker = L.marker([{},{}],{{icon: myIconStop}});\ntoppMarker.addTo(map);\n".format(loc[0],loc[1])
    return s

def exportRedPoints(dataframe):
    s = ''
    for p in reducePoints(dataframe):
        s += '[{0},{1}],'.format(p[1],p[0])
        
    geojson = """var myLines = [{
    "type": "LineString",
    "coordinates": ["""
    geojson += s
    geojson += """]
}];

L.geoJson(myLines, {
    style: myWalk
}).addTo(map);"""     
    
    
    return  geojson

def readkommunexml(xml_file):
    """ Reads the Offical kommunedatalist and yields a dictionary """
    kommunedict = dict()
    
    p = etree.XMLParser(remove_blank_text=True)
    et = etree.parse(xml_file,parser=p)    
    for kommune in et.iter('kommune'):
        d = dict()
        d['areal'] = kommune.find('areal').text
        d['befolkning'] = kommune.find('befolkning').text
        d['beskrivelse'] = kommune.find('beskrivelse').text
        d['besteget'] = kommune.find('besteget').text
        d['dato'] = kommune.find('dato').text
        d['hoyde2'] = kommune.find('hoyde2').text
        d['kommunenavn'] = kommune.find('kommunenavn').text
        d['kommunenr'] = kommune.find('kommunenr').text
        d['lat'] = kommune.find('lat').text
        d['lng'] = kommune.find('lng').text
        d['topp'] = kommune.find('topp').text
        yield d




