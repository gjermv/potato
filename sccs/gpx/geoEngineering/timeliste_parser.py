# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 20:58:54 2021

@author: A485753
"""



import lxml as lxml
import lxml.html
import unicodedata 
import pandas as pd
import glob as glob
import filecmp
import datetime


def get_colums(html_sub): 
    return 

def analyse_line(html_sub,colInp):
    """ tar en dinary med info. 
    Det er funnet feil atarad og returnerer dictioi funksjonen hvis en uke består av flere rader"""
    columns = len(html_sub)
    time_dict = {}
    desc_dict = {}
    
    
    if columns == colInp:
        time_dict['Timekode'] = html_sub[0].text_content()
        time_dict['Oppdrag'] = html_sub[1].text_content()
        time_dict['Oppdrag_Navn'] = html_sub[1][0].attrib['title'].split('\n',1)[1]
        time_dict['Oppdrag_Kunde'] = html_sub[1][0].attrib['title'].split('\n',1)[0]
        time_dict['Aktivitet'] = html_sub[2].text_content()
        time_dict['Timer'] = html_sub[6].text_content()
        
        
        
        return (1, time_dict)
    
    if columns == 3:
        desc_dict['Dato'] = html_sub[1].text_content()
        desc_dict['Tekst'] = html_sub[2].text_content()
        return (2, desc_dict)
    
    else:
        time_dict['Timekode'] = html_sub[0].text_content()
        time_dict['Oppdrag'] = html_sub[1].text_content()
        time_dict['Oppdrag_Navn'] = 'NA'
        time_dict['Oppdrag_Kunde'] = 'NA'
        time_dict['Aktivitet'] = html_sub[2].text_content()
        time_dict['Timer'] = html_sub[6].text_content()
        
        if time_dict['Oppdrag'] == 'Sum':
            return (4,None)
        elif time_dict['Oppdrag'] == '':
            return (4,None)
        else: 
            return (3, time_dict)


def analyse_line2(html_sub,colInp):
    """ Eksprimentell """
    columns = len(html_sub)
    time_dict = {}
    desc_dict = {}
    
    
    if html_sub[1].attrib['bgcolor'] == "#ffffff" or html_sub[1].attrib['bgcolor'] == "#F0F0F0":
        if len(html_sub[1].text_content()) > 0:
            time_dict['Timekode'] = html_sub[0].text_content()
            time_dict['Oppdrag'] = html_sub[1].text_content()
            time_dict['Oppdrag_Navn'] = html_sub[1][0].attrib['title'].split('\n',1)[1]
            time_dict['Oppdrag_Kunde'] = html_sub[1][0].attrib['title'].split('\n',1)[0]
            time_dict['Aktivitet'] = html_sub[2].text_content()
            time_dict['Timer'] = html_sub[6].text_content()
            #time_dict['Timepris'] = html_sub[-3].text_content()
    
            return (1, time_dict)
        return (4,None)
    
    else: 
        return (4,None)

def fix_dictionary(myDict):
    try:
        myDict['Timer'] = unicodedata.normalize("NFKD", myDict['Timer'])
        myDict['Timer'] = myDict['Timer'].strip()
        myDict['Timer'] = float(myDict['Timer'].replace(',','.'))
    except:
        myDict['Timer'] = "Failed"
    myDict['Timeliste'], myDict['Fra-Til']  = myDict['name_id'].split('   ', 1)
    
    if 'Dato' in myDict:
        print(myDict['Dato'])
        myDict['Dato'] = unicodedata.normalize("NFKD", myDict['Dato'])
        myDict['Dato'] = myDict['Dato'].strip()
        myDict['Dato'] = myDict['Dato'].split(' ', 1)[0]


    
    return myDict            



myDf = pd.DataFrame()

def read_VismaFile(filename,df):
    print(filename)
    file = open(filename)
    #Lag LXML element
    html_inp = file.read()
    html_Element = lxml.html.fromstring(html_inp)
    # file.close()
    
    # Finn overskrifter
    element_Dict = {}
    element_Dict['name'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[1]/td[2]/strong')[0].text_content()
    element_Dict['name_id'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[3]/td[2]')[0].text_content()
    element_Dict['filename'] = filename
    # element_Dict['attestert'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[3]/td[4]/a')[0].text_content()
    
    
    # Finn tabell med data
    main_table = html_Element.xpath('/html/body/table[4]/tbody')
    header = html_Element.xpath('/html/body/table[4]/tbody/tr[1]')
    
    # Les gjennom datatabell og hent ut info
    counter = 0
    col = len(main_table[0][0])  # Data kan varierer basert på antall dager i uka. 
    
    for child in main_table[0]:
        if counter == 0:
            pass
        else:
            kat, desc = analyse_line(child,col+1)
            if kat == 1:
                element_Dict.update(desc)
                element_Dict = fix_dictionary(element_Dict)
                df = df.append(element_Dict,ignore_index=True)
            if kat == 3:
                element_Dict.update(desc)
                element_Dict = fix_dictionary(element_Dict)
                df = df.append(element_Dict,ignore_index=True)
            if desc == None:
                break
        counter += 1

    return df


def read_VismaFile_advanced(filename,df):
    print(filename)
    file = open(filename)
    #Lag LXML element
    html_inp = file.read()
    html_Element = lxml.html.fromstring(html_inp)
    # file.close()
    
    # Finn overskrifter
    element_Dict = {}
    element_Dict['name'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[1]/td[2]/strong')[0].text_content()
    element_Dict['name_id'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[3]/td[2]')[0].text_content()
    element_Dict['filename'] = filename
    # element_Dict['attestert'] = html_Element.xpath('/html/body/table[2]/tbody/tr/td[3]/table/tbody/tr[3]/td[4]/a')[0].text_content()
    
    
    print(element_Dict)
    
    # Finn tabell med data
    main_table = html_Element.xpath('/html/body/table[4]/tbody')
    header = html_Element.xpath('/html/body/table[4]/tbody/tr[1]')
    
    # Les gjennom datatabell og hent ut info
    counter = 0
    col = len(main_table[0][0])  # Data kan varierer basert på antall dager i uka. 
    
    for child in main_table[0]:
        if counter == 0:
            pass
        else:
            kat, desc = analyse_line2(child,col+1)
            if kat == 1:
                element_Dict.update(desc)
                element_Dict = fix_dictionary(element_Dict)
                df = df.append(element_Dict,ignore_index=True)
            if kat == 3:
                element_Dict.update(desc)
                element_Dict = fix_dictionary(element_Dict)
                df = df.append(element_Dict,ignore_index=True)
            if desc == None:
                pass #break
        counter += 1

    return df

### Main ###




for file in glob.glob('C:\\python_proj\\vekemail\\tm\\*.html'):
    myDf = read_VismaFile_advanced(file,myDf)

filelocation = 'C:\\python_proj\\vekemail\\tm\\Overview-{}-e.xlsx'.format(str(datetime.date.today()))    
print(myDf.to_excel(filelocation))

print(filelocation)


