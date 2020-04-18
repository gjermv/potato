# -*- coding: utf-8 -*-
'''
Created on 7 Jan 2016

@author: gjermund.vingerhagen
'''

from jinja2 import Environment, FileSystemLoader
import gpxtricks
import os.path
from datetime import timedelta as dtt

def select_statistikk_overskrifter():
    txtstring = '<option selected>Velg liste</option>\n'
    for i,item in enumerate(statistikk_overskrifter()):
        txtstring += '<option value="stat{0:0>2}.html">{1}</option>'.format(i,item)
    return txtstring

def statistikk_overskrifter():
    statfak = ['Dato','Lengde','Turtid','Gåtid','Pausefaktor','Gjennomsnittsfart','Høydemeter','Høydeforskjell','Bratthet','Klatrehastighet','Kuperthetsfaktor','Toppturfaktor']   
    return statfak

def createTotStat():
    """ Creates a placeholder for total stat data. """
    totstat = dict()
    totstat['tot_length'] = 0
    totstat['tot_antall_besteget'] = 0
    totstat['tot_elevation'] = 0
    totstat['tot_tottid'] = dtt(seconds=0)
    return totstat

def modTotStat(totstat):
    mystat = dict()
    mystat['tot_antall_besteget'] = totstat['tot_antall_besteget']
    mystat['tot_tottid'] = totstat['tot_tottid'].days*24 + totstat['tot_tottid'].seconds//3600
    mystat['tot_length'] = round(totstat['tot_length'],1)
    mystat['tot_elevation'] = int(totstat['tot_elevation'])
    return mystat

def createDetailedStat():
    stat = dict()
    for item in statistikk_overskrifter():
        stat[item] = []
    return stat

def updateDetailedStat(stat,mainInfo,kom):
    stat['Dato'].append((mainInfo['dateandtime'],kom['kommunenavn'],kom['kommunenr']))
    stat['Lengde'].append((mainInfo['length'],kom['kommunenavn'],kom['kommunenr']))
    stat['Turtid'].append((mainInfo['tottime'],kom['kommunenavn'],kom['kommunenr']))
    stat['Gåtid'].append((mainInfo['walk_time'],kom['kommunenavn'],kom['kommunenr']))
    stat['Pausefaktor'].append((mainInfo['pause_faktor'],kom['kommunenavn'],kom['kommunenr']))
    stat['Gjennomsnittsfart'].append((mainInfo['avg_speed'],kom['kommunenavn'],kom['kommunenr']))
    #stat['Høyde'].append((mainInfo['hoyde2'],kom['kommunenavn'],kom['kommunenr'])) 
    stat['Høydemeter'].append((mainInfo['climbing'],kom['kommunenavn'],kom['kommunenr']))
    stat['Høydeforskjell'].append((mainInfo['elediff'],kom['kommunenavn'],kom['kommunenr']))
    stat['Bratthet'].append((mainInfo['steepness'],kom['kommunenavn'],kom['kommunenr']))
    stat['Klatrehastighet'].append((mainInfo['climbingrate'],kom['kommunenavn'],kom['kommunenr']))
    stat['Kuperthetsfaktor'].append((mainInfo['kupert_faktor'],kom['kommunenavn'],kom['kommunenr']))
    stat['Toppturfaktor'].append((mainInfo['topptur_faktor'],kom['kommunenavn'],kom['kommunenr']))
    
    return stat

def siste_rapporter_HTML(datolist):
    d = dict()
    rapports = sorted(datolist,reverse=True)[0:4]
    txtstring = ''
    for tur in rapports:
        txtstring += "<a href='{0}.html'>{1} {2}</a><br>".format(tur[2],tur[0].strftime("%Y-%m-%d"),tur[1])
    d['siste_rapporter'] = txtstring
    return  d

def create_stat_details(k_list):
    txtstr = ''
    for item in sorted(k_list,reverse=True):
        txtstr += """<div id="piclist"><img src='img/{2}.jpg' height='20px' align='left'><a href="{2}.html"><div align='right'>{1} - {0}</div></a></div>""".format(item[0],item[1],item[2])
    return txtstr

def create_stat_komm_grenser(k_list):
    txtstr = ''
    for i,item in enumerate(k_list):
        txtstr += """
var polygon{0} = L.polygon(
{1}, kommstyle).addTo(map);
polygon{0}.bindPopup("{2}<br>{3}");""".format(i,gpxtricks.getKommuneGrense(kommune=item[2]),item[1],item[0])
    return txtstr
        
