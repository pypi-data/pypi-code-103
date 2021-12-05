# gobal unspecifc exceptions
class utlityErrors(Exception):
    pass

class pathError(utlityErrors):
    pass

class Depreciated(utlityErrors):
    pass

class DepreciatedFunction(Exception):
    def __init__(self, source, function_name):
        errmsg = """The function .{}() from {} is depreicated""".format(function_name, source)
        raise Depreciated(errmsg)
