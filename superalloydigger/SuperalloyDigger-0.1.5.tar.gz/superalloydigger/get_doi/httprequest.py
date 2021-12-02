# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 11:38:48 2019

@author: JiangXue
"""

import requests 
import xlrd

def data_totxt(sample,path):
    f = open(path,'w',encoding='utf-8')
    f.write(sample)
    f.close()
    

header={'Accept':'text/plain','CR-TDM-Rate-Limit':'4000','CR-TDM-Rate-Limit-Remaining':'76','CR-TDM-Rate-Limit-Reset':'1378072800'}

url_publisher = "https://api.elsevier.com/content/article/doi/" #如果获取全文的话，将abstract替换成article
APIKey="APIKey=aa1b99025fb64e69ff251ad6de1f784a" #developer Elsevier 申请的
arformat = "text/plain" #text/xml,text/plain
data = xlrd.open_workbook(r'alloyDOI.xlsx')
table =data.sheet_by_index(0)
 #输出为数组的形式，好像只能指定某一行输出
start=4671 #开始的行
end=4972 #结束的行
rows=end-start
list_values=[]
for x in range(start,end):
  values=[]
  row =table.row_values(x)
  values.append(row[1])
  list_values.append(values)
dois = list_values
count = len(dois)
articles = []
k = 4671
for i in range(0,count):
    url = url_publisher+str(dois[i][0])+"?"+APIKey+"&httpAccept="+arformat
    #url = "https://api.elsevier.com/content/article/doi/10.1016/j.matchar.2013.01.008?APIKey=36697d0dea0745f5f236356d7f5cd38f&httpAccept=text/plain"
    r = requests.get(url,headers=header)
    print(r.content)
#    path = str(i)+".txt"
    path = r'E:\文本挖掘\陶瓷膜的文献\文献下载doi\web_4971_txt/'+str(k)+".txt"
    k += 1
    data_totxt(r.content.decode(),path)
    



