# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import time
import urllib.request
import os

from PIL import Image


def readFileToList(year, day, testdata = False):
    
    path = 'C:\\python_proj2\\aoc\\'
    file1 = 'aoc{}-{}.txt'.format(str(year),str(day))
    file2 = 'aoc{}-{}t.txt'.format(str(year),str(day))


    if testdata:
        filename = path+file2

    else:
        filename = path+file1
        
    if os.path.isfile(filename):
        print('OK: ', filename)
    else:
        print('File does not exist: ',filename)
        return []
    
    with open(filename, "r") as fp:
        inp = fp.read().splitlines()
        print('Number of lines: ', len(inp))

    return inp

def ao1_2022():
    s = 0
    elves = []

    with open("C:\\python_proj2\\aoc\\aoc2022-1.txt", "r") as fp:
        inp = fp.readlines()
        for line in inp:
            if line == '\n':
                elves.append(s)
                s = 0
            else:
                s += int(line.replace('\n', ''))

    print('1a: ', max(elves))

    top3 = sorted(elves)[-3:]
    print('1b: ', sum(top3))


def ao2_2022():
    s1 = 0
    s2 = 0
    elves = []
    
    pts = {'A X': 1+3, 
           'A Y': 2+6, 
           'A Z': 3+0,
           'B X': 1+0, 
           'B Y': 2+3, 
           'B Z': 3+6,
           'C X': 1+6, 
           'C Y': 2+0, 
           'C Z': 3+3,}

    pts2 = {'A X': 0+3, 
           'A Y': 3+1, 
           'A Z': 6+2,
           'B X': 0+1, 
           'B Y': 3+2, 
           'B Z': 6+3,
           'C X': 0+2, 
           'C Y': 3+3, 
           'C Z': 6+1,}

    with open("C:\\python_proj2\\aoc\\aoc2022-2.txt", "r") as fp:
        inp = fp.readlines()
        for line in inp:
           line = line.replace('\n','')
           s1 += pts[line]
           s2 += pts2[line]
    
    return [s1,s2]


