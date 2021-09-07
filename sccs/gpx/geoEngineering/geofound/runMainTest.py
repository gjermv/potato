# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 08:26:10 2021

@author: A485753
"""

import geoEngineering.geofound as geofound

length = 5
width = 2  # metres
depth = 1  # metres
phi = 34
cohesion = 0
unit_weight = 19  # submerged
youngs_modulus_soil = 30000


fd = geofound.create_foundation(length, width, depth)
sl = geofound.create_soil(phi, cohesion, unit_weight)

sl.unit_sat_weight = 18.5

q_lim = geofound.capacity.capacity_vesic_1975(sl, fd,vertical_load=1000,h_b=3, slope = 0)
p_max = q_lim * length * width

print(' ')
print('Ultimate bearing stress is q_lim = ' + str(round(q_lim,0)) + ' kPa')
print('Ultimate load is Q_lim = ' + str(round(p_max, 0)) + ' kN')

load = p_max*0.8
s = geofound.settlement.settlement_schmertmann(sl, fd, load, youngs_modulus_soil)
print(' ')
print('Settlement is si = ' + str(round(s,2)) + ' m')