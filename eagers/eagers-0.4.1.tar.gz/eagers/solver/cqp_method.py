"""Complimentary Quadratic Programming method (not mcQP method).

Functions:
cqp_method
rule_one
rule_two
rule_three
rule_four
"""

from eagers.solver.ecos_qp import ecos_qp
from eagers.solver.sort_solution import sort_solution, sort_eh
from eagers.update.disable_gen import disable_gen
from eagers.basic.hdf5 import DatetimeFloatConverter as DFC


def cqp_method(names, gen, qp, first_disp, date):
    """Positional arguments:
    gen - (list of dict) Generator dictionary reperesentations.
    qp - (dict)
    first_disp - (2D list) First dispatch.
    date - (list of datetime)
    """
    n_s = len(date) - 1
    n_g = len(gen)
    locked = [[True for t in range(n_s+1)] for i in range(n_g)]
    for i in range(n_g):
        if not gen[i]['enabled']:
            locked[i] = [False for t in range(n_s+1)]
    lower_bound = [0 for i in range(n_g)]
    upper_bound = [0 for i in range(n_g)]
    dx = [[0 for t in range(n_s)] for i in range(n_g)]
    dt_seconds = [(date[t+1] - date[t]).total_seconds() for t in range(n_s)]
    dt = [dt_seconds[t]/3600 for t in range(n_s)]
    for i in range(n_g):
        if qp['organize']['dispatchable'][i]:
            states = gen[i]['states'][-1]
            for j in range(len(states)):
                lower_bound[i] += gen[i][states[j]]['lb'][-1]
                upper_bound[i] += gen[i][states[j]]['ub'][-1]
            # Default to off when initial dispatch is below lb.
            for t in range(n_s):
                if first_disp[i][t+1]<lower_bound[i]:
                    locked[i][t] = False
        if 'ramp' in gen[i]:
            dx[i] = [dt[t]*gen[i]['ramp'] for t in range(n_s)]
    # Make sure it can shut down in time from initial condition.
    for i in range(n_g):
        if qp['organize']['dispatchable'][i]:
            if first_disp[i][0] > 0 and not all(locked[i]):
                d = first_disp[i][0]
                t = 0
                while d > 0:
                    r = qp['organize']['ramp_down'][t]
                    d -= qp['b'][r]
                    if d > 0 and not locked[i][t]:
                        locked[i][t] = True
                    t += 1

    feasible = 1
    attempt = 0
    lb_relax = 1

    # attempt: Integer value describing the number of attempts before
    # reaching feasibility. This determines how close components must be to
    # their lower bound from below to be considered online.
    # 
    # n: Represents the percent of lower bounds on your first try. Just use
    # the locked matrix given, then do unit commitment based on
    # optimal_state > lb * perc_lb
    perc_lb = [0.9, 0.75, 0.5, 0.2, 0.1, 0, -1]
    while feasible != 0 and attempt < len(perc_lb):
        if attempt > 0:
            # Not the first try. Lower limit for online threshold.
            lb_relax = perc_lb[attempt-1]
            # Only change label for unit commitment gens, and don't change the
            # label for initial conditions.
            for i in range(n_g):
                if qp['organize']['dispatchable'][i]:
                    # Default to on unless offline in initial dispatch.
                    locked[i] = [True if first_disp[i][t] > (lower_bound[i] * lb_relax) else False for t in range(len(first_disp[i]))]
        disable_gen(qp, locked)
        x, feasible = ecos_qp(qp['h'], qp['f'], qp['a'], qp['b'], qp['a_eq'], qp['b_eq'], qp['ub'], qp['lb'], qp['x_keep'], qp['r_keep'], qp['req_keep'])
        attempt += 1


    if feasible == 0:
        v_h = [[True if j<1 else False for j in s_eh] for s_eh in sort_eh(x, qp)] #do you value heat generation, or is there tons of extra
        solution = sort_solution(x, qp, names, gen, date, v_h)

        # ----------------------------------------------------------------
        # The following section of code implements superfluous heuristics.
        # ----------------------------------------------------------------
        # 
        # first_disp = solution['dispatch']
        # cost = sum(net_cost(gen,solution.dispatch,date))
        # for i in range(n_g):
        #     if qp.organize.dispatchable[i]:
        #         locked, cost, solution, starts = rule_one(
        #             gen, locked, cost, solution, date, qp, dx, first_disp, i)
        #         locked, cost, solution, stops = rule_two(
        #             gen, locked, cost, solution, date, starts, qp, dx,
        #             first_disp, i)
        #         locked, cost, solution = rule_three(
        #             gen, locked, cost, solution, date, starts, stops, qp, dx,
        #             first_disp, i)
        # _, _, solution = rule_four(
        #     gen, locked, cost, solution, date, qp, dx, upper_bound)
    solution['lb_relax'] = [lb_relax]
    
    return solution


