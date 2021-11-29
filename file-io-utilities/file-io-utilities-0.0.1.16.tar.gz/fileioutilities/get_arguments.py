import sys 

def get_arguments():

    args = {}
    for _ in sys.argv[1:]:
        if "=" in _:
            p = _.split('=')
            args[p[0].replace("--", "", 1)] = p[1]
    return args



def get_argument(argument):
    if argument in get_arguments().keys():
        return get_arguments()[argument]

