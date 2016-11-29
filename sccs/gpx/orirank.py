import ftplib
import urllib
from cryptography.fernet import Fernet
from bs4 import BeautifulSoup
import urllib.request
from numpy import rank
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import collections
from operator import attrgetter
from datetime import datetime, timedelta
import hashlib
import pickle
import os.path


runners = dict()
eventsDict = dict()
courseDict = dict()
event = collections.namedtuple('shortEvent', 'eventName, eventDate, eventPoints')
fullEvent = collections.namedtuple('fullEvent', 'eventName, eventDate, eventCourse, eventTime, eventPos, eventLength, eventClimb, eventControls, eventPoints')
raceResult = collections.namedtuple('raceResult', 'pos,name,club,gender,yob,time,points')
shortResult = collections.namedtuple('shortResult', 'courseId,pos,time,points') 



class Runner():
    def __init__(self,name,club,yob,mf,bofPos=False,bofPoints=False):
        self.name = name
        self.club = club
        self.yob = yob
        self.mf = mf

        self.events = []
        
        if bofPos:
            self.bofPos = int(bofPos)
        if bofPoints:
            self.bofPoints = int(bofPoints)
        
    def addEvent(self,courseId,rResult):
        try:
            int_points = int(rResult.points)
        except:
            int_points = 0 
        try:
            int_pos = int(rResult.pos)
        except:
            int_pos = 99999    
        try:
            t = rResult.time.split(':')
            d_time = timedelta(hours=t[0],minutes=t[1],seconds = t[2])
        except:
            d_time = rResult.time
        
        self.events.append(shortResult(courseId,int_pos,d_time,int_points))

        ## Update bofPoints
        
    def printEvents(self):
        numberOfEvents = 0
        numberOfRankingEvents = 0
        numberOfNoPosition = 0
        for ev in self.events[:]:
            #print(eventsDict[ev.courseId[0]].eName,',',ev.pos,',',ev.time,',',ev.points)
            print(ev.courseId,',',self.name)
            
            
    def getRankingPoints(self):
        sl = sorted(self.events,key=attrgetter('points'),reverse=True)
        su = 0
        sx = 0
        for r in sl[:6]:
            date = datetime.strftime(eventsDict[r.courseId[0]].eDate,'"%d %m %Y')
            print(date,eventsDict[r.courseId[0]].eName,r.points,r.courseId)
            if r.points > 0:
                su += r.points
                sx += 1
        print('Average = {}/{}'.format(su/sx,sx))
                  

class Event():
    def __init__(self):
        self.eID = None
        self.eDate = None
        self.eRegion = None
        self.eClub = None
        self.eLevel = None
        self.eName = None
        self.eVenue = None
        self.eCourses = []
        
    def updateEventFromHTML(self,bsRes):
        self.eDate = datetime.strptime(bsRes[0].text.strip(),"%d %b %Y")
        self.eRegion = bsRes[1].text.strip()
        self.eClub = bsRes[2].text.strip()
        self.eLevel = bsRes[3].text.strip()
        self.eName = bsRes[4].text.strip()
        self.eVenue = bsRes[5].text.strip()
        
        try:
            link = bsRes[6].a['href'].strip().split('eday=')
            if len(link) == 2:
                self.eID = int(link[1])
            else:
                self.eID = False
        except:
            print("No EventResults",self.eDate,self.eRegion,self.eName)
    
    def hasEventID(self):
        return self.eID
    
class EventCourse():
    def __init__(self,courseId=None):
        self.cId  = None
        self.cName = 'No name'
        self.cLength = 0
        self.cClimb = 0
        self.cControls = 0
        self.cParticipants = None
        self.cbofParticipants = None
        self.cDisqualified = None

    def updateCourseFromHTML(self,cId,bsRes):
        self.cId = cId
        self.parseCourseDesc(bsRes.text.strip())

    def updateCourseFromTXT(self,cId,txtLine):
        self.cId = cId
        resstr = txtLine.split(';')
        self.cName = resstr[0]
        self.cLength  = resstr[1]
        self.cClimb = resstr[2]
        self.cControls = resstr[3]
          
    def parseCourseDesc(self,desc):
        a1 = desc.rfind('(')
        self.cName = desc[:a1].strip()
        s2 = desc[a1+1:-1].split(',')
        
        for sub in s2:
            if 'length:' in sub:
                self.cLength = float(sub.replace('length:','').replace('km','').strip())
            elif 'climb:' in sub:
                self.cClimb = int(sub.replace('climb:','').replace('m','').strip())
            elif 'controls' in sub:
                self.cControls = int(sub.replace('controls','').strip())

       