def rule_one(gen, locked, cost, solution, date, qp, dx, first_disp, i):
    # function [locked,cost,solution,starts] = rule_one(gen,locked,cost,solution,date,qp,dx,first_disp,i)
    # %% Rule 1: turn off for longer time at start if possible
    # n_s = length(dx(:,1));
    # index = (1:n_s)';
    # starts = nonzeros(index.*((locked(2:end,i)-locked(1:n_s,i))>0)); % if on at t = 3, start = 3, where IC is t=0
    # if ~locked(1,i) && ~isempty(starts)
    #     p = 0;
    #     ramp_up = dx(starts(1),i);
    #     while ramp_up<first_disp(starts(1)+1,i) && (starts(1)-p>0)
    #         ramp_up = ramp_up+dx(starts(1)-p,i);
    #         p = p+1;
    #     end
    #     if starts(1)-p>0
    #         l2 = locked;
    #         l2(1:(starts(1)-p+1),i) = false;
    #         disable_gen(qp,l2);%Disable generators here
    #         [x,Feasible] = call_solver(qp);
    #         if Feasible == 1
    #             sol_new = sort_solution(x,qp);
    #             new_cost = sum(net_cost(gen,sol_new.dispatch,date));
    #             if new_cost<cost
    #                 locked = l2;
    #                 cost = new_cost;
    #                 solution = sol_new;
    #             end
    #         end
    #     end
    #     if length(starts)>1
    #         starts = starts(2:end);
    #     else
    #         starts = [];
    #     end
    # end
    # end%ends function rule_one

    locked, cost, solution, starts = 0, 0, 0, 0  # TODO: Translate from Matlab.
    return locked, cost, solution, starts


def rule_two(
        gen, locked, cost, solution, date, starts, qp, dx, first_disp, i):
    # function [locked,cost,solution,stops] = rule_two(gen,locked,cost,solution,date,starts,qp,dx,first_disp,i)
    # %% Rule 2: If off for a long enough segment in first dispatch, try turning off for as much of that as possible given ramp rates
    # n_s = length(dx(:,1));
    # index = (1:n_s)';
    # stops = nonzeros(index.*((locked(1:n_s,i)-locked(2:end,i))>0)); % if off at t = 12, stop = 12, where IC is t=0
    # for k = 1:1:length(starts)
    #     if ~isempty(stops) && length(stops)>=k
    #         if sum(dx(stops(k):starts(k)-1,i))>(first_disp(stops(k),i) + first_disp(starts(k)+1,i)) %can ramp all the way down, and back up, and be off for 1 step
    #             l2 = locked;
    #             %find step when it can hit zero given setting at Disp(stops(k)
    #             n=1;
    #             ramp_down = dx(stops(k),i);
    #             while ramp_down<first_disp(stops(k),i)
    #                 ramp_down = ramp_down+dx(stops(k)+n,i);
    #                 n = n+1;
    #             end
    #             p = 1;
    #             ramp_up = dx(starts(k),i);
    #             while ramp_up<first_disp(starts(k)+1,i)
    #                 ramp_up = ramp_up+dx(starts(k)-p,i);
    #                 p = p+1;
    #             end
    #             l2((stops(k)+n):(starts(k)-p+1),i) = false;
    #             disable_gen(qp,l2);%Disable generators here
    #             [x,feasible] = call_solver(qp);
    #             if feasible == 1
    #                 sol_new = sort_solution(x,qp);
    #                 new_cost = sum(net_cost(gen,sol_new.dispatch,date));
    #                 if new_cost<cost
    #                     locked = l2;
    #                     cost = new_cost;
    #                     solution = sol_new;
    #                 end
    #             end
    #         end
    #     end
    # end
    # end%ends function rule_two

    locked, cost, solution, stops = 0, 0, 0, 0  # TODO: Translate from Matlab.
    return locked, cost, solution, stops


