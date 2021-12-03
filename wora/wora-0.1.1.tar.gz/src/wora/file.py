def read_file(fname: str) -> str:
    file = open(fname, 'r')
    res = file.read()
    file.close()
    return res

def write_file(fname: str, content: str) -> str:
    file = open(fname, 'w')
    file.write(content)
    file.close()
