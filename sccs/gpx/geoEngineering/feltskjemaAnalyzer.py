# -*- coding: UTF-8 -*-

import ezdxf
import os



def prettyPrintText(txtObj,T_scale):
    pos = txtObj.get_pos()[1]
    x_pos = int(pos[0])
    y_pos = int(pos[1])
    txt = txtObj.dxf.text
    layer = txtObj.dxf.layer
    
    if pos[0] < -110/500*T_scale :
        return('{};{};Utenfor skjema;{};{};\n'.format(y_pos,x_pos,txt,layer))    
    elif pos[0] < -50/500*T_scale :
        return('{};{};v.s vegg;{};{}\n'.format(y_pos,x_pos,txt,layer))
    elif pos[0] < 0:
        return('{};{};v.s. vederlag/heng;{};{}\n'.format(y_pos,x_pos,txt,layer))
    elif pos[0] < 50/500*T_scale :
        return('{};{};h.s. vederlag/heng;{};{}\n'.format(y_pos,x_pos,txt,layer))
    elif pos[0] < 110/500*T_scale :
        return('{};{};h.s. vegg;{};{}\n'.format(y_pos,x_pos,txt,layer))
    else:
        return('{};{};Utenfor skjema;{};{}\n'.format(y_pos,x_pos,txt,layer))
    
def prettyPrintBlock(blckObj,T_scale):
    pos = blckObj.dxf.insert
    x_pos = int(pos[0])
    y_pos = int(pos[1])
    txt = blckObj.dxf.name
    layer = blckObj.dxf.layer
    
    
    if pos[0] < -110/500*T_scale :
        return('{};Utenfor skjema;{};{};\n'.format(y_pos,txt,layer))    
    elif pos[0] < -50/500*T_scale :
        return('{};v.s vegg;{};{}\n'.format(y_pos,txt,layer))
    elif pos[0] < 0:
        return('{};v.s. vederlag/heng;{};{}\n'.format(y_pos,txt,layer))
    elif pos[0] < 50/500*T_scale :
        return('{};h.s. vederlag/heng;{};{}\n'.format(y_pos,txt,layer))
    elif pos[0] < 110/500*T_scale :
        return('{};h.s. vegg;{};{}\n'.format(y_pos,txt,layer))
    else:
        return('{};Utenfor skjema;{};{}\n'.format(y_pos,txt,layer))
    
def analyseDXF(fname, dxflayer = "Markering ny",T_scale = 500):
    
    csv_file = fname.replace('dxf','csv')
    f = open(csv_file,'w+')
    f.write('Pel;Pos;Side;Registrering;Lag;Bildenavn;Beskrivelse;Plassforhold;Retning;Tiltak;Plassering;Nedfall\n')
    
    dxf_file = ezdxf.readfile(fname)
    
    for obj in dxf_file.entities:
        if obj.dxftype() == "TEXT":
            
            f.write(prettyPrintText(obj,T_scale))
                
    
    for obj in dxf_file.entities:
        if obj.dxf.layer == dxflayer:
            if obj.dxftype() == "INSERT":
                
                f.write(prettyPrintBlock(obj,T_scale))
    
    f.close()
    print(csv_file,'OK')
    return 1


if __name__ == '__main__':
    fname = 'C:\\Users\\gjermund.vingerhagen\\Documents\\637592-06\\Kongsbergtunnelen - østgående.dxf'
    analyseDXF(fname)
    
    print ('Ferdig')