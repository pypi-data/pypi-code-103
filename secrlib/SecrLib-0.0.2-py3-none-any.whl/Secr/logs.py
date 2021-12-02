import os
def log(fname, content):
    f = open(fname, "at")
    f.write(content)
    f.close()
def logcopy(fname, ffname):
        f = open(fname, "rt")
        ff = open(ffname, "at")
        ff.write(f.read())
        f.close()
        ff.close()
def logwordfind(fname, content):
    pass
def logcopyremove(fname, ffname):
    f = open(fname, "rt")
    ff = open(ffname, "at")
    ff.write(f.read())
    try:
        os.remove(fname)
    except:
        print("File doesn't exist.")
    f.close()
    ff.close()
def logmake(fname):
    f = open(fname, "x")
    f.close()
def logdelete(fname):
    try : 
        os.remove(fname)
    except : 
        print("File doesn't exist")
