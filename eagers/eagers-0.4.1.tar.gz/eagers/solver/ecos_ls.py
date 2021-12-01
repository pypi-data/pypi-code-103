import warnings

import numpy as np
from scipy import sparse
from scipy.linalg import sqrtm
import ecos


def ecos_ls(H, f, A, b, Aeq, beq):
    ''' 
    Need to convert to second order conic problem following template for matlab ecos:
    https://github.com/embotech/ecos-matlab/blob/master/bin/ecosqp.m
    See Linear Cone Program example on https://cvxopt.readthedocs.io/en/latest/coneprog.html for creation of G and h
    Other info:
    https://math.stackexchange.com/questions/1932532/converting-from-quadratic-to-second-order-cone-optimization-problem
    https://inst.eecs.berkeley.edu/~ee227a/fa10/login/l_conic_socp.html 
    
    so the states x are expanded with y states representing xHx anytime H[i]>0 so the translation involves:
    x = [x;y] 
    c = [zeros(x); 1]
    Aeq = [Aeq,zeros(x)]
    beq = beq
    U = sqrt(H)  ** easy if H is positive semi-definite
    G = [[A , zeros(x)]             h = [[b;]
        [f'/sqrt(2), -1/sqrt(2)]        [1/sqrt(2);]
        [-U; zeros(x)]                  [zeros(x);]
        [f'/sqrt(2); -1/sqrt(2)]        [1/sqrt(2);]] (second order)
    '''
    x_l = len(f)
    #create triplets for A and A_eq
    val_Aeq = []
    row_Aeq = []
    col_Aeq = []
    req=0
    for row in range(len(Aeq)):
        for i in range(len(Aeq[row])):
            if Aeq[row][i]!=0:
                val_Aeq.append(Aeq[row][i])
                row_Aeq.append(req)
                col_Aeq.append(i)
        req += 1
    

    val_G = []
    row_G = []
    col_G = []
    r=0
    for row in range(len(A)):
        for i in range(len(A[row])):
            if A[row][i]!=0:
                val_G.append(A[row][i])
                row_G.append(r)
                col_G.append(i)
        r+= 1

    # add the first cone constraint 
    for i in range(x_l):
        val_G.append(f[i]/np.sqrt(2))
        row_G.append(r)
        col_G.append(i)
    
    val_G.append(-1/np.sqrt(2))
    row_G.append(r)
    col_G.append(x_l)

    cones = 0
    H_ar = np.array(H)
    U_ar = sqrtm(H_ar)
    with warnings.catch_warnings():
        # Filter out ComplexWarnings.  There might be some miniscule
        # imaginary part from numerical error while taking the square
        # root of a matrix.
        warnings.filterwarnings("ignore", category=np.ComplexWarning)
        U = [[float(U_ar[i,j]) for i in range(x_l)] for j in range(x_l)]
    for row in range(len(U)):
        for i in range(len(U[row])):
            if U[row][i]!=0:         
                #add the state constraint (2nd order part on LHS of inequality)
                val_G.append(-U[row][i])
                row_G.append(r+cones+1)
                col_G.append(i)
        cones += 1

    # add the other cone constraint
    for i in range(x_l):
        val_G.append(-f[i]/np.sqrt(2))
        row_G.append(r + cones + 1)
        col_G.append(i)

    val_G.append(1/np.sqrt(2))
    row_G.append(r + cones + 1)
    col_G.append(x_l)

    G = sparse.csc_matrix((np.array(val_G),(np.array(row_G),np.array(col_G))), shape = (r+cones+2,x_l+1),dtype='float64')

    h = [b[j] for j in range(len(b))]
    h.append(1/np.sqrt(2))
    h.extend([0 for j in range(cones)])
    h.append(1/np.sqrt(2))
    h = np.array(h)

    dims = {}
    dims['l'] = r 
    dims['q'] = [cones+2]
    dims['e'] = 0

    c = [float(0) for j in range(x_l)]
    c.append(1)
    c = np.array(c)

    A_ecos = sparse.csc_matrix((np.array(val_Aeq),(np.array(row_Aeq),np.array(col_Aeq))), shape = (req,x_l+1),dtype='float64')
    b_ecos = np.array([beq[i] for i in range(len(beq))])
    
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

    if solution['info']['exitFlag']==0 or solution['info']['exitFlag'] == 10:
        feasible = 0
    else:
        feasible = solution['info']['exitFlag']
    #add removed states back in as zero
    x = [0 for i in range(x_l)]
    for i in range(x_l):
        x[i] = float(solution['x'][i])
    return x, feasible
