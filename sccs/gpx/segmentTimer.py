'''
Created on 27 Jul 2016

@author: gjermund.vingerhagen
'''

import numpy as np
import matplotlib.pyplot as plt
import gpxtricks
import utmconverter
import xml.etree.ElementTree as ET
import glob


class TrackSegment():
    def __init__(self,name):
        self.name = name
        self.crosslines = []
        self.laps = []
        self.runs = []
        self.counter = 0
        self.starttime = 0
        self.besttime = 99999999
        self.bestrun = 'NA'
        self.distance = [0]

    def createSegmentfromKML(self,filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        ns = '{http://www.opengis.net/kml/2.2}'
        # Reads throught the file, but breaks after the first linestring. 
        for placemark in root.iter(ns+'Placemark'):
            lstring = placemark.find(ns+'LineString')
            kmlcoord = lstring.find(ns+'coordinates').text.strip()
            kmlcoordlist = kmlcoord.split(' ')
            LL = []
            
            for item in kmlcoordlist:
                kmlcoorditem = item.split(',')
                lat = float(kmlcoorditem[1])
                lon = float(kmlcoorditem[0])
                LL.append([lat,lon])
            
                
            p1 = perpLine((LL[0][0],LL[0][1]),(LL[0][0],LL[0][1]),(LL[1][0],LL[1][1]))
            self.addCrossLine(CrossLine(p1[0],p1[1],p1[2],p1[3],'StartLine'))
            
            for i,p in enumerate(LL[1:-1]):
                p = (perpLine((LL[i+1][0],LL[i+1][1]),(LL[i][0],LL[i][1]),(LL[i+2][0],LL[i+2][1])))
                self.addCrossLine(CrossLine(p[0],p[1],p[2],p[3],'Split{}'.format(i+1)))
            
            g = len(LL)-1
            ps = perpLine((LL[g][0],LL[g][1]),(LL[g-1][0],LL[g-1][1]),(LL[g][0],LL[g][1]))
            self.addCrossLine(CrossLine(ps[0],ps[1],ps[2],ps[3],'Goalline'))
            break

    def plotSegments(self):
        fig,ax = plt.subplots()
        for l in self.crosslines:
            l.plotLine(ax)
        plt.show()
    
    def addCrossLine(self,cl):
        self.crosslines.append(cl)
        
    def printkmlPlacemarks(self):
        for cl in self.crosslines:
            cl.kmlPlacemark()

    def getCurrentCrossline(self):
        cl = self.crosslines[self.counter]
        return cl.getLatLonPoint1(),cl.getLatLonPoint2()

    def getStartLine(self):
        cl = self.crosslines[0]
        return cl.getLatLonPoint1(),cl.getLatLonPoint2()
    
    def nextCrossline(self):
        self.counter += 1
        
        if self.counter == len(self.crosslines):
            self.counter = 0
            run = SegmentResult(str(self.starttime),self.laps)
            self.runs.append(run)
        return True  
        
    def resetCounter(self):
        self.counter = 0
        self.laps = []
        
    def reverse(self):
        """ Creates a new TrackSegment in the reverse direction. """
        revTrk = TrackSegment(self.name+'-reverse')
        for cl in self.crosslines[::-1]:
            revTrk.addCrossLine(cl.reverse())
        return revTrk

    def runNewPoint(self,filename,gps1,gps2):
        startpoint1,startpoint2 = self.getStartLine()
        
        
        a0 = lineIntersection(gps1, gps2, startpoint1, startpoint2)
        
        if a0:
            a1 = checkIntersection(gps1, gps2, startpoint1, startpoint2, a0)
            if a1:
                self.resetCounter()
                self.nextCrossline()
                self.starttime = calculateCrossingTime(gps1, gps2, a1)
                self.laps.append(self.starttime-self.starttime)
                print("StartTime",self.starttime)
                
                while self.runNewPoint2(filename,gps1,gps2):
                    continue
                
                return True
        
        self.runNewPoint2(filename,gps1,gps2)
        return False
    
    def runNewPoint2(self,filename,gps1,gps2):
        currpoint1,currpoint2 = self.getCurrentCrossline()
        ac = lineIntersection(gps1, gps2, currpoint1, currpoint2)
        if ac:
            a1 = checkIntersection(gps1, gps2, currpoint1, currpoint2, ac)
            if a1:
                self.nextCrossline()
                time = calculateCrossingTime(gps1, gps2, a1)
                self.laps.append(time-self.starttime)
                
                while self.runNewPoint2(filename,gps1,gps2):
                    continue
                
                return True
        
        return False
                    
    def prettyPrintResults(self):
        
        
        for run in self.runs:
            run.prettyPrint()

    def prettyPlotResults(self):
        sortRun = sorted(self.runs, key=lambda x: max(x.laptimes))
        fastestRun = sortRun[0]
        fig,ax = plt.subplots()
        
        for run in sortRun:
            run.prettyPlot(ax,fastestRun)
        
        plt.legend(loc=2,fontsize=11)   
        plt.show()
          
class CrossLine():
    def __init__(self,lat1,lon1,lat2,lon2,name='Unnamed',t=1):
        self.name = name
        self.x1 = lon1
        self.y1 = lat1
        self.x2 = lon2
        self.y2 = lat2
        self.t = t  #Type 1= Normal, 0=Skip
    
    def __str__(self):
        return 'CL name: {} Coord: ({},{}),({},{}) - {}'.format(self.name,self.y1,self.x1,self.y2,self.x1,self.getLength())
    
    def kmlPlacemark(self):
        s = """    <Placemark>
        <name>CrossLine{}</name>
        <styleUrl>#m_ylw-pushpin</styleUrl>
        <LineString>
            <tessellate>1</tessellate>
            <coordinates>
                {},{},0 {},{},0
            </coordinates>
        </LineString>
    </Placemark>""".format(self.name,self.x1,self.y1,self.x2,self.y2)
        print(s)
    
    def getLength(self):
        l1  = utmconverter.haversine(self.x1, self.y1, self.x2, self.y2)
        l2 = round(l1,2)
        return l2
    
    def getVector(self):
        v = np.array([self.x2-self.x1,self.y2-self.y1])
        return v
    
    def getLatLonPoints(self):
        return np.array([self.y1,self.x1,self.y2,self.x2])

    def getLatLonPoint1(self):
        return np.array([self.y1,self.x1])

    def getLatLonPoint2(self):
        return np.array([self.y2,self.x2])
    
    def plotLine(self,ax):
        ax.plot([self.x1,self.x2],[self.y1,self.y2],color='red')
    
    def reverse(self):
        return CrossLine(self.y2,self.x2,self.y1,self.x1,self.name+'-rev')          


class SegmentResult():
    def __init__(self,name,laps=[]):
        self.name =  name.split('.')[0]
        self.laptimes = laps
    
        
    def prettyPrint(self):
        s = '{}: '.format(self.name.split('.')[0])
        dt  = []
        for laptime in self.laptimes:
            dt = laptime#.components
            #z = dt[0]*3600*24+ dt[1]*3600+dt[2]*60 + dt[3]+dt[4]/1000
            s += '- {} '.format(str(dt).replace('0 days ',''))
        print(s)

    def prettyPlot(self,ax,fst):
        dt  = []
        DT1 = []
        DT2 = []
        for i,laptime in enumerate(self.laptimes):
            dt = laptime.components
            dt2 = fst.laptimes[i].components
            DT1.append(dt[0]*3600*24+ dt[1]*3600+dt[2]*60 + dt[3]+dt[4]/1000)
            DT2.append(dt2[0]*3600*24+ dt2[1]*3600+dt2[2]*60 + dt2[3]+dt2[4]/1000)
            
        ltSec = np.array(DT1)-np.array(DT2)
        ax.plot(DT2,ltSec,label=self.name)
        return ax
    
    def addLap(self,laptime):
        self.laptimes.append(laptime)
    
    def getFinishTime(self):
        self.prettyPrint()
        return max(self.laptimes)
       
def lineIntersection(s1,s2,u1,u2):
    """ calculates Line intersection where Line 1 is defined by point s1,s2 and line 2 by u1,u2 """
    S = np.array(s2[:2])-np.array(s1[:2])
    U = np.array(u2)-np.array(u1)
    
    if S[0] == 0 or U[0] == 0:
        print('Error: Lines are vertical. No solution found (yet)',s1,s2,u1,u2)
        return False        
    
    Sa = S[1]/S[0]
    Ua = U[1]/U[0]
    
    Sb = s1[1]-Sa*s1[0] 
    Ub = u1[1]-Ua*u1[0]
    
    
    if Sa == Ua:
        print('Error: Lines are parallelle. No solution found')
        return False
    
    if Sa-Ua != 0:
        x = (Ub-Sb)/(Sa-Ua)
        y = Sa*x+Sb
        return (x,y)
        
def checkIntersection(s1,s2,u1,u2,cx):  
    x1min = min(s1[0],s2[0])
    x1max = max(s1[0],s2[0])
    x2min = min(u1[0],u2[0])
    x2max = max(u1[0],u2[0])
    
    if cx[0]>x1min and cx[0]<x1max:
        if cx[0]>x2min and cx[0]<x2max:
            if checkDirection(s1, s2, u1, u2):
                return cx
        
    return False

def checkDirection(s1,s2,u1,u2):
    S = np.array(s2[:2])-np.array(s1[:2])
    U = np.array(u2)-np.array(u1)   
    
    cross = np.cross(S,U)

    if cross < 0:
        return False
    else:
        return True

def plotCrossingPoint(p1,p2,q1,q2,a):
    plt.plot([p1[0],p2[0]],[p1[1],p2[1]])
    plt.plot([q1[0],q2[0]],[q1[1],q2[1]])
    plt.scatter(a[0],a[1])
    plt.show()    

def calculateCrossingTime(p1,p2,cx):
    pToCx = np.array(cx[:2])-np.array(p1[:2])
    pToP = np.array(p2[:2])-np.array(p1[:2])
    l_pToCx = np.sqrt(pToCx[0]**2+pToCx[1]**2)
    l_pToP = np.sqrt(pToP[0]**2+pToP[1]**2)
    delta = l_pToCx/l_pToP
    t1 = p1[2]
    t2 =  p2[2]
    tdiff = (t2-t1)*delta
    tn = t1+tdiff
    return tn
 
def perpLine(pointx,point1,point2,):
    px =np.array((float(pointx[0]),float(pointx[1])))
    p1 =np.array((float(point1[0]),float(point1[1])))
    p2 =np.array((float(point2[0]),float(point2[1])))
    #print(p1,p2)
    ex, nx, zone_number, zone_letter = utmconverter.from_latlon(px[0],px[1])
    e1, n1, zn, zl = utmconverter.from_latlon(p1[0],p1[1],zone_number)
    e2, n2, zn, zl = utmconverter.from_latlon(p2[0],p2[1],zone_number)
    
    vect = np.array((e2-e1,n2-n1))
    perpVect = np.array((-vect[1],vect[0]))
    l = np.sqrt(perpVect[0]**2+perpVect[1]**2)
    
    perpVect = perpVect/l*25
    
    p_left = [ex,nx]+perpVect
    p_right = [ex,nx]+perpVect*(-1)
    
    lat1,lon1 = utmconverter.to_latlon(p_left[0],p_left[1],zone_number,northern=True)
    lat2,lon2 = utmconverter.to_latlon(p_right[0],p_right[1],zone_number,northern=True)
    return (lat1,lon1,lat2,lon2)
  
def segmentAnalyzer(filename,trkseg):
    try:
        df = gpxtricks.GPXtoDataFrame(filename)
    except:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    p1 = list(df.iloc[0][['lat','lon','time']])
    
    for row in df.iterrows():
        p2 = [row[1]['lat'],row[1]['lon'],row[1]['time']]
        trkseg.runNewPoint('testfile',p1,p2)
        p1 = p2
        
    #===========================================================================
    # trkseg.resetCounter()
    # seg = 0
    # times = list()
    # dtimes = [0]
    #===========================================================================
    #===========================================================================
    # for row in df.iterrows():
    #     p2 = [row[1]['lat'],row[1]['lon'],row[1]['time']]
    #     
    #     q1,q2 = trkseg.getCurrentCrossline()
    #     
    #     a = lineIntersection(p1,p2,q1,q2)
    #     
    #     if a:
    #         a = checkIntersection(p1,p2,q1,q2, a)
    #     
    #     if a:
    #         times.append(calculateCrossingTime(p1, p2, a))
    #         #plotCrossingPoint(p1, p2, q1, q2, a)
    #         seg += 1
    #         
    #         if not trkseg.nextCrossline():
    #             break
    #     
    #     p1 = p2
    # 
    # if len(times) != len(trkseg.crosslines):
    #     print('Error: All points not passed.')
    # 
    # else:
    #     for i in range(len(times)-1):
    #         #print((times[i+1]-times[0]))
    #         dt = (times[i+1]-times[0]).components
    #         T = dt[0]*3600*24+ dt[1]*3600+dt[2]*60+dt[3]+dt[4]/1000
    #         
    #         dtimes.append(T)
    #     
    #     trkseg.runs.append([max(dtimes),filename,dtimes])
    # 
    #     r = sorted(trkSeg.runs)
    #     a= r[0][2]
    #     print(a)
    # 
    # 
    #     for runs in r:
    #         plt.plot(np.array(a)/60,(np.array(runs[2])-np.array(r[0][2])),color='blue')
    #     
    #     plt.plot(np.array(a)/60,(np.array(r[0][2])-np.array(r[0][2])),'-.',color='yellow',lw=2)
    #     plt.plot(np.array(a)/60,(np.array(dtimes)-np.array(r[0][2])),color='red',lw=2)
    #     plt.show()
    #===========================================================================
  
trkSeg = TrackSegment('recground')
trkSeg.createSegmentfromKML('C:\\python\\testdata\\gpxx4\\segments\\parkrunup.kml')
trkSeg.printkmlPlacemarks()

#filelist = ['2015-11-15 1001 The Coppice.gpx',]
                 
 
for item in glob.glob('C:\\python\\testdata\\gpxx4\\files\\2014-04-26*ParkRun*'):
    print('****',item,'****')    
    #segmentAnalyzer('C:\\python\\testdata\\gpxx4\\files\\{}'.format(item),trkSeg)   
    segmentAnalyzer('{}'.format(item),trkSeg)




#trkSeg.prettyPlotResults()
trkSeg.prettyPrintResults()
trkSeg.prettyPlotResults()

#===============================================================================
# r = sorted(trkSeg.runs)
#  
# a= r[0][2]
# print(a)
#  
#  
# for runs in r:
#     plt.plot(np.array(a)/60,(np.array(runs[2])-np.array(r[0][2])),'.-',)
#      
# plt.show()
#===============================================================================
