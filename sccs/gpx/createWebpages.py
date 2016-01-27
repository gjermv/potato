# -*- coding: utf-8 -*-
'''
Created on 7 Jan 2016

@author: gjermund.vingerhagen
'''

from jinja2 import Environment, FileSystemLoader
from gpx import gpxtricks
import os.path


def func1():
    """ Load the rapport template"""
    dir = os.path.dirname(__file__)
    template_dir = os.path.join(dir, 'res\\templates')
    myloader = FileSystemLoader(template_dir)
    env = Environment(loader=myloader)
    template_rapport = env.get_template('template_rapport.html')
        
    for kom in gpxtricks.readkommunexml(dir+'\\res\\kommunetopplisteV2.xml'):
        
        gpxfile = dir+"\\res\\gpx\\{0}.gpx".format(kom['kommunenr'])
        if os.path.isfile(gpxfile):
            print(kom['kommunenavn'])
            gpx_df = gpxtricks.parseGPX(gpxfile)
            kom['stoplocations'] = gpxtricks.exportStopLoc(gpx_df)
            kom['tripcoordinates'] = gpxtricks.exportRedPoints(gpx_df)
            kom.update(gpxtricks.getmainInfo(gpx_df))
        
        file = open('C:\\python\\kommuner\\outdata\\{}.html'.format(kom['kommunenr']),'w',encoding='utf-8')
        file.write(template_rapport.render(kom))

def func2():
    dir = os.path.dirname(__file__)
    gpxfile = os.path.join(dir, 'res\\gpx\\0105.gpx')
    
    
    
func1()