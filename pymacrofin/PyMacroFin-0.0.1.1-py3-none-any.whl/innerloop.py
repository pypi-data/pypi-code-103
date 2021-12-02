import numpy as np
import pandas as pd
import scipy 
import PyMacroFin.utilities as util 
from scipy.optimize import fsolve, least_squares
import multiprocessing as mp
import joblib as jl
#from dask.distributed import Client
import cloudpickle
pd.options.mode.chained_assignment = None

def innerloop(m,df):
    """
    Function for the inner loop
    """
    # outer static loop
    for i_outer in range(m.options.max_iter_outer_static):
        # reset original endogenous variables 
        orig = df[[x for x in m.endog]].copy()
        # set lagged in state dimension direction variables (and lagged grid distance variables)
        df = util.shift_derivatives(m,df)
        # loop over grid points
        if m.options.parallel:
            with jl.parallel_backend('dask'):
                results = jl.Parallel(verbose=1,timeout=100)(jl.delayed(inner_static)(df.loc[n,:],n,m.name) for n in range(df.shape[0]))
            df = pd.DataFrame(results)
        else:
            for n in range(m.options.N):
                df.loc[n,:] = inner_static(df.loc[n,:],n,m.name)
        # apply dampening
        if m.options._loop == 1:
            for var in m.endog:
                df[var] = (1-m.options._active_damp1)*df[var] + m.options._active_damp1*df[var]
        elif m.options._loop == 2:
            for var in m.endog:
                df[var] = (1-m.options._active_damp2)*df[var] + m.options._active_damp2*df[var]
        # recalculate appropriate price derivatives
        df = util.shift_prices(m,df)
        df = util.calculate_price_derivatives(m,df)
        # recalculate all secondary variables based on new endog variable values
        df = util.calculate_secondary(m,df)
        # calculate outer static error
        outer_static_error = np.power(df[[x for x in m.endog]] - orig,2).sum().sum()
        if not m.options.quiet:
            print("    outer static loop iteration {0} completed with error {1:.3g}".format(i_outer+1,outer_static_error))
        # plot if set to plot
        if m.options.inner_plot:
            if m.use_dash:
                df[m.secondaryplot+m.endog+m.value].to_csv('./tmp{}/dash_data.csv'.format(m.name),index=False)
            else:
                util.plot(m,df)
        if i_outer > m.options.min_iter_outer_static and outer_static_error < m.options.tol_outer_static:
            break
    return df
        
