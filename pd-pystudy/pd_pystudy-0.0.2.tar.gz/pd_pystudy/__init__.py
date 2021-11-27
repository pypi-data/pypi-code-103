import pd_pystudy
name = "pd_pystudy"

def chnum(num,change):
    #将数字转换为想要的进制
    try:
        if change == '10-2':
            finalnum = bin(num)
        elif change == '2-10':
            finalnum = int(num,2)
        elif change == '10-16':
            finalnum = hex(num)
        elif change == '16-10':
            finalnum = int(num,16)
        elif change == '2-16':
            finalnum = hex(int(num,2))
        elif change == '16-2':
            finalnum = bin(int(num,16))
        return finalnum
    except:
        return 'ERROR'

def remele(content,list):
    #删除列表内某些元素的所有
    try:
        while content in list:
            list.remove(content)
        return list
    except:
        return 'ERROR'

def cheele(content,list):
    #确认某些内容是否在列表
    try:
        if content in list:
            return True
        else:
            return False
    except:
        return False
    


def findele(element,list):
    try:
        indexnum = []
        if cheele(element,list) == True:
            while element in list:
                eleindex = list.index(element)
                indexnum.append(eleindex)
                list.remove(element)
                list.insert(eleindex,'')
            for reele in indexnum:
                list.insert(reele,element)
            return indexnum
        if cheele(element,list) == False:
            return None
    except:
        return 'ERROR'
