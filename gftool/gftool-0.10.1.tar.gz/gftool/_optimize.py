"""Try to vectorize root."""
from warnings import warn

import numpy as np

from scipy.optimize.optimize import _check_unknown_options
from scipy.optimize import nonlin, OptimizeResult


def _warn_jac_unused(jac, method):
    if jac is not None:
        warn(f'Method {method} does not use the jacobian (jac).',
             RuntimeWarning)


def root(fun, x0, args=(), method='hybr', jac=None, tol=None, callback=None,
         options=None):
    """Find a root of a vector function.

    Parameters
    ----------
    fun : callable
        A vector function to find a root of.
    x0 : ndarray
        Initial guess.
    args : tuple, optional
        Extra arguments passed to the objective function and its Jacobian.
    method : str, optional
        Type of solver. Should be one of

            - 'hybr'             :ref:`(see here) <optimize.root-hybr>`
            - 'lm'               :ref:`(see here) <optimize.root-lm>`
            - 'broyden1'         :ref:`(see here) <optimize.root-broyden1>`
            - 'broyden2'         :ref:`(see here) <optimize.root-broyden2>`
            - 'anderson'         :ref:`(see here) <optimize.root-anderson>`
            - 'linearmixing'     :ref:`(see here) <optimize.root-linearmixing>`
            - 'diagbroyden'      :ref:`(see here) <optimize.root-diagbroyden>`
            - 'excitingmixing'   :ref:`(see here) <optimize.root-excitingmixing>`
            - 'krylov'           :ref:`(see here) <optimize.root-krylov>`
            - 'df-sane'          :ref:`(see here) <optimize.root-dfsane>`

    jac : bool or callable, optional
        If `jac` is a Boolean and is True, `fun` is assumed to return the
        value of Jacobian along with the objective function. If False, the
        Jacobian will be estimated numerically.
        `jac` can also be a callable returning the Jacobian of `fun`. In
        this case, it must accept the same arguments as `fun`.
    tol : float, optional
        Tolerance for termination. For detailed control, use solver-specific
        options.
    callback : function, optional
        Optional callback function. It is called on every iteration as
        ``callback(x, f)`` where `x` is the current solution and `f`
        the corresponding residual. For all methods but 'hybr' and 'lm'.
    options : dict, optional
        A dictionary of solver options. E.g., `xtol` or `maxiter`, see
        :obj:`show_options()` for details.

    Returns
    -------
    sol : OptimizeResult
        The solution represented as a ``OptimizeResult`` object.
        Important attributes are: ``x`` the solution array, ``success`` a
        Boolean flag indicating if the algorithm exited successfully and
        ``message`` which describes the cause of the termination. See
        `OptimizeResult` for a description of other attributes.

    See Also
    --------
    show_options : Additional options accepted by the solvers

    Notes
    -----
    This section describes the available solvers that can be selected by the
    'method' parameter. The default method is *hybr*.

    Method *hybr* uses a modification of the Powell hybrid method as
    implemented in MINPACK [1]_.

    Method *lm* solves the system of nonlinear equations in a least squares
    sense using a modification of the Levenberg-Marquardt algorithm as
    implemented in MINPACK [1]_.

    Method *df-sane* is a derivative-free spectral method. [3]_

    Methods *broyden1*, *broyden2*, *anderson*, *linearmixing*,
    *diagbroyden*, *excitingmixing*, *krylov* are inexact Newton methods,
    with backtracking or full line searches [2]_. Each method corresponds
    to a particular Jacobian approximations. See `nonlin` for details.

    - Method *broyden1* uses Broyden's first Jacobian approximation, it is
      known as Broyden's good method.
    - Method *broyden2* uses Broyden's second Jacobian approximation, it
      is known as Broyden's bad method.
    - Method *anderson* uses (extended) Anderson mixing.
    - Method *Krylov* uses Krylov approximation for inverse Jacobian. It
      is suitable for large-scale problem.
    - Method *diagbroyden* uses diagonal Broyden Jacobian approximation.
    - Method *linearmixing* uses a scalar Jacobian approximation.
    - Method *excitingmixing* uses a tuned diagonal Jacobian
      approximation.

    .. warning::

        The algorithms implemented for methods *diagbroyden*,
        *linearmixing* and *excitingmixing* may be useful for specific
        problems, but whether they will work may depend strongly on the
        problem.

    .. versionadded:: 0.11.0

    References
    ----------
    .. [1] More, Jorge J., Burton S. Garbow, and Kenneth E. Hillstrom.
       1980. User Guide for MINPACK-1.
    .. [2] C. T. Kelley. 1995. Iterative Methods for Linear and Nonlinear
       Equations. Society for Industrial and Applied Mathematics.
       <https://archive.siam.org/books/kelley/fr16/>
    .. [3] W. La Cruz, J.M. Martinez, M. Raydan. Math. Comp. 75, 1429 (2006).

    Examples
    --------
    The following functions define a system of nonlinear equations and its
    jacobian.

    >>> def fun(x):
    ...     return [x[0]  + 0.5 * (x[0] - x[1])**3 - 1.0,
    ...             0.5 * (x[1] - x[0])**3 + x[1]]

    >>> def jac(x):
    ...     return np.array([[1 + 1.5 * (x[0] - x[1])**2,
    ...                       -1.5 * (x[0] - x[1])**2],
    ...                      [-1.5 * (x[1] - x[0])**2,
    ...                       1 + 1.5 * (x[1] - x[0])**2]])

    A solution can be obtained as follows.

    >>> from scipy import optimize
    >>> sol = optimize.root(fun, [0, 0], jac=jac, method='hybr')
    >>> sol.x
    array([ 0.8411639,  0.1588361])

    """
    if not isinstance(args, tuple):
        args = (args,)

    meth = method.lower()
    if options is None:
        options = {}

    if callback is not None and meth in ('hybr', 'lm'):
        warn('Method %s does not accept callback.' % method,
             RuntimeWarning)

    # set default tolerances
    if tol is not None:
        options = dict(options)
        if meth in ('hybr', 'lm'):
            options.setdefault('xtol', tol)
        elif meth in ('df-sane',):
            options.setdefault('ftol', tol)
        elif meth in ('broyden1', 'broyden2', 'anderson', 'linearmixing',
                      'diagbroyden', 'excitingmixing', 'krylov'):
            options.setdefault('xtol', tol)
            options.setdefault('xatol', np.inf)
            options.setdefault('ftol', np.inf)
            options.setdefault('fatol', np.inf)

    if meth == 'hybr':
        raise NotImplementedError
    elif meth == 'lm':
        raise NotImplementedError
    elif meth == 'df-sane':
        raise NotImplementedError
    elif meth in ('broyden1', 'broyden2', 'anderson', 'linearmixing',
                  'diagbroyden', 'excitingmixing', 'krylov'):
        _warn_jac_unused(jac, method)
        sol = _root_nonlin_solve(fun, x0, args=args, jac=jac,
                                 _method=meth, _callback=callback,
                                 **options)
    else:
        raise ValueError('Unknown solver %s' % method)

    return sol


