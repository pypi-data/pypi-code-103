class ClassA:
    def __init__(self):
        print(__name__)

    
    def __call__(self, x: object):
        print(x)


def func_a():
    print(__name__)


def func_b():
    print(__name__)
    

def main():
    print(__name__)

    
if(__name__=='__main__'):
    main()