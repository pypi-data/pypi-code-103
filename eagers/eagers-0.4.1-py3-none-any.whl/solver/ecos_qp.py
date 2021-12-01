import numpy as np
from scipy import sparse
from scipy.linalg import sqrtm
import ecos
# Notes on speed https://quantsrus.github.io/post/state_of_convex_quadratic_programming_solvers/


def ecos_qp(H, f, A, b, Aeq, beq, ub, lb, x_keep, r_keep, req_keep):
    ''' 
    Refer to details in thesis: https://www.research-collection.ethz.ch/handle/20.500.11850/74559

    Need to convert to second order conic problem following template for matlab ecos:
    https://github.com/embotech/ecos-matlab/blob/master/bin/ecosqp.m
    See Linear Cone Program example on https://cvxopt.readthedocs.io/en/latest/coneprog.html for creation of G and h
    Other info:
    https://math.stackexchange.com/questions/1932532/converting-from-quadratic-to-second-order-cone-optimization-problem
    https://inst.eecs.berkeley.edu/~ee227a/fa10/login/l_conic_socp.html 
    
    so the states x are expanded with y states representing xHx anytime H[i]>0 so the translation involves:
    x = [x;y] 
    c = [f; 1]
    Aeq = [Aeq,zeros(x)]
    beq = beq
    U = sqrt(H)  ** easy if H is diagonal and all values are positive
    G = [[A , zeros(x)]             h = [[b;]
        [-eye(x); zeros(y)]             [-lb;]
        [eye(x); zeros(y)]              [ub;]
        [0, -1/sqrt(2)]                 [1/sqrt(2);]
        [-U; zeros(x)]                  [zeros(x);]
        [0; -1/sqrt(2)]                 [1/sqrt(2);]] (second order)
    '''
    x_scale, eq_scale, ineq_scale = scale_factors(H, f, A, b, Aeq, beq, ub, lb)
    x_l = sum(x_keep)# number of states
    s_num = [None for i in range(len(x_keep))]
    s_rev = []
    s=0
    for i in range(len(x_keep)):
        if x_keep[i]:
            s_num[i] = s
            s_rev.append(i)
            s+=1
    #create triplets for A and A_eq
    val_Aeq = []
    row_Aeq = []
    col_Aeq = []
    req=0
    for row in range(len(Aeq)):
        if req_keep[row]:
            for i in range(len(Aeq[row])):
                if Aeq[row][i]!=0 and not s_num[i] is None:
                    val_Aeq.append(Aeq[row][i]*x_scale[i]/eq_scale[row])
                    row_Aeq.append(req)
                    col_Aeq.append(s_num[i])
            req += 1
    

    val_G = []
    row_G = []
    col_G = []
    r=0
    for row in range(len(A)):
        if r_keep[row]:
            for i in range(len(A[row])):
                if A[row][i]!=0 and not s_num[i] is None:
                    val_G.append(A[row][i]*x_scale[i]/ineq_scale[row])
                    row_G.append(r)
                    col_G.append(s_num[i])
            r+= 1

    if not lb is None:
        r = upper_lower_bound(val_G,row_G,col_G,r,x_l)
    f = [f[i]*x_scale[i] for i in range(len(f))]
    c_scale = max([max(f),-min(f)])
    f = [ff/c_scale for ff in f]        
    if isinstance(H[0],list):
        H = [[H[i][j]*x_scale[j]**2/c_scale for j in range(len(H[i]))] for i in range(len(H))]
        cones = quadratic_cost_constraint(H,val_G,row_G,col_G,s_num,x_keep,r)
    else:
        H = [H[i]*x_scale[i]**2/c_scale for i in range(len(H))]    
        cones = diag_quadratic_cost_constraint_alt(H,val_G,row_G,col_G,s_num,x_keep,r)
    ineq_rows = r+sum([c+2 for c in cones])
    states = x_l + len(cones)
    G = sparse.csc_matrix((np.array(val_G),(np.array(row_G),np.array(col_G))), shape = (ineq_rows,states),dtype='float64')

    h = ineq(b,ub,lb,r_keep,x_keep,cones,x_scale,ineq_scale)

    dims = {}
    dims['l'] = r
    dims['q'] = [c+2 for c in cones]
    dims['e'] = 0

    c = [ff for i,ff in enumerate(f) if x_keep[i]]
    c.extend([1 for i in range(len(cones))])
    c = np.array(c)

    A_ecos = sparse.csc_matrix((np.array(val_Aeq),(np.array(row_Aeq),np.array(col_Aeq))), shape = (req,states),dtype='float64')
    b_ecos = np.array([beq[i]/eq_scale[i] for i in range(len(beq)) if req_keep[i]])
    
    solution = ecos.solve(c, G, h, dims, A_ecos, b_ecos, verbose=False)

    # Exit Flags:
    # 0: optimal
    # 1: primal infeasible
    # 2: dual infeasible
    # 10: close to optimal solution found
    # -1: maximum number of iterations reached
    # -2: numerical problems (unreliable search direction)
    # -3: numerical problems (slacks or multipliers became exterior)
    # -7: unknown problem in solver

    if solution['info']['exitFlag']==0 :
        feasible = 0    
    elif solution['info']['exitFlag'] == 10:
        feasible = 0
    else:
        feasible = solution['info']
        # feasible = solution['info']['exitFlag']
    #add removed states back in as zero
    x = [0 for i in range(len(x_keep))]
    for i in range(x_l):
        x[s_rev[i]] = float(solution['x'][i]*x_scale[s_rev[i]])
    return x, feasible


