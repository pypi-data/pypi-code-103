import numpy as np


class ErrorOptions():
    COHERR = 0
    REGERR = 1
    S2 = 2
    VAR2S = 3
    AVGNNZ = 4
    RECOV = 5
    ALLITERS = 6


class PostOptions():
    WORSTREP = 0
    ATOMUSAGE = 1
    FINALLS = 2
    IPR = 3


def recovered_atoms(D_recovered, D_original, tol=0.99):
    """Total number of recovered atoms"""
    n_recovered = 0
    n_atoms = D_recovered.shape[0]

    """Take care of alternating sign scenarios"""
    D_original = np.sign(D_original[0, :]) * D_original
    D_recovered = np.sign(D_recovered[0, :]) * D_recovered

    """Calculate the correlation matrix"""
    P = D_recovered.T @ D_original

    for i in range(n_atoms):
        pos = np.argmax(np.abs(P[0, :]))
        bestfit = P[0, pos]

        if bestfit > tol:
            n_recovered += 1
            P = np.delete(P, pos, axis=1)
        P = np.delete(P, 0, axis=1)
    return n_recovered


def ipr(Y, D, X, mutual_coh, n_it):
    """
    Iterative projections and rotations,
    Algorithm 4.3 (Barchiesi & Plumbley 2013)
    To be run after each iteration of a DL algorithm (which updates D and X)
    Input:
        Y            - signal matrix
        D            - current dictionary
        X            - current representation matrix
        mutual_coh   - desired mutual coherence
        n_it         - number of iterations (for projections and rotations)
    Output:
        D            - updated dictionary
    """
    m, n = D.shape

    for it in range(n_it):
        # project Gram matrix on bounded coherences set
        G = D.T @ D
        pos = np.where(np.abs(G) > mutual_coh)
        G[pos] = np.sign(G[pos]) * mutual_coh
        np.fill_diagonal(G, 1)

        # spectral projection
        s, V = np.linalg.eig(G)
        s[np.where(s < 0)] = 0
        D = np.diag(np.sqrt(s[:m])) @ V[:, :m].T

        # rotation on the data set
        U, _, V = np.linalg.svd(D @ X @ Y.T, full_matrices=False)
        D = np.linalg.multi_dot([V.T, U.T, D])
        D = D / np.linalg.norm(D, axis=0)


def dictionary_extra(Y, D, X, params, iter_num):
    #    Q = np.identity(Y.shape[0]) # TODO who is shared ?
    #    Q2s = np.identity(Y.shape[0])
    #    Dtrue = np.zeros(D.shape)
    #
    #    mutual_coh_ipr = 0.2
    #    nit_ipr = 5
    #
    #    """Calculate RMSE"""
    #    rmse = np.linalg.norm(Y - D * X, 'fro') / np.sqrt(Y.size)
    #
    #    """Handle DL Extra"""
    #    if options.post == ErrorOptions.WORSTREP:
    #        E = Y - D*X
    #        r = np.sqrt(np.sum(E*E, axis=0)) # TODO maybe other name ?
    #        ndx = np.where(np.sum(r, axis=1) == 0)
    #        n_zero = np.sum(ndx)
    #        if n_zero > 0:
    #            ndx_sort = np.argsort(r)[::-1]
    #            D_new = Y[:, ndx_sort[:n_zero+1]]
    #            D_new = D_new / np.linalg.norm(D_new, axis=0)
    #            D[:, ndx] = D_new
    #    elif options.post == ErrorOptions.ATOMUSAGE:
    #        # TODO what are going to do with the animations?
    #        print('animation')
    #    elif options.post == ErrorOptions.FINALLS:
    #        if iter == iter_num:
    #            X = ompreg(Y, D, X, 0)

    if params['ipr_flag']:
        D = ipr(Y, D, X, params['mutual_coh_ipr'], params['n_it_ipr'])

    error_extra = 0
#    if params['reg_flag']:
#        error_extra = (np.linalg.norm(Y - D @ X, 'fro')**2 +
#                       params['regmu'] * np.linalg.norm(X, 'fro')**2)
    return error_extra

    #    """Handle DL Error"""
    #    if options.error == ErrorOptions.COHERR:
    #        error_extra = (np.linalg.norm(Y - D * X, 'fro')**2 +
    #                       coh * np.linalg.norm(D.T @ D -
    #                       np.identity(D.shape[2]), 'fro')**2)
    #    elif options.error == ErrorOptions.REGERR:
    #        reg = reg * vanish
    #        error_extra = (np.linalg.norm(Y - D * X, 'fro')**2 +
    #                       reg * np.linalg.norm(X, 'fro')**2)
    #    elif options.error == ErrorOptions.S2:
    #        rmse = np.linalg.norm(Y - Q2s*D*X, 'fro') / np.sqrt(Y.size)
    #        error_extra = 0
    #        return rmse, error_extra
    #    elif options.error == ErrorOptions.VAR2S:
    #        rmse = np.linalg.norm(Y - Q*D*X, 'fro') / np.sqrt(Y.size)
    #        error_extra = 0
    #    elif options.error == ErrorOptions.AVGNNZ:
    #        error_extra = np.mean((X != 0).sum(axis=0))
    #    elif options.error == ErrorOptions.RECOV:
    #        error_extra = recovered_atoms(D, Dtrue)
    #    elif options.error == ErrorOptions.ALLITERS:
    #        error_extra = D;
    #    else:
    #        error_extra = 0
    #
    #    return rmse, error_extra
