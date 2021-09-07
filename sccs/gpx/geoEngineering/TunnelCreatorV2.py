# -*- coding: UTF-8 -*-


import ezdxf
import math
import pandas as pd
from _operator import pos
import os


T_scale = 200      #skala på kartleggingskjema // Kan ikke endres

def hor_lines(start_coord, stop_coord, inc):
    l = []
    a = math.ceil(start_coord/inc)*inc
    print('hor_lines a:',a)
    
    if a != start_coord:
        l.append(start_coord)
        
    b = math.floor(stop_coord/inc)*inc
    print('hor_lines b:',b)
     
    for i in range(a,stop_coord, inc):
        l.append(i)
        
    l.append(stop_coord)
    return l

def getPages(start_coord, stop_Coord):
    a = math.floor(start_coord/T_scale)*T_scale
    b = math.ceil(stop_Coord/T_scale)*T_scale
    
    pages = int((b-a)/T_scale)
    
    ans = {'pages': pages, 'start':a}
    print(ans)
    
    return ans

def verticalLines(tunnelLayout):
    if tunnelLayout == 1:
        return verticalLines_199()
    else:
        return verticalLines_East()
        
def verticalLines_199():

    vl_max = 110/500*T_scale 
    vl_mid = 50/500*T_scale 
    return  [-vl_max,-vl_mid, 0, vl_mid, vl_max]   

def verticalLines_East():
    return [-21.5, 21.5, -10.25, 10.25, 0, 53.5, 63.75, 43.25, 75.0, 32.0]


