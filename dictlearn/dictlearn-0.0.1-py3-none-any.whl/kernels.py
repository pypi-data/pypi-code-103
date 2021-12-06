from sklearn.metrics.pairwise import rbf_kernel


def dl_rbf_kernel(X, Y, params):
    return rbf_kernel(X.T, Y.T, params['gamma'])


def dl_poly_kernel(X, Y, params):
    return (params['gamma'] * X.T @ Y + params['coef0']) ^ params['degree']
