'''
Created on 16 Mar 2016

@author: gjermund.vingerhagen
'''

from lxml import etree as etree
from datetime import datetime as dt
from datetime import timedelta as dtt
import googlemaps
import os.path
import utmconverter as utmconv
import collections as cs

import pandas as pd
import matplotlib.pyplot as plt

def copyTCX(filename):
    """ Reads a TCX file, renames the file and saves it in a different folder """
    f = open(filename,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    rawdata = findTCXFirstPoint(xml, ns)
    pdata = normalizedata(rawdata['rawlat'],rawdata['rawlon'],rawdata['rawtime'])
    
    loc = googleLocation(pdata['lat'], pdata['lon'])
    timezone = googleTimezone(pdata['lat'], pdata['lon'],pdata['time'])
    
    newfilename = createfilename(loc,pdata['time'],timezone,'tcx')
    
    trkname = xml.find(ns+"Activities/"+ns+"Activity/"+ns+"Id")
    trkname.text = str(pdata['time']+dtt(seconds=timezone))[:16]
    
    fullFilePath = 'C:\\python\\testdata\\tcxnew\\{}'.format(newfilename)
    f = open(fullFilePath,'wb')
    f.write(etree.tostring(xml))
    f.close()
    return fullFilePath

def copyTCX2(originalFile,saveFilepath,newFilename):
    """ Reads a TCX file, renames the file and saves it in a different folder """
    f = open(originalFile,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    rawdata = findTCXFirstPoint(xml, ns)
    pdata = normalizedata(rawdata['rawlat'],rawdata['rawlon'],rawdata['rawtime'])
    
    loc = googleLocation(pdata['lat'], pdata['lon'])
    timezone = googleTimezone(pdata['lat'], pdata['lon'],pdata['time'])
    
    
    trkname = xml.find(ns+"Activities/"+ns+"Activity/"+ns+"Id")
    trkname.text = str(pdata['time']+dtt(seconds=timezone))[:16]
    
    fullFilePath = saveFilepath+'\\'+newFilename

    f = open(fullFilePath,'wb')
    f.write(etree.tostring(xml))
    f.close()
    
    return fullFilePath

def copyGPX(filename):
    """ Reads a GPX file, renames the file and saves it in a different folder """
    
    f = open(filename,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    point = xml.find(ns+"trk/"+ns+"trkseg/"+ns+"trkpt")
    startlat = float(point.attrib['lat'])
    startlon = float(point.attrib['lon'])
    starttime = normalizetimedata(point.find(ns+'time').text)
    
    loc = googleLocation(startlat, startlon)
    timezone = googleTimezone(startlat, startlon, starttime)
     
    newfilename = createfilename(loc,starttime,timezone,'gpx')
    
    trkname = xml.find(ns+"trk/"+ns+"name")
    trkname.text = str(starttime+dtt(seconds=timezone))[:16]
    
    fullFilePath = 'C:\\python\\testdata\\tcxnew\\{}'.format(newfilename)
    
    f = open(fullFilePath,'wb')
    f.write(etree.tostring(xml))
    f.close()
    
    return fullFilePath

def copyGPX2(originalFile,saveFilepath,newFilename):
    """ Reads a GPX file, renames the file and saves it in a different folder """
    
    f = open(originalFile,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    point = xml.find(ns+"trk/"+ns+"trkseg/"+ns+"trkpt")
    startlat = float(point.attrib['lat'])
    startlon = float(point.attrib['lon'])
    starttime = normalizetimedata(point.find(ns+'time').text)
    timezone = googleTimezone(startlat, startlon, starttime)
    try:
        trkname = xml.find(ns+"trk/"+ns+"name")
        trkname.text = str(starttime+dtt(seconds=timezone))[:16]
    except:
        pass       
    
    fullFilePath = saveFilepath+'\\'+newFilename
  
    f = open(fullFilePath,'wb')
    f.write(etree.tostring(xml))
    f.close()
    
    return 0#fullFilePath

def copyGPSFile(originalFile,saveFilepath,newFilename):
    extension = os.path.splitext(originalFile)[1]
    print("at -copyGPSFile-",originalFile,saveFilepath,newFilename)
    if 'gpx' in extension:
        copyGPX2(originalFile, saveFilepath, newFilename)
    elif 'tcx' in extension:
        copyTCX2(originalFile, saveFilepath, newFilename)
    return 1

def getNewFileName(filename):
    f = open(filename,encoding='utf-8')
    ns = findNamespace(f)
    xml = etree.parse(f)
    f.close()
    
    extension = os.path.splitext(filename)[1]
    
    if 'gpx' in extension:
        point = xml.find(ns+"trk/"+ns+"trkseg/"+ns+"trkpt")
        startlat = float(point.attrib['lat'])
        startlon = float(point.attrib['lon'])
        starttime = normalizetimedata(point.find(ns+'time').text)
    elif 'tcx' in extension:
        rawdata = findTCXFirstPoint(xml, ns)
        pdata = normalizedata(rawdata['rawlat'],rawdata['rawlon'],rawdata['rawtime'])
        startlat = pdata['lat']
        startlon = pdata['lon']
        starttime = pdata['time']
        
    
    knowLoc = getKnownLocation(startlat, startlon)
    loc = 'Unknown'
    if knowLoc:
        loc = knowLoc.placename
    else:   
        loc = googleLocation(startlat, startlon)
        
    timezone = googleTimezone(startlat, startlon, starttime)
    newfilename = createfilename(loc,starttime,timezone,extension)
    
    return newfilename
    
def normalizedata(lat,lon,mytime):
    """ Normalize the important objects to correct format """
    lat = float(lat)
    lon = float(lon)
    normtime = normalizetimedata(mytime)
    return ({'time':normtime,'lat':lat,'lon':lon})

def normalizetimedata(mytime):
    """ Normalize the time to datetime object """
    if len(mytime) == 24:
        normtime = dt.strptime(mytime,'%Y-%m-%dT%H:%M:%S.%fZ')
    else:
        normtime = dt.strptime(mytime,'%Y-%m-%dT%H:%M:%SZ')
    return normtime

def findTCXFirstPoint(xml,ns):
    """ Find the first location in a TCX xml """
    for trkPoint in (xml.iter(ns+"Trackpoint")):
        starttime = (trkPoint.find(ns+"Time").text)
        try:
            lat = trkPoint.find(ns+"Position/"+ns+"LatitudeDegrees").text
            lon = trkPoint.find(ns+"Position/"+ns+"LongitudeDegrees").text
            return ({'rawtime':starttime,'rawlat':lat,'rawlon':lon})
        except:
            print("Error - No location:",starttime)

def TCXtoDataFrame(xml,ns):
    TCXlist = list()
    for trkPoint in (xml.iter(ns+"Trackpoint")):
        trkpoint = dict()
        trkpoint['time'] = (trkPoint.find(ns+"Time").text)
        try:
            trkpoint['lat'] = trkPoint.find(ns+"Position/"+ns+"LatitudeDegrees").text
            trkpoint['lon'] = trkPoint.find(ns+"Position/"+ns+"LongitudeDegrees").text
            trkpoint['altitude'] = trkPoint.find(ns+"AltitudeMeters").text
            trkpoint['distance'] = trkPoint.find(ns+"DistanceMeters").text
        except:
            print(trkpoint['time'])
        try:
            trkpoint['heartrate']= int(trkPoint.find(ns+"HeartRateBpm/"+ns+"Value").text)
        except:
            trkpoint['heartrate']= 0
        
        TCXlist.append(trkpoint)
    
    df = pd.DataFrame(TCXlist)
    df['time'] = pd.to_datetime(df['time'])
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    df['altitude'] = df['altitude'].astype(float)
    df['distance'] = df['distance'].astype(float)
    return df

def createfilename(location,time,timezone=0,fileextension='.gpx'):
    normtime = str(time+dtt(seconds=timezone))
    normtime = normtime[:16]
    normtime = normtime.replace(':','')
    newfilename = '{0} {1}{2}'.format(normtime,location,fileextension)
    return newfilename

def findNamespace(file):
    """Finds the gpxfile namespace in a gpx file """
    str = file.read(1000)
    file.seek(0)
    ind1 = str.find('xmlns=')+7
    ind2 = str[ind1+1:].find('"')
    s = '{'+str[ind1:ind1+ind2+1]+'}'
    return s

def googleLocation(lat,lon):
    """ Takes a location in lat, lon and returns the closest road or similar """
    gmaps = googlemaps.Client(key='AIzaSyC2F01wKnb0vmW8qxF5KvGIe2pbJgmm7HY')
    reverse_geocode_result = gmaps.reverse_geocode([lat,lon])
    
    if len(reverse_geocode_result) > 0:
        return reverse_geocode_result[0]['formatted_address'].replace(',',' -').replace(' - ','-')
    else: return "Location not known"

def googleTimezone(lat,lon,starttime):
    gmaps = googlemaps.Client(key='AIzaSyC2F01wKnb0vmW8qxF5KvGIe2pbJgmm7HY')
    timezone_result = gmaps.timezone(location=[lat,lon],timestamp=starttime)
    
    totOffset = timezone_result['rawOffset']+timezone_result['dstOffset']
    if len(timezone_result) > 0:
        return totOffset
    else: return "Location not known"

def getKnownLocation(lat,lon):
    radius = 75 # unit: meter
    loc = cs.namedtuple('Location','placename,lat, lon')
    
    locList = list()
    locList.append(loc('The Coppice', 52.23757, 0.111214))
    locList.append(loc('Moaveien', 59.278336, 11.026042))
    locList.append(loc('Rotherwick', 51.302635,  -0.971286))
    
    for item in locList:
        print(utmconv.haversine(item.lon, item.lat, lon, lat))
        if utmconv.haversine(item.lon, item.lat, lon, lat)< radius:
            return item
    
    return False
    