def tunnelCreator_Run(tunnel_name, tunnel_start, tunnel_stop, tunnel_placeUp, tunnel_down, xlsx_fil_import, tunnelLayout ):
    "Tunnel parameteres"
    T_start = tunnel_start    # Pel ved tunnelportal
    T_stop = tunnel_stop
    T_length =  T_stop - T_start  #meter
    
    
    T_Name = tunnel_name
    T_Date = ''
    T_Reg = ''  
    T_PlaceUp = tunnel_placeUp
    T_PlaceDown = tunnel_down
    
    
    # Fil som skal importeres
    xlsx_file = xlsx_fil_import
    
    drawing = ezdxf.new(dxfversion='R2010')
    drawing.styles.new('myStandard', dxfattribs={'font' : 'OpenSans-Regular.ttf'})
    
    "Layers"
    drawing.layers.new('V_Background', dxfattribs={'color': 0})
    drawing.layers.new('V_Background_grid', dxfattribs={'color': 8})
    drawing.layers.new('V_rightField', dxfattribs={'color': 0})
    drawing.layers.new('V_PaperRightField', dxfattribs={'color': 0})
    
    drawing.layers.new('V_import_point', dxfattribs={'color': 252})
    
    
    drawing.layers.new('Markering_ny', dxfattribs={'color': 1})
    drawing.layers.new('Markering_eksisterende', dxfattribs={'color': 5})
    drawing.layers.new('Registeringer_generell', dxfattribs={'color': 0})
    drawing.layers.new('Registeringer_test', dxfattribs={'color': 0})
    
    drawing.layers.new('PDF_Import', dxfattribs={'color': 0})
    drawing.layers.new('PDF_Registered', dxfattribs={'color': 0})

    modelspace = drawing.modelspace()
    
    "Background_grid - Modelspace"
    txtSize = T_scale/100
    vl_max = 110/500*T_scale
    
    
    vertical_lines = verticalLines(tunnelLayout) 
    
    
    for x in vertical_lines:
        modelspace.add_line((x, T_start), (x,T_stop), dxfattribs={'layer': 'V_Background_grid'})
     
       
    for i in hor_lines(T_start, T_stop, T_scale//20):
        if tunnelLayout == 1:
            modelspace.add_line((-vl_max, i), (vl_max,i), dxfattribs={'layer': 'V_Background_grid'})
        else: 
            modelspace.add_line((-21.5, i), (21.5,i), dxfattribs={'layer': 'V_Background_grid'})
            modelspace.add_line((32, i), (75.0,i), dxfattribs={'layer': 'V_Background_grid'})
        
    
    for i in hor_lines(T_start, T_stop, T_scale//10):
        if tunnelLayout == 1:
            modelspace.add_text(str(i), dxfattribs={'layer': 'V_Background', 'height': txtSize}).set_pos((-vl_max-2, i-1), align='RIGHT')
        else: 
            modelspace.add_text(str(i), dxfattribs={'layer': 'V_Background', 'height': 2}).set_pos((-22, i-1), align='RIGHT')
        
    
    
    'Div registration blocks'
    
    pos_x = 300
    pos_y = T_start + 100
    
    
    block_bolt = drawing.blocks.new(name = "Bolt")
    block_bolt.add_circle((0,0),0.75)
    block_bolt.add_circle((0,0),1.25)
    
    block_rensk = drawing.blocks.new(name = "Rensk")
    block_rensk.add_lwpolyline([(-0.5867,0.4887),(0.7248,0.2875), (-0.4861,-0.0058), (0.4142,-0.2415), (-0.3020,-0.3593), (0.1812,-0.4254)])
    
    block_luke = drawing.blocks.new(name = "Luke")
    block_luke.add_lwpolyline([(-1.5,-1.5),(1.5,-1.5), (1.5,1.5), (-1.5,1.5), (-1.5,-1.5)])
    block_luke.add_text('L', dxfattribs={'height': 1.5}).set_pos((0,0), align='MIDDLE_CENTER')

    block_luke = drawing.blocks.new(name = "Door")
    block_luke.add_lwpolyline([(-1.5,-1.5),(1.5,-1.5), (1.5,1.5), (-1.5,1.5), (-1.5,-1.5)])
    block_luke.add_text('D', dxfattribs={'height': 1.5}).set_pos((0,0), align='MIDDLE_CENTER')

    
    modelspace.add_blockref('Bolt',(pos_x,pos_y+5), dxfattribs={'layer': 'Markering_ny'})
    modelspace.add_blockref('Bolt',(pos_x+3,pos_y+5), dxfattribs={'layer': 'Markering_eksisterende'})
    modelspace.add_blockref('Rensk',(pos_x,pos_y+2.5), dxfattribs={'layer': 'Markering_ny','xscale': 1.5,'yscale': 1.5})
    modelspace.add_blockref('Rensk',(pos_x+3,pos_y+2.5), dxfattribs={'layer': 'Markering_eksisterende','rotation': 30})
    modelspace.add_blockref('Luke',(pos_x,pos_y+7.5), dxfattribs={'layer': 'Markering_ny','rotation': 0})
    modelspace.add_blockref('Luke',(pos_x+3,pos_y+7.5), dxfattribs={'layer': 'Markering_eksisterende','rotation': 0})
    modelspace.add_blockref('Door',(pos_x,pos_y+10.5), dxfattribs={'layer': 'Markering_ny','rotation': 0})
    modelspace.add_blockref('Door',(pos_x+3,pos_y+10.5), dxfattribs={'layer': 'Markering_eksisterende','rotation': 0})

    
    hatch_portal = modelspace.add_hatch(color=254 , dxfattribs={'layer': 'Registeringer_generell'})
    with hatch_portal.edit_boundary() as boundary:
        boundary.add_polyline_path([(100, pos_y+10), (143, pos_y+10), (143, pos_y+20), (100, pos_y+20)], is_closed=1)
    modelspace.add_text('Portal', dxfattribs={'layer': 'Registeringer_generell', 'height': txtSize}).set_pos((121.5, pos_y+15), align='MIDDLE_CENTER')   
    
    hatch_PE = modelspace.add_hatch(color=141, dxfattribs={'layer': 'Registeringer_generell'})
    with hatch_PE.edit_boundary() as boundary:
        boundary.add_polyline_path([(100, pos_y+22), (121.5, pos_y+22), (121.5, pos_y+32), (100, pos_y+32)], is_closed=1)
    modelspace.add_text('PE-skum', dxfattribs={'layer': 'Registeringer_generell', 'height': txtSize}).set_pos((110.35, pos_y+37), align='MIDDLE_CENTER')   
    
    'Lage tegneforklaring i modelspace'
    reg_list = ["F1","F2","F3","F4","F5","F6","F7","S1","S2","S3","S4","S5","S6","S7","S8","S9","B1x","B2","B3","B4","B5","M1","M2","M3","M4","M5", "I/X", "X", "L", "D"]
    
    for sym in reg_list:
        modelspace.add_text(sym, dxfattribs={'layer': 'Markering_ny', 'height': txtSize}).set_pos((pos_x, pos_y), align='MIDDLE_CENTER')
        modelspace.add_text(sym, dxfattribs={'layer': 'Markering_eksisterende', 'height': txtSize}).set_pos((pos_x+3, pos_y), align='MIDDLE_CENTER')
        modelspace.add_text(sym, dxfattribs={'layer': 'Registeringer_generell', 'height': txtSize}).set_pos((pos_x+6, pos_y), align='MIDDLE_CENTER')
        pos_y = pos_y - 2.5
    
    
    'Les tegneforklaring / Full tekst fra fil'
    with open("C:\\python_proj\\tunnelinspek\\legend_mal.txt", encoding="utf-8") as f:
        content = f.readlines()
        
    
    "Create paperspace"
    'Legend block'
    block_legend = drawing.blocks.new(name = "Legend")
    pos_y = 100
    
    for t in content:
        txt = str(t).replace('\n','')
        print(txt)
        block_legend.add_text(txt, dxfattribs={ 'height': 1.5,'layer': 'V_rightField'}).set_pos((0, pos_y), align='LEFT')
        block_legend.add_line((-2, pos_y-0.25), (48,pos_y-0.1),dxfattribs={'layer': 'V_rightField'})
        pos_y = pos_y - 2.5
        
    block_legend.add_line((-2, pos_y+2.25), (-2,102.5),dxfattribs={'layer': 'V_rightField'})
    block_legend.add_line((48, pos_y+2.25), (48,102.5),dxfattribs={'layer': 'V_rightField'})
    block_legend.add_line((-2, 102.5), (48,102.5),dxfattribs={'layer': 'V_rightField'})
    
    'Notes block'
    block_notes = drawing.blocks.new(name = "Notes")
    block_notes.add_line((0, 0), (0, 130),dxfattribs={'layer': 'V_rightField'})
    block_notes.add_line((50, 0), (50, 130),dxfattribs={'layer': 'V_rightField'})
    block_notes.add_line((0, 0), (50, 0),dxfattribs={'layer': 'V_rightField'})      
    block_notes.add_line((0, 130), (50, 130),dxfattribs={'layer': 'V_rightField'})      
    block_notes.add_text('Notater:', dxfattribs={'height': 1.5,'layer': 'V_rightField'}).set_pos((1, 128), align='LEFT')
    
    'Header block'
    block_header = drawing.blocks.new(name = "Header")
    block_header.add_text('Bilag 2 - Oversikt over registreringer', dxfattribs={'layer': 'V_Background', 'height': 3}).set_pos((0.6, 265), align='LEFT')
    block_header.add_line((0, 263), (180, 263), dxfattribs={'layer': 'V_Background'})
    block_header.add_line((0, 255), (180, 255), dxfattribs={'layer': 'V_Background'})
    block_header.add_line((0, 255), (0, 263), dxfattribs={'layer': 'V_Background'})
    block_header.add_line((79, 255), (79, 263), dxfattribs={'layer': 'V_Background'})
    block_header.add_line((108, 255), (108, 263), dxfattribs={'layer': 'V_Background'})
    block_header.add_line((180, 255), (180, 263), dxfattribs={'layer': 'V_Background'})
    
    block_header.add_text('Tunnel (og løp)', dxfattribs={'layer': 'V_Background', 'height': 1.5}).set_pos((1, 261), align='LEFT')
    block_header.add_text('Dato', dxfattribs={'layer': 'V_Background', 'height': 1.5}).set_pos((80, 261), align='LEFT')
    block_header.add_text('Registert av', dxfattribs={'layer': 'V_Background', 'height': 1.5}).set_pos((109, 261), align='LEFT')
                          
    block_header.add_text(T_Name, dxfattribs={'layer': 'V_Background', 'height': 3}).set_pos((1, 256), align='LEFT')
    block_header.add_text(T_Date, dxfattribs={'layer': 'V_Background', 'height': 3}).set_pos((80, 256), align='LEFT')
    block_header.add_text(T_Reg, dxfattribs={'layer': 'V_Background', 'height': 3}).set_pos((109, 256), align='LEFT')

    'Document control'
    block_drawnby = drawing.blocks.new(name = "drawnBy")
    block_drawnby.add_line((0, 2.5), (50, 2.5),dxfattribs={'layer': 'V_rightField'})
    block_drawnby.add_line((0, 5), (50, 5),dxfattribs={'layer': 'V_rightField'})
    block_drawnby.add_line((0, 7.5), (50, 7.5),dxfattribs={'layer': 'V_rightField'})
    block_drawnby.add_line((13, 0), (13, 7.5),dxfattribs={'layer': 'V_rightField'})
    block_drawnby.add_line((31, 0), (31, 7.5),dxfattribs={'layer': 'V_rightField'})
    block_drawnby.add_text('Dato', dxfattribs={'layer': 'V_rightField', 'height': 1.5}).set_pos((1, 5.5), align='LEFT')
    block_drawnby.add_text('Tegnet av', dxfattribs={'layer': 'V_rightField', 'height': 1.5}).set_pos((14, 5.5), align='LEFT')
    block_drawnby.add_text('Kontrollert av', dxfattribs={'layer': 'V_rightField', 'height': 1.5}).set_pos((32, 5.5), align='LEFT')
    
    pages = getPages(T_start, T_stop)
    p = getPages(T_start, T_stop)['start']
    
    
    l = []
    for paper in range(getPages(T_start, T_stop)['pages']):
        l.append(paper)
        l[paper] = drawing.layouts.new('Pel {} - {}'.format(p,p+T_scale))
        l[paper].page_setup(size=(210,297),margins=(10, 5, 10, 5),offset=(5.7,-4.8),scale=(1,0.9546), units='mm')
        
        if tunnelLayout == 1:
            l[paper].add_viewport(center=(65, 130), size=(130, 240), view_center_point=(0, p + (T_scale/2)), view_height=T_scale+T_scale*0.02)
        else:
            l[paper].add_viewport(center=(65, 130), size=(130, 240), view_center_point=(26, p+100), view_height=205)
        p = p + T_scale
    
    
    
        'Sett på notat og tegneforklaring felt : Comment / Uncomment'
        l[paper].add_blockref('Legend',(132,147), dxfattribs={
            'xscale': 1,
            'yscale': 1,
            'rotation': 0,
            'layer': 'V_PaperRightField'
        })
        
        'Notater og kontrollert av '
        l[paper].add_blockref('Notes', (130,10), dxfattribs={'layer': 'V_PaperRightField'})
        l[paper].add_blockref('drawnBy', (130,10), dxfattribs={'layer': 'V_PaperRightField'})
        
        'Header'
        l[paper].add_blockref('Header', (0,0))
        
        
        #l[paper].add_text('Inspeksjon - Kartleggingsskjema', dxfattribs={'layer': 'V_Background', 'height': 3}).set_pos((0.6, 265), align='LEFT')
        
    
    
        'Tunnelinformation'
    #    l[paper].add_text('Skaderegistrering', dxfattribs={'layer': 'V_Background', 'height': 1.5}).set_pos((35, 7), align='CENTER')
    #    l[paper].add_text('Fremkommelighet', dxfattribs={'layer': 'V_Background', 'height': 1.5}).set_pos((96.5, 7), align='CENTER')
        l[paper].add_text(T_PlaceDown, dxfattribs={'layer': 'V_Background', 'height': 2}).set_pos((65, 5), align='CENTER')
        l[paper].add_text(T_PlaceUp, dxfattribs={'layer': 'V_Background', 'height': 2}).set_pos((65, 251), align='CENTER')
        
        if tunnelLayout != 0:
            l[paper].add_text("Skaderegistering", dxfattribs={'layer': 'V_Background', 'height': 2}).set_pos((34.561, 8), align='CENTER')
            l[paper].add_text("Fremkommelighet", dxfattribs={'layer': 'V_Background', 'height': 2}).set_pos((97.1951, 8), align='CENTER')
        
    
    'Les inn notater fra Excel-ark: KUN HVIS EXCEL ARK EKSISTERER'
    
    if os.path.isfile(xlsx_file):
        df_obs = pd.read_excel (xlsx_file, header=0)
         
        print(df_obs['Kommentar']) 
         
        for index, row in df_obs.iterrows():
            pel = 0
            pos = -100
            
            if tunnelLayout == 2: 
                vl_max = 21.5
                               
            try:
                pel = float(row['Pel'])
                pos = row['Pos']
                   
                try: 
                    if pos > -100 or pos < 100:
                        pos = float(pos)*vl_max/100
                    else: 
                        pos = 0.0
                except:
                    pel = 0.0
                    pos = 0.0
                   
                if row['Symbol'] == 'Bolt':
                    modelspace.add_blockref('Bolt',(pos,pel), dxfattribs={'layer': 'V_import_point'})
                elif row['Symbol'] == 'Rensk':
                    modelspace.add_blockref('Rensk',(pos,pel), dxfattribs={'layer': 'V_import_point','xscale': 1,'yscale': 1,})
                elif row['Symbol'] == 'Luke':
                    modelspace.add_blockref('Luke',(pos,pel), dxfattribs={'layer': 'V_import_point','xscale': 1,'yscale': 1,})
                elif row['Symbol'] == 'Dør':
                    modelspace.add_blockref('Door',(pos,pel), dxfattribs={'layer': 'V_import_point','xscale': 1,'yscale': 1,})
                
                else: 
                    modelspace.add_text(row['Symbol'], dxfattribs={'layer': 'V_import_point', 'height': 1.5}).set_pos((pos, pel), align='MIDDLE_CENTER')
                    modelspace.add_text(row['Kommentar'], dxfattribs={'layer': 'V_import_point', 'height': 1.2}).set_pos((pos, pel-1.5), align='MIDDLE_CENTER')
                   
            except:
                print("Error:",row['Pel'],row['Tekst'])
            
    
    dwg_filename = 'C:\\python_proj\\tunnelinspek\\{}.dxf'.format(T_Name)
    drawing.saveas(dwg_filename)
    
    print("Drawing saved:", dwg_filename)

if __name__ == '__main__':
    tunnelCreator_Run('Updated - Kontrollert av 2', 12000, 13400, '-', '-', 'C:\\Users\\A485753\\Desktop\\Prosjekter lokalt\\19500 Tunnelinspeksjoner\\tem.xlsx',1)
    
""" To FIX:
Feilmelding hvis Pel kolonne ikke har tall. """