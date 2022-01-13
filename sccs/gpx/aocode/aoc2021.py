# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def ao2():
    with open("C:\\python_proj\\aocode\\aoc2.txt", "r") as fp:
        inp = fp.readlines()
        
        
    hpos = 0
    vpos = 0
    aim = 0
    for line in inp:
        course, speed = line.replace('\n','').split(' ')
        if course == 'forward':
            hpos += int(speed)
            vpos += aim * int(speed)
        elif course == 'down':
            aim += int(speed)
        elif course == 'up':
            aim -= int(speed)
        else: 
            print(course, 'Unknown command')
            
    print(hpos, vpos, hpos*vpos)

def ao3a():
    with open("C:\\python_proj\\aocode\\aoc3.txt", "r") as fp:
        inp = fp.readlines()
    
        
    bits1 = [0]*12
    bits0 = [0]*12
    
    for line in inp:
        line = line.replace('\n','')
        
        for i in range(12):
            if line[i] == '0':
                bits0[i] = bits0[i]+1
            elif line[i] == '1':
                bits1[i] = bits1[i]+1
    
    mynumbA = [0]*12         
    mynumbB = [1]*12
     
    for j in range(12):
        if int(bits1[j])>int(bits0[j]):
            mynumbA[j] = 1
            mynumbB[j] = 0
            
    print(mynumbA)
    
    
    gamma = 0
    epsilon = 0
    
    for k in range(12):
        gamma += mynumbA[k]*(2**(11-k))
        epsilon += mynumbB[k]*(2**(11-k))
    print('Answer 3A')
    print(gamma*epsilon)

def ao3b():
    df = pd.DataFrame()    
    
    with open("C:\\python_proj\\aocode\\aoc3.txt", "r") as fp:
        inp = fp.read().split('\n')
    
    for line in inp:
        df = df.append([list(line)])
    
    for i in range(12):
        df[i] = pd.to_numeric(df[i])    
    
    df.reset_index(inplace=True)
    df2 = df.copy()
    
    
    c = 0
    while len(df)>1 and c<12:
        if df[c].sum()>len(df)/2:
            df.drop(df[df[c] == 1].index, inplace = True)
        elif df[c].sum()<len(df)/2:
            df.drop(df[df[c] == 0].index, inplace = True)
        elif df[c].sum()==len(df)/2:
            df.drop(df[df[c] == 1].index, inplace = True)
            print(c)
        c +=1
        
    print(df)
    
    life_support_rating = 4089*1923
    print(life_support_rating)
 
