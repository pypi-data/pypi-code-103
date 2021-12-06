import numpy as np

from sklearn import preprocessing
from sklearn.base import BaseEstimator
from dictlearn import sparse_encode, dictionary_learning, _get_fit_handle


class DDL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\min _{D, W, \\boldsymbol{X}}\\|\\boldsymbol{Y}-\\boldsymbol{D}
        \\boldsymbol{X}\\|_{F}^{2}+\\alpha\\|\\boldsymbol{H}-\\boldsymbol{W}
        \\boldsymbol{X}\\|_{F}^{2}

    Parameters
    ----------
    fit_algorithm : {'ksvd', 'aksvd', 'uaksvd', 'sgk', 'nsgk', 'mod'}, default='aksvd'
        Algorithm used to update the dictionary:
        
        * `'ksvd'`: uses the ksvd algorithm 
        * `'aksvd'`: uses the aksvd algorithm
        * `'uaksvd'`: uses the uaksvd algorithm
        * `'sgk'`: uses the sgk algorithm
        * `'nsgk'`: uses the nsgk algorithm
        * `'mod'`: uses the mod algorithm

    transform_algorithm : {'omp'}, default='omp'
        Algorithm for computing the sparse representation:
        
        * `'omp'`: uses orthogonal matching pursuit to estimate the sparse solution.

    n_components : int, default=n_features
        Number of dictionary elements to extract.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    params : None, default=None
        Dictionary with provided parameters for the DL problem. If the
        params are not given then they will be automatically initialized.

    alpha : scalar constant

    init_method : scalar constant

    init_iter : int, default=100
        Maximum number of iterations to perform.

    gamma : scalar constant


    Example::

        import numpy as np
        
        from dictlearn.models import DDL
        from dictlearn.datasets import yaleb
        
        
        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()
        
        alpha = 2               # classification penalty
        n_components = 200      # number of atoms
        n_nonzero_coefs = 4     # sparsity constraint
        
        # define dl parameters
        params = {}
        
        # train model
        ddl = DDL('ksvd', 'omp', n_components, n_nonzero_coefs, params, alpha)
        ddl.fit(X_train, y_train, max_iter=10, batches=4)
        
        # test model
        y_pred = ddl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = ddl.predict_proba(X_test)

    **References:**
    Q. Zhang, B. Li, Discriminative K-SVD for dictionary learning in face recognition, in
    Proceedings of IEEE Conf. Computer Vision and Pattern Recognition (2010), pp. 2691–2698
    """

    def __init__(
        self,  
        fit_algorithm,
        transform_algorithm,
        n_components,
        n_nonzero_coefs,
        params,
        alpha,
        init_method=0,
        init_iter=20,
        gamma=1e-3
    ):
        self.fit_algorithm = _get_fit_handle(fit_algorithm)
        self.transform_algorithm = transform_algorithm
        self.n_components = n_components
        self.n_nonzero_coefs = n_nonzero_coefs
        self.params = params
        self.alpha = alpha
        self.init_method = init_method
        self.init_iter = init_iter
        self.gamma = gamma

    def _plain_init(self, rows, cols):
        D0 = np.random.randn(rows, cols)
        D0 = preprocessing.normalize(D0, norm='l2', axis=0)
        return D0

    def _trained_init(self, rows, cols, X, H):
        # initialize dictionary
        D0 = np.zeros((rows, cols))
        D0c = preprocessing.normalize(X[:, :cols], norm='l2', axis=0)

        # train initial dictionary
        D0[:X.shape[0], :], _, _, _ = dictionary_learning(
            X,
            D0c,
            self.init_iter,
            self.fit_algorithm,
            self.transform_algorithm,
            self.n_nonzero_coefs,
            self.params
        )

        Encoding, _ = sparse_encode(
            X,
            D0[:X.shape[0], :],
            self.transform_algorithm,
            self.n_nonzero_coefs
        )

        W = np.linalg.solve(
            (Encoding @ Encoding.T).T + self.gamma * np.eye(Encoding.shape[0]),
            Encoding @ H.T
        ).T

        D0[X.shape[0]:, :] = np.sqrt(self.alpha) * W
        D0 = preprocessing.normalize(D0, norm='l2', axis=0)

        return D0

    def _fit(self, X, y, max_iter=1, verbose=0):
        # initialize one hot encoding matrix
        unique_labels = np.unique(y)
        n_classes = len(unique_labels)
        H = np.zeros((n_classes, len(y)))

        # populate one hot encoding matrix
        for index, label in enumerate(y):
            H[label, index] = 1

        # extend signals matrix
        X_ext = np.vstack((X, np.sqrt(self.alpha)*H))

        # initialize D according to the init_method
        n_features = X.shape[0] + n_classes
        if hasattr(self, 'D0'):
            D0 = self.D0
        else:
            if self.init_method == 0:
                D0 = self._plain_init(n_features, self.n_components)
            else:
                D0 = self._trained_init(n_features, self.n_components, X, H)

        # train extended dictionary
        self.D0, _, _, _ = dictionary_learning(
            X_ext,
            D0,
            max_iter,
            self.fit_algorithm,
            self.transform_algorithm,
            self.n_nonzero_coefs,
            self.params
        )

        # extract dictionary
        self.D = self.D0[:X.shape[0], :]
        norm_D = np.linalg.norm(self.D, axis=0)
        self.D = self.D / norm_D

        # extract classifier matrix
        self.W = self.D0[X.shape[0]:, :]
        self.W = self.W / np.sqrt(self.alpha) / norm_D

    def fit(self, X, y, max_iter=1, batches=1):
        batch_size = int(X.shape[1] / batches)
        for iter in range(max_iter):
            # shuffle data
            rp = np.random.permutation(len(y))
            X = X[:, rp]
            y = y[rp]

            for i in range(batches):
                self._fit(
                    X[:, i*batch_size:(i+1)*batch_size],
                    y[i*batch_size:(i+1)*batch_size],
                    max_iter=1
                )

    def predict(self, X):
        encodings, _ = sparse_encode(
            X,
            self.D,
            self.transform_algorithm,
            self.n_nonzero_coefs
        )
        positions = np.argmax(self.W @ encodings, axis=0)
        return positions

    def predict_proba(self, X):
        encodings, _ = sparse_encode(
            X,
            self.D,
            self.transform_algorithm,
            self.n_nonzero_coefs
        )
        W = self.W @ encodings
        proba = (np.exp(W) / np.sum(np.exp(W), axis=0)).T
        return proba
