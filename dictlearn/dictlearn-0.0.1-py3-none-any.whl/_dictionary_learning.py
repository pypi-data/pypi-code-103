import numpy as np

from .methods import _odl
from .methods import _mod
from .methods import _sgk
from .methods import _nsgk
from .methods import _ksvd
from .methods import _aksvd
from .methods import _uaksvd
from .kernels import dl_rbf_kernel
from .methods._atom import ReplAtoms

from sklearn.preprocessing import normalize
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_is_fitted


def _safe_params_init(params, fit_algorithm):
    if 'threshold_svd' not in params:
        params['threshold_svd'] = 1e-8

    if 'atom_norm_tolerance' not in params:
        params['atom_norm_tolerance'] = 1e-10

    if 'reg_flag' not in params:
        params['reg_flag'] = False

    if 'replatoms' not in params:
        params['replatoms'] = ReplAtoms.RANDOM

    if 'n_patoms' not in params:
        params['n_patoms'] = None

    if 'gamma' not in params:
        params['gamma'] = 6

    if 'mutual_coh_ipr' not in params:
        params['mutual_coh_ipr'] = 0.2

    if 'n_it_ipr' not in params:
        params['n_it_ipr'] = 5

    if 'sigma' not in params:
        params['sigma'] = 1

    if 'ff' not in params:
        params['ff'] = 0.99

    if fit_algorithm.endswith('reg'):
        params['reg_flag'] = True

        if 'regmu' not in params:
            params['regmu'] = 0.01
        if 'regvanish' not in params:
            params['regvanish'] = 0.95
        if 'regstop' not in params:
            params['regstop'] = np.Inf

    return params


def _params_update(params, fit_algorithm, iter):
    if fit_algorithm.endswith('reg'):
        if params['regstop'] > iter:
            params['regmu'] *= params['regvanish']
        else:
            params['regmu'] = 0

    return params


def _get_fit_handle(fit_algorithm):
    if callable(fit_algorithm):
        # fit_algorithm is already a function
        return fit_algorithm
    elif type(fit_algorithm) == str:
        if fit_algorithm in ['uaksvd', 'uaksvd_reg', 'uaksvd_coh',
                             'puaksvd', 'puaksvd_reg', 'puaksvd_coh',
                             'ker_uaksvd', 'ker_uaksvd_reg', 'ker_uaksvd_coh',
                             'ker_puaksvd', 'ker_puaksvd_reg', 'ker_puaksvd_coh']:
            return getattr(_uaksvd, fit_algorithm)
        if fit_algorithm in ['aksvd', 'aksvd_reg', 'aksvd_coh',
                             'paksvd', 'paksvd_reg', 'paksvd_coh',
                             'ker_aksvd', 'ker_aksvd_reg', 'ker_aksvd_coh',
                             'ker_paksvd', 'ker_paksvd_reg', 'ker_paksvd_coh']:
            return getattr(_aksvd, fit_algorithm)
        if fit_algorithm in ['ksvd', 'ksvd_reg', 'ksvd_coh',
                             'pksvd', 'pksvd_reg', 'pksvd_coh',
                             'ker_ksvd', 'ker_ksvd_reg', 'ker_ksvd_coh',
                             'ker_pksvd', 'ker_pksvd_reg', 'ker_pksvd_coh']:
            return getattr(_ksvd, fit_algorithm)
        if fit_algorithm in ['nsgk', 'nsgk_reg', 'nsgk_coh',
                             'pnsgk', 'pnsgk_reg', 'pnsgk_coh',
                             'ker_nsgk', 'ker_nsgk_reg', 'ker_nsgk_coh',
                             'ker_pnsgk', 'ker_pnsgk_reg', 'ker_pnsgk_coh']:
            return getattr(_nsgk, fit_algorithm)
        if fit_algorithm in ['sgk', 'sgk_reg', 'sgk_coh',
                             'psgk', 'psgk_reg', 'psgk_coh',
                             'ker_sgk', 'ker_sgk_reg', 'ker_sgk_coh',
                             'ker_psgk', 'ker_psgk_reg', 'ker_psgk_coh']:
            return getattr(_sgk, fit_algorithm)
        if fit_algorithm in ['mod', 'mod_reg', 'ker_mod']:
            return getattr(_mod, fit_algorithm)
        if fit_algorithm in ['ocddl', 'rlsdl']:
            return getattr(_odl, fit_algorithm)
        else:
            raise ValueError(
                "Unknown transform_algorithm"
            )
    else:
        raise ValueError(
            "transform_algorithm must be a string or a function"
        )


