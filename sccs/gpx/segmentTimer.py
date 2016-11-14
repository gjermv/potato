'''
Created on 27 Jul 2016

@author: gjermund.vingerhagen
'''

import numpy as np
import matplotlib.pyplot as plt
import gpxtricks
import utmconverter
import pandas as pd
import xml.etree.ElementTree as ET
import glob
import os.path
import pickle
import datetime as dt


class TrackSegment():
    def __init__(self,name):
        self.name = name
        self.crosslines = []
        self.laps = [] # Seems like a temporary timedelta thing used in segmentResults...
        self.segmentResults = []
        self.counter = 0
        self.starttime = 0
        self.besttime = 99999999
        self.bestrun = 'NA'
        self.trkdistance = [0]
    
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
            
            self.trackSegDistance(LL)    
            p1 = perpLine((LL[0][0],LL[0][1]),(LL[0][0],LL[0][1]),(LL[1][0],LL[1][1]))
            self.addCrossLine(CrossLine(p1[0],p1[1],p1[2],p1[3],'StartLine'))
            
            for i,p in enumerate(LL[1:-1]):
                p = (perpLine((LL[i+1][0],LL[i+1][1]),(LL[i][0],LL[i][1]),(LL[i+2][0],LL[i+2][1])))
                self.addCrossLine(CrossLine(p[0],p[1],p[2],p[3],'Split{}'.format(i+1)))
            
            g = len(LL)-1
            ps = perpLine((LL[g][0],LL[g][1]),(LL[g-1][0],LL[g-1][1]),(LL[g][0],LL[g][1]))
            self.addCrossLine(CrossLine(ps[0],ps[1],ps[2],ps[3],'Goalline'))
            break

    def trackSegDistance(self,latlonList):
        p1 = latlonList[0]
        d =[0]
        dm = 0
        for p2 in latlonList[1:]:
            dm += utmconverter.haversine(p1[1],p1[0],p2[1],p2[0])
            d.append(round(dm,2))
            p1 = p2
        self.trkdistance = d  
        print('TrackDist',d)
        

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
            run = SegmentResult(str(self.starttime),self.laps)
            self.segmentResults.append(run)
            self.resetCounter()
        return True  
        
    def resetCounter(self):
        self.starttime = 0
        self.counter = 0
        self.laps = []
        
    def reverse(self):
        """ Creates a new TrackSegment in the reverse direction. """
        revTrk = TrackSegment(self.name+'-reverse')
        revTrk.trkdistance = []
        m = max(self.trkdistance)
        for d in self.trkdistance[::-1]:
            print(round(m-d,2))
            revTrk.trkdistance.append(round(m-d,2))
        
        for cl in self.crosslines[::-1]:
            revTrk.addCrossLine(cl.reverse())
        return revTrk
    
    def runNewPoint(self,filename,gps1,gps2,hasStarted=False):
        startpoint1,startpoint2 = self.getStartLine()
        currpoint1,currpoint2 = self.getCurrentCrossline()
        a0 = lineIntersection(gps1, gps2, startpoint1, startpoint2)
        c0 = lineIntersection(gps1, gps2, currpoint1, currpoint2)
        a1 = False
        c1 = False
        
        if a0:
            a1 = checkIntersection(gps1, gps2, startpoint1, startpoint2, a0)
            
        if c0:
            c1 = checkIntersection(gps1, gps2, currpoint1, currpoint2, c0)
        
        if not hasStarted:
            if (a1 and c1 and self.counter == 0):
                self.starttime = calculateCrossingTime(gps1, gps2, a1)
                self.laps.append(self.starttime-self.starttime)
                print("a1 and c1 and self.counter == 0",self.starttime,self.name)
                self.nextCrossline()
                self.runNewPoint(filename,gps1,gps2,True)
                
            
            elif (a1 and c1 and self.counter != 0):
                time = calculateCrossingTime(gps1, gps2, c1)
                self.laps.append(time-self.starttime)
                print("a1 and c1 and self.counter != 0".format(self.counter),time-self.starttime,self.name)
                self.nextCrossline()
                self.runNewPoint(filename,gps1,gps2,True)
                

            elif (c1):
                time = calculateCrossingTime(gps1, gps2, c1)
                self.laps.append(time-self.starttime)
                print("c1".format(self.counter),time-self.starttime,self.name)
                self.nextCrossline()
                self.runNewPoint(filename,gps1,gps2,True)
    

            elif(a1):
                self.resetCounter()
                self.starttime = calculateCrossingTime(gps1, gps2, a1)
                self.laps.append(self.starttime-self.starttime)
                self.nextCrossline()
                self.runNewPoint(filename,gps1,gps2,True)
                                
            else:
                return False

        if hasStarted:
            if c1:
                time = calculateCrossingTime(gps1, gps2, c1)
                self.laps.append(time-self.starttime)
                self.nextCrossline()
                self.runNewPoint(filename,gps1,gps2,True)
        
        return False
        
    def prettyPrintResults(self):
        for run in self.segmentResults:
            run.prettyPrint(max(self.trkdistance))

    def prettyPrintInfo(self,filename):
        sortRun = sorted(self.segmentResults, key=lambda x: max(x.laptimes))
        date_str = filename.split(' ')[0]
        flag = False
        if len(sortRun) < 1:
            return 123
        
        l = len(sortRun)
        besttime = sortRun[0].getFinishTime()
        info_str = "{} - {:2}/{:2} Time: {} {: >10.2f} sec\n".format(sortRun[0].name,1,l,sortRun[0].getFinishTime(),(besttime-sortRun[0].getFinishTime()).total_seconds())
        
        for i,run in enumerate(sortRun):
            if date_str in run.name:
                flag = True
                info_str += "{} - {:2}/{:2} Time: {} {: >10.2f} sec\n".format(run.name,i+1,l,run.getFinishTime(),(besttime-run.getFinishTime()).total_seconds())
        if flag:               
            return info_str              
        else:
            return 124
    def prettyPrintBestResult(self):
        bestrun = self.segmentResults[0]
        for run in self.segmentResults[1:]:
            if run.getFinishTime() <bestrun.getFinishTime():
                bestrun = run
        
        print(bestrun.name,bestrun.getFinishTime())
            
    def prettyPlotResults(self):
        sortRun = sorted(self.segmentResults, key=lambda x: max(x.laptimes))
        
        if len(sortRun) < 1:
            print("Return code 123: No data to display")
            return 123
        
        fastestRun = sortRun[0]
        fig,ax = plt.subplots()
        plt.title(self.name,fontsize=18)
        for run in sortRun:
            run.prettyPlot(ax,fastestRun,self.trkdistance)
        
        plt.legend(loc=2,fontsize=11)   
        plt.show()
 
    def prettyPlotResults2(self):
        sortRun = self.segmentResults
        
        if len(sortRun) < 1:
            print("Return code 123: No data to display")
            return 123
        
        fastestRun = sortRun[0]
        fig,ax = plt.subplots()
        plt.title(self.name,fontsize=18)
        
        for run in sortRun:
            run.prettyPlot2(ax)
        
        plt.show()
 
        
    def save(self,activity):
        pickle.dump(self, open( "C:\\python\\testdata\\gpxx4\\segments\\{0}\\{1}.p".format(activity,self.name), "wb" ) )
    
    
      
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
    
    def prettyPrint(self,distance):
        dt = max(self.laptimes).components
        timesec = dt[0]*3600*24+ dt[1]*3600+dt[2]*60 + dt[3]+dt[4]/1000
        avg = distance/timesec*3.6
        s = '{} Avg: {:.2f} '.format(self.name.split('.')[0],avg)
        dt  = []
        for laptime in self.laptimes:
            dt = laptime#.components
            #z = dt[0]*3600*24+ dt[1]*3600+dt[2]*60 + dt[3]+dt[4]/1000
            s += '- {} '.format(str(dt).replace('0 days ',''))
        print(s)

    def prettyPlot(self,ax,fst,trkdist):
        dt  = []
        DT1 = []
        DT2 = []

        for i,laptime in enumerate(self.laptimes):
            dt = laptime.components
            dt2 = fst.laptimes[i].components
            DT1.append(dt[0]*3600*24+ dt[1]*3600+dt[2]*60 + dt[3]+dt[4]/1000)
            DT2.append(dt2[0]*3600*24+ dt2[1]*3600+dt2[2]*60 + dt2[3]+dt2[4]/1000)
            
        ltSec = np.array(DT1)-np.array(DT2)
        ax.plot(trkdist,ltSec,label=self.name)
        return ax

    def prettyPlot2(self,ax):
        x = dt.datetime.strptime(self.name ,"%Y-%m-%d %H:%M:%S")
        y =self.getFinishTime()

        ax.scatter(x,y.total_seconds())  
        return ax

    
    def addLap(self,laptime):
        self.laptimes.append(laptime)
    
    def getFinishTime(self):
        #self.prettyPrint(100)
        return max(self.laptimes)


       
