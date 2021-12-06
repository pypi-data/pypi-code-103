import numpy as np

from sklearn.base import BaseEstimator
from dictlearn import sparse_encode, dictionary_learning, _get_fit_handle


class LCDL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\min _{D, W, \\boldsymbol{A}, X}\\|\\boldsymbol{Y}-\\boldsymbol{D}
        \\boldsymbol{X}\\|_{F}^{2}+\\alpha\\|\\boldsymbol{H}-\\boldsymbol{W}
        \\boldsymbol{X}\\|_{F}^{2}+\\beta\\|\\boldsymbol{Q}-\\boldsymbol{A}
        \\boldsymbol{X}\\|_{F}^{2}

    Parameters
    ----------
    fit_algorithm : {'ksvd', 'aksvd', 'uaksvd', 'sgk', 'nsgk', 'mod'}, default='aksvd'
        Algorithm used to update the dictionary:
        
        * `'ksvd'`: uses the ksvd algorithm problem
        * `'aksvd'`: uses the aksvd algorithm problem
        * `'uaksvd'`: uses the uaksvd algorithm problem
        * `'sgk'`: uses the sgk algorithm problem
        * `'nsgk'`: uses the nsgk algorithm problem
        * `'mod'`: uses the mod algorithm problem

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

    beta : scalar constant

    init_method : scalar constant

    init_iter : int, default=100
        Maximum number of iterations to perform.

    gamma : scalar constant


    Example::

        import numpy as np
        
        from dictlearn.models import LCDL
        from dictlearn.datasets import yaleb
        
        
        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()
        
        alpha = 2               # classification penalty
        beta = 4                # label consistent penalty
        n_components = 5        # number of atoms
        n_nonzero_coefs = 4     # sparsity constraint
        
        # define general parameters
        params = {}
        
        # train model
        lcdl = LCDL('aksvd', 'omp', n_components, n_nonzero_coefs, params, alpha, beta,
                    init_method=0)
        lcdl.fit(X_train, y_train, max_iter=10)
        
        # test model
        y_pred = lcdl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = lcdl.predict_proba(X_test)

    **References:**
    Z. Jiang, Z. Lin, L.S. Davis, Label consistent K-SVD: learning a discriminative dictionary
    for recognition. IEEE Trans. Pattern Anal. Mach. Intell. 35(11), 2651–2664 (2013)
    """
    def __init__(
        self,
        fit_algorithm,
        transform_algorithm,
        n_components,
        n_nonzero_coefs,
        params,        
        alpha,
        beta,
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
        self.beta = beta
        self.init_method = init_method
        self.init_iter = init_iter
        self.gamma = gamma

    def column_normalization(self, M):
        return M / np.linalg.norm(M, axis=0)

    def _plain_init(self, rows, cols):
        D0 = np.random.randn(rows, cols)
        D0 = self.column_normalization(D0)
        return D0

    def _trained_init_1(self, rows, cols, X, H, Q):
        D0 = np.zeros((rows, cols))

        jj = 0
        for i in range(H.shape[0]):
            jc = np.where(H[i, :] == 1)[0]
            Xc = X[:, jc]
            nc = int(np.sum(Q[:, jc[0]]))

            D0c = Xc[:, :nc]
            D0c = self.column_normalization(D0c)
            Dc, _, _, _ = dictionary_learning(
                Xc,
                D0c,
                self.init_iter,
                self.fit_algorithm,
                self.transform_algorithm,
                self.n_nonzero_coefs,
                self.params
            )
            D0[:X.shape[0], jj:jj+nc] = Dc
            jj += nc

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

        A = np.linalg.solve(
            (Encoding @ Encoding.T).T + self.gamma * np.eye(Encoding.shape[0]),
            Encoding @ Q.T
        ).T

        D0[X.shape[0]:X.shape[0]+H.shape[0], :] = np.sqrt(self.alpha) * W
        D0[X.shape[0]+H.shape[0]:, :] = np.sqrt(self.beta) * A
        D0 = self.column_normalization(D0)

        return D0

    def _trained_init_2(self, rows, cols, X, H, Q):
        ns = np.sum(np.count_nonzero(Q, axis=1) == Q.shape[1])
        D0 = np.zeros((rows, cols))

        jj = 0
        for i in range(H.shape[0]):
            jc = np.where(H[i, :] == 1)[0]
            Xc = X[:, jc]
            nc = int(np.sum(Q[:, jc[0]])) - ns

            D0c = Xc[:, :nc]
            D0c = self.column_normalization(D0c)
            Dc, _, _, _ = dictionary_learning(
                Xc,
                D0c,
                self.init_iter,
                self.fit_algorithm,
                self.transform_algorithm,
                self.n_nonzero_coefs,
                self.params
            )
            D0[:X.shape[0], jj:jj+nc] = Dc
            jj += nc

        # train the shared dictionary
        Xs = X[:, np.random.permutation(X.shape[1])[:ns]]
        D0s = self.column_normalization(Xs)
        Ds, _, _, _ = dictionary_learning(
            X,
            D0s,
            self.init_iter,
            self.fit_algorithm,
            self.transform_algorithm,
            self.n_nonzero_coefs,
            self.params
        )
        D0[:X.shape[0], jj:] = Ds

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

        A = np.linalg.solve(
            (Encoding @ Encoding.T).T + self.gamma * np.eye(Encoding.shape[0]),
            Encoding @ Q.T
        ).T

        D0[X.shape[0]:X.shape[0]+H.shape[0], :] = np.sqrt(self.alpha) * W
        D0[X.shape[0]+H.shape[0]:, :] = np.sqrt(self.beta) * A
        D0 = self.column_normalization(D0)

        return D0

    def _fit(self, X, y, max_iter=1):
        # initialize one hot encoding matrix
        unique_labels = np.unique(y)
        n_classes = len(unique_labels)
        H = np.zeros((n_classes, len(y)))

        # initialize label consistency matrix
        Q = np.zeros((self.n_components*n_classes, X.shape[1]))
        if self.init_method == 2:
            Q = np.vstack((Q, np.ones((self.n_components, Q.shape[1]))))

        # create label -> position dict
        self.label_pos = {}
        for index, label in enumerate(unique_labels):
            self.label_pos[label] = index

        # populate one hot encoding matrix
        for index, label in enumerate(y):
            H[self.label_pos[label], index] = 1
            Q[self.n_components * self.label_pos[label]:
              self.n_components * (self.label_pos[label] + 1), index] = 1

        # extend signals matrix
        X_ext = np.vstack((X, np.sqrt(self.alpha)*H, np.sqrt(self.beta)*Q))

        # initialize D according to the init_method
        atom_size = X.shape[0] + n_classes + self.n_components*n_classes
        if hasattr(self, 'D0'):
            D0 = self.D0
        else:
            if self.init_method == 0:
                D0 = self._plain_init(atom_size, self.n_components*n_classes)
            elif self.init_method == 1:
                D0 = self._trained_init_1(
                    atom_size,
                    self.n_components*n_classes,
                    X,
                    H,
                    Q
                )
            else:
                atom_size += self.n_components
                D0 = self._trained_init_2(
                    atom_size,
                    self.n_components * (n_classes + 1),
                    X,
                    H,
                    Q
                )

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
        self.W = self.D0[X.shape[0]:X.shape[0]+n_classes, :]
        self.W = self.W / np.sqrt(self.alpha) / norm_D

        # extract A matrix
        self.A = self.D0[X.shape[0]+n_classes:, :]
        self.A = self.A / np.sqrt(self.beta) / norm_D

    def fit(self, X, y, max_iter=1, batches=1):
        batch_size = int(X.shape[1] / batches)
        for iter in range(max_iter):
            # shuffle data
            rp = np.random.permutation(len(y))
            X = X[:, rp]
            y = y[rp]

            for i in range(batches):
                self._fit(X[:, i*batch_size:(i+1)*batch_size],
                          y[i*batch_size:(i+1)*batch_size], max_iter=1)

    def predict(self, X):
        encodings, _ = sparse_encode(
            X,
            self.D,
            self.transform_algorithm,
            self.n_nonzero_coefs
        )
        positions = np.argmax(self.W @ encodings, axis=0)

        # create position -> label dict
        pos_label = {pos: label for label, pos in self.label_pos.items()}

        for index, value in enumerate(positions):
            positions[index] = pos_label[value]

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
