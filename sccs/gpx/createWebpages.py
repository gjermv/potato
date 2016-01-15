# -*- coding: utf-8 -*-
'''
Created on 7 Jan 2016

@author: gjermund.vingerhagen
'''

from jinja2 import Environment, FileSystemLoader
from gpx import gpxtricks

""" Load the rapport template"""
myloader = FileSystemLoader('C:\\python\\kommuner')
env = Environment(loader=myloader)
template_rapport = env.get_template('template_rapport.html')

file = open('C:\\python\\kommuner\\outdata\\testfile.html','w')
file.write(template_rapport.render(topp='test'))

print('hurra')
print('hurrra,hurra')