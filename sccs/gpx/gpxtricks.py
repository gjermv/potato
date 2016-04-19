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
import glob 
import json


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
    
    startTime = gpxtimeToStr(point.find(ns+'time').text)
    
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
                    timez = gpxtimeToStr(time)
                    duration = (timez - startTime).total_seconds()
                    tmp_lat,tmp_lon = lat,lon
                    
                    print(time)
                    hr = getHeartRate(point,ns,filename)
                    gpxinfo.append([name,desc,segc,dist,lat,lon,ele,timez,duration,hr])
                    ## Test function
                    
                except:
                    print("Points does not have all information needed, or namespace is wrong")
    
    gpxdf = pd.DataFrame(gpxinfo,columns=['name','desc','segno','dist','lat','lng','ele','time','duration','heartrate'])
    gpxdf['speed'] = (gpxdf['dist'].shift(-1)-gpxdf['dist'])/(gpxdf['duration'].shift(-1)-gpxdf['duration'])
    gpxdf['speed'] = gpxdf['speed'].shift(1)
    
    return gpxdf

def getHeartRate(point,ns,filename):
    # Returns heartrate from a xml track point exported from Garmin Connect gpx. 
    try:
        hr = point.find(ns+'extensions')
        trkhr = hr.find('{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension')
        heartrate = int(trkhr.find('{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr').text)
        # print(heartrate)
        print(filename)
        return heartrate
    except:
        # print("Point does not have heartrate / Namespace wrong")
        return 'NA'
    
def gpxtimeToStr(timestr):
    try:
        t = dt.strptime(timestr,'%Y-%m-%dT%H:%M:%SZ')
        return t
    except:
        t = dt.strptime(timestr,'%Y-%m-%dT%H:%M:%S.%fZ')
        return t
    
def findNamespace(file):
    str = file.read(1000)
    file.seek(0)
    ind1 = str.find('xmlns=')+7
    ind2 = str[ind1+1:].find('"')
    s = '{'+str[ind1:ind1+ind2+1]+'}'
    return s

def calcEleDiff(elemin,elemax):
    if elemin < 0:
        return elemax
    else:
        elediff = elemax-elemin
        return elediff

def getmainInfo(dataframe):
    length = max(dataframe['dist'])
    tottime = max(dataframe['duration'])
    dateandtime = dataframe['time'][0] 
    
    stopframe = (dataframe[dataframe['speed']<0.4167][['duration']].index)
    stoptime = sum(dataframe['duration'].diff()[stopframe])
    walktime = tottime - stoptime
    average_speed = length/walktime
    pausefaktor = stoptime/tottime
    ele_min = min(dataframe['ele'])
    ele_max = max(dataframe['ele'])
    elediff = calcEleDiff(ele_min,ele_max)
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

def reducedElePoints(df):
    dataframe = df[df['lat'] != 0]
    dist = dataframe['dist']
    ele = dataframe['ele']
    l = []
    
    for i in dist.index:
        l.append((dist[i],ele[i]))
    red = pd.DataFrame(algos.ramerdouglas(l,dist=7.5),columns=['dist','ele'])
    red['elediff'] = red['ele'].diff()
    
    #===========================================================================
    # print(sum(red[red['elediff']>0]['elediff']))
    # print(sum(red[red['elediff']<0]['elediff']))
    #===========================================================================
 
    return sum(red[red['elediff']>0]['elediff'])

def createElevationProfile(dataframe,filename):
    dist = list(dataframe['dist'])
    ele = list(dataframe['ele'])
    
    dist = [0] +dist+ [max(dist)]
    ele = [0] +ele+ [0]

    plt.figure(figsize=(15, 4), dpi=80)
    plt.plot(dist,ele,'#666666',linewidth=2)
    plt.axis([0, max(dist), 0, max(ele)*1.1])
    ax = plt.axes()
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    plt.fill(dist,ele,'#838fd7')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    
def reducePoints(dataframe):
    lat = dataframe['lat']
    lng = dataframe['lng']
    desc = dataframe['desc']
    
    #===========================================================================
    # l = []
    # for i in range(len(lat)):
    #     coord = utm.from_latlon(lat[i],lng[i])
    #     l.append((coord[0],coord[1]))
    #===========================================================================

    #red = pd.DataFrame(algos.ramerdouglas(l,dist=5),columns=['lat','lng'])
    #plt.plot(*zip(*l))
    #plt.plot(red['lat'],red['lng'])
    #plt.show()
    pos = zip(lat,lng,desc)
    return pos
    
def findStopLocations(dataframe):
    stopLoc = []
    
    ind = dataframe[dataframe['speed']<0.4167][['duration']].index
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
                if totdur>121:
                    stopLoc.append([latS,lngS,totdur])
                latS = lat[i]
                lngS = lng[i]
                totdur = 0
            tmp = i

              
    return stopLoc

