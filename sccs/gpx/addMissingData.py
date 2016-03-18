'''
Created on 22 Feb 2016

@author: gjermund.vingerhagen
'''

from lxml import etree as etree
from gpx import utmconverter as utm
from gpx import algos as algos
from gpx import  gpxtricks as gpxtricks
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as dtt
from matplotlib import pyplot as plt
import time
import googlemaps
import glob
import datetime


def calcTime(startTime,avgSpeed,dist):
    t = datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ")
    sec =  dist/avgSpeed
    t2 = t + datetime.timedelta(seconds=sec)
    print(t2.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return t2.strftime("%Y-%m-%dT%H:%M:%SZ")

def GPXaddTimes(filename,startTime,avgSpeed=5):
    """ Reads a gpx file ' """
    
    f = open(filename,encoding='utf-8')
    ns = gpxtricks.findNamespace(f)
    xml = etree.parse(f)
    f.close()
    trks = xml.iterfind(ns+'trk')
    tmp_lat = 0
    tmp_lon = 0
    dist = 0
    for trk in trks:
        trksegs = trk.iterfind(ns+'trkseg')
        for trkseg in trksegs:
            points = trkseg.iterfind(ns+'trkpt')
            for i,point in enumerate(points):
                if i == 0:         
                    tmp_lat = float(point.attrib['lat'])
                    tmp_lon = float(point.attrib['lon'])       
                    txt =  etree.SubElement(point, "time")
                    txt.text = startTime
                else:
                    lat = float(point.attrib['lat'])
                    lon = float(point.attrib['lon'])       
                    
                    length = round(utm.haversine(tmp_lon,tmp_lat,lon,lat),5)
                    dist += length
                    txt =  etree.SubElement(point, "time")
                    txt.text =  calcTime(startTime,avgSpeed,dist)
                    tmp_lat,tmp_lon = lat,lon
                
    print(etree.tostring(xml,pretty_print= True))
    f = open('C:\\python\\testdata\\Svanetind-export.gpx','wb')
    f.write(etree.tostring(xml,pretty_print= True))
    f.close()


  
GPXaddTimes('C:\\python\\testdata\\Svanetind-c.gpx','2011-08-28T08:30:00Z',4.5/3.6)
