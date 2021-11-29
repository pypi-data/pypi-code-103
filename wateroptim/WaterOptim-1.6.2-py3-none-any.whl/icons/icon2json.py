# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 05:40:41 2021

@author: HEDI
"""
import json
data={}
import base64
import os
for d in os.listdir():
    if d.endswith('.png'):
        with open(d, "rb") as imageFile:
            str = base64.b64encode(imageFile.read())
            
            data[d.replace('.png','')]=str.decode('utf-8')

with open('icons.json', 'w') as json_file:
    json.dump(data,json_file)