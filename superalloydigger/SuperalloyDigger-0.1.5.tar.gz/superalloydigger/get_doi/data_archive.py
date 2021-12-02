# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 10:32:00 2019

@author: JiangXue
"""


from pandas import DataFrame

def data_archive(sample,filename,sheet):   
    data  = DataFrame(sample)
    DataFrame(data).to_excel(filename,sheet_name=sheet)
    

if __name__ == '__main__':
    sample = [[1,2],[1,3],[3,4]]
    data_archive(sample,"1.xlsx","test")