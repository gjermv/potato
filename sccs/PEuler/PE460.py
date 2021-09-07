# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt


smallest = 1504170715041707
l = [[1,11504170715041707]]
ix = [1]

for i in range(2,10**8):
    x = 1504170715041707*i % 4503599627370517
    
    if x < smallest:
        smallest = x
        l.append(x)
        ix.append(i)
        
print(ix)    


plt.plot(ix,'o')


