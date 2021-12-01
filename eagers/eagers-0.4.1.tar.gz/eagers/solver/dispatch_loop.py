import time

from eagers.solver.ecos_qp import ecos_qp
from eagers.solver.sort_solution import sort_solution, sort_gen_disp, sort_eh
from eagers.solver.fix_infeasible import fix_infeasible
from eagers.solver.dispatch_step import dispatch_step
from eagers.solver.cqp_method import cqp_method
from eagers.solver.verify_ramping import verify_ramping
from eagers.basic.marginal_cost import net_marginal_cost
from eagers.update.update_matrices import update_matrices
from eagers.update.disable_gen import disable_gen
from eagers.solver.minimize_start_costs import minimize_start_costs
from eagers.solver.inverter_correction import inverter_correction


def dispatch_loop(gen,observer,subnet,names,op_mat_a,op_mat_b,one_step,options,date,forecast,prediction):
    """
    This is the function that gets called to solve the receding horizon
    dispatch optimization problem. Depending on user selected options, the
    dispatch will be created using mcQP or cQP. This function calculates 
    the optimal dispatch over the forecast horizon.
    
    INPUTS:
    gen        - a list of dictionaries with relevant parameters for each generator
    observer   - a disctionary tracking the current state of generators, buildings and fluid loops and a short history relevant for forecasting methods
    subnet     - a dictionary with all of the network nodes, line properties and equipment lists
    op_mat_a   - optimization matrices for fit a
    op_mat_b   - optimization matrices for fit b
    options    - instance of class Options for all user defined optimization options
    date       - list of timestamps for initial condition through last timestep
    forecast   - forecast of demand profiles, weather, and any other parameters
    prediction - estimate taken from previoius solution used to get initial marginal costs

    OUTPUTS:
    solution   - dispatch optimization solution matrix

    FLAGS:
        0 -- Standard operation.
        1 -- Initial dispatch (Fit A) infeasible.
        2 -- Second dispatch (Fit B) infeasible.
    """
    flag = 0# Initialize flag.
    dt = [(date[t+1] - date[t]).total_seconds()/3600 for t in range(len(date)-1)]
    net_abbrev = [subnet[net]['abbreviation'] for net in subnet['network_names']]
    margin_cost = net_marginal_cost(gen,net_abbrev,observer['market'],prediction, forecast['input_cost'], dt, None)
    t_sim = [0 for i in range(3)]# Initialize t_sim
    update_matrices(gen, observer, subnet, options, op_mat_a, date,
        forecast['input_cost'], margin_cost, forecast, None)

    # STEP 1: Determine initial dispatch.
    t_start = time.time()
    disable_gen(op_mat_a, None)
    x, feasible = ecos_qp(op_mat_a['h'], op_mat_a['f'], op_mat_a['a'], op_mat_a['b'], op_mat_a['a_eq'], op_mat_a['b_eq'], op_mat_a['ub'], op_mat_a['lb'], op_mat_a['x_keep'], op_mat_a['r_keep'], op_mat_a['req_keep'])
    t_sim[0] = time.time() - t_start
    v_h = [[True if j<1 else False for j in s_eh] for s_eh in sort_eh(x, op_mat_a)] #do you value heat generation, or is there tons of extra
    if feasible == 0:
        dispatch1 = [sort_gen_disp(x, op_mat_a, i) for i in range(len(gen))]
        if options['mixed_integer'] and any(op_mat_a['organize']['dispatchable']): # Might be some on/off combinations.
            # STEP 2: dispatch step by step.
            gen_output, stor_power, binary_comb, disp_comb, build_temp, fluid_temp, cost_comb, verified, flag = dispatch_step(
                gen, observer, subnet, options, one_step,date, forecast, forecast['input_cost'], dt, dispatch1,v_h)
             # #change best dispatch based on re-start costs
            optimal_state,_ = minimize_start_costs(
                one_step ,gen, observer['market'], subnet, options, forecast, dispatch1,
                forecast['input_cost'], gen_output, stor_power, binary_comb,disp_comb, 
                build_temp, fluid_temp, cost_comb, verified, observer, dt, v_h)
        else:
            optimal_state = dispatch1
        t_sim[1] = time.time() - t_start - t_sim[0]
        # STEP 3: 2nd complete optimization.
        margin_cost = net_marginal_cost(gen,net_abbrev,observer['market'],optimal_state, forecast['input_cost'], dt, None)
        update_matrices(gen, observer, subnet, options, op_mat_b, date,# Update fit B matrices.
            forecast['input_cost'], margin_cost, forecast, None)
        if not options['mixed_integer']:
            solution = cqp_method(names, gen, op_mat_b, dispatch1, date)
        else:
            locked = verify_ramping(gen, subnet, op_mat_b, optimal_state, forecast['input_cost'], dt)
            disable_gen(op_mat_b, locked)
            x, feasible = ecos_qp(op_mat_b['h'], op_mat_b['f'], op_mat_b['a'], op_mat_b['b'], op_mat_b['a_eq'], op_mat_b['b_eq'], op_mat_b['ub'], op_mat_b['lb'], op_mat_b['x_keep'], op_mat_b['r_keep'], op_mat_b['req_keep'])
            if feasible != 0:
                flag = 2
                print('Dispatch error: Cannot find feasible dispatch.')
                x, feasible = fix_infeasible(op_mat_b)
            v_h = [[True if j<1 else False for j in s_eh] for s_eh in sort_eh(x, op_mat_b)] #do you value heat? record in solution for later
            solution = sort_solution(x, op_mat_b, names, gen, date, v_h)
            inverter_correction(gen,subnet,forecast,solution,0)
        t_sim[2] = time.time() - t_start  - sum(t_sim[:2])
    else:
        flag = 1
        x, feasible = fix_infeasible(op_mat_a)
        solution = sort_solution(x, op_mat_a, names, gen, date, v_h)
    solution['timer'] = t_sim

    return solution, flag