def _sparse_encode(
    Y,
    D,
    algorithm="omp",
    n_nonzero_coefs=None,
    verbose=0,
):
    """Generic sparse coding.

    Each column of the result is the solution to a OMP problem.

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    algorithm : {omp'}, default='omp'
        The algorithm for computing the sparse representations:

        * `'omp'`: Orthogonal Matching Pursuit;

    n_nonzero_coefs : int, default=None
        Desired number of non-zero entries in the solution.
        If None (by default) this value is set to 10% of n_features.

    verbose : int, default=0
        Controls the verbosity; the higher, the more messages.

    Returns
    -------
    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    err : float
          The approximation error
    """
    if Y.ndim == 1:
        Y = Y[:, np.newaxis]
    n_samples, n_features = Y.shape
    if D.shape[0] != Y.shape[0]:
        raise ValueError(
            "Dictionary D and signals Y have different numbers of features:"
            "D.shape: {} Y.shape: {}".format(D.shape, Y.shape)
        )

    if callable(algorithm):
        # algorithm is already a handle function
        X, err = algorithm(Y, D, n_nonzero_coefs)
        return X, err

    if algorithm == "omp":
        omp = OrthogonalMatchingPursuit(n_nonzero_coefs=n_nonzero_coefs)
        X = omp.fit(D, Y).coef_.T
        err = (np.linalg.norm(Y - D @ X, 'fro') /
               np.sqrt(Y.size))
        return X, err
    else:
        raise ValueError(
            'Sparse coding method must be "omp", got %s.' % algorithm
        )


def sparse_encode(
    Y,
    D,
    algorithm="omp",
    n_nonzero_coefs=None,
    verbose=0
):
    """Sparse coding

    Each column of the result is the solution to a sparse coding problem.
    The goal is to find a sparse array `code` such that::

        Y ~= D * X

    Parameters
    ----------
    Y : ndarray of shape (n_samples, n_features)
        Data matrix.

    D : ndarray of shape (n_components, n_features)
        Initial dictionary, with normalized columns.

    algorithm : {'omp'}, default='omp'
        The algorithm for computing sparse representations:

        * `'omp'`: Orthogonal Matching Pursuit;

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    verbose : int, default=0
        Controls the verbosity; the higher, the more messages.

    Returns
    -------
    X : ndarray of shape (n_samples, n_components)
        The sparse representations matrix

    err : float
      The approximation error
    """

    n_samples, n_features = Y.shape
    n_components = D.shape[0]

    if algorithm in ("omp"):
        if n_nonzero_coefs is None:
            n_nonzero_coefs = min(max(n_features / 10, 1), n_components)

    X, error = _sparse_encode(
        Y,
        D,
        n_nonzero_coefs=n_nonzero_coefs,
        verbose=verbose,
    )
    return X, error


def dictionary_learning(
    Y,
    D,
    max_iter,
    fit_algorithm,
    transform_algorithm,
    n_nonzero_coefs,
    params
):
    """Standard Dictionary Learning

    Parameters
    ----------
    Y : ndarray of shape (n_features, n_samples)
        Data matrix.

    D : ndarray of shape (n_features, n_components)
        Initial dictionary, with normalized columns.

    max_iter : int, default=100
        Maximum number of iterations to perform.

    fit_algorithm : handle function
        Fit algorithm function.

    transform_algorithm : handle function
        Transform algorithm function.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. This is only used by `algorithm='omp'`.
        If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    params : dict
        Dictionary with provided parameters for the DL problem.

    Returns
    -------
    D : ndarray of shape (n_features, n_components).
        The learned dictionary

    X : ndarray of shape (n_components, n_samples)
        The sparse codes.

    rmse : float
        The approximation error for each iteration.

    error_extra : float
      The extra error for each iteration.
    """

    rmse = np.zeros(max_iter)
    error_extra = np.zeros(max_iter)

    # Safe initialization of params
    _safe_params_init(params, fit_algorithm.__name__)

    for iter in range(max_iter):
        # Update coefs
        X, _ = sparse_encode(
            Y,
            D,
            transform_algorithm,
            n_nonzero_coefs
        )

        # Update dictionary
        D, X = fit_algorithm(Y, D, X, params)

        # Compute error
        rmse[iter] = (np.linalg.norm(Y - D @ X, 'fro') /
                      np.sqrt(Y.size))

        # Compute extra error
        # error_extra[iter] = dictionary_extra(Y, D, X, params, iter)

        # Update DL params
        _params_update(params, fit_algorithm.__name__, iter)

    return D, X, rmse, error_extra