def lineIntersection(s1,s2,u1,u2):
    """ calculates Line intersection where Line 1 is defined by point s1,s2 and line 2 by u1,u2 """
    S = np.array(s2[:2])-np.array(s1[:2])
    U = np.array(u2)-np.array(u1)
    
    if S[0] == 0 or U[0] == 0:
        #print('Error: Lines are vertical. No solution found (yet)',s1,s2,u1,u2)
        return False        
    
    Sa = S[1]/S[0]
    Ua = U[1]/U[0]
    
    Sb = s1[1]-Sa*s1[0] 
    Ub = u1[1]-Ua*u1[0]
    
    if Sa == Ua:
        print('Error: Lines are parallelle. No solution found')
        return False
    
    elif Sa-Ua != 0:
        x = (Ub-Sb)/(Sa-Ua)
        y = Sa*x+Sb
        return (x,y)
    
    else:
        "Error: Something else went wrong. Possibly precision error "
        return False
        
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
    
    perpVect = perpVect/l*40
    
    p_left = [ex,nx]+perpVect
    p_right = [ex,nx]+perpVect*(-1)
    
    lat1,lon1 = utmconverter.to_latlon(p_left[0],p_left[1],zone_number,northern=True)
    lat2,lon2 = utmconverter.to_latlon(p_right[0],p_right[1],zone_number,northern=True)
    return (lat1,lon1,lat2,lon2)
  