def exportStopLoc(dataframe):
    stopLoc = findStopLocations(dataframe)
    s = ''
    
    for loc in stopLoc:
        s += "stopMarker = L.marker([{},{}],{{icon: myIconStop}});\nstopMarker.addTo(map);\n".format(loc[0],loc[1])
        s += 'stopMarker.bindPopup("{} minutter");\n'.format(int(loc[2]//60))
    return s

def exportRedPoints(dataframe):
    geojson = ''
    groups = dataframe.groupby('desc')
    movtype = 'NA'
    
    for group,items in groups:
        s = ''
        for p in reducePoints(items):
            s += '[{0},{1}],'.format(p[1],p[0])
            
        geojson += """var myLines = [{
        "type": "LineString",
        "coordinates": ["""
        geojson += s
        if group == 'Ski':
            geojson += getSkiText()

        elif group == 'Cycle':
            geojson += getCycleText()
        
        else:
            geojson += getWalkText()
    
    return  geojson

def getWalkText():
    txt = """]
}];

L.geoJson(myLines, {
    style: myWalk
}).addTo(map);

"""
    return txt

def getCycleText():
    txt = """]
}];

L.geoJson(myLines, {
    style: myCycle
}).addTo(map);

"""
    return txt

def getSkiText():
    txt = """]
}];

L.geoJson(myLines, {
    style: mySki
}).addTo(map);

"""
    return txt

def readkommunexml(xml_file):
    """ Reads the Offical kommunedatalist and yields a dictionary with basic information """
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
        
        if d['beskrivelse'] == None:
            d['beskrivelse'] = ''
        
        yield d

def get_besteget_kommuner(xml_file):
    """ Returns a list of all kommuner that is besteget"""
    kommunelist = []
    
    p = etree.XMLParser(remove_blank_text=True)
    et = etree.parse(xml_file,parser=p)    
    
    for kommune in et.iter('kommune'):
        kommunelist.append(kommune.find('kommunenr').text)
    
    kommunelist = [kommunelist[len(kommunelist)-1]] + kommunelist + [kommunelist[0]]
    return kommunelist

def get_selected_fylke(kommunenr):
    
    fylke_to_line = {0:0,
                     2:1,
                     9:2,
                     6:3,
                     20:4,
                     4:5,
                     12:6,
                     15:7,
                     17:8,
                     18:9,
                     5:10,
                     3:11,
                     11:12,
                     14:13,
                     16:14,
                     8:15,
                     19:16,
                     10:17,
                     7:18,
                     1:19}
    fylkenr = fylke_to_line[int(kommunenr[:2])]
    
    line = list()
    line.append('\t\t\t<option>Velg fylke</option>\n') #0
    line.append('\t\t\t<option>Akershus</option>\n') #1
    line.append('\t\t\t<option>Aust-Agder</option>\n')#2
    line.append('\t\t\t<option>Buskerud</option>\n')#3
    line.append('\t\t\t<option>Finmark</option>\n')#4
    line.append('\t\t\t<option>Hedmark</option>\n')#5
    line.append('\t\t\t<option>Hordaland</option>\n')#6
    line.append('\t\t\t<option>Møre og Romsdal</option>\n')#7
    line.append('\t\t\t<option>Nord-Trøndelag</option>\n')#8
    line.append('\t\t\t<option>Nordland</option>\n')#9
    line.append('\t\t\t<option>Oppland</option>\n')#10
    line.append('\t\t\t<option>Oslo</option>\n')#11
    line.append('\t\t\t<option>Rogaland</option>\n')#12
    line.append('\t\t\t<option>Sogn og Fjordane</option>\n')#13
    line.append('\t\t\t<option>Sør-Trøndelag</option>\n')#14
    line.append('\t\t\t<option>Telemark</option>\n')#15
    line.append('\t\t\t<option>Troms</option>\n')#16
    line.append('\t\t\t<option>Vest-Agder</option>\n')#17
    line.append('\t\t\t<option>Vestfold</option>\n')#18
    line.append('\t\t\t<option>Østfold</option>\n')#19
    
    line[fylkenr] = line[fylkenr].replace('option','option selected')
    selecttxt = ''
    for item in line:
        selecttxt += item
        
    return selecttxt

def get_selected_kommune(xml_file):
    txtstr = 'kommuner[0] = "";\n'
    
    p = etree.XMLParser(remove_blank_text=True)
    et = etree.parse(xml_file,parser=p)    
    i = 1
    for fylke in et.iter('fylke'):
        txtstr += 'kommuner[{}] = ["Velg kommune|0000",'.format(i)
        i += 1
        for kommune in fylke.iter('kommune'):
            knavn = kommune.find('kommunenavn').text
            knum = kommune.find('kommunenr').text
            bes = kommune.find('besteget').text
            if bes == 'True':
                txtstr += '"* {0}|{1}",'.format(knavn,knum)
            else:
                txtstr += '"{0}|{1}",'.format(knavn,knum)
        txtstr += '];\n'
        
        txtstr.replace(',];\n','];\n')
    return txtstr

def createPicPage():
    for image in glob.glob('C:\\python\\kommuner\\outdata\\img\\*.jpg'):
        print('<img id="pagepic2" src="img/{}">'.format(image.split('\\')[5]))

def getKommuneGrense(filename='C:\\python\\kommuner\\kom_grens-mod.json',kommune='0101'):
    """ Leser kom-grens-mod og henter ut geometrien til en kommune
    basert paa kommunenummer   """
    l = []
    s = open(filename,'r',encoding='utf-8').read()
    js = json.loads(s)
    for item in js['features']:
        if item['properties']['komm'] == int(kommune):
            for pos in item['geometry']['coordinates'][0]:
                l.append([pos[1],pos[0]])
    return l

def getGPXheartzone(df):
   
    #===========================================================================
    # plt.plot(df['time'],df['heartrate'])
    # plt.show()
    # plt.close()
    #===========================================================================
    if df['heartrate'][0] == 'NA':
        return (0,0,0,0,0)
    
    print(df['heartrate'])
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

#===============================================================================
# for filename in glob.glob('C:\\python\\testdata\\gpxx4\\2016-02-03 2043 Impington.gpx'):
#     df = parseGPX(filename)
#     print(getGPXheartzone(df))
#===============================================================================