
def parse_exeption(excinfo):
    return excinfo.value.args[0].split('\n')[1:]

