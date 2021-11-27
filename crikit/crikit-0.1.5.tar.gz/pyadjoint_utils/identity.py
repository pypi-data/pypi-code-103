class JacobianIdentity:
    pass


def make_jacobian_identities(n):
    jac = [None] * n
    for i in range(n):
        jac[i] = [None] * n
        jac[i][i] = JacobianIdentity()
    return jac
