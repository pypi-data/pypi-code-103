import re
import numpy as np
from PIL import Image
import collections

class Shannon_fano_encoding:
    def __init__(self, img_name):
        self.img_name = img_name
    
    def image_to_array(self):
        img_array = np.asarray(Image.open(self.img_name),np.uint8)
        list_string = str(img_array.tolist())
        return list_string

    def create_list(self, data):
        list = dict(collections.Counter(data)) 
        list_sorted = sorted(iter(list.items()), key = lambda k_v:(k_v[1],k_v[0]),reverse=True)
        final_list = []
        for key,value in list_sorted:
            final_list.append([key,value,''])
        return final_list

    def divide_list(self, list):
        if len(list) == 2:               
            return [list[0]],[list[1]]
        else:
            n = 0
            for i in list:
                n+= i[1]
            x = 0
            distance = abs(2*x - n)
            j = 0
            for i in range(len(list)):               
                x += list[i][1]
                if distance < abs(2*x - n):
                    j = i         
        return list[0:j+1], list[j+1:]
    c ={}
    def label_list(self, list):
        
        list1,list2 = self.divide_list(list)
        for i in list1:
            i[2] += '0'
            Shannon_fano_encoding.c[i[0]] = i[2]
        for i in list2:
            i[2] += '1'
            Shannon_fano_encoding.c[i[0]] = i[2]
        if len(list1)==1 and len(list2)==1:        
            return
        self.label_list(list2)
        return Shannon_fano_encoding.c

    def encode(self):
        data = self.image_to_array()
        return self.label_list(self.create_list(data))

