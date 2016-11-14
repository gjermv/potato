# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 15:38:35 2015
@author: gjermund.vingerhagen
"""

from lxml import etree as etree
from gpx import utmconverter as utm
from gpx import algos as algos
from gpx import dtmdata as dtm
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as dtt
from matplotlib import pyplot as plt
import time
import googlemaps
import glob
import json
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
import matplotlib.cm as cm

def GPXtoDataFrame(filename):
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
                    
                    hr = getHeartRate(point,ns)
                    gpxinfo.append([name,desc,segc,dist,lat,lon,ele,timez,duration,hr])
                    ## Test function
                    
                except:
                    print("Points does not have all information needed, or namespace is wrong")
    
    gpxdf = pd.DataFrame(gpxinfo,columns=['name','desc','segno','dist','lat','lon','ele','time','duration','heartrate'])
    gpxdf['speed'] = (gpxdf['dist'].shift(-1)-gpxdf['dist'])/(gpxdf['duration'].shift(-1)-gpxdf['duration'])
    gpxdf['speed'] = gpxdf['speed'].shift(1)
    
    return gpxdf

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
        startTime = gpxtimeToStr(item.text)
        break
    
    
    for lap in xml.iter(ns+"Lap"):
        segno += 1
        for trkPoint in lap.iter(ns+"Trackpoint"):
            trkpoint = dict()
            trkpoint['name'] = name
            trkpoint['desc'] = desc
            trkpoint['segno'] = segno
            trkpoint['time'] = trkPoint.find(ns+"Time").text
            trkpoint['duration'] = (gpxtimeToStr(trkpoint['time'])-startTime).total_seconds()
            
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

def getHeartRate(point,ns):
    # Returns heartrate from a xml track point exported from Garmin Connect gpx. 
    try:
        hr = point.find(ns+'extensions')
        trkhr = hr.find('{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension')
        heartrate = int(trkhr.find('{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr').text)
        # print(heartrate)
        return heartrate
    except:
        # print("Point does not have heartrate / Namespace wrong")
        return -1
    
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
    length = dataframe['dist'].max()
    tottime = max(dataframe['duration'])
    dateandtime = dataframe['time'][0] 
    
    stopframe = (dataframe[dataframe['speed']<0.4167][['duration']].index)
    stoptime = sum(dataframe['duration'].diff()[stopframe])
    walktime = tottime - stoptime
    average_speed = length/walktime
    pausefaktor = stoptime/tottime
    ele_min = dataframe['ele'].min()
    ele_max = dataframe['ele'].max()
    elediff = calcEleDiff(ele_min,ele_max)
    climbing = getClimbingHeightGPS(dataframe)
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

def googleElevation(dataframe,df2=None):
    
    dist1 = []
    ele1 = []
    ele2 = []
    
    gmaps = googlemaps.Client(key='AIzaSyC2F01wKnb0vmW8qxF5KvGIe2pbJgmm7HY')
    
    for df in dataframe.iterrows():
        tub = {'lat':df[1]['lat'],'lng':df[1]['lon']}
        reverse_geocode_result = gmaps.elevation(tub)
        tmp_ele = reverse_geocode_result[0]['elevation']
       
        print(df[1]['duration'],df[1]['lat'],df[1]['lon'],df[1]['dist'],df[1]['ele'],tmp_ele)
        time.sleep(0.15)    
        dist1.append(df[1]['dist'])
        ele1.append(df[1]['ele'])
        ele2.append(tmp_ele)
    
    dataframe['googleele'] = ele2
    return dataframe

def kartverketElevation(lat=52.14363,lon=-1.24902):
    with urllib.request.urlopen('http://openwps.statkart.no/skwms1/wps.elevation?request=Execute&service=WPS&version=1.0.0&identifier=elevation&datainputs=%5blat={0};lon={1};epsg=4326%5d'.format(lat,lon)) as response:
        html = response.read()
    
    root = ET.fromstring(html)
    for child in root:
        print(child.tag, child.attrib,child.text)
        for child2 in child:
            
    
            print('-',child2.tag, child2.attrib, child2.text)
            for child3 in child2:
                print('--',child3.tag, child3.attrib, child3.text)
                for child4 in child3:
                    print('---',child4.tag, child4.attrib, child4.text)
    
    elevation = root[2][2][2][0].text
    return elevation

def kartverketElevation2(dataframe):
    kartele = []
    for df in dataframe.iterrows():
        easting, northing, zone_number, zone_letter = utm.from_latlon(df[1]['lat'],df[1]['lon'],force_zone_number=32)
        
        ele = dtm.calculateEle(easting,northing)
        kartele.append(ele)
        
    dataframe['kartele'] = kartele
    
    return dataframe
            
def getClimbingHeightGPS(df):
    dataframe = df[df['lat'] != 0]
    dist = dataframe['dist']
    ele = dataframe['ele']
    l = []
    
    for i in dist.index:
        l.append((float(dist[i]),float(ele[i])))
    
    red = pd.DataFrame(algos.ramerdouglas(l,dist=7.5),columns=['dist','ele'])
    red['elediff'] = red['ele'].diff()
 
    return round(sum(red[red['elediff']>0]['elediff']),2)

def getClimbingHeightDTM(df):
    dataframe = df[df['lat'] != 0]
    dist = dataframe['dist']
    try:
        ele = kartverketElevation2(df)['kartele']
        l = []
    
        for i in dist.index:
            l.append((float(dist[i]),float(ele[i])))
        
        red = pd.DataFrame(algos.ramerdouglas(l,dist=7.5),columns=['dist','ele'])
        red['elediff'] = red['ele'].diff()
     
        return round(sum(red[red['elediff']>0]['elediff']),2)
    except:
        return -1
    
def reduceElevationPoints(df):
    dataframe = df[df['lat'] != 0]
    dist = dataframe['dist']
    ele = dataframe['ele']
    l = []
    
    for i in dist.index:
        l.append((float(dist[i]),float(ele[i])))
    
    red = pd.DataFrame(algos.ramerdouglas(l,dist=7.5),columns=['dist','ele'])
    
    l2 = list()
    for item in red['dist']:
        l2.append(df[df['dist']==item])
        
    df_red = pd.concat(l2)
    df_red['speed'] = (df_red['dist'].shift(-1)-df_red['dist'])/(df_red['duration'].shift(-1)-df_red['duration'])
    df_red['speed'] = df_red['speed'].shift(1)
    return df_red

def plotElevationProfile(dataframe,filename=None):
    ""
    dist = list(dataframe[dataframe['ele'] != np.nan]['dist'])
    ele = list(dataframe[dataframe['ele'] != np.nan]['ele'])
    
    dist = [0] +dist+ [max(dist)]
    ele = [0] +ele+ [0]
    
    plt.figure(figsize=(15, 4), dpi=80)
    plt.plot(dist,ele,'#666666',linewidth=2)
    
    plt.axis([0, max(dist), 0, max(ele)*1.1])
    ax = plt.axes()
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    plt.fill(dist,ele,'#838fd7')
    
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print("file saved" , filename)
    else:
        plt.show()
def plotElevationProfile2(dataframe,filename=None):
    ""
    dist = list(dataframe[dataframe['ele'] != np.nan]['dist'])
    ele = list(dataframe[dataframe['ele'] != np.nan]['ele'])
    
    dist = [0] +dist+ [max(dist)]
    ele = [0] +ele+ [0]
    
    plt.figure(figsize=(15, 8), dpi=80)
    plt.plot(dist,ele,'#666666',linewidth=2)
    
    plt.axis([0, max(dist), 0, max(ele)*1.1])
    ax = plt.axes()
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print("file saved" , filename)
    else:
        plt.show()

def plotSpeedProfile(dataframe,filename=None):
    
    dist = list(dataframe['duration'])[1:]
    y_val = np.array(list(dataframe['speed'])[1:])*3.6
    
    plt.figure(figsize=(15, 8), dpi=80)
    plt.axis([0, max(dist), 0, max(y_val)*1.1])
    ax = plt.axes()
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    plt.plot(dist,y_val,'#838fd7')
    
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print("file saved" , filename)
    else:
        plt.show()

def plotHeartrateProfile(dataframe,filename=None):
    hrz_lim = heartZoneTable()
    dist = list(dataframe['duration'])
    y_val = list(dataframe['heartrate'])
    
    plt.figure(figsize=(15, 8), dpi=80)
    plt.axis([0, max(dist), 80, 200])
    ax = plt.axes()
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    plt.yticks([hrz_lim['sone1'],hrz_lim['sone2'],hrz_lim['sone3'],hrz_lim['sone4']])
    plt.plot(dist,y_val,'#b30000',linewidth=3)
    
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print("file saved" , filename)
    else:
        plt.show()

def plotHeartZone(dataframe,filename=None):
    
    hrzone = heartZone(dataframe)
    print('hr',hrzone)
    
    if hrzone == -1: 
        yax = np.array([0,0,0,0,0])
    if hrzone != -1:
        tot = sum(hrzone)
        yax = np.array([hrzone[0],hrzone[1],hrzone[2],hrzone[3],hrzone[4]])/tot*100
    
    xax = np.array([1,2,3,4,5])
    cax = ['#fef0d9','#fdcc8a','#fc8d59','#e34a33','#b30000']
    
    fig, ax = plt.subplots(figsize=(6.2,3.2))
    ax.yaxis.grid(True)
    rects1 = ax.bar(xax, yax, width = 1, color=cax)
    ax.set_xticks(xax + 0.5)
    ax.set_xticklabels(('Sone1', 'Sone2', 'Sone3', 'Sone4', 'Sone5'))
    ax.axis([1,6,0,100])


    if filename:
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print("file saved" , filename)
    else:
        plt.show()
             
def reducePoints(dataframe):
    lat = dataframe['lat']
    lon = dataframe['lon']
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
    pos = zip(lat,lon,desc)
    return pos
    
def findStopLocations(dataframe):
    stopLoc = []
    
    ind = dataframe[dataframe['speed']<0.4167][['duration']].index
    dur = (dataframe['duration'].diff()[ind])
    lat = (dataframe['lat'][ind])
    lon = (dataframe['lon'][ind])
    
    tmp = None
    totdur = 0
    
    for i in ind:
        if tmp == None:        
            latS = lat[i]
            lonS = lon[i]
            totdur += dur[i]
            tmp = i
        
        else:
            if i - tmp == 1:
                totdur += dur[i]
            else:
                if totdur>121:
                    stopLoc.append([latS,lonS,totdur])
                latS = lat[i]
                lonS = lon[i]
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
            if not np.isnan(p[0]):
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

def getTrackBounds(dataframe):
    minlat= dataframe['lat'].min()
    maxlat= dataframe['lat'].max()
    
    minlon= dataframe['lon'].min()
    maxlon= dataframe['lon'].max()
    
    jstxt = """map.fitBounds([
    [{0}, {1}],
    [{2}, {3}]
]);""".format(minlat,minlon,maxlat,maxlon)
    print(minlat,maxlat,minlon,maxlon)
    return jstxt

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
        d['lon'] = kommune.find('lng').text
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

def heartZoneTable():
    """Defines max values for heartrate zones"""
    hr_tab = dict()
    hr_tab['sone1'] = 135
    hr_tab['sone2'] = 155
    hr_tab['sone3'] = 165
    hr_tab['sone4'] = 175
    return hr_tab


def heartZone(df):
    df = df[df['heartrate'].notnull()][:]
    df['timediff'] = df['duration'].diff()
    df['heartrate2'] = (df['heartrate'].shift()+df['heartrate'])/2
    hrzones = heartZoneTable()
    hz =  dict()
    hz[1] = 0
    hz[2] = 0
    hz[3] = 0
    hz[4] = 0
    hz[5] = 0
    
    for row in df.iterrows():
        if row[1]['heartrate2'] > 0:
            if row[1]['heartrate2'] < hrzones['sone1']:
                hz[1] += row[1]['timediff']
            elif row[1]['heartrate2'] < hrzones['sone2']:
                hz[2] += row[1]['timediff']
            elif row[1]['heartrate2'] < hrzones['sone3']:
                hz[3] += row[1]['timediff']
            elif row[1]['heartrate2'] < hrzones['sone4']:
                hz[4] += row[1]['timediff']
            elif row[1]['heartrate2'] > hrzones['sone4']: 
                hz[5] += row[1]['timediff']
    
    if hz[1]+hz[2]+hz[3]+hz[4]+hz[5] == 0:
        return -1
    return (hz[1],hz[2],hz[3],hz[4],hz[5])

def heartAverage(df):
    df = df[df['heartrate']>0][:]
    df['timediff'] = df['duration'].diff()
    df['heartrate2'] = (df['heartrate'].shift()+df['heartrate'])/2
    
    if len(df)>0:
        hr = dict()
        hr['max'] = df['heartrate'].max()
        hr['mean'] = (df['heartrate2']*df['timediff']).sum()/df['timediff'].sum()
        hr['avg'] =df['heartrate'].mean()
        hr['total'] =(df['heartrate2']*df['timediff']).sum()/60
        
        return hr
    else:
        return False

def getExtrapolatedInterpolatedValue(dataGrid,x):
    
    if x not in dataGrid['dist'].values:
        dg2 = dataGrid.append({'dist':x},ignore_index=True)
        dataGrid = dg2.sort(['dist'])
        dataGrid.index = dataGrid['dist']
        df = dataGrid.interpolate(method='index')
        dataGrid = df
    else:
        dataGrid.index = dataGrid['dist']
    return [dataGrid[dataGrid['dist']==x]['duration']]

def findBestTempo(dataframe,avgdist):
    avg_dist = avgdist
    speedlist = []
    
    for dist2 in dataframe[dataframe['dist']>avg_dist]['dist']:
        v1 = getExtrapolatedInterpolatedValue(dataframe,dist2-avg_dist)
        v2 = getExtrapolatedInterpolatedValue(dataframe,dist2)
        
        t1 = 1
        t2 = 1
        
        for item1 in v1[0]:
            t1 = item1
        for item2 in v2[0]:
            t2 = item2
        
        sec = t2-t1
        
        speed = avg_dist/sec
        speedlist.append([speed*3.6,dist2-avg_dist,dist2])
    
    if len(speedlist) > 0:   
        return max(speedlist)
    return 'Not found'

def findBestTempo2(dataframe):
    df =  dataframe.copy()
    distances =  [100,200,400,800,1000,1500,3000,5000,10000,20000,50000]
    rbest = dict()
    for item in distances:
        rbest[item] = [0,-1]
    #print(df['dist'].head())
    
    for i,line in enumerate(df.iterrows()):
        currpos = line[1]['dist']
        #print(i,currpos)
        A = np.array(df['dist'])
        
        for dist in distances:
            ind = A.searchsorted(dist+currpos,side='right')
            if ind < len(df)-1:
                d = df.iloc[ind]['dist']-df.iloc[i]['dist']
                t = df.iloc[ind]['duration']-df.iloc[i]['duration']
                if d/t > rbest[dist][0]:
                    rbest[dist][0] = d/t
                    rbest[dist][1] = currpos
            else:
                break
    
    return rbest
            
def updateBestTimes(dists,ditimes,distart,dist,ti,startdist):
    for i in range(len(dists)):        
        if dist > dists[i]:
            if (dist / ti) > ditimes[i]:
                ditimes[i] = dist / ti
                distart[i] = startdist
                
    return ditimes,distart

def showEleMap(dataframe,filename='None'):
    df = dataframe.copy()
    
    df = kartverketElevation2(df)
    
    eastings = []
    northings = []
    
    for row in df.iterrows():
        east, north, zone_number, zone_letter = utm.from_latlon(row[1]['lat'],row[1]['lon'],force_zone_number=32)
        eastings.append(east)
        northings.append(north)
    
    print(min(eastings),min(northings))
    
    p1 = dtm.findClosestPoint(min(eastings)-100,min(northings)-100)
    p2 = dtm.findClosestPoint(max(eastings)+100,max(northings)+100)

    c1east = p1[5]+(p1[0])*10
    c1north = p1[6]+(p1[1])*10

    
    ns = p2[1]-p1[1]
    df['easting'] = eastings
    df['northing'] = northings
    df['easting2'] = (df['easting']-c1east)/10
    df['northing2'] = (-(df['northing']-c1north)/10)+ns
    
    try:
        a = dtm.getElevationArea(p1[0], p1[1], p2[0], p2[1]+1,p1[2])
        a = np.rot90(a)
         
        plt.imshow(a,cmap=cm.gist_earth)
        CS  = plt.contour(a,colors=['yellow','red','black'],levels=[df['kartele'].min()*10+100,df['kartele'].max()*10-100,(df['kartele'].max()+df['kartele'].min())/2*10],linewidths=[0.7,0.7,0.7])
        #plt.clabel(CS, fontsize=8, inline=1)
        plt.plot(df['easting2'],df['northing2'],linewidth=2)
        plt.show()
        plt.close()
    except:
        print("Something went wrong with creating the map. ")

    fig, (ax,ax1) = plt.subplots(nrows=2, ncols=1)
    ax.set_xlim([0,df['dist'].max()])
    ax1.set_xlim([0,df['dist'].max()])
    ax.axhline(df['kartele'].min()+10, linestyle='-', color='green')
    ax.axhline(df['kartele'].max()-10, linestyle='-', color='red')
    ax.axhline((df['kartele'].max()+df['kartele'].min())/2, linestyle='--', color='black')
    ax.plot(df['dist'],df['kartele'],linewidth=2)
    ax.plot(df['dist'],df['ele'],'--',linewidth=1,color='blue')
    

    ax1.plot(df['dist'],pd.rolling_mean(df['speed']*3.6,window=5,center=True),linewidth=1.2)
    plt.gca().xaxis.grid(True)

    ax.xaxis.grid(True)
    ax1.xaxis.grid(True)
    plt.show()

def calculateSufferScore(dataframe):
    if sum(dataframe['heartrate'])<0:
        return -1
    
    a = 0.00002
    b = 0.0422
    
    df = dataframe.copy()
    df['d_dur'] = df['duration'].diff()
    df['r_hr'] = (df['heartrate']+df['heartrate'].shift())/2

    df['suffer'] = df['d_dur']*a*np.exp(df['r_hr']*b)

    return df['suffer'].sum()
    
if __name__ == "__main__":
    df = pd.read_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df_time = df[df['dateandtime']>'2016-01-01']
    df_act = df_time[df_time['activity']!='Gree']
    filelist = list(df_act['filename'])
    l = list()
    
    for item in filelist:  
        filename = 'C:\\python\\testdata\\gpxx4\\files\\{}'.format(item)
        #print(filename)
        try:
            trk=GPXtoDataFrame(filename)
        except:
            trk=TCXtoDataFrame(filename)
        #print('Number of points: ',len(trk))
        x = calculateSufferScore(trk)
        print(item)
        l.append([item,calculateSufferScore(trk)])
            
    p = pd.DataFrame(l)
    p.to_csv('C:\\python\\testdata\\gpxx4\\test.csv')

        
        

  #=============================================================================
  #       gpsh = showEleMap(trk)
  #       dtmh = getClimbingHeightDTM(trk)
  # 
  #       if dtmh>0:
  #           print('{};{};{}'.format(item,gpsh,dtmh))
  #           showEleMap(trk)
  #=============================================================================
