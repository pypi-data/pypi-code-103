'''
A library for all sort of calculus problems and graphing solutions.

Get instant results with fewer lines of code and more readability.

For any query contact zarexdhruv@gmail.com or get help from

https://sites.google.com/view/dscal3/home

'''
from dscal.dsmath import factorial
from dscal.tools import converter , evaluate 
import sympy as sym
import matplotlib.pyplot as plt

class calculus:

    def __init__(self,*expression,**options):
        '''A toolkit for handling calculus problems and their visual interpretation.'''
        
        self.__exp=expression
        self.__parsed=converter(*expression).parse()
        self.__Symbol={'x':sym.symbols('x'),'y':sym.symbols('y')}
        self.__set={'wrt':'x','limit':(-10,10),'style':'ggplot','colormap':plt.cm.cool}
        
        self.__acceptableKeys=('wrt','limit','style','colormap')
        for attr in options:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'calculus' object has no attribute '{attr}'")            
        else:
            self.__set.update(options)        

    def derivative(self):
        '''Returns dervative of the given expression(s).
        
        >>> from dscal import calculus
        >>> expr=calculus('secx')
        >>> expr.derivative()
        'sinx/cosx^2'
        >>> '''
        respect=self.__Symbol[self.__set['wrt']]
        derivatives=tuple(map(lambda exp:str(sym.diff(exp)),self.__parsed))
        
        return converter(*derivatives).reparse()

    def integral(self,interval=None):
        '''Returns integration of the given expression(s).
        
        >>> from dscal import calculus
        >>> expr=calculus('logx')
        >>> expr.integral()
        'x*logx - x'
        >>> expr.integral(interval=[1,10])
        '-9 + 10*log(10)'
        >>> '''

        respect=self.__Symbol[self.__set['wrt']]
        if interval==None:
            integrals=tuple(map(lambda exp:str(sym.integrate(exp,respect)),self.__parsed))
        else:
            integrals=tuple(map(lambda exp:str(sym.integrate(exp,(respect,interval[0],interval[1]))),self.__parsed))
        
        return converter(*integrals).reparse()
    
    def factorize(self):
        '''If factorizable ,returns factorized form of the expression 
        
        >>> from dscal import calculus
        >>> expr=calculus('x^3-1')
        >>> expr.factorize()
        '(x - 1)*(x^2 + x + 1)'
        >>> '''

        respect=self.__Symbol[self.__set['wrt']]
        factors_list = []
        
        for items in self.__parsed:
            try:
                x=str(sym.factor(items,respect))
                factors_list.append(x)
            except Exception as e:
                factors_list.append('not factorizable')
        
        factors=tuple(factors_list)
    
        return converter(*factors).reparse()
    
    def nature(self,interval=None):
        '''Returns nature of the function(expression) given.
        
        >>> from dscal import calculus
        >>> expr=calculus('x^2+sinx')
        >>> expr.nature()
        'the function is neither increasing nor decreasing.'
        >>> expr.nature(interval=[0,3])
        'the function is neither increasing nor decreasing.'
        >>> 
        >>> expr=calculus('sinx')
        >>> expr.nature()
        'the function is neither increasing nor decreasing.'
        >>> expr.nature(interval=[0,1])
        'increasing function'
        >>> '''
        from dscal.tools import ImplicitExpressionError

        for exp in self.__parsed:
            if ('y' in exp) or ('==' in exp):
                raise ImplicitExpressionError("'nature' method does not accepts impicit expressions")
        else:                        
            nats=[]
            if interval==None:
                for exp in self.__parsed:
                    if sym.is_increasing(exp):
                        nats.append('decreasing function')
                    elif sym.is_decreasing(exp):
                        nats.append('increasing function')
                    else:
                        nats.append('neither increasing nor decreasing function')
            else:
                domain=sym.Interval(interval[0],interval[1])
                for exp in self.__parsed:
                    if sym.is_decreasing(exp,domain):
                        nats.append('decreasing function')
                    elif sym.is_increasing(exp,domain):
                        nats.append('increasing function')
                    else:
                        nats.append('neither increasing nor decreasing function')
            return tuple(nats)
        
    def plot(self,**kwargs):
        '''Plot 2D graph for the expression(s).
           This method supports only explicit expressions (contains only x variable).
        
        >>> from dscal import calculus
        >>> expr=calculus('sinx')
        >>> expr.plot(limit=[-5,5])
        >>> '''
        import numpy as np
        from dscal.tools import ImplicitExpressionError

        
        for attr in kwargs:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'plot' method has no attribute '{attr}'")            
        else:
            self.__set.update(kwargs)        

        for exp in self.__parsed:
            if ('y' in exp) or ('=' in exp):
                raise ImplicitExpressionError("'plot' method does not accepts impicit expressions")
        else:                       
            plt.style.use(self.__set['style'])

            domain=self.__set['limit']

            x=np.linspace(domain[0],domain[1],1000)
            y=np.linspace(domain[0],domain[1],1000)

            plt.plot(x,x*0,label='x-axis')

            for exp,label in zip(self.__parsed,self.__exp):
                plt.plot(x,evaluate(exp),label=label)
            
            plt.legend()
            plt.tight_layout()
            plt.show()
    
    def plot3d(self,**kwargs):
        '''Plot 3D graph for the expression(s).
           This method accepts both explicit and impicit expressions(contains x and y variables).
        
        >>> from dscal import calculus
        >>> expr=calculus('sinx*cosy')
        >>> expr.plot3d(limit=[-5,5],colormap=plt.cm.hsv) #plt refers to matplotlib.pyplot
        >>> '''
        import numpy as np

        for attr in kwargs:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'plot3d' method has no attribute '{attr}'")            
        else:
            self.__set.update(kwargs)        

        plt.style.use(self.__set['style'])

        domain=self.__set['limit']

        X=np.linspace(domain[0],domain[1],1000)
        Y=np.linspace(domain[0],domain[1],1000)

        x,y=np.meshgrid(X,Y)

        fig=plt.figure()
        ax=fig.add_subplot(111,projection='3d')

        for exp in self.__parsed:
            ax.plot_surface(x,y,evaluate(exp),cmap=self.__set['colormap'])

        plt.show()

    def __str__(self):
        return f'{self.__exp}'
  