def rule_three(
        gen, locked, cost, solution, date, starts, stops, qp, dx, first_disp,
        i):
    # function [locked,cost,solution] = rule_three(gen,locked,cost,solution,date,starts,stops,qp,dx,first_disp,i)
    # %% Rule 3: try turning off @ end
    # n_s = length(dx(:,1));
    # if length(stops)>length(starts)
    #     n=stops(end);
    #     ramp_down = dx(n,i);
    #     while ramp_down<first_disp(stops(end),i) && n<(n_s) && n>0
    #         ramp_down = ramp_down+dx(n,i);
    #         n = n-1;
    #     end
    #     if n<(n_s)
    #         l2 = locked;
    #         l2((n+1):n_s+1,i) = false;
    #         disable_gen(qp,l2);%Disable generators here
    #         [x,feasible] = call_solver(qp);
    #         if feasible == 1
    #             sol_new = sort_solution(x,qp);
    #             new_cost = sum(net_cost(gen,sol_new.dispatch,date));
    #             if new_cost<cost
    #                 locked = l2;
    #                 cost = new_cost;
    #                 solution = sol_new;
    #             end
    #         end
    #     end
    # end
    # end%ends rule_three

    locked, cost, solution = 0, 0, 0  # TODO: Translate from Matlab.
    return locked, cost, solution


def rule_four(gen, locked, cost, solution, date, qp, dx, upper_bound):
    # function [locked,cost,solution] = rule_four(gen,locked,cost,solution,date,qp,dx,upper_bound)
    # %% Rule 4: if on for a short time and sufficient capacity in remaining active generators, turn gen off completely
    # n_s = length(dx(:,1));
    # n_g = length(gen);
    # index = (1:n_s)';
    # for i = 1:1:n_g
    #     starts = nonzeros(index.*((locked(2:end,i)-locked(1:n_s,i))>0)); % if on at t = 3, start = 3, where IC is t=0
    #     stops = nonzeros(index.*((locked(1:n_s,i)-locked(2:end,i))>0)); % if off at t = 12, stop = 12, where IC is t=0
    #     if qp.Organize.Dispatchable(i)
    #         if locked(1,i)
    #             if length(stops)>1
    #                 stops = stops(2:end);
    #             else
    #                 stops = [];
    #             end
    #         end
    #         for k = 1:1:length(stops)
    #             if sum(dx(starts(k):stops(k),i))<upper_bound(i) && sum(locked(:,i))<floor(n_s/4)%can only ramp to 1/2 power and less than 1/4 of horizon
    #                 l2 = locked;
    #                 l2(starts(k):(stops(k)+1),i)= false;
    #                 disable_gen(qp,l2);%Disable generators here
    #                 [x,feasible] = call_solver(qp);
    #                 if feasible == 1
    #                     sol_new = sort_solution(x,qp);
    #                     new_cost = sum(net_cost(gen,sol_new.dispatch,date));
    #                     if new_cost<cost
    #                         locked = l2;
    #                         cost = new_cost;
    #                         solution = sol_new;
    #                     end
    #                 end
    #             end
    #         end
    #     end
    # end
    # end%ends function rule_four

    locked, cost, solution = 0, 0, 0  # TODO: Translate from Matlab.
    return locked, cost, solution
