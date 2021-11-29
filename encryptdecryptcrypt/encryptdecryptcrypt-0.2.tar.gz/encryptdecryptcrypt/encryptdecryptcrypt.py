def decrypt(text, offset):
    x=-1
    tex=[]
    for i in text:
        if x!=len(offset)-1:
            x+=1
        else:
            x=0
        tex.append(chr(ord(i)-offset[x]))
    return ''.join(tex)
def encrypt(text,offset):
    x=-1
    tex=[]
    for i in text:
        if x!=len(offset)-1:
            x+=1
        else:
            x=0
        tex.append(chr(ord(i)+offset[x]))
    return ''.join(tex)
def encryptfromfile(filename):
    off=[31, 67, 5, 53, 86, 5, 34, 51, 84, 62, 67, 100, 77, 60, 66, 74, 61, 74, 54, 65, 78, 76, 41, 73, 31, 73, 66, 9, 46, 11, 100, 79, 64, 32, 13, 42, 23, 47, 67, 18, 15, 49, 28, 79, 73, 38, 6, 88, 58, 65, 85, 91, 35, 34, 81, 65, 86, 61, 45, 40, 92, 95, 9, 70, 1, 3, 29, 84, 87, 39, 28, 75, 64, 52, 47, 95, 66, 44, 13, 5, 74, 23, 10, 62, 8, 17, 51, 12, 16, 80, 75, 67, 45, 59, 39, 40, 87, 58, 82, 43]
    red=open(filename,encoding="utf-8")
    red=red.read()
    file=open(filename,'w',encoding="utf-8")
    file.write(encrypt(red,off))
def decryptfromfile(filename):
    off=[31, 67, 5, 53, 86, 5, 34, 51, 84, 62, 67, 100, 77, 60, 66, 74, 61, 74, 54, 65, 78, 76, 41, 73, 31, 73, 66, 9, 46, 11, 100, 79, 64, 32, 13, 42, 23, 47, 67, 18, 15, 49, 28, 79, 73, 38, 6, 88, 58, 65, 85, 91, 35, 34, 81, 65, 86, 61, 45, 40, 92, 95, 9, 70, 1, 3, 29, 84, 87, 39, 28, 75, 64, 52, 47, 95, 66, 44, 13, 5, 74, 23, 10, 62, 8, 17, 51, 12, 16, 80, 75, 67, 45, 59, 39, 40, 87, 58, 82, 43]
    file=open(filename,encoding="utf-8")
    text=file.read()
    return decrypt(text,off)