def kernel_dictionary_learning(
    Y,
    A,
    max_iter,
    fit_algorithm,
    transform_algorithm,
    n_nonzero_coefs,
    kernel_function,
    params
):
    """Kernel Dictionary Learning

    Parameters
    ----------
    Y : ndarray of shape (n_samples, n_features)
        Data matrix.

    D : ndarray of shape (n_components, n_features)
        Initial dictionary, with normalized columns.

    max_iter : int, default=100
        Maximum number of iterations to perform.

    fit_algorithm : handle function
        Fit algorithm function.

    transform_algorithm : handle function
        Transform algorithm function.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. This is only used by `algorithm='omp'`.
        If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    kernel_function : handle function
        Computes a kernel matrix.

    params : dict
        Dictionary with provided parameters for the DL problem.

    Returns
    -------
    A : ndarray of shape (n_components, n_features).
        The learned dictionary

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    rmse : float
        The approximation error for each iteration.

    error_extra : float
        The extra error for each iteration.
    """

    rmse = np.zeros(max_iter)
    error_extra = np.zeros(max_iter)

    # Safe initialization of params
    _safe_params_init(params, fit_algorithm.__name__)

    # Initialize kernel matrix
    K = kernel_function(Y, Y, params)

    # Initialize coding coefs
    X, _ = sparse_encode(
        A.T @ K,
        A.T @ K @ A,
        transform_algorithm,
        n_nonzero_coefs
    )

    for iter in range(max_iter):
        # Update dictionary
        A, X = fit_algorithm(K, A, X, params)

        # Update coefs
        X, rmse[iter] = sparse_encode(
            A.T @ K,
            A.T @ K @ A,
            transform_algorithm,
            n_nonzero_coefs
        )

        # Compute extra error
        # error_extra[iter] = dictionary_extra(Y, A, X, params, iter)

        # Update DL params
        _params_update(params, fit_algorithm.__name__, iter)

    return A, X, rmse, error_extra


def online_dictionary_learning(
    Y,
    D,
    max_iter,
    fit_algorithm,
    transform_algorithm,
    n_nonzero_coefs,
    params
):
    """Online Dictionary Learning

    Parameters
    ----------
    Y : ndarray of shape (n_samples, n_features)
        Data matrix.

    D : ndarray of shape (n_components, n_features)
        Initial dictionary, with normalized columns.

    max_iter : int, default=100
        Maximum number of iterations to perform.

    fit_algorithm : handle function
        Fit algorithm function.

    transform_algorithm : handle function
        Transform algorithm function.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. This is only used by `algorithm='omp'`.
        If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    params : dict
        Dictionary with provided parameters for the DL problem.

    Returns
    -------
    D : ndarray of shape (n_components, n_features).
        The learned dictionary

    X : ndarray of shape (n_components, n_features)
        The sparse codes.

    rmse : float
        The approximation error for each iteration.

    error_extra : float
      The extra error for each iteration.
    """

    rmse = np.zeros(max_iter)
    error_extra = np.zeros(max_iter)

    # Safe initialization of params
    _safe_params_init(params, fit_algorithm.__name__)

    # Initialize learning method attributes
    fit_algorithm.A = np.eye(D.shape[1])
    fit_algorithm.B = D

    for iter in range(max_iter):
        # Shuffle data
        rp = np.random.permutation(Y.shape[1])
        Y = Y[:, rp]

        # Initialize coding coefs
        X, _ = sparse_encode(
            Y,
            D,
            transform_algorithm,
            n_nonzero_coefs
        )

        for y_index in range(Y.shape[1]):
            # Update dictionary
            D, X[:, y_index] = fit_algorithm(
                Y[:, y_index],
                D,
                X[:, y_index],
                params
            )

            # Update coefs
            X, rmse[iter] = sparse_encode(
                Y,
                D,
                transform_algorithm,
                n_nonzero_coefs
            )

            # Compute extra error
            # error_extra[iter] = dictionary_extra(Y, D, X, params, iter)

            # Update DL params
            _params_update(params, fit_algorithm.__name__, iter)

    return D, X, rmse, error_extra


