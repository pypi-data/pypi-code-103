import threading
from utils.thread_helpers.animations import animate_iteration

def thread(func, args=None, daemon=True):
    '''
    Must be a function in without ()
    example if the function is def hello():
    thread would be called like so thread(func=hello, args=['argument1', 'argument2']
    '''
    if args is None:
        args = []

    Obj = threading.Thread(target=func, args=args, daemon=daemon)
    Obj.start()
    return Obj

def multiple_threads(function_data, daemon=True):
    """
    Functions must be in a list like so [function1, function2, function3]
    :param daemon:
    true by default
    :param function_data:

    List of Dictionary like so
    function_data = [
        {
        'function' : function
        'args' : [arg1, arg2]
        }
    ]

    :return:
    A list of all the started threads
    """
    x = 0
    Objs = []
    for f in function_data:
        Args = f['args']
        if Args == None:
            Args = []

        Function = f['function']
        Objs.append(threading.Thread(target=Function, args=Args, daemon=daemon))


    for o in Objs:
        o.start()


    return Objs