def inner_static(row,n,name):
    """
    Run inner static loop for a grid point
    """
    # load model
    m = cloudpickle.load(open('modeltmp_{}.pkl'.format(name),'rb'))
    # find boundtag
    boundtag = row.loc['boundtag'] 
    # check if you are on a boundary with a defined boundary condition, and if so, simply return the boundary and exit
    on_boundary, results = util.check_boundary_condition(m.boundaries,boundtag,m.endog,row,m.params,m.state)
    if on_boundary:
        assert len(results)==len(m.endog), "invalid function used for boundary condition. Must return a vector corresponding to the endogenous variables"
        for idx,var in enumerate(m.endog):
            row.loc[var] = results[idx]
    else:
        # increase tolerance for early iterations on grid corners
        if boundtag in ['b0min_b1min','b0min_b1max','b0max_b1min','b0max_b1max']:
            working_inner_tolerance = m.options.tol_inner_static_corner
        elif 'min' in boundtag or 'max' in boundtag:
            working_inner_tolerance = m.options.tol_inner_static_boundary
        else:
            working_inner_tolerance = m.options.tol_inner_static
        best_solution = {'val':[],'error':1000}
        if m.options.inner_solver=='newton-raphson':
            # newton raphson in a loop for the grid point (inner static loop)
            for i_inner in range(m.options.max_iter_inner_static):
                # get ordered endog variables at this point
                x = [row.loc[var] for var in m.endog]
                # get jacobian and endog zero function values
                jac_args = eval("m.engine.{0}_jacobian_args".format(boundtag))
                argslist = [args.name for args in jac_args]
                problematic = [arg for arg in argslist if np.isnan(row.loc[arg])]
                if len(problematic)>0:
                    if best_solution['error'] < working_inner_tolerance:
                        for idx,var in enumerate(m.endog):
                            row.loc[var] = best_solution['val'][idx]
                        break
                    else:
                        #if m.options.parallel:
                        #    m.client.close()
                        raise ValueError("There are nans in the arguments for the jacobian at point {0} and inner static loop iteration {1}.\nThis typically is the result of an infeasible endogenous system at this grid point.\nBest solution found is {2} with error {3}".format(n,i_inner,best_solution['val'],best_solution['error']))
                jacobian = eval("m.engine.{0}_jacobian({1})".format(boundtag,','.join(["row.loc['{}']".format(x) for x in jac_args])))
                fargs = eval("m.engine.{0}_Ffcn_args".format(boundtag))
                ff = eval("m.engine.{0}_Ffcn({1})".format(boundtag,','.join(["row.loc['{}']".format(x) for x in fargs])))
                if np.isnan(ff).any() or np.isnan(jacobian).any():
                        #if m.options.parallel:
                        #    m.client.close()
                        raise ValueError("There are nans in the jacobian or endogenous equation results at point {0} and inner static loop iteration {1}.\nThis typically is the result of an infeasible endogenous system at this grid point.\nBest solution found is {2} with error {3}".format(n,i_inner,best_solution['val'],best_solution['error']))
                # filter the system for Newton Raphson to remove elements that have active constraints
                notbinding = [True for i in range(len(m.endog))]
                active_bounds = {}
                for i,constraint in enumerate(m.constraints):
                    idx = m.endog.index(constraint.endog_var)
                    exec("if not {0}{1}{2}: notbinding[{3}] = False".format(row.loc[constraint.endog_var],constraint.constraint_type,constraint.bound,idx))
                    if notbinding[idx] == False:
                        active_bounds[constraint.endog_var] = constraint.bound
                # now we need to filter the rest of the newton raphson behavior by the binding array
                workable_jacobian = pd.DataFrame(jacobian).loc[notbinding,notbinding].to_numpy()
                workable_ff = pd.Series(ff.flatten()).loc[notbinding].to_numpy()
                # precondition inversion
                try:
                    xdff = np.diag(1./np.abs(workable_jacobian).sum(axis=0))
                    idff = xdff @ np.linalg.inv(workable_jacobian @ xdff)
                except:
                    if best_solution['error'] < working_inner_tolerance:
                        for idx,var in enumerate(m.endog):
                            row.loc[var] = best_solution['val'][idx]
                        break
                    else:
                        #if m.options.parallel:
                        #    m.client.close()
                        raise ValueError("precondition inversion failure in the static loop at grid index {0} and inner static loop iteration {1}. Please check your model for infeasibilities in the endogenous system. \nBest solution found is {2} with error {3}".format(n,i_inner,best_solution['val'],best_solution['error']))
                # calculate new vector of endogenous variables 
                # -- usable uses newton raphson and non usable just gets the bound
                workable_newx = pd.Series(x).loc[notbinding].to_numpy() - idff @ workable_ff
                newx = []
                workable_idx = 0
                for idx in range(len(m.endog)):
                    if notbinding[idx]:
                        newx.append(workable_newx[workable_idx])
                        workable_idx += 1
                    else:
                        newx.append(active_bounds[m.endog[idx]])
                # calculate the error for this grid point in the endogenous equation system
                inner_static_error = np.linalg.norm(workable_ff)
                # update best solution
                if inner_static_error < best_solution['error']:
                    best_solution['error'] = inner_static_error
                    best_solution['val'] = newx
                # reset x for next iteration
                for idx,var in enumerate(m.endog):
                    row.loc[var] = newx[idx]
                # break if appropriate
                if i_inner > m.options.min_iter_inner_static and inner_static_error < m.options.tol_inner_static: #working_inner_tolerance:
                    # replace with best solution if better than final iteration 
                    if best_solution['error'] < inner_static_error:
                        for idx,var in enumerate(m.endog):
                            row.loc[var] = best_solution['val'][idx]
                    break
        elif m.options.inner_solver=='fsolve' or m.options.inner_solver=='least_squares':
            def prepare_inputs():
                guess = [row.loc[x] for x in m.endog]
                fargs = eval("m.engine.{0}_Ffcn_args".format(boundtag))
                other = [row.loc[x.name] for x in fargs if x.name not in m.endog]
                order = {'endog':np.ones(len(m.endog))*np.nan,'other':[]}
                for i,x in enumerate(list(fargs)):
                    if x.name in m.endog:
                        j = m.endog.index(x.name)
                        order['endog'][j] = i
                    else:
                        order['other'].append(i)
                packed = (other,order,boundtag,m.engine,None)
                return [packed,guess]
            packed, guess = prepare_inputs()
            if m.options.inner_solver=='fsolve':
                result = fsolve(util.scipy_solver_feed,guess,args=packed,xtol=working_inner_tolerance)
            elif m.options.inner_solver=='least_squares':
                bounds = ([-np.inf for x in m.endog],[np.inf for x in m.endog])
                for c in m.constraints:
                    i = m.endog.index(c.endog_var) 
                    if c.constraint_type in ['<','<=']:
                        bounds[1][i] = c.bound
                    elif c.constraint_type in ['>','>=']:
                        bounds[0][i] = c.bound
                result_ = least_squares(util.scipy_solver_feed,guess,args=packed,xtol=working_inner_tolerance,bounds=bounds,jac=util.scipy_jacobian_feed)
                result = result_.x
                # check for systems with constraint triggers satisfied
                finished = False
                for sidx,s in enumerate(m.systems):
                    triggers = []
                    for c in m.constraints:
                        if c.label != '' and c.label in s.constraint_trigger:
                            triggers.append(c)
                    satisfied = all([util.triggered(result_,c,m.endog) for c in triggers])
                    if satisfied:
                        # if constraint system is binding then run the constraint system and label the grid point with that system 
                        result = run_system_scipy(s,sidx,row,m,bounds,boundtag,working_inner_tolerance)
                        row.loc['_sidx'] = sidx
                        break
                    else:
                        # if this constraint system is nonbinding, then ensure that this grid point is correctly label 
                        # ... (i.e. could have been binding on a previous iteration but not anymore)
                        if row.loc['_sidx'] == sidx:
                            row.loc['_sidx'] = np.nan
            for idx,var in enumerate(m.endog):
                row.loc[var] = result[idx]
            packed, endog_result = prepare_inputs()
            should_be_zeros = util.scipy_solver_feed(endog_result,*packed)
            inner_static_error = np.linalg.norm(should_be_zeros)
        
    return row
    
def run_system_scipy(system,sidx,row,m,bounds,boundtag,working_inner_tolerance):
    """
    Run an endogenous system on a grid point
    """
    guess = [row.loc[x] for x in m.endog]
    fargs = eval("m.engine.{0}_system{1}_Ffcn_args".format(boundtag,sidx))
    other = [row.loc[x.name] for x in fargs if x.name not in m.endog]
    order = {'endog':np.ones(len(m.endog))*np.nan,'other':[]}
    for i,x in enumerate(list(fargs)):
        if x.name in m.endog:
            j = m.endog.index(x.name)
            order['endog'][j] = i
        else:
            order['other'].append(i)
    packed = (other,order,boundtag,m.engine,sidx)
    result_ = least_squares(util.scipy_solver_feed,guess,args=packed,xtol=working_inner_tolerance,bounds=bounds,jac=util.scipy_jacobian_feed)
    result = result_.x
    return result