class _BaseSparseCoding(TransformerMixin):
    """Base class from SparseCoder and DictionaryLearning algorithms."""

    def __init__(
        self,
        transform_algorithm,
        n_nonzero_coefs,
    ):
        self.transform_algorithm = transform_algorithm
        self.n_nonzero_coefs = n_nonzero_coefs

    def _transform(self, Y, D):
        """Private method allowing to accomodate both DictionaryLearning and
        SparseCoder."""
        Y = self._validate_data(Y, reset=False)

        X, err = sparse_encode(
            Y,
            D,
            self.transform_algorithm,
            self.n_nonzero_coefs
        )
        return X, err

    def transform(self, Y):
        """Encode the data as a sparse combination of the dictionary atoms.
        Coding method is determined by the object parameter
        `transform_algorithm`.

        Parameters
        ----------
        Y : ndarray of shape (n_samples, n_features)
            Test data to be transformed, must have the same number of
            features as the data used to train the model.

        Returns
        -------
        Y_new : ndarray of shape (n_samples, n_components)
            Transformed data.
        """
        check_is_fitted(self)
        return self._transform(Y, self.components_)


class DictionaryLearning(_BaseSparseCoding, BaseEstimator):
    """Dictionary learning

    Parameters
    ----------
    n_components : int, default=n_features
        Number of dictionary columns (atoms).

    max_iter : int, default=100
        Maximum number of iterations.

    fit_algorithm : string, default='aksvd'
        Algorithm for dictionary optimization:

        * Standard DL: `'ksvd'`, `'aksvd'`, `'uaksvd'`, `'sgk'`, `'nsgk'`, `'mod'`
        * Regularized DL: `'ksvd_reg'`, `'aksvd_reg'`, `'uaksvd_reg'`, `'sgk_reg'`, `'nsgk_reg'`, `'mod_reg'`
        * Incoherent DL: `'ksvd_coh'`, `'aksvd_coh'`, `'uaksvd_coh'`, `'sgk_coh'`, `'nsgk_coh'`
        * Parallel Standard DL: `'pksvd'`, `'paksvd'`, `'puaksvd'`, `'psgk'`, `'pnsgk'`
        * Parallel Regularized DL: `'pksvd_reg'`, `'paksvd_reg'`, `'puaksvd_reg'`, `'psgk_reg'`, `'pnsgk_reg'`
        * Incoherent DL: `'pksvd_coh'`, `'paksvd_coh'`, `'puaksvd_coh'`, `'psgk_coh'`, `'pnsgk_coh'`
        * Kernel DL: `'ker_ksvd'`, `'ker_aksvd'`, `'ker_uaksvd'`, `'ker_sgk'`, `'ker_nsgk'`, `'ker_mod'`
        * Regularized Kernel DL: `'ker_ksvd_reg'`, `'ker_aksvd_reg'`, `'ker_uaksvd_reg'`, `'ker_sgk_reg'`, `'ker_nsgk_reg'`
        * Incoherent Kernel DL: `'ker_ksvd_coh'`, `'ker_aksvd_coh'`, `'ker_uaksvd_coh'`, `'ker_sgk_coh'`, `'ker_nsgk_coh'`
        * Parallel Kernel DL: `'ker_pksvd'`, `'ker_paksvd'`, `'ker_puaksvd'`, `'ker_psgk'`, `'ker_pnsgk'`
        * Parallel Regularized Kernel DL: `'ker_pksvd_reg'`, `'ker_paksvd_reg'`, `'ker_puaksvd_reg'`, `'ker_psgk_reg'`, `'ker_pnsgk_reg'`
        * Parallel Incoherent Kernel DL: `'ker_pksvd_coh'`, `'ker_paksvd_coh'`, `'ker_puaksvd_coh'`, `'ker_psgk_coh'`, `'ker_pnsgk_coh'`
        * Custom algorithm: If you want to propose a personal method of updating atoms you can use a handle function. For linear cases the handle \
                     function should respect the template ``custom_fit_algorithm(Y, D, X, params)`` and  \
                     ``ker_custom_fit_algorithm(K, A, X, params)`` for the nonlinear cases.

    transform_algorithm : {'omp'}, default='omp'
        Algorithm used for computing the sparse representations:

        * `'omp'`: Orthogonal Matching Pursuit.
        * custom algorithm: If you want to propose a personal method for computing the sparse representation you can use a handle function \
                         respecting the template ``custom_transform_algorithm(Y, D, n_nonzero_coefs)``. \
                         The handle function should return `X`, the sparse codes, and `err`, the approximation error.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. This is only used by `algorithm='omp'`.
        If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    code_init : ndarray of shape (n_samples, n_components), default=None
        Initial sparse representations matrix, for warm restart.
        Only used if `dict_init` is None.

    dict_init : ndarray of shape (n_components, n_features), default=None
        Initial dictionary, for warm restart.
        Only used if `code_init` is None.

    verbose : bool, default=False
        To control the verbosity of the procedure.

    random_state : int, RandomState instance or None, default=None
        Used for initializing the dictionary when `dict_init` is not
        specified. Pass an int for reproducible results across multiple
        function calls.

    kernel_function : {'rbf', 'poly'}, default='rbf'
        Function used to compute the kernel matrix. If no kernel is
        provided then the standard dictionary learning algorithm will be
        used.

    params : None, default=None
        Dictionary with provided parameters for the DL problem. If the
        parameters are not given, then they will be automatically initialized.

        * `'threshold_svd'` - threshold used to approximate singular values with zero, when solving a linear system (default = 1e-8)
        * `'atom_norm_tolerance'` - if an atom norm is less than this threshold, then it is considered zero (default = 1e-10)
        * `'reg_flag'` - flag used for regularization problems (default = False)
        * `'replatoms'` - unused dictionary atoms replacement strategy, (default = ReplAtoms.RANDOM)

            * `'ReplAtoms.ZERO'` : returns a zero column
            * `'ReplAtoms.RANDOM'` : returns a randomly generated atom
            * `'ReplAtoms.NO'` : perform no replacement
            * `'ReplAtoms.WORST'` : replace the worst represented signal
        * `'n_patoms'` - the number of atoms updated in parallel for parallel dictionary update strategies (default = None, meaning all atoms)
        * `'gamma'` - weight of coherence term in the Incoherent DL problem (default = 6)
        * `'mutual_coh_ipr'` - desired mutual coherence for iterative projections and rotations (default = 0.2)
        * `'n_it_ipr'` - number of iterations for iterative projections and rotations (default = 0)
        * `'sigma'` - value used for random Fourier features approximation (default = 1)
        * `'ff'` - forgetting factor value used for online strategies (default = 0.99)
        * `'regmu'` - weight of the regularization term in the Regularized DL problem (default = 0.1)
        * `'regvanish'` - value of vanishing factor in the Regularized DL problem (default = 0.95); after each iteration, regmu takes the value regmu*regvanish
        * `'regstop'` - maximum number of iterations in the Regularized DL problem (default = np.Inf); after regstop iterations, regmu becomes zero

    data_sklearn_compat: bool, default=True
        Flag that establishes the compatibility of the data with the sklearn standard.
        When `True`, data should have dimensions (n_samples, n_features); otherwise, dimensions are (n_features, n_samples).
        Based on this value, the resulting dictionary will be a ndarray of shape (n_components, n_features) or (n_features, n_components).


    Attributes
    ----------
    D_ : ndarray of shape (n_components, n_features)
        Trained dictionary

    error_ : array
        Vector of RMSE values :math:`\|\mathbf{Y} - \mathbf{DX}\|_F/ \sqrt{mN}` at each iteration

    error_extra_ : array
        Vector of errors at each iteration; the meaning depends on the DL objective function


    Example::

        import matplotlib.pyplot as plt

        from dictlearn import DictionaryLearning
        from sklearn.datasets import make_sparse_coded_signal

        n_components = 50      # number of atoms
        n_features = 20        # signal dimension
        n_nonzero_coefs = 3    # sparsity
        n_samples = 100        # number of signals
        n_iterations = 20      # number of dictionary learning iterations

        max_iter = 10
        fit_algorithm = "aksvd"
        transform_algorithm = "omp"

        Y, D_origin, X_origin = make_sparse_coded_signal(
            n_samples=n_samples,
            n_components=n_components,
            n_features=n_features,
            n_nonzero_coefs=n_nonzero_coefs,
            random_state=0
        )

        dl = DictionaryLearning(
            n_components=n_components,
            max_iter=max_iter,
            fit_algorithm=fit_algorithm,
            transform_algorithm=transform_algorithm,
            n_nonzero_coefs=n_nonzero_coefs,
            code_init=None,
            dict_init=None,
            verbose=False,
            random_state=None,
            kernel_function=None,
            params=None,
            data_sklearn_compat=False
        )

        dl.fit(Y)

        plt.plot(range(max_iter), dl.error_, label=fit_algorithm)
        plt.legend()
        plt.show()

    Notes
    -----
    **References:**
    Bogdan Dumitrescu and Paul Irofti.
    Dictionary learning algorithms and applications. Springer, 2018.
    """

    def __init__(
        self,
        n_components=None,
        max_iter=1000,
        fit_algorithm="aksvd",
        transform_algorithm="omp",
        n_nonzero_coefs=None,
        code_init=None,
        dict_init=None,
        verbose=False,
        random_state=None,
        kernel_function=None,
        params=None,
        data_sklearn_compat=True
    ):

        super().__init__(
            transform_algorithm,
            n_nonzero_coefs
        )
        self.n_components = n_components
        self.max_iter = max_iter
        self.fit_algorithm = fit_algorithm
        self.code_init = code_init
        self.dict_init = dict_init
        self.verbose = verbose
        self.random_state = random_state
        self.kernel_function = kernel_function
        self.params = params
        self.data_sklearn_compat = data_sklearn_compat

    def fit(self, Y):
        """Fit the model from data in Y.

        Parameters
        ----------
        Y : array-like of shape (n_samples, n_features)
            Training vector, where `n_samples` in the number of samples
            and `n_features` is the number of features.

        Returns
        -------
        self : object
            Returns the object itself.
        """
        Y = self._validate_data(Y)
        if self.data_sklearn_compat:
            Y = Y.T
        if self.n_components is None:
            n_components = Y.shape[1]
        else:
            n_components = self.n_components

        if self.params is None:
            self.params = _safe_params_init({}, self.fit_algorithm)

        fit_algorithm = _get_fit_handle(self.fit_algorithm)
        if self.fit_algorithm.startswith("ker_"):
            # Compute Kernel Dictionary Learning
            if self.kernel_function is None:
                self.kernel_function = dl_rbf_kernel
            if self.dict_init is None:
                D0 = np.random.randn(Y.shape[1], n_components)
                D0 = normalize(D0, axis=0, norm='l2')
            else:
                D0 = self.dict_init

            D, X, error, error_extra = kernel_dictionary_learning(
                Y,
                D0,
                self.max_iter,
                fit_algorithm,
                self.transform_algorithm,
                self.n_nonzero_coefs,
                self.kernel_function,
                self.params
            )
        elif self.fit_algorithm in ["ocddl", "rlsdl"]:
            # Compute Online Dictionary Learning
            if self.dict_init is None:
                D0 = np.random.randn(Y.shape[0], n_components)
                D0 = normalize(D0, axis=0, norm='l2')
            else:
                D0 = self.dict_init

            D, X, error, error_extra = online_dictionary_learning(
                Y,
                D0,
                self.max_iter,
                fit_algorithm,
                self.transform_algorithm,
                self.n_nonzero_coefs,
                self.params
            )
        else:
            # Compute Standard Dictionary Learning
            if self.dict_init is None:
                D0 = np.random.randn(Y.shape[0], n_components)
                D0 = normalize(D0, axis=0, norm='l2')
            else:
                D0 = self.dict_init

            D, X, error, error_extra = dictionary_learning(
                Y,
                D0,
                self.max_iter,
                fit_algorithm,
                self.transform_algorithm,
                self.n_nonzero_coefs,
                self.params
            )

        if self.data_sklearn_compat:
            self.D_ = D.T
        else:
            self.D_ = D
        self.error_ = error
        self.error_extra_ = error_extra
        return self
