from functools import cache
from numexpr.necompiler import evaluate

pi : float = 3.141592653589793
e  : float = 2.718281828459045

class converter:

    conversion_keys={'sin^-1':'arcsin','cos^-1':'arccos','tan^-1':'arctan',
    '^':'**','++':'+','+-':'-','-+':'-','--':'+','cosec':'1/sin','sec':'1/cos','cot':'1/tan','e':str(e),'pi':str(pi),
    chr(960):str(pi)}

    reverse_converter={'(x)':'x','(y)':'y','**':'^',
    'arcsin': 'sin^-1', 'arccos': 'cos^-1', 'arctan': 'tan^-1',
    '1/sin': 'cosec', '1/cos': 'sec',
    '1/tan': 'cot', str(e): 'e', str(pi): chr(960)}
        

    def __init__(self,*args):
        '''A parser to convert string(s) from free-hand written mathematical expression(s)
           to a python-based form and vice-versa .'''
        self.__args=args

    def parse(self):
        '''Method converts free-hand written mathematical expression(s)
           to a python-based form.'''
        parsed_items=[]
        for iterable in self.__args:
            for key in converter.conversion_keys.keys(): #conversion of keys(functions and constants)
                if key in iterable:
                    iterable=iterable.replace(key,converter.conversion_keys[key])
            
            s=iterable[0]
            for index in range(1,len(iterable)): #check for brackets around variables
                if iterable[index]=='x':
                    if iterable[index-1].isdigit():
                        s+='*(x)'
                    else:
                        s+='(x)'
                elif iterable[index]=='y':
                    if iterable[index-1].isdigit():
                        s+='*(y)'
                    else:
                        s+='(y)'
                else:
                    s+=iterable[index]
            
            if '(x)(y)' in s:
                s=s.replace('(x)(y)','((x)*(y))')
            
            if '(y)(x)' in s:
                s=s.replace('(y)(x)','((x)*(y))')

            parsed_items.append(s)
            
        return tuple(parsed_items)

    def reparse(self):
        '''Method converts python-based arithematic expression(s)
           from free-hand written mathematical expression(s).'''
        reparsed_items=[]
        for iterable in self.__args:
            for key in converter.reverse_converter.keys():
                if key in iterable:
                    iterable=iterable.replace(key,converter.reverse_converter[key])
            reparsed_items.append(iterable)

        return tuple(reparsed_items)

class ImplicitExpressionError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        