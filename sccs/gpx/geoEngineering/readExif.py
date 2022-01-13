# -*- coding: utf-8 -*-

import PIL.Image
import glob
img = PIL.Image.open('T:\\19500 - Tunnelinspeksjoner SVV Region Øst 2019\\024 Operatunnelen (Svartdal)\\03 Bilder\\Svartdaltunnelen\\Lag 2 - GVi//IMG_7739.JPG')
exif_data = img._getexif()

for image in glob.glob('T:\\19500 - Tunnelinspeksjoner SVV Region Øst 2019\\024 Operatunnelen (Svartdal)\\03 Bilder\\Svartdaltunnelen\\Lag 2 - GVi//*.JPG'):
    img = PIL.Image.open(image)
    exif_data = img._getexif()
    try: 
        image_text =  exif_data[270]
        if len(image_text.split('\n')) == 2:
            
            print(image_text.split('\n')[1].split(' '))
    except:
        print(image)