def createWebpages():
    """ Load the rapport template """
    my_dir = os.path.dirname(__file__)
    template_dir = os.path.join(my_dir, 'res\\templates')
    myloader = FileSystemLoader(template_dir)
    env = Environment(loader=myloader)
    template_rapport = env.get_template('template_rapport.html')
    template_stat = env.get_template('template_stat.html')
    template_stat_expl = env.get_template('template_stat_forklaring.html')
    
    besteget = gpxtricks.get_besteget_kommuner(my_dir+'\\res\\kommunetopplisteV2.xml') # links to previous and next kommune.
    bC=2
    
    kommune_selected = gpxtricks.get_selected_kommune(my_dir+'\\res\\kommunetopplisteV2.xml') 
    
    ## Create a dict for each kommune
    komm_data = []
    # Create placeholders for tot stat data
    totstat = createTotStat()
    
    # Create placeholders for individual stat
    stat = createDetailedStat()
    
    for kom in gpxtricks.readkommunexml(my_dir+'\\res\\kommunetopplisteV2.xml'):
        
        # links to previuous and next kommune, updated select list, 
        kom['neste_kommune'] = besteget[bC]
        kom['forrige_kommune'] = besteget[bC-2]
        bC+=1
        print(kom)
        kom['select_fylkeliste'] = gpxtricks.get_selected_fylke(kom['kommunenr'])
        kom['select_kommuneliste'] = kommune_selected
        
        
        if kom['besteget'] == 'True':
            totstat['tot_antall_besteget'] +=1
        
        # Info from GPX file, if the file exist
        gpxfile = my_dir+"\\res\\gpx\\{0}.gpx".format(kom['kommunenr'])
        if os.path.isfile(gpxfile):
            
            gpx_df = gpxtricks.GPXtoDataFrame(gpxfile)
            kom['stoplocations'] = gpxtricks.exportStopLoc(gpx_df)
            kom['tripcoordinates'] = gpxtricks.exportRedPoints(gpx_df)
            gpxtricks.plotElevationProfile(gpx_df, 'C:\\python\\kommuner\\outdata\\profile2\\{}.png'.format(kom['kommunenr']))
            mainInfo = gpxtricks.getmainInfo(gpx_df)
            kom.update(mainInfo)
        
            stat = updateDetailedStat(stat, mainInfo, kom)
            
            totstat['tot_length'] += mainInfo['length']
            totstat['tot_elevation'] += mainInfo['climbing']
            totstat['tot_tottid'] += mainInfo['tottime']
        
        else:
            gpxfile_ex = my_dir+"\\res\\gpx\\{0}_ex.gpx".format(kom['kommunenr'])
            if os.path.isfile(gpxfile_ex):
                gpx_df = gpxtricks.GPXtoDataFrame(gpxfile_ex)
                kom['stoplocations'] = gpxtricks.exportStopLoc(gpx_df)
                kom['tripcoordinates'] = gpxtricks.exportRedPoints(gpx_df)
                gpxtricks.plotElevationProfile(gpx_df, 'C:\\python\\kommuner\\outdata\\profile2\\{}.png'.format(kom['kommunenr']))
                mainInfo = gpxtricks.getmainInfo(gpx_df)
                kom.update(mainInfo)
            
                stat = updateDetailedStat(stat, mainInfo, kom)    
        
        komm_data.append(kom)
        print(kom['kommunenavn'])
        
    
    totstat1 = modTotStat(totstat)
    siste_rapporter = siste_rapporter_HTML(stat['Dato'])
    # Creating the actual reports
    
    print("Starting creating reports!")
    
    for komm in komm_data:
        komm.update(totstat1)
        komm.update(siste_rapporter)
        
        file = open('C:\\python\\kommuner\\outdata\\{}.html'.format(komm['kommunenr']),'w',encoding='utf-8')
        file.write(template_rapport.render(komm))
        file.close()
        
    print("Finished creating reports!")

    # Lage forklaring til statistikk sidene. 
    newStatExpl = dict()
    newStatExpl['select_fylkeliste'] = gpxtricks.get_selected_fylke('00')
    newStatExpl['select_kommuneliste'] = kommune_selected
    newStatExpl.update(totstat1)
    newStatExpl.update(siste_rapporter)
    file = open('C:\\python\\kommuner\\outdata\\stat_forklaring.html','w',encoding='utf-8')
    
    newStat = dict()
    newStat['stat_select_list'] = select_statistikk_overskrifter()
    newStat.update(totstat1)
    newStat.update(siste_rapporter)
    
    for i,key in enumerate(statistikk_overskrifter()):
        newStat['stat_overskrift'] = key
        newStat['stat_detaljer'] = create_stat_details(stat[key])
        newStat['stat_komm_grenser'] = create_stat_komm_grenser(stat[key])
        
        
        file = open('C:\\python\\kommuner\\outdata\\stat{:0>2}.html'.format(i),'w',encoding='utf-8')
        file.write(template_stat.render(newStat))
        file.close()
    
createWebpages()

 