class Result():
    def __init__(self):
        self.rCourseID = None
        self.rPos = None
        self.rTime = None
        self.rPoints = None
        
        
def hashNumber(name,club,year):
    hash_object = hashlib.md5(("{}{}".format(name,club).encode('utf-8')))
    hashnr = hash_object.hexdigest()
    return hashnr
        
def readRankingWebpages(local = True):
    for i in range(0,53):
        print("Page",i)
        
        if not local:
            response = urllib.request.urlopen("https://www.britishorienteering.org.uk/index.php?page={}&pagesize=100&pg=rankings&pg=rankings&results=0".format(str(i)))
        else:
            response = open('C:\\python\\testdata\\BTRANK_{}.html'.format(str(i)),'r')
        
        
        soup = BeautifulSoup(response.read(), 'html.parser')
        response.close()
        ## Find table with runners
        for tr in soup.tbody.find_all('tr')[:-1]:          
            td = tr.find_all('td')
            per = dict()
            per['pos'] = td[0].text.split(' ')[0] 
            
            try:
                per['dpos'] = td[0].text.split(' ')[1]
            except:
                per['dpos'] = 0
                
            per['name'] = td[1].text.strip()
            per['club'] = td[2].text.strip()
            per['yob'] = td[3].text.strip()
            per['mf'] = td[4].text.strip()
            per['points'] = td[5].text.strip()
            
            abbr = td[6].find_all('abbr')
            #name,club,yob,pos,points
            newRunner = Runner(per['name'],per['club'],per['yob'],per['mf'],per['pos'],per['points'])
            
            for race in abbr:
                eventName = '-'.join(race['title'].split('-'))[:-1]
                evtDate =  datetime.strptime(race['title'].split('-')[-1],' %d/%m/%Y')    
                _event = event(eventName,evtDate,race.text)
                newRunner.addEvent(_event)
                
            hashnr = hashNumber(per['name'], per['club'], per['yob'])
            
            if  hashnr in runners:
                print(per['name'],per['club'],'already There')
            else:
                runners[hashnr] = newRunner

def readFabiabFour(url):
    courses = {'Black','Brown','Blue','Green'}
    response = urllib.request.urlopen(url)   
    soup = BeautifulSoup(str(response.read()).replace('\\n','').replace('\\r','').replace('\\t',''), 'html.parser')
    response.close()
    print("Soup,",len(soup.find_all('table')[3]))
    courseDict = dict()
    for i,tr in enumerate(soup.find_all('b')):
        if tr.text in courses:
            r = int(tr.nextSibling.replace('(','').replace(')',''))
            par = tr.parent.parent.nextSibling
            courseDict[tr.text] = []
            for i in range(r):
                
                p1 = par.find_all('td')
                name = p1[2].text.strip()
                club = p1[4].text.strip()
                try:
                    courseDict[tr.text].append(runners[hashNumber(name, club, 2000)])
                except:
                    print(tr.text,name,"No rankingpoints")
        
                par = par.nextSibling
    return courseDict

def parseEventWebPage(local=True):
    eventList = list()
    eventDict = dict()
    
    for i in range(10):
        url = 'https://www.britishorienteering.org.uk/index.php?bSearch=1&evt_name=&evt_postcode=&evt_radius=0&evt_level=0&evt_type=0&event_club=0&evt_start_d=0&evt_start_m=0&evt_start_y=0&evt_end_d=0&evt_end_m=0&evt_end_y=0&evt_assoc=0&evt_start=0&evt_end=1479827802&&perpage=100&pg=results&pagi=res_list&page={}'.format(str(i))
        
        if not local:
            response = urllib.request.urlopen(url)
            f = open('C:\\python\\testdata\\bori\\BTMAINRES_{}.html'.format(str(i)),'w')
            soup = BeautifulSoup(response.read(), 'html.parser')
            f.write(soup.prettify())
            f.close()
            print('Saved file: C:\\python\\testdata\\bori\\BTMAINRES_{}.html'.format(str(i)))
        
        else:
            print("local file...",i)
            response = open('C:\\python\\testdata\\bori\\BTMAINRES_{}.html'.format(str(i)),'r')
    
        soup = BeautifulSoup(response.read(), 'html.parser')
        
        for table in soup.find_all('table'):
            for tr in table.find_all('tr')[1:]:
                newEvent = Event()
                newEvent.updateEventFromHTML(tr.find_all('td'))
                if newEvent.hasEventID():
                    eventDict[newEvent.eID] = newEvent
                    
                td = tr.find_all('td')
                event = dict()
                event['eDate'] = datetime.strptime(td[0].text.strip(),"%d %b %Y")
                event['eRegion'] = td[1].text.strip()
                event['eClub'] = td[2].text.strip()
                event['eLevel'] = td[3].text.strip()
                event['eName'] = td[4].text.strip()
                event['eVenue'] = td[5].text.strip()
                if event['eLevel'] != 'Level D':
                    try:
                        link = td[6].a['href'].strip().split('eday=')
                        if len(link) == 2:
                            event['eLink'] = link[1]
                            eventList.append(event)
                    except:
                        print("No results",event['eDate'],event['eClub'],event['eVenue'])
    return eventDict  

