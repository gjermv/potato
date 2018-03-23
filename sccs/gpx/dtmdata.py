'''
Created on 14 Jun 2016

@author: gjermund.vingerhagen
'''

import numpy as np
import scipy.interpolate as intp
import linecache
import utmconverter as utm

def splitHead(inp):
    return inp

def lineToArr(l1):
    arra = np.array(np.fromstring(l1[144:1024],dtype=int,sep=' '))
    
    for i in range(1,30):
        arra = np.append(arra,np.fromstring(l1[1024*i:1024*(i+1)],dtype=int,sep=' '))
    return arra

def findClosestPoint(east,north):
    try:
        dtminfo = getDTMFile(east,north)
        eastLine = round((east-dtminfo[1])//10)
        northLine = round((north-dtminfo[2])//10)
        east_delta = (east-dtminfo[1])%10
        north_delta = (north-dtminfo[1])%10
    
        return [eastLine,northLine,dtminfo[0],east_delta,north_delta,dtminfo[1],dtminfo[2]]
    except: 
        raise Exception("Closest point has no DTM file ")

def readFile(filename):  
    line1 = open("C:\\python\\dtms\\{}".format(filename), 'r').read(500000)

    print(line1[0:134])
    print(line1[150:156])
    print(line1[156:162])
    print(line1[162:168])
    print(line1[529:535])
    print(line1[535:541])
    print('{:9}{}'.format('MinEast:',line1[546:570]))
    print('{:9}{}'.format('MinNorth:',line1[570:594]))
    print(line1[594:618])
    print(line1[618:642])
    print(line1[642:666])
    print(line1[666:690])
    print(line1[690:714])
    print(line1[714:738])
    print(line1[738:762])
    print(line1[762:786])
    print('{:9}{}'.format('dy:',line1[816:828]))
    print('{:9}{}'.format('dx:',line1[828:840]))
    print('{:10}{}'.format('Rows:',line1[858:864]))
    print('-----')
    print()
    
    minEast = float(line1[546:570])
    minNorth = float(line1[570:594])
    print(line1[1024+30720*0:1024+144+30720*0])
#===============================================================================
# print(line1[1168:2048])
# print(line1[1024*2:1024*3])
# print(line1[1024*4:1024*5])
#===============================================================================

def getElevation(eastL,northL,dtmfile):
    rows = 5041
    head = 1024
    lhead = 144
    blockSize = 30720
    
    eastLine = eastL
    northLine = northL
    
    with open("C:\\python\\dtms\\{}".format(dtmfile), 'r') as fin:
        fin.seek(head+blockSize*eastLine)
        data = fin.read(blockSize)
        
        if northLine < 146:
            s = 144+northLine*6
            
        else:
            c = (northLine-146) // 170 +1
            d = (northLine-146) % 170
            
            s = 1024*(c)+d*6
            
        return float(data[s:s+6])/10

def getElevationArea(eastLmin,northLmin,eastLmax,northLmax,dtmfile):
    rows = 5041
    head = 1024
    lhead = 144
    blockSize = 30720
    
    rect = []
    
    with open("C:\\python\\dtms\\{}".format(dtmfile), 'r') as fin:
        for eastLine in range(eastLmin,eastLmax+1):
            
            line = []
            fin.seek(head+blockSize*eastLine)
            data = fin.read(blockSize)
            for northLine in range(northLmin,northLmax):
                if northLine < 146:
                    s = 144+northLine*6
                    
                else:
                    c = (northLine-146) // 170 +1
                    d = (northLine-146) % 170
                    
                    s = 1024*(c)+d*6
                    
                line.append(int(data[s:s+6]))
            
            rect.append(line)
    return rect        
    
def calculateEle(x,y,coordsys='utm'):
    if coordsys == 'latlon':
        east, north, zone_number, zone_letter = utm.from_latlon(x, y)
    else:
        east,north = x,y
    try:
        p = findClosestPoint(east, north)
        dpx = p[3]
        dpy = p[4]
        
        ele1 = getElevation(p[0], p[1],p[2])
        ele2 = getElevation(p[0]+1, p[1],p[2])
        ele3 = getElevation(p[0], p[1]+1,p[2])
        ele4 = getElevation(p[0]+1, p[1]+1,p[2])
        #c_ele = getInterpolatedEle(ele1,ele2,ele3,ele4,[dpx,dpy])[2]
        d_ele = interpolateEle2(ele1,ele2,ele3,ele4,[dpx,dpy])
    
        return d_ele
    except Exception:
        raise Exception("Something went wrong")
        
def getInterpolatedEle(p1e=10,p2e=5,p3e=5,p4e=0,pxc=[5,5]):
    if sum(pxc)>10:
        p1 = np.array([10,10,p4e])
    else:
        p1 = np.array([0,0,p1e])
        
    p2 = np.array([10,0,p2e])
    p3 = np.array([0,10,p3e])
    
    px = np.array([pxc[0],pxc[1]])
    
    a = p2-p1
    b = p3-p1
    N = np.cross(a,b)

    
    c = px-p1[:2]
    x = -(N[0]*c[0]+N[1]*c[1]) / N[2]

    C =  np.array([c[0],c[1],x])

    
    p4 = p1 + C

    return p4

def interpolateEle2(p1e=10,p2e=5,p3e=5,p4e=0,pxc=[5,5]):
    x = np.array([0,10])
    y = np.array( [0,10])
    z = np.array([[p1e,p3e],[p2e,p4e]])
    p1=pxc[0]
    p2=pxc[1]
    
    f = intp.RectBivariateSpline(x,y,z,kx=1, ky=1, s=0)
    return f(p1,p2)[0][0]
    

def getDTMFile(east,north):
    try:
        dtmfile = getDTMdict()
    
        for key in dtmfile:
            if north>=dtmfile[key][1] and north<=dtmfile[key][1]+50000:
                if east>=dtmfile[key][0] and east<=dtmfile[key][0]+50000:
                    return [key,int(dtmfile[key][0]),int(dtmfile[key][1])]
    except: 
        raise Exception('DTM file not available')

def getDTMdict():
    dtmfile = dict()
    dtmfile['6404_3_10m_z32.dem'] = [399800,6399900]
    dtmfile['6404_4_10m_z32.dem'] = [399800,6449800]
    
    dtmfile['7005_2_10m_z32.dem'] = [549800,6999800]
    
    dtmfile['6503_3_10m_z32.dem'] = [299800,6499800]
    dtmfile['6903_1_10m_z32.dem'] = [349800,6949800]
    dtmfile['6904_4_10m_z32.dem'] = [399795,6949795]
    
    dtmfile['6505_4_10m_z32.dem'] = [499800,6549800]
    dtmfile['6504_1_10m_z32.dem'] = [449800,6549800]
    dtmfile['6604_2_10m_z32.dem'] = [449800,6599800]
    dtmfile['6605_3_10m_z32.dem'] = [499800,6599800]
    dtmfile['6603_2_10m_z32.dem'] = [349800,6599800]
    
    dtmfile['6506_1_10m_z32.dem'] = [649800,6549800]
    dtmfile['6506_2_10m_z32.dem'] = [649800,6503000]
    dtmfile['6506_3_10m_z32.dem'] = [599800,6503000]
    dtmfile['6506_4_10m_z32.dem'] = [599800,6549800]
    return dtmfile

def hasDTMFile(minEast, minNorth,maxEast,maxNorth):
    dtmfile = getDTMdict()
    
    dtm = getDTMFile(minEast, minNorth)
    
    if dtm != -1:
        if (maxEast-50000)< dtm[1] and (maxNorth-50000)<dtm[2]:
            return True
    return False
 
if __name__ == "__main__":
    readFile('6506_3_10m_z32.dem')       


