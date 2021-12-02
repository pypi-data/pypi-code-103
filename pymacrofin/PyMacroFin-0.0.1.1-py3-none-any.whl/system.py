import numpy as np
import pandas as pd
import PyMacroFin.equation as eq_mod
import collections


class system:
    """
    A system of equations to solve when a set of constraints is binding.
    
    Parameters
    ---------------
    constraint_trigger: list(str)
        List of labels corresponding to constraints which, when all binding, will 
        trigger this system to become active when solving for endogenous variable values.
    m: macro_model
        Model object to which the system will be attached.
    """
    
    def __init__(self,constraint_trigger,m):
        self.endog_equations = []
        self.equations = []
        self.constraint_trigger = constraint_trigger
        self.state = m.state
        self.value = m.value 
        self.prices = m.prices
        
    def endog_equation(self,eq):
        """
        Add an equation to the system to solve for endogenous variable values. This equation will be solved 
        to be equal to zero to find the values of the endogenous variables at each grid point where the 
        constraints corresonding to this system are binding.
        
        Parameters
        ------------
        eq: str
            This string should be of the form :code:`f(<previously defined variables>)`. 
            For example, if :code:`b` and :code:`c` are already defined as parameters, endogenous variables,
            value variables, or defined in previous equations, then :code:`eq='b + c'` is acceptable. At equilibrium, 
            the expression given by :code:`eq` should be equal to zero.
            
        Notes
        --------
        
        1. There should be as many :code:`endog_equation` calls as there are endogenous equations. For a variable (i.e. :code:`x`) that is set to a known value (i.e. :code:`c`) in this system, simply write :code:`system.endog_equation('c - x')`.
        """
        self.endog_equations.append(eq_mod.endog_equation(eq,self.state,self.value,self.prices))
        self.endog_equations[-1].name = 'F{}'.format(len(self.endog_equations)-1)
        
    def equation(self,eq):
        """
        Define a new intermediate variable with an equation (specific to this system). 
        
        Parameters
        ------------
        eq: str
            This string should be of the form :code:`newvar = f(<previously defined variables>)`. 
            For example, if :code:`b` and :code:`c` are already defined as parameters, endogenous variables,
            value variables, or defined in previous equations, then :code:`eq='a = b + c'` is acceptable.
        
        Notes
        --------
        
        1. It is important to note that you may re-define intermediate variables from the core set of equations in the system. 
        2. See :ref:`the derivatives section <Derivatives>` for using derivatives in equations.
        3. As of the current release, system specific intermediate variables may not be plotted. However, if the equation re-defines a core equation variable then it will be plotted based on the plot input in the core system.
        4. To re-define HJB variables such as the drift and volatility of state variables in a constraint system, simply define intermediates that are referenced in the :code:`macro_model.hjb_equation` calls, then re-define those intermediates in the constraint system.
        """
        self.equations.append(eq_mod.equation(eq,self.state,self.value,self.prices,plot=False))


class boundary:
    """
    A boundary condition to assign to the model.
    
    Parameters
    -------------
    boundary: dict
        This boundary must be of the following form: :code:`{'state':'bound_type'}` where 'state' is the name of the state
        variable as a string and 'bound_type' is either :code:`'min'` or :code:`'max'`. For example, if my state variables were 
        :code:`'e'` and :code:`'z'` and I would like to create a boundary condition for the grid boundary where :code:`'e'` takes 
        its minimum value, I would set this argument equal to :code:`{'e':'min'}`. You can specify boundaries at corners by giving 
        the dictionary two entries as follows: :code:`{'e':'min','z':'max'}`.
    condition: function
        A function that accepts a dictionary as an input with state variable and parameter names as keys (and appropriate values as 
        dictionary values). This function should return a vector of endogenous variable values (with the same order as input with 
        :code:`macro_model.set_endog`).
    endog: list(str)
        The endogenous variables from the model
    
    """
    
    def __init__(self,boundary_,condition,state):
        self.assertions(boundary_,condition,state)
        self.boundary = self.parse(boundary_,state)
        self.condition = condition
        
    @staticmethod
    def assertions(boundary_,condition,state):
        assert isinstance(boundary_,dict), "the boundary argument must be a dictionary (see the documentation)"
        for key in boundary_.keys():
            assert key in state, "the keys of the boundary dictionary must be state variables (see the documentation)"
            assert boundary_[key] in ['min','max'], "invalid values in the boundary argument (see the documentation)"
        assert isinstance(condition,collections.Callable)
    
    @staticmethod
    def parse(boundary_,state):
        result = []
        joiners = [['','']]
        switch = {0:1,1:0}
        for key in boundary_.keys():
            if key==state[0]:
                joiners[0][0] = 'b0'+boundary_[key]
            if key==state[1]:
                joiners[0][1] = 'b1'+boundary_[key]
        for i in range(2):
            # if this is not a corner (only one state boundary defined)...
            if joiners[0][i] == '':
                j = switch[i]
                # then define this to cover that edge...
                joiners[0][i] = 'b'+str(i)
                joiners.append(['',''])
                # and the corners on that edge...
                joiners[-1][j] = joiners[0][j]
                joiners[-1][i] = 'b'+str(i)+'min'
                joiners.append(['',''])
                joiners[-1][j] = joiners[0][j]
                joiners[-1][i] = 'b'+str(i)+'max'
                # note that if the corners are defined here with just the edge and separately 
                # with another boundary condition, that will be cleaned up in macro_model.run() which 
                # calls utilities.clean_boundaries()
        result = ['_'.join(joiner) for joiner in joiners]
        return result