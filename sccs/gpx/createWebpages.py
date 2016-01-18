# -*- coding: utf-8 -*-
'''
Created on 7 Jan 2016

@author: gjermund.vingerhagen
'''

from jinja2 import Environment, FileSystemLoader
from gpx import gpxtricks
import os

dir = os.path.dirname(__file__)
tempdir = os.path.join(dir, 'res\\templates')

""" Load the rapport template"""
myloader = FileSystemLoader(tempdir)
env = Environment(loader=myloader)
template_rapport = env.get_template('template_rapport.html')

file = open('C:\\python\\kommuner\\outdata\\testfile2.html','w',encoding='utf-8')

kommunenr = '0105'
#print(gpxtricks.parseGPX(dir+'\\res\\gpx\\{0}.gpx'.format(kommunenr)))

#file.write(template_rapport.render(topp='test',kommunenavn='0105'))
print('Sucessfully finished...')

for kom in gpxtricks.readkommunexml(dir+'\\res\\kommunetopplisteV2.xml'):
    for element in kom:
        print(kom[element].text)