def ao4():    
    with open("C:\\python_proj\\aocode\\aoc4.txt", "r") as fp:
        inp = fp.read()
        
    inp = inp.split('\n')
    bingo_numbers = inp[0].split(',')
    bingo_boards = []
    
    for i in range(len(inp)//6):
        l = []
        
        for j in range(5): 
            l.append(inp[6*i + j+2].split())
        bingo_boards.append(np.array(l).astype(int))
    
    
    # winner = False
    # for number in bingo_numbers:
    #     n = int(number)
    #     c = 0
    #     for board in bingo_boards:
    #         c += 1
    #         board[board == n] = -1
    #         #print(np.sum(board,axis=0))
            
    #         if -5 in np.sum(board,axis=1):
    #             print(board)
    #             winner = True
    #             break
    #         elif -5 in np.sum(board,axis=0):
    #             print(board)
    #             winner = True
    #             break
    #     if winner == True:
    #         print(c*6+2,number)
    #         break
        
    winner = False
    for number in bingo_numbers:
        n = int(number)
        c = 0
        
        for board in bingo_boards:
            c += 1
            board[board == n] = -1
            #print(np.sum(board,axis=0))
            
            if -5 in np.sum(board,axis=1):
                print(board[board>0].sum(),number)
                board[board > -10] = -999
    
    
            if -5 in np.sum(board,axis=0):
                print(board[board>0].sum(),number)
                board[board > -10] = -999
                
    
    
        if winner == True:
            print(c*6+2,number)
            break

def ao5():        
    with open("C:\\python_proj\\aocode\\aoc5.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    
    myMap = np.zeros((1000,1000))
    
    
    for obs in inp:
        line = obs.split('->')
        x1,y1 = line[0].split(',')
        x2,y2 = line[1].split(',')
        
        x1 = int(x1)
        x2 = int(x2)
        y1 = int(y1)
        y2 = int(y2)
        
        if x1 == x2:
            steps = max(abs(x1-x2),abs(y1-y2))+1
            x_dir = 0
            y_dir = (y2-y1) //  abs(y1-y2)
    
            for step in range(steps): 
                x = x1+step*x_dir
                y = y1+step*y_dir
                myMap[x,y] += 1
                
                
        
        elif y1 == y2:
            steps = max(abs(x1-x2),abs(y1-y2))+1
            x_dir = (x2-x1) //  abs(x1-x2)
            y_dir = 0
    
            for step in range(steps): 
                x = x1+step*x_dir
                y = y1+step*y_dir
                myMap[x,y] += 1
        else: 
            steps = max(abs(x1-x2),abs(y1-y2))+1
            x_dir = (x2-x1) //  abs(x1-x2)
            y_dir = (y2-y1) //  abs(y1-y2)
            #print(x1,y1,x2,y2, steps, x_dir,y_dir)
            for step in range(steps): 
                x = x1+step*x_dir
                y = y1+step*y_dir
                myMap[x,y] += 1
    
    myMap[myMap<2] = 0
    print(x1,y1,x2,y2,steps,x_dir,y_dir)
    print(myMap.T)
    print(myMap.sum())
    print(np.count_nonzero(myMap))

def ao6():
    with open("C:\\python_proj\\aocode\\aoc6.txt", "r") as fp:
       inp = fp.read()
    
    l = inp.split(',')   
    arr = np.array(l)
    fishage = np.zeros(9)
    print(fishage)
    start = np.unique(arr, return_counts=True)
    fishage[start[0].astype(int)] = start[1]
    print(fishage)
    
    for i in range(256):
        newFish = fishage[0]
        fishage[0:8] = fishage[1:9]
        fishage[8] = newFish
        fishage[6] += newFish
        print(fishage)
    
    print(fishage.sum())

def ao7():
    with open("C:\\python_proj\\aocode\\aoc7.txt", "r") as fp:
       inp = fp.read()
    
    l = inp.split(',')   
    arr = np.array(l).astype(int)
    print(len(arr))
    
    print(arr.mean())
    print(arr.max())
    print(arr.min())
    
    fuelList = []
    x = 0
    for i in range(arr.max()+1):
        x += i
        fuelList.append(x)
    fuelList = np.array(fuelList)
    
    minFuel = 100**10 # Stort nummer
    
    for i in range(arr.min(),arr.max()):
        fuel = fuelList[abs(arr[:] - i)]
        if fuel.sum() < minFuel:
            minFuel = fuel.sum()
            
    print('Result',minFuel)

def ao8():

    with open("C:\\python_proj\\aocode\\aoc8.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    count = 0
    
    for l in inp:
        sig,out = l.split(' | ')
       
        for x in out.split():
            v = ''.join(set(x))
            if len(v) in [2,3,4,7]:
                count += 1
        
        sigs = sig.split()
        sList = sorted(sigs, key=len)
        
        sList[0] = set(sList[0])
        sList[1] = set(sList[1])
        sList[2] = set(sList[2])
        sList[3] = set(sList[3])
        sList[4] = set(sList[4])
        sList[5] = set(sList[5])
        sList[6] = set(sList[6])
        sList[7] = set(sList[7])
        sList[8] = set(sList[8])
        sList[9] = set(sList[9])
        
        cde = sList[9].difference(sList[7].intersection(sList[6],sList[8]))
        adg = sList[3].intersection(sList[4],sList[5])
        bd = sList[2].difference(sList[0])
        a = sList[1].difference(sList[0])
        cf = sList[0]
        d = cde.intersection(bd)
        b = bd.intersection(d)
        c = cde.intersection(cf)
        e = cde.difference(c,d)
        g = adg.difference(a,d)
        f = cf.difference(c)
        
        print(a,b,c,d,e,f,g)
        
            
                
        
    print(count)
    
def a09():  
    with open("C:\\python_proj\\aocode\\aoc9.txt", "r") as fp:
       inp = fp.read().split('\n')
       
    
    
    l = []
    for line in inp:
        l.append(list(line))
        
    arr = np.array(l).astype(int)
    
    dim_x, dim_y = arr.shape
    
    arr2 = np.zeros((arr.shape[0]+2, arr.shape[1]+2))
    arr2[:,:] = arr.max()
    arr2[1:-1,1:-1] = arr
    arr = arr2
    
    c = 0
    for i in range(1,len(arr)-1):
        for j in range(1,len(arr[0])-1):
            if arr[i,j] < min(arr[i-1,j],arr[i+1,j],arr[i,j-1],arr[i,j+1]):
                c += arr[i,j]+1
    
                   
    print(c)
    
def a10():    
    def remove(s):
        if s.find('()') > -1:
            s = s.replace('()','',1)
            return s
        elif s.find('[]') > -1:
            s = s.replace('[]','',1)
            return s
        elif s.find('{}') > -1:
            s = s.replace('{}','',1)
            return s
        elif s.find('<>') > -1:
            s = s.replace('<>','',1)
            return s
        else: 
            return s
    
    
    with open("C:\\python_proj\\aocode\\aoc11.txt", "r") as fp:
        inp = fp.read().split('\n')
    
    COUNT = 0 
    teller = 0
    for code in inp[:]:
        red_code = remove(code)
        
        while len(red_code) < len(code):
            code = red_code
            red_code = remove(red_code)
    
    
        
        a = []
        a.append(code.find('}'))
        a.append(code.find(')'))
        a.append(code.find('>'))
        a.append(code.find(']'))
    
        for n in range(len(a)):
            if a[n] == -1:
                a[n] = 999999999
        
        teller += 1  
        if min(a) < 999999999:
            print(teller, 'Error',code[min(a)])
            if code[min(a)] == ')':
                COUNT += 3
            if code[min(a)] == ']':
                COUNT += 57
            if code[min(a)] == '}':
                COUNT += 1197   
            if code[min(a)] == '>':
                COUNT += 25137    
             
    print(COUNT)
    
def a11():
    with open("C:\\python_proj\\aocode\\aoc11.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    l = []
    for line in inp:
        l.append(list(line))
        
    arr_org = np.array(l).astype(int)
    arr = np.zeros((arr_org.shape[0]+2,arr_org.shape[1]+2))
    arr[:,:] = -999999
    arr[1:-1,1:-1] = arr_org
    
    count = 0
    for i in range(100000):
        arr = arr+1
        ixy = np.where(arr==10)
        explosions = set(zip(ixy[0],ixy[1]))
        
        while (len(explosions)) > 0:
            a = explosions.pop()
            count += 1
            x,y = a[0],a[1]
            arr[x-1:x+2,y-1:y+2] = arr[x-1:x+2,y-1:y+2] + 1
            
            jxy = np.where(arr==10)
            new_expl = set(zip(jxy[0],jxy[1]))
            
    
            explosions = explosions.union(new_expl)
    
        arr[arr[:,:] > 9] = 0
        
        if arr[1:-1,1:-1].sum() == 0:
            print(i)
            break
    
    print(arr[1:-1,1:-1])
        
    print(count)

def a12():
    counter = 0 

    def goToDest(dest, list_of_visited, to_go_dest, routes):
    
        if to_go_dest == None:
            return 0
        
        list_of_v = list_of_visited[:]
        list_of_v.append(dest)
        to_go_d = to_go_dest[:]
        
        if not dest.isupper():
            # print(dest,'lowercase')
            to_go_d.remove(dest)
        
        for p in routes[dest]:
            if p in to_go_dest:
                if p == 'end':
                    print('-- End --', list_of_v)
                    global counter
                    counter += 1
                else:
                    goToDest(p, list_of_v, to_go_d, routes)
        
        
    with open("C:\\python_proj\\aocode\\aoc12t.txt", "r") as fp:
        inp = fp.read().split('\n')
    
    r = dict() # r = routes
    
    for i in inp:
        a, b = i.split('-')
        
        if a in r:
            tmp = r[a]
            tmp.append(b)
            r[a] = r[a]
        else: 
            r[a] = [b]
        
        if b in r:
            tmp = r[b]
            tmp.append(a)
            r[b]  = r[b]
    
        else:
            r[b] = [a]
    
    destinations = list(r.keys())
    dest2 = destinations[:]
    for item in destinations:
        if not item.isupper():
            dest2.append(item)
    destinations = dest2[:]
    destinations.remove('start')
    destinations.remove('start')
            
    for dest in r['start']:
        goToDest(dest, ['start'], destinations, r)
        
        
    print(counter)

def a13():    
    with open("C:\\python_proj\\aocode\\aoc13.txt", "r") as fp:
        inp = fp.read().split('\n')
        
    arr = np.zeros((447*2+1,655*2+1))
    com = []
    for line in inp:
        print(line)
        if ',' in line:
            x,y = line.split(',')
            arr[int(y),int(x)] = 1      
        elif 'fold' in line:
            q,w = line.replace('fold along ','').split('=')
            com.append([q,int(w)])
    
    arr = arr.astype(int)
    
    
    
    
    
    for di, row in com:
        print(di,row)
        if di == 'y':
            flip = arr[row+1:,:]
            flipped = np.flipud(flip)
        
            arr[0:row,:][flipped[:,:] == 1] = flipped[flipped[:,:] == 1]
            arr = arr[0:row,:]
    
        elif di == 'x':
            xflip = row
            flip = arr[:,xflip+1:]
            flipped = np.fliplr(flip)
        
            arr[:,0:xflip][flipped[:,:] == 1] = flipped[flipped[:,:] == 1]
            arr = arr[:,0:xflip]
            
        print(arr.sum())
    
        
    print(arr)

def a14():
    # Løste nr 1, for treg til å løse 2.. Rotet det til. 
    with open("C:\\python_proj\\aocode\\aoc14t.txt", "r") as fp:
        inp = fp.read().split('\n')
        
    myStr = inp[0].replace(' ','')
    d = dict()
    
    sDict = dict()
    for i in range(len(myStr)-1):
        sDict[myStr[i:i+2]] = 1
        
    
    s = myStr
    
    for line in inp[2:]:
        a, b = line.split(' -> ')
    
        d[a] = b
    
    for rounds in range(3):
        myKey = list(dict((k, v) for k, v in sDict.items() if v > 0))
        print(myKey)
        
        for key in myKey:
            s += d[key]*sDict[key]
            
            s1 = key[0] + d[key]
            s2 = d[key] + key[0] 
            print(key, s1,s2)
            
            if s1 not in sDict.keys():
                sDict[s1] = 1
            else:
                sDict[s1] += 1
            
            if s2 not in sDict.keys():
                sDict[s2] = 1
            else:
                sDict[s2] += 1    
            
            sDict[key] -= 1
        
        print(s)
    
    
    
    print(len(s))   

def a11():
    with open("C:\\python_proj\\aocode\\aoc11.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    l = []
    for line in inp:
        l.append(list(line))
        
    arr_org = np.array(l).astype(int)
    arr = np.zeros((arr_org.shape[0]+2,arr_org.shape[1]+2))
    arr[:,:] = -999999
    arr[1:-1,1:-1] = arr_org

def a15():
    def goTo(x,y,s):
        global arr
        global arrS
        
        dx = [-1,1]
        dy = [-1,1]
        
        if s < arrS[x,y]:
            arrS[x,y] = s
            
        if s > 500:
            return 0
    
       
        
        for i in dx:
            x2 = x+i
            
            if x2>=0 and x2<100:
                if s + arr[x2,y] < arrS[x2,y]:
                    arrS[x2,y] = s + arr[x2,y]
                    goTo(x2,y,arrS[x2,y])
        for j in dy:
            y2 = y+j
            if y2>=0 and y2<100:
                if s + arr[x,y2] < arrS[x,y2]:
                    arrS[x,y2] = s + arr[x,y2]
                    goTo(x,y2,arrS[x,y2])
    
    
    with open("C:\\python_proj\\aocode\\aoc15.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    l = []
    for line in inp:
        l.append(list(line))
    
    
    arr = np.array(l).astype(int)
    
    arrS = arr.copy()
    arrS[:,:] = 9999999
    
    goTo(0,0,arr[0,0])
    
    print(arr[:10,:10])
    print(arrS[:10,:10])
    
    print(arrS[99,99]-arr[0,0])

    
######## A16 ###########
def a16():
    with open("C:\\python_proj\\aocode\\aoc15.txt", "r") as fp:
       inp = fp.read().split('\n')
    
    l = []
    for line in inp:
        l.append(list(line))
        
    myD = {'0' : '0000',
    '1' : '0001' ,
    '2' : '0010' ,
    '3' : '0011' ,
    '4' : '0100' ,
    '5' : '0101' ,
    '6' : '0110' ,
    '7' : '0111' ,
    '8' : '1000' ,
    '9' : '1001' ,
    'A' : '1010' ,
    'B' : '1011' ,
    'C' : '1100' ,
    'D' : '1101' ,
    'E' : '1110' ,
    'F' : '1111'}
    
    myS = ''
    for s in 'C0015000016115A2E0802F182340':
        myS += myD[s]
        

with open("C:\\python_proj\\aocode\\aoc25t.txt", "r") as fp:
   inp = fp.read().split('\n')

l = []
for line in inp:
    l2 = line.replace('.','0').replace('>','1').replace('v','2')
    l.append(list(l2))

arr = np.array(l).astype(int)
print(arr)