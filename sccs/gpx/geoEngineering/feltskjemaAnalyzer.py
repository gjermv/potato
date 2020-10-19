# -*- coding: UTF-8 -*-

import ezdxf
import os



def prettyPrintText(txtObj,T_scale):
    pos = txtObj.get_pos()[1]
    y_pos = int(pos[1])
    txt = txtObj.dxf.text
    
    if pos[0] < -110/500*T_scale :
        return('{};Utenfor skjema;{};\n'.format(y_pos,txt))    
    elif pos[0] < -50/500*T_scale :
        return('{};v.s vegg;{}\n'.format(y_pos,txt))
    elif pos[0] < 0:
        return('{};v.s. vederlag/heng;{}\n'.format(y_pos,txt))
    elif pos[0] < 50/500*T_scale :
        return('{};h.s. vederlag/heng;{}\n'.format(y_pos,txt))
    elif pos[0] < 110/500*T_scale :
        return('{};h.s. vegg;{}\n'.format(y_pos,txt))
    else:
        return('{};Utenfor skjema;{}\n'.format(y_pos,txt))
    
def prettyPrintBlock(blckObj,T_scale):
    pos = blckObj.dxf.insert
    y_pos = int(pos[1])
    txt = blckObj.dxf.name
    
    
    if pos[0] < -110/500*T_scale :
        return('{};Utenfor skjema;{}\n'.format(y_pos,txt))    
    elif pos[0] < -50/500*T_scale :
        return('{};v.s vegg;{}\n'.format(y_pos,txt))
    elif pos[0] < 0:
        return('{};v.s. vederlag/heng;{}\n'.format(y_pos,txt))
    elif pos[0] < 50/500*T_scale :
        return('{};h.s. vederlag/heng;{}\n'.format(y_pos,txt))
    elif pos[0] < 110/500*T_scale :
        return('{};h.s. vegg;{}\n'.format(y_pos,txt))
    else:
        return('{};Utenfor skjema;{}\n'.format(y_pos,txt))
    
def analyseDXF(fname, dxflayer = "Markering ny",T_scale = 500):
    csv_file = fname.split('.')[0] + '.csv'
    f = open(csv_file,'w+')
    
    
    dxf_file = ezdxf.readfile(fname)
    for obj in dxf_file.entities:
        if obj.dxf.layer == dxflayer:
            if obj.dxftype() == "TEXT":
                f.write(prettyPrintText(obj,T_scale))
                
    
    for obj in dxf_file.entities:
        if obj.dxf.layer == dxflayer:
            if obj.dxftype() == "INSERT":
                
                f.write(prettyPrintBlock(obj,T_scale))
    
    f.close()
    
    return 1


if __name__ == '__main__':
    fname = 'C:\\python_proj\\tunnelinspek\\Kartleggingsskjema Ljøtunnelen.dxf'
    analyseDXF(fname)
    
    print ('Ferdig')