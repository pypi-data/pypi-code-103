def log(fname, content):
    f = open(fname, "at")
    f.write(content)
    f.close()