def ao3_2022():
    with open("C:\\python_proj2\\aoc\\aoc2022-3.txt", "r") as fp:
        inp = fp.readlines()
    s = 0  
    s1 = 0
    
    def calcPoints(cc):
        t1 = cc.pop()
        t = ord(t1)
        if t > 95:
            return(t-96)
        else:
            return(t-65+27)
        
    for line in inp:
        line = line.replace('\n','')
        L = len(line)
        a = set(line[:L//2])
        b = set(line[L//2:])
        res = a.intersection(b)
        s += calcPoints(res)

    for i in range(0,len(inp),3):
        
        a = set(inp[i].replace('\n',''))
        b = set(inp[i+1].replace('\n',''))
        c = set(inp[i+2].replace('\n',''))

        res1 = a.intersection(b)  
        res2 = res1.intersection(c)
        s1 += calcPoints(res2)
        
            
            
    print(s,s1)
        
def ao4_2022():
    inp = readFileToList('C:\\python_proj2\\aoc\\aoc2022-4.txt')
    myS = 0
    myS2 = 0
    for line in inp:
        elfA, elfB = line.split(',')
        elfA1, elfA2 = elfA.split('-')
        elfB1, elfB2 = elfB.split('-')
        
        secA = set(range(int(elfA1),int(elfA2)+1))
        secB = set(range(int(elfB1),int(elfB2)+1))
        
      
        if secA.issubset(secB) or secB.issubset(secA):
            myS += 1
            
        if len(secA.intersection(secB)) > 0:
            myS2 += 1

    print(myS, myS2)


def ao5_2022():
    inp = readFileToList('C:\\python_proj2\\aoc\\aoc2022-5.txt')
    stack = {}
    numberOfstacks = 9
    numberOfRows = 8

    for c in range(numberOfstacks):
        stack[c+1] = []

    for crate in range(numberOfRows):
        for i in range(0, numberOfRows*4+1, 4):
            box = inp[crate][i:i+4]
            if box.replace(' ', '') != '':
                stack[i//4 + 1].insert(0, box)

    stack2 = stack.copy()
    print(stack2)

    for move in range(numberOfRows+2, len(inp)):
        data = inp[move].split(' ')
        times = int(data[1])
        f = int(data[3])
        t = int(data[5])

        """### Del 1 #### """
        # for i in range(times):
        #     c = stack[f].pop()
        #     stack[t].append(c)

        tmp = stack[f][-times:]

        for i in range(times):
            c = stack[f].pop()

        stack[t].extend(tmp)


        print(times,tmp)


    for c in range(numberOfstacks):
        try:
            print(stack[c+1].pop().replace('[','').replace(']',''))
        except:
            print('-')
            
def ao6_2022():
    inp = str(readFileToList('C:\\python_proj2\\aoc\\aoc2022-6.txt')[0])
    seqL = 14
    
    for i in range(0,len(inp)-seqL):

        
        if len(set(inp[i:i+seqL])) == seqL:
            
            print(i+14)
            return True

def ao7_2022():
    inp = readFileToList('C:\\python_proj2\\aoc\\aoc2022-7.txt')
    
    dirList = ['Root']
    fileDict = dict()

    
    for command in inp:
        if '$ cd' in command:  
            c = str(command.split(' ')[2])

            if c == '/':
                dirList = ['Root']  
            elif c == '..':
                dirList.pop()
            else:
                dirList.append(c)

                
        elif '$ ls' in command:
            currentDir =  '/'.join(dirList)
            if currentDir in fileDict:
                print('Error- Included before', currentDir)
            
            if currentDir not in fileDict:
                fileDict[currentDir] = 0


        elif '$' not in command:
            if 'dir ' in command:
                pass
            
            else:
               filesize = int(command.split(' ')[0])

               for j in range(1,len(dirList)+1):
                   jkey = '/'.join(dirList[:j])       
                   fileDict[jkey] += filesize
        else:
            print('Error')

    

    """Part 1  gir svaret under. 
    Del 2 løses delvis i Excel... 
    """   
    myS = 0
    for key in fileDict:
        if fileDict[key] < 100000:
            print(key,fileDict[key])
            myS += fileDict[key]
    
    print('myS',myS)     

         
def ao8_2022():
    inp = readFileToList(2022,8,testdata=False)
    xdim,ydim = len(inp[0]),len(inp)
    
    
    inpArr = np.zeros([xdim,ydim],int)
    visArr = np.zeros([xdim,ydim],int)
    
    
    
    for i in range(xdim):
        for j in range(ydim):
            inpArr[i,j] = int(inp[i][j])

    """ PART 1 """    
    for i in range(xdim):
        tree = -1
        myL = inpArr[i,:]
        
        for v in range(len(myL)):
            if myL[v] > tree:
                visArr[i,v] = 1
                tree = myL[v]

        tree = -1
        for v in range(len(myL)-1,-1,-1):
            if myL[v] > tree:
                visArr[i,v] = 1
                tree = myL[v]

    for i in range(ydim):
        tree = -1
        myL = inpArr[:,i]
        
        for v in range(len(myL)):
            if myL[v] > tree:
                visArr[v,i] = 1
                tree = myL[v]    

        tree = -1
        for v in range(len(myL)-1,-1,-1):
            if myL[v] > tree:
                visArr[v,i] = 1
                tree = myL[v]    

    print(np.sum(visArr))

    """ PART 2 """   
    def lookEast(ii, h, arr):
        c = 0
        # print(ii,arr)
        for val in range(ii+1, len(arr)):
            c += 1
            
            if h > arr[val]:
                # print(h,'>',arr[val])
                pass
            else:
                # print(ii,'return,',c)
                return c
        
        # print('End',c)
        return c


    myS2 = 0
    print(inpArr)
    a = inpArr[i,:]
    b = np.flip(a)
    print(a)
    print(b)
    for i in range(xdim):
        for j in range(ydim):
            # print('dim',ydim-j)
            height = inpArr[i,j]
            #print(i,j,height)
            x1 = lookEast(j,height,inpArr[i,:])
            x2 = lookEast(ydim-j-1,height,np.flip(inpArr[i,:]))
            y1 = lookEast(i,height,inpArr[:,j])
            y2 = lookEast(xdim-i-1,height,np.flip(inpArr[:,j]))
            # print(x2)
            print(x1,x2,y1,y2)
            
        
            if x1*y1*x2*y2 > myS2:
                myS2 = x1*y1*x2*y2
    print(myS2)


def ao9_2022():
    inp = readFileToList(2022,9,testdata=False)
    h = np.zeros(2,int)
    h1 = np.array((500,500))
    tailList = []
    for tail in range(9):
        tailList.append(np.array((500,500)))
    
    t1 = np.array((500,500))
    t2 = np.array((500,500))
    t3 = np.array((500,500))
    t4 = np.array((500,500))
    t5 = np.array((500,500))
    t6 = np.array((500,500))
    t7 = np.array((500,500))
    t8 = np.array((500,500))
    t9 = np.array((500,500))
    
    
    
    def getV(v1,v2):
        h = v1-v2
        #print(h)
        #print(np.sqrt(h[0]**2+h[1]**2))
        if np.sqrt(h[0]**2+h[1]**2) <= 1.5:
            return np.array((0,0))
        
        for i in range(2):    
            if h[i]>1 or h[i]<-1:
                h[i] = h[i]/abs(h[i])    
        return h
    
    
    tab = np.zeros([1000,1000],int)
    
    for line in inp:
        d, s = line.split(' ')
        s = int(s)
        head_dir = np.array((0,1))
        if d == 'U':
            head_dir = np.array((0,1))
        elif d == 'D':
            head_dir = np.array((0,-1))
        elif d == 'R':
            head_dir = np.array((1,0))
        elif d == 'L':
            head_dir = np.array((-1,0))    
        else:
            print('Unknow direction')                
        
        for step in range(s):
            h1 = h1 + head_dir
            vxy = getV(h1,tailList[0])
            
    
            for tail in range(0,len(tailList)-1):
                tailList[tail] = tailList[tail] + vxy
                vxy = getV(tailList[tail],tailList[tail+1])
            
            tailList[-1] = tailList[-1] + vxy
            # vxy = getV(h1,t1)
            # t1 = t1 + vxy

            # vxy = getV(t1,t2)
            # t2 = t2 + vxy

            # vxy = getV(t2,t3)
            # t3 = t3 + vxy
            
            # vxy = getV(t3,t4)
            # t4 = t4 + vxy

            # vxy = getV(t4,t5)
            # t5 = t5 + vxy 
            
            # vxy = getV(t5,t6)
            # t6 = t6 + vxy            

            # vxy = getV(t6,t7)
            # t7 = t7 + vxy            

            # vxy = getV(t7,t8)
            # t8 = t8 + vxy

            # vxy = getV(t8,t9)
            # t9 = t9 + vxy
            
            tab[tailList[8][0],tailList[8][1]] = 1
            
            
            #tab[h1[0],h1[1]] = 2
            
            #print(tab,'\n')
    print(np.sum(tab))
            
    
def ao10_2022():
    inp = readFileToList(2022,10,testdata=False)
            
    cycle = 0

    x_reg = np.array([1],int)
    # x_reg= np.append(x_reg,[2])
    
    
    for i in range(len(inp)):
        mem = 0
        
        if inp[i] == 'noop':
            
            x_reg = np.append(x_reg, x_reg[-1:])
            cycle += 1

        else: 
            com, val = inp[i].split(' ')
            
            val = int(val)
            mem = val
            
            x_reg = np.append(x_reg, x_reg[-1:])
            x_reg = np.append(x_reg, x_reg[-1:]+[val])


    myS = 0
    for m in range(20,221,40):
        print(x_reg[m-1],m,x_reg[m]*m)
        myS += x_reg[m-1]*m
        
    print(myS)

        
    screen = np.zeros([6,40],int)

    
    x_reg = x_reg[0:240].reshape(6,40)
    

    for x in range(6):
        for y in range(40):
            if abs(x_reg[x,y]-y) <= 1:
                screen[x,y] = 1
                # print('SpritePos',x_reg[x,y],'X',y)
            else:
                pass
                # print('SpritePos',x_reg[x,y],'.',y)
    

    print(screen)

    screen2 = []
    
    for x in range(6):
        screen2.append([])
        
        for y in range(40):
            if x_reg[x,y] == 1:
                screen2[x].append('#')
            else:
                screen2[x].append('.')
    
    for line in screen2:
        print(''.join(line))

    
def ao11_2022():
    
    def calcWorry(oldInt, s):

        mySign = s[3]
        
        oldW = int(oldInt)
        factor = 0
        
        if 'old' in s[4:]:
            factor = int(oldInt)
        else:
            factor = int(s[4:])
        
        if mySign == '*':
            currentW =  oldW*factor
        elif mySign == '+':
            currentW = oldW+factor 
        
        
        currentW2 = currentW // 1
        #print(currentW, currentW2)
        return currentW2
        
    def getMulti(fac):
        mmm = 1
        for key in fac:
            mmm *= fac[key]
            
        return mmm
    
    inp = readFileToList(2022,11,testdata=False)
    
    monkeyItems = {}
    monkeyOperation = {}
    monkeyTest = {}
    monkeyTrue = {}
    monkeyFalse= {}
    monkeyInsp = {}
    
    i = 0
    for row in inp:
        
        if 'Starting items:' in row:
            #print(row.replace('Starting items: ','').split(','))
            monkeyInsp[i] = 0
            monkeyItems[i] = row.replace('Starting items: ','').replace(' ','').split(',')
            #print(monkeyItems)
        elif  'Operation: new' in row: 
            monkeyOperation[i] = row.replace('Operation: new =','').replace(' ','')
            
        elif  ' Test: divisible by ' in row: 
            monkeyTest[i] = int(row.replace(' Test: divisible by ',''))
            
        elif '    If true: throw to monkey ' in row: 
            monkeyTrue[i] = int(row.replace('    If true: throw to monkey ',''))
        elif '    If false: throw to monkey ' in row: 
            monkeyFalse[i] = int(row.replace('    If false: throw to monkey ',''))
        
        if len(row) == 0:
            
            i += 1
            
    print(monkeyInsp)        
    for i in range(10000):
        print(i)
        for key in monkeyOperation:
            #print('key',key,monkeyItems[key])
            c = 0 
            
            for item in monkeyItems[key]:
                testCase = calcWorry(item,monkeyOperation[key]) % getMulti(monkeyTest)
                #print(item)
                monkeyInsp[key] += 1
               
                if testCase % monkeyTest[key] == 0:

                    monkeyItems[monkeyTrue[key]].append(testCase  )
                    #print('True',item,'to',monkeyTrue[key])
                else:
                    monkeyItems[monkeyFalse[key]].append(testCase  )
                    #print('False',item,'to',monkeyFalse[key])
                    
                c += 1
                if c > 100:
                    print('Help')
                    break
                    
            monkeyItems[key] = []
    for monkey in monkeyItems:
        # print(monkey,monkeyItems[monkey],monkeyTest[monkey])
        print(monkey, monkeyInsp[monkey])
        
        
    print(getMulti(monkeyTest))

def ao12_2022():
    inp = readFileToList(2022,12,testdata=False)
    xdim = len(inp[0])
    ydim = len(inp)

    terrain  = np.zeros((ydim,xdim),int)
    myMap = np.zeros((ydim,xdim),int)

    startPoint = np.array([0,0])
    endPoint = np.array([0,0])
    part2Solution = [999]
    
    
    for row in range(xdim):
        for char in range(ydim):
            height = ord(inp[char][row])-ord('a')
            if height == -14:
                startPoint = np.array((row,char),int)
                terrain[char,row] = 0
                # myMap[char,row] = 2   ### Part 1
                myMap[char,row] = 99999
            elif height == -28:
                endPoint = np.array((row,char))
                terrain[char,row] = ord('z')-ord('a')
                myMap[char,row] = 99999
            else:        
                terrain[char,row] = ord(inp[char][row])-ord('a')
                myMap[char,row] = 99999
    


    def traverse(coord,height,step):
        
        myStep = step + 1
        myHeight =  terrain[coord[1],coord[0]]
        
        
        
        """ PART 1 """
        # diffHeight =  myHeight-height
        # if diffHeight > 1:
        #     print('Climbing',myHeight, height,coord)
        #     return False
        
        # if myMap[coord[1],coord[0]] > myStep:
        #     myMap[coord[1],coord[0]] = myStep
        
        # else:
        #     print('More efficient ways to get here... ',coord)
        #     return False
        
        # if coord[0] == endPoint[0] and coord[1] == endPoint[1]:
        #     print('solution',myStep)
        #     return True
            
        """ PART 2 """
        diffHeight =  height - myHeight
       
        if diffHeight > 1:
            print('Climbing',myHeight, height,coord)
            return False
        
        if myMap[coord[1],coord[0]] > myStep:
            myMap[coord[1],coord[0]] = myStep
        
        else:
            print('More efficient ways to get here... ',coord)
            return False
        
        if height == 0:
            print('Solution',myStep)
            part2Solution.append(myStep)

            return True
         
        x = part2Solution.copy()
        
        if myStep >= min(x):
            print('Dont bother walking longer',myStep)
            return False
        
                
        if coord[0] < xdim-1:
            #print('GO 1,0')
            newCoord = coord + (1,0)
            traverse(newCoord,myHeight,myStep)


        if coord[0] > 0:
            #print('GO -1,0')
            newCoord = coord + (-1,0)
            traverse(newCoord,myHeight,myStep)


        if coord[1] > 0:
           #print('GO 0,-1')
            newCoord = coord + (0,-1)
            traverse(newCoord,myHeight,myStep)

        
        if coord[1] < ydim-1:
            #print('GO 0,1')
            newCoord = coord + (0,1)
            traverse(newCoord,myHeight,myStep)



    """Part 1"""
    #traverse(startPoint,0,-1)
    
    """Part 2"""
    traverse(endPoint,25,-1)
    print(terrain)
    print(endPoint)
    print(myMap)

    
    print(part2Solution)
    
    img = Image.fromarray(myMap)
    img.show()
    
    


def aoX_2022():
    inp = readFileToList(2022,9,testdata=True)


### Run code
start_time = time.perf_counter_ns()

ao12_2022()


print('Running time (ms):', (time.perf_counter_ns()-start_time)/10**6)