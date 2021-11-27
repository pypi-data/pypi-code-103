from dscal import calculus

class tkcal(calculus):
    
    def __init__(self, *expression,**options):
        '''A toolkit for implementing the methods of class calculus into tkinter utility.
           This class has all the functions class calculus (with same usage and functionality).'''
        super().__init__(*expression, **options)
        import matplotlib.pyplot as plt
        self.__config={'wrt':'x','limit':(-10,10),'style':'ggplot',
        'colormap':plt.cm.cool,'master':None}
        
        self.__acceptableKeys=('wrt','limit','master','style','colormap')
        self.__parsed=self._calculus__parsed        
        for attr in options:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'tkcal' object has no attribute '{attr}'")            
        else:
            self.__config.update(options)

        
    def graph(self,**kwargs):
        '''Method returns canvas widget with a 2D plot of the expression(s) [graph same as obtained
           by plot method].
           Use tkinter packing methods [pack(), grid()] to add the graph into the GUI.'''
        for attr in kwargs:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'graph' method has no attribute {attr}")
        else:
            self.__config.update(kwargs)
    
        import matplotlib.pyplot as plt
        import numpy as np
        from dscal.tools import ImplicitExpressionError
        from numexpr import evaluate

        for exp in self.__parsed:
            if ('y' in exp) or ('=' in exp):
                raise ImplicitExpressionError
        else:
            self.__fig2=plt.figure()
                
            plt.style.use(self.__config['style'])

            domain=self.__config['limit']

            x=np.linspace(domain[0],domain[1],1000)
            y=np.linspace(domain[0],domain[1],1000)

            plt.plot(x,x*0,label='x-axis')

            for exp,label in zip(self.__parsed,self._calculus__exp):
                plt.plot(x,evaluate(exp),label=label)
            
            plt.legend()
            plt.tight_layout()

            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            return FigureCanvasTkAgg(self.__fig2,master=self.__config['master']).get_tk_widget()
                
    def graph3d(self, **kwargs):
        '''Method returns canvas widget with a 3D plot of the expression(s) [graph same as obtained
           by plot3d method].
           Use tkinter packing methods [pack(), grid()] to add the graph into the GUI.'''
        for attr in kwargs:
            if attr not in self.__acceptableKeys:
                raise AttributeError(f"'graph3d' method has no attribute {attr}")
        else:
            self.__config.update(kwargs)
    
        import matplotlib.pyplot as plt
        import numpy as np
        from dscal.tools import ImplicitExpressionError
        from numexpr import evaluate

        self.__fig3=plt.figure()
        ax=self.__fig3.add_subplot(111,projection='3d')

        domain1,domian2=self.__config['limit']

        d=np.linspace(domain1,domian2,1000)

        x,y=np.meshgrid(d,d)

        for exp in self.__parsed:
            ax.plot_surface(x,y,evaluate(exp),cmap=self.__config['colormap'])

        plt.tight_layout()

        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        return FigureCanvasTkAgg(self.__fig3,self.__config['master']).get_tk_widget()