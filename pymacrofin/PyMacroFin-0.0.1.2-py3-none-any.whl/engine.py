import numpy as np
import pandas as pd
import sympy as sp
from numbers import Number

class model_engine:

    def __init__(self,m):
        self.construct_engine(m)
        
    def construct_engine(self,m):
        for bound1 in ['min','','max']:
            for bound2 in ['min','','max']:
                if m.options._legacy_price_deriv:
                    self.construct_specific_legacy([bound1,bound2],m)
                else:
                    self.construct_specific([bound1,bound2],m)
                
    def construct_specific(self,bounds,m):
        # define an tag for this set of boundaries 
        boundtag = "b0{0}_b1{1}".format(bounds[0],bounds[1])
        # make state variables and value variables sympy symbols
        for var in m.state:
            exec("{0} = sp.symbols('{0}')".format(var))
        for var in m.value:
            exec("{0} = sp.symbols('{0}')".format(var))
        # make endogenous variables sympy symbols
        for var in m.endog:
            exec("{0} = sp.symbols('{0}')".format(var))
        # make parameters sympy symbols (values to be substituted later)
        for var in m.params.names:
            exec("{0} = sp.symbols('{0}')".format(var))
        # define derivatives for price as sympy symbols and expressions
        for var in m.prices:
            exec("{0} = sp.symbols('{0}')".format(var))
            for i in range(len(bounds)):
                if i == 0:
                    j = 1
                elif i == 1:
                    j = 0
                if bounds[i] != 'min':
                    exec("_dm{0} = sp.symbols('_dm{0}')".format(m.state[i]))
                    exec("_{0}m{1} = sp.symbols('_{0}m{1}')".format(var,m.state[i]))
                    exec("_{0}{1}m{1} = sp.symbols('_{0}{1}m{1}')".format(var,m.state[i]))
                    exec("_{0}{1}m{2} = sp.symbols('_{0}{1}m{2}')".format(var,m.state[j],m.state[i]))
                if bounds[i] != 'max':
                    exec("_dp{0} = sp.symbols('_dp{0}')".format(m.state[i]))
                    exec("_{0}p{1} = sp.symbols('_{0}p{1}')".format(var,m.state[i]))
                    exec("_{0}{1}p{1} = sp.symbols('_{0}{1}p{1}')".format(var,m.state[i]))
                    exec("_{0}{1}p{2} = sp.symbols('_{0}{1}p{2}')".format(var,m.state[j],m.state[i]))
            for i in range(len(bounds)):
                if bounds[i] == '' and m.options.price_derivative_method == 'central':
                    exec("_{0}{1} = (_{0}p{1}*_dm{1} - {0}*_dm{1} + {0}*_dp{1} - _{0}m{1}*_dp{1})/(2*_dp{1}*_dm{1})".format(var,m.state[i]))
                    exec("_{0}{1}{1} = (_{0}{1}p{1}*_dm{1} - _{0}{1}m{1}*_dm{1} + _{0}{1}*_dp{1} - _{0}{1}m{1}*_dp{1})/(2*_dp{1}*_dm{1})".format(var,m.state[i]))
                if bounds[i] == 'min' or (m.options.price_derivative_method == 'forward' and bounds[i] != 'max'):
                    exec("_{0}{1} = (_{0}p{1} - {0})/(_dp{1})".format(var,m.state[i]))
                    exec("_{0}{1}{1} = (_{0}{1}p{1} - _{0}{1})/(_dp{1})".format(var,m.state[i]))
                if bounds[i] == 'max' or (m.options.price_derivative_method == 'backward' and bounds[i] != 'min'):
                    exec("_{0}{1} = ({0} - _{0}m{1})/(_dm{1})".format(var,m.state[i]))
                    exec("_{0}{1}{1} = (_{0}{1} - _{0}{1}m{1})/(_dm{1})".format(var,m.state[i]))
            # define cross derivative components on the interior
            if bounds[0] == '' and m.options.price_derivative_method == 'central':
                exec("_{0}{1}{2}a = (_{0}{2}p{1}*_dm{1} - _{0}{2}*_dm{1} + _{0}{2}*_dp{1} - _{0}{2}m{1}*_dm{1})/(2*_dp{1}*_dm{1})"
                    .format(var,m.state[0],m.state[1]))
            if bounds[1] == '' and m.options.price_derivative_method == 'central':
                exec("_{0}{1}{2}b = (_{0}{1}p{2}*_dm{2} - _{0}{1}*_dm{2} + _{0}{1}*_dp{2} - _{0}{1}m{2}*_dm{2})/(2*_dp{2}*_dm{2})"
                    .format(var,m.state[0],m.state[1]))
            # define cross derivative components at the boundaries
            if bounds[0] == 'min' or (m.options.price_derivative_method == 'forward' and bounds[0] != 'max'):
                exec("_{0}{1}{2}a = (_{0}{2}p{1}-_{0}{2})/_dp{1}"
                        .format(var,m.state[0],m.state[1]))
            if bounds[1] == 'min' or (m.options.price_derivative_method == 'forward' and bounds[1] != 'max'):
                exec("_{0}{1}{2}b = (_{0}{1}p{2}-_{0}{1})/_dp{2}"
                        .format(var,m.state[0],m.state[1]))
            if bounds[0] == 'max' or (m.options.price_derivative_method == 'backward' and bounds[0] != 'min'):
                exec("_{0}{1}{2}a = (_{0}{2}-_{0}{2}m{1})/_dm{1}"
                        .format(var,m.state[0],m.state[1]))
            if bounds[1] == 'max' or (m.options.price_derivative_method == 'backward' and bounds[1] != 'min'):
                exec("_{0}{1}{2}b = (_{0}{1}-_{0}{1}m{2})/_dm{2}"
                        .format(var,m.state[0],m.state[1]))
            exec("_{0}{1}{2} = 0.5*_{0}{1}{2}a + 0.5*_{0}{1}{2}b".format(var,m.state[0],m.state[1]))
            # define some engine methods to collect derivatives
            for i in range(len(bounds)):
                element = '_{0}{1}'.format(var,m.state[i])
                exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                        '_{0}{1}.free_symbols'.format(var,m.state[i])))
                exec("self.{0}_{1}fcn_args = list({1}.free_symbols)".format(boundtag,element))
                element = '_{0}{1}{1}'.format(var,m.state[i])
                exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                        '_{0}{1}{1}.free_symbols'.format(var,m.state[i])))
                exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
            element = '_{0}{1}{2}'.format(var,m.state[0],m.state[1])
            exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                    '_{0}{1}{2}.free_symbols'.format(var,m.state[0],m.state[1])))
            exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
        # define derivatives for value as sympy symbols
        for var in m.value:
            for i in range(len(m.state)):
                exec("_{0}{1} = sp.symbols('_{0}{1}')".format(var,m.state[i]))
                exec("_{0}{1}{1} = sp.symbols('_{0}{1}{1}')".format(var,m.state[i]))
            exec("_{0}{1}{2} = sp.symbols('_{0}{1}{2}')".format(var,m.state[0],m.state[1]))
        # define engine methods for derivatives here as necessary for other segments of the package
        for equation in m.equations:
            exec("{0} = {1}".format(equation.name,equation.eq))
            args = eval("list({0}.free_symbols)".format(equation.name))
            exec("self.{0}_{1}fcn = sp.lambdify({2},{1})".format(boundtag,equation.name,str(args)))
            exec("self.{0}_{1}fcn_args = args".format(boundtag,equation.name))
        # define expressions for endogenous equations
        for i,equation in enumerate(m.endog_equations):
            exec("_f{0}_ = {1}".format(i,equation.eq))
        # define methods for the jacobian and set of endogenous equations 
        bigF = sp.Matrix([1 for i in range(len(m.endog))])
        for i in range(len(m.endog)):
            exec("bigF[{0}] = _f{0}_".format(i))
        jac = bigF.jacobian(m.endog)
        myargs = list(bigF.free_symbols.union(jac.free_symbols))
        exec("self.{0}_Ffcn = sp.lambdify(myargs,bigF)".format(boundtag))
        exec("self.{0}_jacobian = sp.lambdify(myargs,jac)".format(boundtag))
        exec("self.{0}_jacobian_args = myargs".format(boundtag))
        exec("self.{0}_Ffcn_args = myargs".format(boundtag))
        # define methods (or constants as appropriate) for HJB equations
        self.isconstant = []
        for tup in m.hjb_equations.keys():
            expr = eval("{}".format(m.hjb_equations[tup].eq))
            if isinstance(expr,Number):
                self.isconstant.append(tup)
                m.params.add_parameter("_{0}_{1}".format(tup[0],tup[1]),expr)
            else:
                args = list(expr.free_symbols)
                exec("self.{0}_{1}{2}hjbfcn = sp.lambdify({3},{4})".format(boundtag,tup[0],tup[1],args,'expr'))        
                exec("self.{0}_{1}{2}hjbfcn_args = args".format(boundtag,tup[0],tup[1]))
        # define methods for endogenous equation systems triggered by constraints
        # .... note that this is done last to enable re-defining intermediates without causing issues for the core system
        self.redefined_intermediates = {}
        for sidx,s in enumerate(m.systems):
            # find redefiend variables 
            core_intermediates = [e.name for e in m.equations]
            system_intermediates = [e.name for e in s.equations]
            self.redefined_intermediates[sidx] = list(set(system_intermediates).intersection(set(core_intermediates)))
            # define expressions for equations
            for equation in s.equations:
                exec("{0} = {1}".format(equation.name,equation.eq))
                args = eval("list({0}.free_symbols)".format(equation.name))
                exec("self.{0}_system{1}_{2}fcn = sp.lambdify({3},{2})".format(boundtag,sidx,equation.name,str(args)))
                exec("self.{0}_system{1}_{2}fcn_args = args".format(boundtag,sidx,equation.name))
            # redefine other intermediates and HJB equations that may be affected by the redefined system intermediates
            for equation in m.equations:
                if equation.name not in self.redefined_intermediates[sidx]:
                    exec("{0} = {1}".format(equation.name,equation.eq))
                    args = eval("list({0}.free_symbols)".format(equation.name))
                    exec("self.{0}_system{1}_{2}fcn = sp.lambdify({3},{2})".format(boundtag,sidx,equation.name,str(args)))
                    exec("self.{0}_system{1}_{2}fcn_args = args".format(boundtag,sidx,equation.name))
            for tup in m.hjb_equations.keys():
                if tup not in self.isconstant:
                    expr = eval("{}".format(m.hjb_equations[tup].eq))
                    args = list(expr.free_symbols)
                    exec("self.{0}_system{1}_{2}{3}hjbfcn = sp.lambdify({4},{5})".format(boundtag,sidx,tup[0],tup[1],args,'expr'))        
                    exec("self.{0}_system{1}_{2}{3}hjbfcn_args = args".format(boundtag,sidx,tup[0],tup[1]))
            # define expressions for endogenous equations
            for i,equation in enumerate(s.endog_equations):
                exec("_f{0}_ = {1}".format(i,equation.eq))
            # define methods for the jacobian and set of endogenous equations 
            bigF = sp.Matrix([1 for i in range(len(m.endog))])
            for i in range(len(s.endog_equations)):
                exec("bigF[{0}] = _f{0}_".format(i))
            jac = bigF.jacobian(m.endog)
            myargs = list(bigF.free_symbols.union(jac.free_symbols))
            exec("self.{0}_system{1}_Ffcn_args = myargs".format(boundtag,sidx))
            exec("self.{0}_system{1}_Ffcn = sp.lambdify(myargs,bigF)".format(boundtag,sidx))
            exec("self.{0}_system{1}_jacobian = sp.lambdify(myargs,jac)".format(boundtag,sidx))
            exec("self.{0}_system{1}_jacobian_args = myargs".format(boundtag,sidx))
        

    def construct_specific_legacy(self,bounds,m):
        """
        Note: This is legacy from Matlab. It does not include functionality for supporting 
              constraint triggered endogenous systems. For the time being, it is considered 
              to be obsolete. It also does not support forward and backward differences
        """
        # define an tag for this set of boundaries 
        boundtag = "b0{0}_b1{1}".format(bounds[0],bounds[1])
        # make state variables and value variables sympy symbols
        for var in m.state:
            exec("{0} = sp.symbols('{0}')".format(var))
        for var in m.value:
            exec("{0} = sp.symbols('{0}')".format(var))
        # make endogenous variables sympy symbols
        for var in m.endog:
            exec("{0} = sp.symbols('{0}')".format(var))
        # make parameters sympy symbols (values to be substituted later)
        for var in m.params.names:
            exec("{0} = sp.symbols('{0}')".format(var))
        # define derivatives for price as sympy symbols and expressions
        for var in m.prices:
            exec("{0} = sp.symbols('{0}')".format(var))
            for i in range(len(bounds)):
                if i == 0:
                    j = 1
                elif i == 1:
                    j = 0
                if bounds[i] != 'min':
                    exec("_dm{0} = sp.symbols('_dm{0}')".format(m.state[i]))
                    exec("_{0}m{1} = sp.symbols('_{0}m{1}')".format(var,m.state[i]))
                    exec("_{0}{1}m{1} = sp.symbols('_{0}{1}m{1}')".format(var,m.state[i]))
                    exec("_{0}{1}m{2} = sp.symbols('_{0}{1}m{2}')".format(var,m.state[j],m.state[i]))
                    exec("_{0}{1}{1}m{1} = sp.symbols('_{0}{1}{1}m{1}')".format(var,m.state[i]))
                    exec("_{0}{1}{1}{1}m{1} = sp.symbols('_{0}{1}{1}{1}m{1}')".format(var,m.state[i]))
                if bounds[i] != 'max':
                    exec("_dp{0} = sp.symbols('_dp{0}')".format(m.state[i]))
                    exec("_{0}p{1} = sp.symbols('_{0}p{1}')".format(var,m.state[i]))
                    exec("_{0}{1}p{1} = sp.symbols('_{0}{1}p{1}')".format(var,m.state[i]))
                    exec("_{0}{1}p{2} = sp.symbols('_{0}{1}p{2}')".format(var,m.state[j],m.state[i]))
                    exec("_{0}{1}{1}p{1} = sp.symbols('_{0}{1}{1}p{1}')".format(var,m.state[i]))
                    exec("_{0}{1}{1}{1}p{1} = sp.symbols('_{0}{1}{1}{1}p{1}')".format(var,m.state[i]))
            for i in range(len(bounds)):
                if bounds[i] == '':
                    exec("_{0}{1} = (_{0}p{1}*_dm{1} - {0}*_dm{1} + {0}*_dp{1} - _{0}m{1}*_dp{1})/(2*_dp{1}*_dm{1})".format(var,m.state[i]))
                    exec("_{0}{1}{1} = (_{0}{1}p{1}*_dm{1} - _{0}{1}m{1}*_dm{1} + _{0}{1}*_dp{1} - _{0}{1}m{1}*_dp{1})/(2*_dp{1}*_dm{1})".format(var,m.state[i]))
                    exec("_{0}{1}{1}{1} = (_{0}{1}{1}p{1}*_dm{1} - _{0}{1}{1}*_dm{1} + _{0}{1}{1}*_dp{1} - _{0}{1}{1}m{1}*_dp{1})/(2*_dp{1}*_dm{1})".format(var,m.state[i]))
                if bounds[i] == 'min':
                    exec("_{0}{1} = _{0}{1}p{1} - _{0}{1}{1}p{1}*_dp{1}".format(var,m.state[i]))
                    exec("_{0}{1}{1} = _{0}{1}{1}p{1} - _{0}{1}{1}{1}p{1}*_dp{1}".format(var,m.state[i]))
                    exec("_{0}{1}{1}{1} = (_{0}{1}{1}p{1} - _{0}{1}{1})/_dp{1}".format(var,m.state[i]))
                if bounds[i] == 'max':
                    exec("_{0}{1} = _{0}{1}m{1} + _{0}{1}{1}m{1}*_dm{1}".format(var,m.state[i]))
                    exec("_{0}{1}{1} = _{0}{1}{1}m{1} + _{0}{1}{1}{1}m{1}*_dm{1}".format(var,m.state[i]))
                    exec("_{0}{1}{1}{1} = (_{0}{1}{1} - _{0}{1}{1}m{1})/_dm{1}".format(var,m.state[i]))
            # define cross derivatives 
            if bounds[0] != 'min':
                exec("_{0}{1}{2}m{1} = sp.symbols('_{0}{1}{2}m{1}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{1}m{1} = sp.symbols('_{0}{1}{2}{1}m{1}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{2}m{1} = sp.symbols('_{0}{1}{2}{2}m{1}')".format(var,m.state[0],m.state[1]))
            if bounds[1] != 'min':
                exec("_{0}{1}{2}m{2} = sp.symbols('_{0}{1}{2}m{2}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{1}m{2} = sp.symbols('_{0}{1}{2}{1}m{2}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{2}m{2} = sp.symbols('_{0}{1}{2}{2}m{2}')".format(var,m.state[0],m.state[1]))
            if bounds[0] != 'max':
                exec("_{0}{1}{2}p{1} = sp.symbols('_{0}{1}{2}p{1}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{1}p{1} = sp.symbols('_{0}{1}{2}{1}p{1}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{2}p{1} = sp.symbols('_{0}{1}{2}{2}p{1}')".format(var,m.state[0],m.state[1]))
            if bounds[1] != 'max':
                exec("_{0}{1}{2}p{2} = sp.symbols('_{0}{1}{2}p{2}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{1}p{2} = sp.symbols('_{0}{1}{2}{1}p{2}')".format(var,m.state[0],m.state[1]))
                exec("_{0}{1}{2}{2}p{2} = sp.symbols('_{0}{1}{2}{2}p{2}')".format(var,m.state[0],m.state[1]))
            if bounds[0] == '':
                exec("_{0}{1}{2}a = (_{0}{2}p{1}*_dm{1} - _{0}{2}*_dm{1} +_{0}{2}*_dp{1} - _{0}{2}m{1}*_dp{1})/(2*_dm{1}*_dp{1})".format(var,m.state[0],m.state[1]))
            if bounds[1] == '':
                exec("_{0}{1}{2}b = (_{0}{1}p{2}*_dm{2} - _{0}{1}*_dm{2} +_{0}{1}*_dp{2} - _{0}{1}m{2}*_dp{2})/(2*_dm{2}*_dp{2})".format(var,m.state[0],m.state[1]))
            if bounds[0] == 'min':
                exec("_{0}{1}{2}a = _{0}{1}{2}p{1} - _{0}{1}{2}{1}p{1}*_dp{1}".format(var,m.state[0],m.state[1]))
            if bounds[1] == 'min':
                exec("_{0}{1}{2}b = _{0}{1}{2}p{2} - _{0}{1}{2}{2}p{2}*_dp{2}".format(var,m.state[0],m.state[1]))
            if bounds[0] == 'max':
                exec("_{0}{1}{2}a = _{0}{1}{2}m{1} + _{0}{1}{2}{1}m{1}*_dm{1}".format(var,m.state[0],m.state[1]))
            if bounds[1] == 'max':
                exec("_{0}{1}{2}b = _{0}{1}{2}m{2} + _{0}{1}{2}{2}m{2}*_dm{2}".format(var,m.state[0],m.state[1]))
            exec("_{0}{1}{2} = 0.5*_{0}{1}{2}a + 0.5*_{0}{1}{2}b".format(var,m.state[0],m.state[1]))
            if bounds[0] == '':
                exec("_{0}{1}{2}{1} = (_{0}{1}{2}p{1}*_dm{1} - _{0}{1}{2}*_dm{1} + _{0}{1}{2}*_dp{1} - _{0}{1}{2}m{1}*_dm{1})/(2*_dp{1}*_dm{1})".format(var,m.state[0],m.state[1]))
            if bounds[1] == '':
                exec("_{0}{1}{2}{2} = (_{0}{1}{2}p{2}*_dm{2} - _{0}{1}{2}*_dm{2} + _{0}{1}{2}*_dp{2} - _{0}{1}{2}m{2}*_dm{2})/(2*_dp{2}*_dm{2})".format(var,m.state[0],m.state[1]))
            if bounds[0] == 'min':
                exec("_{0}{1}{2}{1} = (_{0}{1}{2}p{1} - _{0}{1}{2})/_dp{1}".format(var,m.state[0],m.state[1]))
            if bounds[1] == 'min':
                exec("_{0}{1}{2}{2} = (_{0}{1}{2}p{2} - _{0}{1}{2})/_dp{2}".format(var,m.state[0],m.state[1]))
            if bounds[0] == 'max':
                exec("_{0}{1}{2}{1} = (_{0}{1}{2} - _{0}{1}{2}m{1})/_dm{1}".format(var,m.state[0],m.state[1]))
            if bounds[1] == 'max':
                exec("_{0}{1}{2}{2} = (_{0}{1}{2} - _{0}{1}{2}m{2})/_dm{2}".format(var,m.state[0],m.state[1]))
            # define some engine methods to collect derivatives
            for i in range(len(bounds)):
                element = '_{0}{1}'.format(var,m.state[i])
                exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                        '_{0}{1}.free_symbols'.format(var,m.state[i])))
                exec("self.{0}_{1}fcn_args = list({1}.free_symbols)".format(boundtag,element))
                element = '_{0}{1}{1}'.format(var,m.state[i])
                exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                        '_{0}{1}{1}.free_symbols'.format(var,m.state[i])))
                exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
                element = '_{0}{1}{1}{1}'.format(var,m.state[i])
                exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                        '_{0}{1}{1}.free_symbols'.format(var,m.state[i])))
                exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
            element = '_{0}{1}{2}'.format(var,m.state[0],m.state[1])
            exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                    '_{0}{1}{2}.free_symbols'.format(var,m.state[0],m.state[1])))
            exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
            element = '_{0}{1}{2}{1}'.format(var,m.state[0],m.state[1])
            exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                    '_{0}{1}{2}.free_symbols'.format(var,m.state[0],m.state[1])))
            exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
            element = '_{0}{1}{2}{2}'.format(var,m.state[0],m.state[1])
            exec("self.{0}_{1}fcn = sp.lambdify(list({2}),{1})".format(boundtag,element,
                    '_{0}{1}{2}.free_symbols'.format(var,m.state[0],m.state[1])))
            exec("self.{0}_{1}fcn_args = {1}.free_symbols".format(boundtag,element))
        # define derivatives for value as sympy symbols
        for var in m.value:
            for i in range(len(m.state)):
                exec("_{0}{1} = sp.symbols('_{0}{1}')".format(var,m.state[i]))
                exec("_{0}{1}{1} = sp.symbols('_{0}{1}{1}')".format(var,m.state[i]))
            exec("_{0}{1}{2} = sp.symbols('_{0}{1}{2}')".format(var,m.state[0],m.state[1]))
        # define engine methods for derivatives here as necessary for other segments of the package
        for equation in m.equations:
            exec("{0} = {1}".format(equation.name,equation.eq))
            args = eval("list({0}.free_symbols)".format(equation.name))
            exec("self.{0}_{1}fcn = sp.lambdify({2},{1})".format(boundtag,equation.name,str(args)))
            exec("self.{0}_{1}fcn_args = args".format(boundtag,equation.name))
        # define expressions for endogenous equations
        for i,equation in enumerate(m.endog_equations):
            exec("_f{0}_ = {1}".format(i,equation.eq))
        # define methods for the jacobian and set of endogenous equations 
        bigF = sp.Matrix([1 for i in range(len(m.endog))])
        for i in range(len(m.endog)):
            exec("bigF[{0}] = _f{0}_".format(i))
        exec("self.{0}_Ffcn_args = list(bigF.free_symbols)".format(boundtag))
        exec("self.{0}_Ffcn = sp.lambdify(self.{0}_Ffcn_args,bigF)".format(boundtag))
        jac = bigF.jacobian(m.endog)
        exec("self.{0}_jacobian = sp.lambdify(list(jac.free_symbols),jac)".format(boundtag))
        exec("self.{0}_jacobian_args = list(jac.free_symbols)".format(boundtag))
        # define methods (or constants as appropriate) for HJB equations
        self.isconstant = []
        for tup in m.hjb_equations.keys():
            expr = eval("{}".format(m.hjb_equations[tup].eq))
            if isinstance(expr,Number):
                self.isconstant.append(tup)
                m.params.add_parameter("_{0}_{1}".format(tup[0],tup[1]),expr)
            else:
                args = list(expr.free_symbols)
                exec("self.{0}_{1}{2}hjbfcn = sp.lambdify({3},{4})".format(boundtag,tup[0],tup[1],args,'expr'))        
                exec("self.{0}_{1}{2}hjbfcn_args = args".format(boundtag,tup[0],tup[1]))
