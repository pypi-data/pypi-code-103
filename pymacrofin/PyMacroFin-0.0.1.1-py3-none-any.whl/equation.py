import numpy as np
import sympy
from sympy.parsing.sympy_parser import parse_expr
from numbers import Number


class equation:
    """
    Class documentation here
    """
    
    def __init__(self,eq,state,value,prices,plot=False,latex=None):
        """
        Split the string, generate the sympy equation, raise an error if the variables aren't specified in the 
        variables from the parameters object from the model object.
        """
        self.state = state
        self.value = value
        self.operators = ['*','-','+','^','/',' ','(',')']
        self.prices = prices
        self.assertions(eq)
        self.latex = latex
        self.parse(eq)
        self.plot = plot
        
    def assertions(self,eq):
        assert ~('==' in eq), "Use = rather than == for equality in Equation method"
        assert '=' in eq, "Must be an equality statement (no equals sign found in expression)"
        assert len(eq.split('='))==2, "There must be one and only one equals sign in the expression"
        assert len(self.state)==2, "There must be two state variables"
        for operator in self.operators:
            assert len(eq.split('=')[0].strip().split(operator))==1, "The equation should be an assignment equation (one variable to the left of the equals sign)"
        # probably need to assert that (1) the first element of the equation is one variable (for autowrap)
        # and (2) that the first variable has not been defined already (decided that doesn't need to be in secondary
        
    def derivative_parse(self,s):
        # find the appropriate end parentheses
        pos = s.find('d(')
        for i in range(len(s)-pos):
            if s[pos+1+i] == ')':
                endpos = pos+1+i
                break
        # assert that the first entry before the comma must be a price or a value, and the second entry/entries must be state variables
        inside = s[pos+2:endpos]
        inside_broken = inside.split(',')
        assert (len(inside_broken)==2 or len(inside_broken)==3), "Invalid format for the derivative operator"
        assert ((inside_broken[0] in self.value) or (inside_broken[0] in self.prices)), "The derivative must be taken of either a value or a price"
        assert (inside_broken[1] in self.state), "The derivative must be taken with respect to a state variable"
        if len(inside_broken)==3:
            assert (inside_broken[2] in self.state), "The derivative must be taken of either a value or a price"
        outside = s[pos:endpos+1]
        if len(inside_broken)==2:
            s = s.replace(outside,'_{0}{1}'.format(inside_broken[0],inside_broken[1]))
        elif len(inside_broken)==3:
            if inside_broken[1]==inside_broken[2]:
                s = s.replace(outside,'_{0}{1}{1}'.format(inside_broken[0],inside_broken[1]))
            else:
                s = s.replace(outside,'_{0}{1}{2}'.format(inside_broken[0],self.state[0],self.state[1]))
        return s
        
    def parse(self,eq):
        broken = eq.split('=')
        broken[1] = self.built_ins(broken[1])
        if 'd(' in broken[1]:
            while 'd(' in broken[1]:
                broken[1] = self.derivative_parse(broken[1])
        self.eq = broken[1].strip()
        self.name = broken[0].strip()
        assert self.name != 'o', "'o' is a protected variable in the library's namespace. Please use a different intermediate variable name"
        self.args = self.extract_args(self.eq)
        if self.latex == None:
            self.latex = self.name
        
    def built_ins(self,s):
        if 'log(' in s:
            s = s.replace('log(','sp.log(')
        return s 
        
    def extract_args(self,eq):
        args = [x.strip() for x in eq.split('*')]
        for operator in self.operators[1:]:
            for i in range(len(args)):
                args[i] = [x.strip() for x in args[i].split(operator)]
            args = [item for sublist in args for item in sublist]
            args = [x for x in args if x!='']
        isnumber = []
        for x in args:
            try:   
                # remove from args if it is a number
                test = float(x)
                isnumber.append(x)
            except:
                pass
        for x in isnumber:
            args = [v for v in args if v!=x]
        builtins = ['sp.log']
        args = [v for v in args if v not in builtins]
        args = list(set(args))
        return args
        
            
            
class endog_equation(equation):

    def __init__(self,eq,state,value,prices):
        self.state = state
        self.value = value
        self.prices = prices
        self.operators = ['*','-','+','^','/',' ','(',')']
        self.assertions(eq)
        self.parse(eq)
        
    def assertions(self,eq):
        assert ~('==' in eq), "Use = rather than == for equality in Equation method"
        assert '=' not in eq, "Must not be an equality statement (equals sign found in expression)"
        
    def parse(self,eq):
        self.eq = super().built_ins(eq)
        if 'd(' in self.eq:
            while 'd(' in self.eq:
                self.eq = super().derivative_parse(self.eq)
        self.args = super().extract_args(self.eq)

class hjb_equation(equation):
    
    def __init__(self,hjbvar,linkvar,eq,state,value,prices):
        self.hjbvar = hjbvar
        self.linkvar = linkvar
        self.state = state
        self.value = value
        self.prices = prices
        self.assertions(eq)
        if isinstance(eq,str):
            self.parse(eq)
        elif isinstance(eq,Number):
            self.eq = str(eq)
        
    def assertions(self,eq):
        assert self.hjbvar in ['mu','u','r','sig'], "Invalid HJB variable"
        if self.hjbvar == 'mu':
            assert self.linkvar in self.state
        if self.hjbvar == 'sig':
            assert self.linkvar in self.state or self.linkvar == 'cross', "Invalid link variable"
        if self.hjbvar == 'u' or self.hjbvar == 'r':
            assert self.linkvar in self.value, "Invalid link variable"
    
    def parse(self,eq):
        eq = super().built_ins(eq)
        if 'd(' in eq:
            while 'd(' in eq:
                eq = super().derivative_parse(eq)
        self.eq = eq
        
class constraint:

    # desired functionality: constraints on any variable (portfolio choice)
    # desired functionality: flexible model change on binding constraint 
    # example: Brunnermeier and Sannikov in the handbook - lecture notes
    #          skin in the game constraint

    def __init__(self,endog_var,constraint_type,bound,endog,label):
        self.endog_var = endog_var
        self.constraint_type = constraint_type
        self.bound = bound 
        self.label = label
        self.assertions(endog)
        
    def assertions(self,endog):
        # assert that first argument is an endog variable
        assert self.endog_var in endog, "endog_var must be an endogenous variable of the model"
        # assert that second argument is > or <
        assert self.constraint_type in ['>','<','>=','<='], "constraint type must be '>', '<', '>=', or '<='"
        # assert that third argument is a numeric value
        assert isinstance(self.bound,Number), "bound must be a numeric type"
        

        
       
        