def _root_nonlin_solve(fun, x0, args=(), jac=None,
                       _callback=None, _method=None,
                       nit=None, disp=False, maxiter=None,
                       ftol=None, fatol=None, xtol=None, xatol=None,
                       tol_norm=None, line_search='armijo', jac_options=None,
                       **unknown_options):
    _check_unknown_options(unknown_options)

    f_tol = fatol
    f_rtol = ftol
    x_tol = xatol
    x_rtol = xtol
    verbose = disp
    if jac_options is None:
        jac_options = dict()

    jacobian = {'broyden1': nonlin.BroydenFirst,
                'broyden2': nonlin.BroydenSecond,
                'anderson': nonlin.Anderson,
                'linearmixing': nonlin.LinearMixing,
                'diagbroyden': nonlin.DiagBroyden,
                'excitingmixing': nonlin.ExcitingMixing,
                'krylov': nonlin.KrylovJacobian
                }[_method]

    if args:
        if jac:
            def f(x):
                return fun(x, *args)[0]
        else:
            def f(x):
                return fun(x, *args)
    else:
        f = fun

    x, info = nonlin.nonlin_solve(f, x0, jacobian=jacobian(**jac_options),
                                  iter=nit, verbose=verbose,
                                  maxiter=maxiter, f_tol=f_tol,
                                  f_rtol=f_rtol, x_tol=x_tol,
                                  x_rtol=x_rtol, tol_norm=tol_norm,
                                  line_search=line_search,
                                  callback=_callback, full_output=True,
                                  raise_exception=False)
    sol = OptimizeResult(x=x)
    sol.update(info)
    return sol