def quadratic_cost_constraint(H,val_G,row_G,col_G,s_num,x_keep,r):
    x_l = sum(x_keep)# number of states
    
    H_ar = np.array(H)
    U_ar = sqrtm(H_ar)
    U = [[float(U_ar[i,j]) for i in range(x_l)] for j in range(x_l)]
    
    val_G.append(-1/np.sqrt(2))
    row_G.append(r)
    col_G.append(x_l)

    #create a single cone for all of the quadratic terms
    cones = [0]
    for row in range(len(U)):
        if x_keep[row]:
            for i in range(len(U[row])):
                if x_keep[i] and U[row][i]!=0:         
                    #add the state constraint (2nd order part on LHS of inequality)
                    val_G.append(-U[row][i])
                    row_G.append(r+cones[0]+1)
                    col_G.append(s_num[i])
                if any([j!=0 for j in U[row]]):
                    cones[0] += 1

    val_G.append(1/np.sqrt(2))
    row_G.append(r + cones[0] + 1)
    col_G.append(x_l)
    return cones


def diag_quadratic_cost_constraint(H,val_G,row_G,col_G,s_num,x_keep,r):
    x_l = sum(x_keep)# number of states
    # add the first cone constraint     
    val_G.append(-1/np.sqrt(2))
    row_G.append(r)
    col_G.append(x_l)

    #create a single cone for all of the quadratic terms
    cones = [0]
    for i in range(len(x_keep)):
        if x_keep[i] and H[i]>0:          
            #add the state constraint (2nd order part on LHS of inequality)
            val_G.append(-float(np.sqrt(H[i])))
            row_G.append(r+cones[0]+1)
            col_G.append(s_num[i])
            cones[0] += 1

    val_G.append(1/np.sqrt(2))
    row_G.append(r + cones[0] + 1)
    col_G.append(x_l)
    
    return cones


def upper_lower_bound(val_G,row_G,col_G,r,x_l):
    #add upper and lower bounds
    val_G.extend([-1 for i in range(x_l)])
    row_G.extend([r+i for i in range(x_l)])
    col_G.extend([i for i in range(x_l)])
    val_G.extend([1 for i in range(x_l)])
    row_G.extend([r+x_l+i for i in range(x_l)])
    col_G.extend([i for i in range(x_l)])
    r += 2*x_l
    return r


