def read_file(fname: str) -> str:
    file = open(fname, 'r')
    res = file.read()
    file.close()
    return res
