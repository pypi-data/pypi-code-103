import numpy as np
from numbers import Number

class parameters:
    """
    A simple container class for model parameters.
    """
    def __init__(self):
        self.names = []
        self.values = []
        
    def add_parameter(self,name,value):
        """
        Add a constant parameter to be used in model equations.
        
        Parameters
        -----------
        name: str
            The name of the parameter.
        value: numeric
            The numeric value assigned to the parameter.
        
        Notes
        -------
        
        1. It is typically useful to define all parameters prior to defining equations so that parameters can be used in equations.
        """
        assert isinstance(name,str), "name must be a string"
        assert isinstance(value,Number), "value must be a numeric type"
        self.names.append(name)
        self.values.append(value)
        

class options:
    """
    This simple container class houses configurable model options. See the notes below the attribute definitions 
    for more detailed descriptions of the loops referenced in the attribute descriptions.
    
    Attributes
    -------------------
    loop: bool
        Whether or not to enable the second loop stage of the outer loop. If :code:`True`, after the minimum 
        number of iterations and the tolerance is satisfied on the outer loop, a second loop stage is activated.
        If enabled, this allows for two stages with varying levels of error tolerance.
        Defaults to :code:`False`.
    min_iter_inner_static: int
        Minimum iterations for the inner static loop. Defaults to 2.
    max_iter_inner_static: int 
        Maximum iterations for the inner static loop. Defaults to 10,000.
    tol_inner_static: numeric
        Error tolerance for the inner static loop. Defaults to 1.0e-6.
    min_iter_outer_static: int
        Minimum iterations for the outer static loop. Defaults to 2.
    max_iter_outer_static: int
        Maximum iterations for the outer static loop. Defaults to 100.
    tol_outer_static: numeric
        Error tolerance for outer static loop. Defaults to 1.0e-4
    damp1: numeric  
        Initial dampening factor for the static loop. Defaults to 0.1.
    damp1_adjustment: numeric
        Dampening adjustment factor. This number should be between zero and one. The dampening factor 
        is multiplied by this adjustment each loop to speed up convergence. Defaults to 1.
    min_damp1: numeric
        Minimum dampening factor. Defaults to 0.
    damp2: numeric  
        Initial dampening factor for the static loop (second stage). Defaults to 0.1.
    damp2_adjustment: numeric
        Dampening adjustment factor (second stage). This number should be between zero and one. The dampening factor 
        is multiplied by this adjustment each loop to speed up convergence. Defaults to 1.
    min_damp2: numeric
        Minimum dampening factor for the second stage. Defaults to 0.
    min_hjb1: int
        Minimum iterations for the outer HJB update loop (dynamic loop). Defaults to 100.
    min_hjb2: int
        Minimum iterations for the outer HJB update loop (second stage). Defaults to 10.
    max_hjb: int
        Maximum iterations for the outer HJB update loop (dynamic loop). Defaults to 10000.
    tol_hjb: numeric  
        Error tolerance for the outer HJB update loop (dynamic loop). Defaults to 0.01.
    dt: numeric 
        Time step for the HJB update loop (dynamic loop). Defaults to 0.1.
    dt2: numeric
        Time step for the HJB update loop (second stage). Defaults to 0.1.
    tol_d: numeric
        Error tolerance for the stencil decomposition algorithm. Defaults to 1.0e-4.
    max_p: int 
        Maximum stencil size for decomposition algorithm.
    n0: int
        Number of points to use in the finite difference grid in the dimension associated with the 
        first element of the model :code:`state` attribute. Defaults to 50.
    n1: int
        Number of points to use in the finite difference grid in the dimension associated with the 
        second element of the model :code:`state` attribute. Defaults to 50.
    start0: numeric
        First point use in the finite difference grid in the dimension associated with the 
        first element of the model :code:`state` attribute. Defaults to 0.01.
    start1: numeric
        First point use in the finite difference grid in the dimension associated with the 
        second  element of the model :code:`state` attribute. Defaults to 0.01.    
    end0: numeric
        Last point use in the finite difference grid in the dimension associated with the 
        first element of the model :code:`state` attribute. Defaults to 0.99.
    end1: numeric
        Last point use in the finite difference grid in the dimension associated with the 
        second  element of the model :code:`state` attribute. Defaults to 0.99.       
    quiet: bool
        Whether or not to suppress update output. Defaults to :code:`False`.
    import_guess: bool  
        Whether or not to import an initial guess to work from. Defaults to :code:`False`.
    guess_function: False or function
        Possibility to provide a function to calculate initial guesses from state variable values. 
        If not :code:`False`, initial guesses for endogenous and value variables will be calculated from 
        the provided function. The function should return a vector in the order of endogenous variables first, then value variables, 
        such that the length of the vector returned by the function should be equal to the lengths of :code:`macro_model.endog` and 
        :code:`macro_model.value` summed. The function provided should accept two arguments, corresponding to the 
        two state variables in :code:`macro_model.state`. Defaults to :code:`False`
    import_guess_location: str
        File path to the csv file where the guess file is located. Defaults to :code:`None` and is not used 
        unnless :code:`import_guess` is set to :code:`True`. The guess file should be a comma-separated values
        file with columns labeled and completed for all value, state, and endogenous variables. Note that 
        the grid specified by options :code:`start0`, :code:`start1`, :code:`end0`, :code:`end1`, :code:`n0`, above
        and :code:`n1` must be consistent with the grid implied by the guess file. It is useful to run a simple dummy
        model without a guess file with the same grid specification, then modify the file saved down by the dummy 
        model without changing the ordering or specification of state variables to create a guess file.
    inner_plot: bool    
        Whether or not to plot after each outer static loop iteration. Defaults to :code:`False`.
    outer_plot: bool    
        Whether or not to plot after each HJB loop iteration. Defaults to :code:`False`.
    final_plot: bool
        Whether to plot after convergence. Defaults to :code:`True`.
    derivative_plotting: list(tuple(str))
        List of tuples to indicate derivatives to be plotted in addition to endogenous variables and selected 
        secondary variables. Tuples should be of the same form as the input to equations. For example, for the second
        derivative of a price :code:`q` to state variable :code:`x` will have the tuple :code:`('q','x','x')`.
    parallel: bool
        Whether or not to run the static loop in parallel. Defaults to :code:`True`. 
    dash_debug: bool
        Whether or not to run the visualization Dash application in debug mode. Defaults to :code:`False`.
    dash_port: int 
        Local port on which to run the Dash visualization application. Defaults to :code:`8050`.
    dash_port_stationary: int
        Local port on which to run a second Dash visualization application for calculation of a stationary distribution. Defaults to :code:`8000`.
    ignore_HJB_loop: bool
        An option to ignore the HJB loop and return after running one iteration of the outer static loop. This is suitable for 
        problems that do not require iteration through the dynamic HJB loop. Defaults to :code:`False`.
    inner_solver: str
        Solver to use for the inner static loop. Defaults to :code:`'newton-raphson'`. Other options include :code:`'least_squares'` and 
        :code:`'fsolve'`. :code:`'fsolve'` is currently in alpha stages and is unstable.
    suppress_warnings: bool 
        Option to suppress warnings associated with solving the endogenous equations. These warnings are typically harmless and occur due 
        to functions compiled by SymPy. Defaults to :code:`True`. It is only recommended to set this option to :code:`False` if you are 
        debugging issues in the endogenous equations and want to see output of exact equations being solved.
    return_solution: bool
        Whether or not to return the solution in the form of a Pandas DataFrame from the :code:`macro_model.run` method. Defaults to :code:`False`.
    save_solution: bool
        Whether or not to save the solution down to a file after convergence. Defaults to :code:`True`. 
    price_derivative_method: str
        Price derivative method. Options include :code:`'central'`, :code:`'forward'`, and :code:`'backward'`. Defaults to 
        :code:`'central'`.
    
    Notes
    -------
    1. The HJB update loop, or dynamic loop, is the iteration involving the PDE system. The HJB or dynamic loop iterates backward in time using the equation found :ref:`on this page <general-overview>` and a monotone finite difference scheme.
    2. The inner static loop is the first level of iteration in solving the endogenous system of equations. The inner static loop is run separately for each grid point, solving for the endogenous equations to equal zero. The outer static loop calculates derivatives across the grid using a monotone finite difference scheme after all grid points have completed the inner static loop. This outer static loop continues, running the inner static loop and derivative re-calculation, until the endogenous system of equations is solved at all grid points with consistency with derivatives between grid points.
    """
    def __init__(self):
        self.set_defaults()
        
    def set_defaults(self):
        """
        Reset all options to default values.
        
        Parameters
        --------------
        None
 
        Notes
        ---------
        1. See the documentation for the class for descriptions of options as well as their default values.
        """
        self.loop = False
        
        # Inner static loop
        self.min_iter_inner_static = 2
        self.max_iter_inner_static = 10000
        self.tol_inner_static = 1.0e-6
        
        # outer static loop
        self.min_iter_outer_static = 2
        self.max_iter_outer_static = 100
        self.tol_outer_static = 1.0e-4
        
        # Dampening
        self.damp1 = 0.10
        self.damp2 = 0.10
        self.min_damp1 = 0.0
        self.min_damp2 = 0.0
        self.damp1_adjustment = 1.0
        self.damp2_adjustment = 1.0
        
        # HJB Loop
        self.min_hjb1 = 100
        self.min_hjb2 = 10
        self.max_hjb = 10000
        self.tol_hjb = 0.01
        
        # Time difference
        self.dt = 0.1
        self.dt2 = 0.1
        
        # Stencil
        self.tol_d = 1.0e-4
        self.max_p = 4
        #self.nextr = 4
        
        # grid 
        self.n0 = 50 # associated with first element in macro_model.state
        self.n1 = 50 # associated with second element in macro_model.state
        self.start0 = 0.01 # associated with first element in macro_model.state
        self.start1 = 0.01 # associated with second element in macro_model.state
        self.end0 = 0.99 # associated with first element in macro_model.state
        self.end1 = 0.99 # associated with second element in macro_model.state
        
        # printed output
        self.quiet = False
        
        # guess
        self.import_guess = False
        self.import_guess_location = None
        
        # plotting
        self.inner_plot = False
        self.outer_plot = False
        self.derivative_plotting = []
        self.final_plot = True
        
        # parallel processing 
        self.parallel = True
        
        # private attribute to denote loop phase
        self._loop = 1
        
        # publicly undocumented attribute to denote whether or not to use legacy price derivative treatment
        self._legacy_price_deriv = False
        
        # attribute to denote whether or not to run dash app in debug model
        self.dash_debug = False
        
        # attribute denoting dash application port number 
        self.dash_port = 8050
        self.dash_port_stationary = 8000
    
        # publicly undocumented attribute denoting solver to use for inner loop (options: 'newton-raphson','least_squares','fsolve')
        self.inner_solver = 'newton-raphson'
                
        # publicly undocumented attribute for whether to warn if there are state variable drift terms that lead outside of the grid
        self.warn_drift_out = True
        
        # publicly undocumented attributes for values above or below which the user is warned that value is strange
        self.value_lower = -1
        self.value_upper = 100
        
        # publicly undocumented attributes for different error tolerances at boundaries / corners of the grid
        self.tol_inner_static_corner = self.tol_inner_static
        self.tol_inner_static_boundary = self.tol_inner_static
        
        # possibility to use guess functions to calculate initial guesses
        self.guess_function = False
        
        # ignore the HJB loop
        self.ignore_HJB_loop = False
        
        # suppress inner loop warnings
        self.suppress_warnings = True
        
        # return / save solution from m.run()
        self.return_solution = False
        self.save_solution = True
        
        # price derivative method 
        self.price_derivative_method = 'central'