def ineq(b,ub,lb,r_keep,x_keep,cones,x_scale,ineq_scale):
    h = [b[r]/ineq_scale[r] for r in range(len(b)) if r_keep[r]]
    if not lb is None:
        h.extend([-lb[j]/x_scale[j] for j in range(len(lb)) if x_keep[j]])
        h.extend([ub[j]/x_scale[j] for j in range(len(lb)) if x_keep[j]])
    for j in range(len(cones)):
        h.append(1/np.sqrt(2))
        h.extend([0 for j in range(cones[j])])
        h.append(1/np.sqrt(2))
       
    h = np.array(h)
    return h


def diag_quadratic_cost_constraint_alt(H,val_G,row_G,col_G,s_num,x_keep,r):
    '''
    Tried making smaller cones (faster?)
    '''
    states = sum(x_keep)# number of states
    cones = [1 for i in range(len(x_keep)) if x_keep[i] and H[i]>0]
    #create a new cone for each nonzero quadratic cost term
    for i in range(len(x_keep)):
        if x_keep[i] and H[i]>0:  
            val_G.append(-1/np.sqrt(2))
            row_G.append(r)
            col_G.append(states)

            #add the state constraint (2nd order part on LHS of inequality)
            val_G.append(-float(np.sqrt(H[i])))
            row_G.append(r + 1)
            col_G.append(s_num[i])

            val_G.append(1/np.sqrt(2))
            row_G.append(r + 2)
            col_G.append(states)

            states +=1
            r +=3
    return cones


def ecos_scaling(H, f, A, b, Aeq, beq, ub, lb):
    xl = len(f)
    if not ub is None:
        x_scale = [max([abs(ub[i]), abs(lb[i])]) for i in range(xl)]
        x_scale = [s if s!=0 else 1 for s in x_scale]
    else:
        x_scale = [1 for i in range(xl)]
    H2 = [H[i]*x_scale[i]**2 for i in range(xl)]
    f2 = [f[i]*x_scale[i] for i in range(xl)]
    ub2 = [ub[i]/x_scale[i] if ub[i]>0 else 1e-6 for i in range(xl)]
    lb2 = [lb[i]/x_scale[i] for i in range(xl)]
    A2 = [[row[i]*x_scale[i] for i in range(xl)] for row in A]
    Aeq2 = [[row[i]*x_scale[i] for i in range(xl)] for row in Aeq]
    b2 = [j for j in b]
    beq2 = [j for j in beq]
    for r,row in enumerate(A2):
        row_nz = [abs(j) for j in row if j!=0]
        if abs(b[r])>0:
            row_nz.append(abs(b[r]))
        r_scale = float(np.sqrt(min(row_nz)*max(row_nz)))
        if r_scale !=1:
            A2[r] = [j/r_scale for j in row]
            b2[r] = b2[r]/r_scale
    for r,row in enumerate(Aeq2):
        row_nz = [abs(j) for j in row if j!=0]
        if abs(beq[r])>0:
            row_nz.append(abs(beq[r]))
        r_scale = float(np.sqrt(min(row_nz)*max(row_nz)))
        if r_scale !=1:
            Aeq2[r] = [j/r_scale for j in row]
            beq2[r] = beq2[r]/r_scale
    return H2, f2, A2, b2, Aeq2, beq2, ub2, lb2, x_scale


def scale_factors(H, f, A, b, Aeq, beq, ub, lb):
    xl = len(f)
    if not ub is None:
        x_scale = [max([abs(ub[i]), abs(lb[i])]) for i in range(xl)]
        x_scale = [s if s!=0 else 1 for s in x_scale]
    else:
        x_scale = [1 for i in range(xl)]
    eq_scale = [1 for j in beq]
    ineq_scale = [1 for j in b]
    for r,row in enumerate(A):
        row_nz = [abs(j*x_scale[i]) for i,j in enumerate(row) if j!=0]
        if abs(b[r])>0:
            row_nz.append(abs(b[r]))
        ineq_scale[r] = float(np.sqrt(min(row_nz)*max(row_nz)))
    for r,row in enumerate(Aeq):
        row_nz = [abs(j*x_scale[i]) for i,j in enumerate(row) if j!=0]
        if abs(beq[r])>0:
            row_nz.append(abs(beq[r]))
        eq_scale[r] = float(np.sqrt(min(row_nz)*max(row_nz)))
    return x_scale, eq_scale, ineq_scale