def getCourseIDs(eDay,courseNr=1,local=True):
    url = 'https://www.britishorienteering.org.uk/index.php?pg=results&eday={0}&results={0}&course={1}&'.format(str(eDay),str(courseNr))
    if local:
        response = open('C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr),'r'))
    else:
        if os.path.isfile('C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr))):
            return -1
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response.read(), 'html.parser')
        f2 = open('C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr)),'wb')
        try:
            f2.write(soup.prettify())
        except:
            f2.write(soup.prettify(encoding='utf-8'))
        
        f2.close()
        print('Saved: C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr)))
        return -1
    
    soup = BeautifulSoup(response.read(), 'html.parser')
    courseList = [(eDay,courseNr)]
    for main in soup.find_all('main'):
        for a in main.find_all('a'):
            if '/index.php' in a['href']:
                l = a['href']
                eday_id = l[l.find('eday=')+5:l.find('results=')-1]
                result_id = l[l.find('results=')+8:l.find('course=')-1]
                if eday_id == result_id:
                    courseList.append((eDay,int(l[l.find('course=')+7:len(l)-1])))

    return courseList


def parseCourseWebpage(courseID,local=True):
    eDay = courseID[0]
    courseNr = courseID[1]
    url = 'https://www.britishorienteering.org.uk/index.php?pg=results&eday={0}&results={0}&course={1}&'.format(str(eDay),str(courseNr))
    
    if local:
        response = open('C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr),'r'))
    else:
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response.read(), 'html.parser')
        f2 = open('C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr)),'wb')
        f2.write(bytes(str(soup),encoding='utf-8')) # Creates an error in the s
        f2.close()
        print('Saved: C:\\python\\testdata\\bori\\BOResults_{0}_{1}.html'.format(str(eDay),str(courseNr)))
        return False
    
    soup = BeautifulSoup(response.read(), 'html.parser')
    
    newCourse = EventCourse()
    
    for main in soup.find_all('main'):
        for strong in main.find_all('strong')[:1]:
            newCourse = EventCourse()
            newCourse.updateCourseFromHTML(courseID,strong)
            
    resList = list()
    
    try:
        all_tr =  soup.tbody.find_all('tr')
    except:
        print('No results available')
        return newCourse,[]
    if not all_tr:
        return newCourse,[] 
    for tr in soup.tbody.find_all('tr'):
        if tr == None:
            return newCourse,[]
        td = tr.find_all('td')
        
        if len(td)<7: # Tried with thead, but HTML is faulty...
            return newCourse,[]

        try:
            pos = int(td[0].text.strip())
        except:
            pos = '-'
            
        name = td[1].text.replace('mp -','').strip()
        club = td[2].text.strip()
        gender = td[3].text.strip().replace('W','F')
        yob = td[4].text.strip()
        try:
            t = datetime.strptime(td[5].text.strip(),"%H:%M:%S")
            time = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        except:
            print("Timestring not in correct format")
            return newCourse,[]
        try:
            points = int(td[6].text.strip())
        except:
            points = 0
        
        resList.append(raceResult(pos,name,club,gender,yob,time,points))
    
    return newCourse,resList

def parseCourseTXT(courseId):
    eDay = courseId[0]
    courseNr = courseId[1]
    
    f = open('C:\\python\\testdata\\bori\\txt\\Results_{0}_{1}.res'.format(str(eDay),str(courseNr)),'r')
    newEventCourse = EventCourse()
    newEventCourse.updateCourseFromTXT(courseId, f.readline())
    courseDict[courseId] = newEventCourse
    for line in f.readlines():
        r1 = line.replace('\n','').split(';')
        r2 = raceResult(r1[0],r1[1],r1[2],r1[3],r1[4],r1[5],r1[6])
        updateRunnerDict(r2,newEventCourse)

def BOFResultWebpageToTxt(courseID):
    
    eDay = courseID[0]
    courseNr = courseID[1]
    
    if os.path.isfile('C:\\python\\testdata\\bori\\txt\\Results_{0}_{1}.res'.format(str(eDay),str(courseNr))):
        #return True
        pass
    
    courseInfo,resList = parseCourseWebpage(courseID,local=True)
    s1 = courseInfo.cName+';'+str(courseInfo.cLength)+';'+str(courseInfo.cClimb)+';'+str(courseInfo.cControls)+'\n'
    f = open('C:\\python\\testdata\\bori\\txt\\Results_{0}_{1}.res'.format(str(eDay),str(courseNr)),'w')
    f.write(s1)

    for res in resList:
        s2 = str(res.pos)+';'+res.name+';'+res.club+';'+res.gender+';'+str(res.yob)+';'+str(res.time)+';'+str(res.points)+'\n'
        f.write(s2)
    f.close()


def updateRunnerDict(eventRes,cInfo):
    hnr = hashNumber(eventRes.name, eventRes.club, eventRes.yob)
     
    if hnr not in runners:
        runners[hnr] = Runner(eventRes.name,eventRes.club,eventRes.yob,eventRes.gender)
        runners[hnr].addEvent(cInfo.cId,eventRes)
    else:
        runners[hnr].addEvent(cInfo.cId,eventRes)


eventsDict = parseEventWebPage(local=True)
print("*****")
#===============================================================================
#    
# for key,event in eventsDict.items():
#     if event.eDate > datetime.now()-timedelta(days=365) and event.eLevel != 'Level D':
#         print(key,event.eName)
#         courses = getCourseIDs(key, local=True)
#         for courseId in courses:
#             print(courseId)
#             parseCourseTXT(courseId)
#             #===================================================================
#             # courseDict[course] = c
#             # for p in res:
#             #     updateRunnerDict(p,c)
#             #===================================================================
#     
#            
#===============================================================================
runners = pickle.load(open( "C:\\python\\testdata\\bori\\runnersdump.p", "rb" ))
eventsDict = pickle.load(open( "C:\\python\\testdata\\bori\\eventsdump.p", "rb" ))
courseDict = pickle.load(open( "C:\\python\\testdata\\bori\\coursesdump.p", "rb" ))



for key,run in runners.items():
    if run.club == "WAOC":
        run.printEvents()
        






 
#===============================================================================
# pickle.dump(runners, open( "C:\\python\\testdata\\bori\\runnersdump.p", "wb" ))
# pickle.dump(eventsDict, open( "C:\\python\\testdata\\bori\\eventsdump.p", "wb" ))
# pickle.dump(courseDict, open( "C:\\python\\testdata\\bori\\coursesdump.p", "wb" ))
#===============================================================================


#===============================================================================
# f = open( "C:\\python\\testdata\\bori\\runner.csv", "w" )
# for key,runner in runners.items():
#     if runner.club == 'WAOC':
#         print(runner.name,runner.club)
#         f.write(runner.printEvents())
#      
# f.close()
#===============================================================================
     
#cr = getCourseIDs(69649,local=False)
#===============================================================================
# evList = parseEventWebPage()
# for event in evList:
#     if event['eClub'] == 'WAOC':
#         print(event['eDate'],event['eLink'],event['eClub'],event['eVenue'],event['eLevel'])
#===============================================================================
#===============================================================================
# readRankingWebpages()    
# df = readFabiabFour('http://www.fabian4.co.uk/start/list.aspx?EventID=1606')
# 
# for key,val in df.items():
#     print('\n****',key)
#     s = 0
#     for person in val:
#         print('{},{},{:.2f}'.format(person.name,person.club,person.points/len(person.events)))
#         s+=person.points/len(person.events)
#     print(key,"AVG: {:.1f}".format(s/len(val)))
#===============================================================================