def segmentAnalyzer(filename,segList):
    """ Reset for new file"""
    for seg in segList:
        seg.resetCounter()

    try:
        df = gpxtricks.GPXtoDataFrame(filename)
    except:
        df = gpxtricks.TCXtoDataFrame(filename)
    
    p1 = list(df.iloc[0][['lat','lon','time']])
    

    for row in df.iterrows():
        p2 = [row[1]['lat'],row[1]['lon'],row[1]['time']]
        if p2[0] != 0.0 and p2[1] != 0.0:
            for seg in segList:
                seg.runNewPoint(filename,p1,p2)
            p1 = p2


def getkmlSegmentList(activity=None):
    allSegments = set()
    
    activitySegments = set()
    for kml_file in glob.glob("C:\\python\\testdata\\gpxx4\\segments\\*.kml"):
        filename = os.path.basename(kml_file).replace('.kml','')
        allSegments.add(filename)
    
    for p_file in glob.glob("C:\\python\\testdata\\gpxx4\\segments\\{}\\*.p".format(activity)):
        filename = os.path.basename(p_file).replace('.p','')
        activitySegments.add(filename)
    
    newSegs = allSegments.difference(activitySegments)

    return [newSegs,activitySegments]
    
def getSegmentResults(filename,originalfile,activity):
    myActivity = activity
    myInfo = ''
    
    for segname in getkmlSegmentList(myActivity)[1]:
        trkSeg = pickle.load( open( "C:\\python\\testdata\\gpxx4\\segments\\{}\\{}.p".format(myActivity,segname), "rb" ) )
        segmentAnalyzer(originalfile, [trkSeg])
        seginfo = trkSeg.prettyPrintInfo(filename)
        if seginfo == 123:
            pass
        elif seginfo == 124:
            pass
        else:
            print(trkSeg.name,max(trkSeg.trkdistance))
            myInfo += '\n****' + trkSeg.name + ' ' + str(max(trkSeg.trkdistance))+'\n'
            myInfo += seginfo
    
    print("MyInfo",myInfo)
    return myInfo
     
if __name__ == "__main__":
    # Create a tracksegment
    myActivity = 'Running'
    seglist = []
    
    newkmlfiles = getkmlSegmentList(myActivity)[0]
    
    for segname in newkmlfiles:
        print(segname)
        trkSeg = TrackSegment(segname)
        trkSeg.createSegmentfromKML('C:\\python\\testdata\\gpxx4\\segments\\{}.kml'.format(segname))
        seglist.append(trkSeg)
    
    df = pd.read_csv('C:\\python\\testdata\\gpxx4\\Activity_Summary2.csv',parse_dates=[2], infer_datetime_format=True,encoding='latin-1')
    df_time = df[df['dateandtime']>'2010-01-01']
    df_act = df_time[df_time['activity']==myActivity]
    filelist = list(df_act['filename'])

    
    if len(seglist) > 0:
        for item in filelist:
            print('****',item,'****')      
            segmentAnalyzer('C:\\python\\testdata\\gpxx4\\files\\{}'.format(item),seglist)
    else:
        print("No new segments to analyse")
    
    for segname in seglist:
        segname.save(activity=myActivity)
    

    for segname in getkmlSegmentList(myActivity)[1]:

        trkSeg = pickle.load( open( "C:\\python\\testdata\\gpxx4\\segments\\{}\\{}.p".format(myActivity,segname), "rb" ) )
        
        seginfo = trkSeg.prettyPrintInfo('2013-10-05 0930 Parkrun.gpx')
        if seginfo == 123:
            pass
        elif seginfo == 124:
            pass
        else:
            print(trkSeg.name,max(trkSeg.trkdistance))
            print(seginfo)
    
        

    


