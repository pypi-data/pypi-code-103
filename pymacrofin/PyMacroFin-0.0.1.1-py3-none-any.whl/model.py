import numpy as np
import pandas as pd
from PyMacroFin.parameters import parameters, options
from PyMacroFin.engine import model_engine
import PyMacroFin.equation as eq_mod
from PyMacroFin.outerloop import outerloop
from numbers import Number
import PyMacroFin.utilities as util
from PyMacroFin.grid import grid
import pickle
import time
import PyMacroFin.system as system_mod
import os


class macro_model:
    """
    Model class to assign equations, variables, parameters, options, constraints, etc. Once 
    the model is defined by the user, upon calling the :code:`run` method, the jacobians are 
    computed and the model is run to convergence.
    
    Parameters
    ------------
    name: str
        Name of the model. This will be used in file names when saving down solution files (the file name
        will consist of the time, date, and model name). This is also used for the visualization application.
        
    Attributes
    -------------
    options: PyMacroFin.parameters.options
        An options class with highly configurable options (documentation :ref:`here <options-documentation>`.
        When a :code:`macro_model` object is instantiated, this attribute is created with default values that 
        can be modified by the user.
    parameters: PyMacroFin.parameters.parameters
        An attribute to house model parameters. An empty parameters object is created upon :code:`macro_model` 
        instantiation. See documentation :ref:`here <parameters-documentation>`.
    """

    def __init__(self,name=''):
        """
        Instantiates necessary attributes to nans so we can check if the attributes have been properly added by user
        """
        self.name = name
        self.options = options()
        self.endog = []
        self.state = [] # must assert that the length of this is two (for now)
        self.secondary = [] # this is the list that we calculate and store, etc. however, don't instantiate, just make sure they are all created by equations
        self.prices = []
        self.value = []
        self.equations = [] 
        self.endog_equations = []
        self.hjb_equations = {}
        self.params = parameters() # these are constants that go into the engine / equations, as opposed to options for the model operation
        self.constraints = []
        self.value_latex = []
        self.endog_latex = []
        self.state_latex = []
        self.systems = []
        self.boundaries = []
        self.one_dimension = False
        
    def set_state(self,state,latex=None):
        """
        Define state variables and (optionally) provide associated latex strings.
        
        Parameters
        ------------
        endog: list(str)
            List of strings that define endogenous variables. 
        latex: list(str)
            List of raw strings 
            
        Notes
        --------
        
        1. The values of the state variables are defined by the options in :ref:`this section <options-documentation>`.
        2. In the current release, due to issues in packages used for the visualization, the state variables are rendered simply as :code:`x` and :code:`y` in plots regardless of the inputs for the :code:`latex` argument.
        """
        self.state = state
        if latex != None:
            self.state_latex = latex
        else:
            self.state_latex = state
        assert 'd' not in self.state, "'d' is not an available state variable name due to namespace restrictions"
        assert len(self.state) in [1,2], "invalid number of state variables. only 1D and 2D problems are currently accepted"
        if len(self.state)==1:
            self.one_dimension = True
            self.options.n1 = 2
            self.state.append('o') # dummy state variable (protected in the namespace)
            self.hjb_equation('sig','o',0.0001)
            self.hjb_equation('mu','o',0)
            self.hjb_equation('sig','cross',0)
        assert all([len(x)==1 for x in self.state]), "state variables should be one character strings"
        assert all([isinstance(x,str) for x in self.state]), "state variables should be one character strings"
        
    def set_endog(self,endog,init='default',latex=None):
        """
        Define endogenous variables and (optionally) provide associated initialization values and latex strings.
        
        Parameters
        ------------
        endog: list(str)
            List of strings that define endogenous variables. 
        init: str or list(numeric)
            List of values to initialize the endogenous variables with, or :code:`'default'` (default value). 
            If :code:`'default'` then each endogenous variable is initialized at zero.
        latex: list(str)
            List of raw strings 
            
        Notes
        --------
        
        1. The number of endogenous variables must be equal to the number of endogenous equations specified. 
        2. Rather than using initialization with constant values as supported in this method, you can also specify a file or function from which to initialize each variable value at each individual grid point. This can be done in the :code:`options` class.
        3. See the documentation :ref:`in this section <Endogenous Variables>` for more detail on which variables to define with this method.
        """
        if init != 'default':
            assert len(endog)==len(init), "init and endog must have the same length"
        assert len(endog)>0, "there must be at least one endogenous variable"
        assert 'o' not in endog, "'o' is a protected variable in the library namespace. Please use a different name for the endogenous variable."
        self.endog = endog
        if init == 'default':
            self.endog_init = [0 for x in endog]
        else:
            assert all([isinstance(x,Number) for x in init]), "elements of init must be single numbers"
            self.endog_init = init
        assert latex==None or isinstance(latex,list), "Invalid latex argument. Must be None or a list"
        if latex==None:
            self.endog_latex = self.endog 
        else:
            assert all([isinstance(x,str) for x in latex]), "Invalid elemements in latex argument. Elements must be strings"
            self.endog_latex = latex

    def set_value(self,value,init='default',latex=None):
        """
        Define value variables and (optionally) provide associated initialization values and latex strings.
        See :ref:`the value variable section <Value Variables>` for more detail on value variables.
        
        Parameters
        ------------
        value: list(str)
            List of strings that define value variables. 
        init: str or list(numeric)
            List of values to initialize the endogenous variables with, or :code:`'default'` (default value). 
            If :code:`'default'` then each endogenous variable is initialized at zero.
        latex: list(str)
            List of raw strings 
            
        Notes
        ---------------
        
        1. Rather than using initialization with constant values as supported in this method, you can also specify a file from which to initialize each variable value at each individual grid point. This can be done in the :code:`options` class.
        """
        if init != 'default':
            assert len(value)==len(init), "init and endog must have the same length"
        assert len(value)>0, "there must be at least one endogenous variable"
        assert 'o' not in value, "'o' is a protected variable in the library namespace. Please use a different name for the value variable."
        self.value = value
        if init == 'default':
            self.value_init = [0 for x in value]
        else:
            assert all([isinstance(x,Number) for x in init]), "elements of init must be single numbers"
            self.value_init = init
        assert latex==None or isinstance(latex,list), "Invalid latex argument. Must be None or a list"
        if latex==None:
            self.value_latex = self.value 
        else:
            assert all([isinstance(x,str) for x in latex]), "Invalid elemements in latex argument. Elements must be strings"
            self.value_latex = latex
        
    def equation(self,eq,plot=False,latex=None):
        """
        Define a new intermediate variable with an equation.
        
        Parameters
        ------------
        eq: str
            This string should be of the form :code:`newvar = f(<previously defined variables>)`. 
            For example, if :code:`b` and :code:`c` are already defined as parameters, endogenous variables,
            value variables, or defined in previous equations, then :code:`eq='a = b + c'` is acceptable.
        plot: bool
            Whether or not to include the defined variable in the visualization application.
        latex: str
            Latex to be used for plot labels. Unused if :code:`plot=False`. Defaults to :code:`None`. 
        
        Notes
        --------
        
        1. See :ref:`the derivatives section <Derivatives>` for using derivatives in equations.
        """
        self.equations.append(eq_mod.equation(eq,self.state,self.value,self.prices,plot=plot,latex=latex))
        
    def endog_equation(self,eq):
        """
        Add an equation to the core system to solve for endogenous variable values. This equation will be solved 
        to be equal to zero to find the values of the endogenous variables at each grid point.
        
        Parameters
        ------------
        eq: str
            This string should be of the form :code:`f(<previously defined variables>)`. 
            For example, if :code:`b` and :code:`c` are already defined as parameters, endogenous variables,
            value variables, or defined in previous equations, then :code:`eq='b + c'` is acceptable. At equilibrium, 
            the expression given by :code:`eq` should be equal to zero.
            
        Notes
        --------
        
        1. See :ref:`the derivatives section <Derivatives>` for using derivatives in equations.
        """
        self.endog_equations.append(eq_mod.endog_equation(eq,self.state,self.value,self.prices))
        self.endog_equations[-1].name = 'F{}'.format(len(self.endog_equations)-1)
        
    def hjb_equation(self,hjbvar,linkvar,eq):
        """
        Define variables to be used in the dynamic iteration of the equation shown :ref:`in this section <Value Variables>`.
        You must specify the drift and volatilty of each state variable's law of motion and you must specify the :math:`u` and 
        :math:`r` values for each value variable (for each :math:`F(X,t)`).
                    
        Parameters
        ------------
        hjbvar: str
            This is the type of variable you are specifying. This should either be :code:`'mu'`, :code:`'sig'`, :code:`'u'`, 
            or :code:`'r'`. 
        linkvar: str
            This is the variable you are associating the :code:`hjbvar` with. For example, if :code:`hjbvar = 'mu'` and 
            :code:`linkvar = 'a'`, then you are assigning the equation to the drift of the state variable :code:`a`.
        eq: str
            This string should be of the form :code:`f(<previously defined variables>)`. 
            For example, if :code:`b` and :code:`c` are already defined as parameters, endogenous variables,
            value variables, or defined in previous equations, then :code:`eq='b + c'` is acceptable. The expression 
            given by :code:`eq` should be the variable described in the descriptions of :code:`hjbvar` and :code:`linkvar`.
        
        Notes
        --------
        
        1. See :ref:`the derivatives section <Derivatives>` for using derivatives in equations.
        """
        self.hjb_equations[(hjbvar,linkvar)] = eq_mod.hjb_equation(hjbvar,linkvar,eq,self.state,self.value,self.prices) 
        
    def constraint(self,endog_var,constraint_type,bound,label=''):
        """
        Add constraint to an endogenous variable. Constraint behavior depends on the solver selected by the 
        :code:`macro_model.options.inner_solver` option. For details on constraint behavior with different 
        solvers and usage of constraints with equation systems, see :ref:`this section <system-documentation>`.
        
        Parameters
        ------------
        endog_var: str
            The endogenous variable to be constrainted.
        constraint_type: str
            This must be :code:`'<'` or :code:`'>'`. The reading is that if :code:`m.constraint('a','<',10)` is 
            specified than the constraint written is :code:`a < 10`. 
        bound: numeric
            The constraint bound value.
        label: str
            A label to use when referencing this constraint in endogenous equation systems. Defaults to an empty string, meaning the constraint 
            cannot be referenced in a system.
            
        Notes
        ---------
        
        1. Any variable to be constrained, whether traditionally considered to be "endogenous" or not, must be defined by the :code:`set_endog` method. See details :ref:`here <Endogenous Variables>`.
        """
        self.constraints.append(eq_mod.constraint(endog_var,constraint_type,bound,self.endog,label=label))
        
    def boundary_condition(self,boundary,condition):
        """
        Add a boundary condition for endogenous variable values to the model.
        
        Parameters
        ------------
        boundary_: dict
            This boundary must be of the following form: :code:`{'state':'bound_type'}` where 'state' is the name of the state
            variable as a string and 'bound_type' is either :code:`'min'` or :code:`'max'`. For example, if my state variables were 
            :code:`'e'` and :code:`'z'` and I would like to create a boundary condition for the grid boundary where :code:`'e'` takes 
            its minimum value, I would set this argument equal to :code:`{'e':'min'}`. You can specify boundaries at corners by giving 
            the dictionary two entries as follows: :code:`{'e':'min','z':'max'}`.
        condition: function
            A function that accepts a dictionary as an input with state variable and parameter names as keys (and appropriate values as 
            dictionary values). This function should return a vector of endogenous variable values (with the same order as input with 
            :code:`macro_model.set_endog`).
            
        Notes
        -------------
        
        1. While the function should accept a dictionary as an argument, the function is not required to use any entries in the dictionary. A boundary unrelated to parameters and state variable values may be defined.
        2. Allowing boundaries to be specified by user-defined functions allows for high flexibility in defining boundary conditions as opposed to using the equation definition format.
        
        """
        self.boundaries.append(system_mod.boundary(boundary,condition,self.state))
        
    def construct(self):
        """
        Constructs model engine
        """
        self.construction_assertions()
        if len(self.systems)>0:
            self.systems = util.system_ordering(self.systems)
        self.engine = model_engine(self)
        for tup in self.engine.isconstant:
            del self.hjb_equations[tup]
        self.secondaryplot = util.get_secondary_plot(self)
        self.secondarylatex = util.get_secondary_latex(self)

    def construction_assertions(self):
        """
        Error checking prior to model engine construction
        """
        assert len(self.endog_equations)==len(self.endog), "The number of endogenous equations must equal the number of endogenous varables"
        assert 'd' not in self.state, "'d' is not an available state variable name due to namespace restrictions"
        eq_defined = [eq.name for eq in self.equations]
        for var in self.secondary:
            assert var in eq_defined, "{} is not defined by an equation. All secondary variables must be defined in an equation".format(var)
        assert len(self.state) in [1,2], "invalid number of state variables. only 1D and 2D problems are currently accepted"
        if len(self.state)==1:
            self.one_dimension = True
        assert all([len(x)==1 for x in self.state]), "state variables should be one character strings"
        assert all([isinstance(x,str) for x in self.state]), "state variables should be one character strings"
        
    def run_assertions(self):
        """
        Error checking prior to running model
        """
        assert len(self.equations)>0, "There are no model equations"
        assert len(self.endog)>0, "There are no endogenous variables"
        assert isinstance(self.options.n0,int), "the n0 option must be an integer"
        assert isinstance(self.options.n1,int), "the n1 option must be an integer"
        assert self.options.inner_solver in ['least_squares','newton-raphson','fsolve'], "Invalid input for inner_solver option"
        if not self.options.ignore_HJB_loop:
            for s in self.state:   
                assert ('mu',s) in [*self.hjb_equations]+self.engine.isconstant, "HJB equation for 'mu' and state {} must be defined".format(s)
                assert ('sig',s) in [*self.hjb_equations]+self.engine.isconstant, "HJB equation for 'sig' and state {} must be defined".format(s)
            for v in self.value:
                assert ('u',v) in [*self.hjb_equations]+self.engine.isconstant, "HJB equation for 'u' and {} must be defined".format(v)
                assert ('r',v) in [*self.hjb_equations]+self.engine.isconstant, "HJB equation for 'r' and {} must be defined".format(v)
            if not self.one_dimension:
                assert ('sig','cross') in [*self.hjb_equations]+self.engine.isconstant, "HJB equation for 'sig' and 'cross' must be defined"
        for element in self.options.derivative_plotting:
            assert len(element)==2 or len(element)==3, "Invalid element in derivative_plotting option"
            assert ((element[0] in self.prices) or (element[0] in self.value)), "First entry in a derivative_plotting entry must be \
                a value or price variable"
            for entry in element[1:]:
                assert entry in self.state, "Invalid element in derivative_plotting option"
        if self.one_dimension:
            # ensure the user has not misspecified the number of points for the second dummy direction
            self.options.n1 = 2
            
    def run(self):
        """
        Runs the specified model to convergence according to the process described `here <http://www.adriendavernas.com/papers/solutionmethod.pdf>`_. 
        
        Parameters
        -------------
        None
        
        Notes
        -------
        
        1. It can be helpful to run the visualization application along with the model to see live updates of 3D surfaces of any chosen variable from the model (or derivative). The plots are shown in a browser and are fully interactive. Documentation for the visualization application can be found :ref:`here <dash-documentation>`.
        2. Although there are no direct inputs to this method, the behavior of the model is highly configurable by specifying options in the :code:`macro_model.options` attribute (see :ref:`here <options-documentation>` for documentation on model options). 
        """
        if not hasattr(self,'engine'):
            if not self.options.quiet:
                print("Constructing model...")
                tic = time.time()
            self.construct()
            if not self.options.quiet:
                toc = time.time()
                print("Model construction completed: {0:.3g} sec".format(toc-tic))
        else:
            print("Using previously constructed model")
        self.run_assertions()
        self.options.N = self.options.n0 * self.options.n1
        # construct grid 
        self.grid = grid(self.options)
        # initialize plotting dash application 
        if self.options.inner_plot or self.options.outer_plot:
            self.use_dash = True
            util.start_dash(self)
            #dash_process = util.start_dash(self)
        else:
            self.use_dash = False
        if self.options.import_guess:
            df = util.initialize_from_guess(self)
        elif self.options.guess_function != False:
            df = util.initialize_from_function(self)
        else:
            df = util.initialization(self)
        # clean boundaries 
        self.boundaries = util.clean_boundaries(self.boundaries)
        # run the outer loop
        df = outerloop(self,df)    
        # final plotting 
        if self.use_dash:
            #dash_process.terminate()
            pass
        else:
            if self.options.final_plot:
                util.plot(self,df,use_dash = False)
        # clean solution from 2d-dummy before returning to user if 1d problem
        if self.one_dimension:
            df = util.transposal(df,self.state,self.value,self.options)
            df = util.extract_1d(df,self.options)            
        # save down solution 
        if self.options.save_solution:
            df.to_csv("{0}_solution-{1}.csv".format(self.name,time.strftime("%Y%m%d-%H%M%S")))
        # return solution
        if self.options.return_solution:
            return df