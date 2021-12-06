import numpy as np

from sklearn import preprocessing
from sklearn.base import BaseEstimator
from dictlearn import sparse_encode


class KDDL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\min _{\\boldsymbol{A}, \\boldsymbol{W}, \\boldsymbol{X}}\\|
        \\boldsymbol{\\varphi}(\\boldsymbol{Y})-\\boldsymbol{\\varphi}
        (\\boldsymbol{Y}) \\boldsymbol{A} \\boldsymbol{X}\\|_{F}^{2}+\\alpha
        \\|\\boldsymbol{H}-\\boldsymbol{W} \\boldsymbol{X}\\|_{F}^{2}

    Parameters
    ----------
    transform_algorithm : {'omp'}, default='omp'
        Algorithm for computing the sparse representation:
        
        * `'omp'`: uses orthogonal matching pursuit to estimate the sparse solution.

    n_components : int, default=n_features
        Number of dictionary elements to extract.

    n_nonzero_coefs : int, default=None
        Number of nonzero coefficients to target in each column of the
        solution. If `None`, then `n_nonzero_coefs=int(n_features / 10)`.

    kernel_function : handle function
        Computes the kernel matrix.

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
        
        from dictlearn.models import KDDL
        from dictlearn.datasets import yaleb
        from dictlearn.kernels import dl_rbf_kernel
        
        
        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()
        
        alpha = 2               # classification penalty
        n_components = 200      # number of atoms
        n_nonzero_coefs = 4     # sparsity constraint
        
        # define general parameters
        params = {}
        params['gamma'] = 1e-5
        
        # train model
        kddl = KDDL('omp', n_components, n_nonzero_coefs, dl_rbf_kernel, params, alpha)
        kddl.fit(X_train, y_train, max_iter=10, batches=2)
        
        # test model
        y_pred = kddl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = kddl.predict_proba(X_test)
    """
    def __init__(
        self,
        transform_algorithm,
        n_components,
        n_nonzero_coefs,
        kernel_function,
        params,
        alpha
    ):
        self.transform_algorithm = transform_algorithm
        self.n_components = n_components
        self.n_nonzero_coefs = n_nonzero_coefs
        self.kernel_function = kernel_function
        self.params = params
        self.alpha = alpha

    def _fit(self, X, y, max_iter=1, verbose=0):
        # save training data
        self.X_train = X

        # initialize one hot encoding matrix
        unique_labels = np.unique(y)
        n_classes = len(unique_labels)
        H = np.zeros((n_classes, len(y)))

        # populate one hot encoding matrix
        for index, label in enumerate(y):
            H[label, index] = 1

        # init dictionary and kernel
        n_signals = X.shape[1]
        self.K = np.zeros((n_signals, n_signals))
        if not hasattr(self, 'A'):
            self.A = np.random.randn(n_signals, self.n_components)
            self.A = preprocessing.normalize(self.A, norm='l2', axis=0)
            self.W = np.zeros((n_classes, self.n_components))

        self.K = self.kernel_function(X, X, self.params)

        for iter in range(max_iter):
            # sparse coding
            self.Encoding, _ = sparse_encode(
                self.A.T @ self.K + self.alpha * self.W.T @ H,
                self.A.T @ self.K @ self.A + self.alpha * self.W.T @ self.W,
                self.transform_algorithm,
                self.n_nonzero_coefs
            )

            # update each column from dictionary
            for atom_index in range(self.n_components):
                atom_usages = np.nonzero(self.Encoding[atom_index, :])[0]

                if len(atom_usages) == 0:
                    # replace with the new atom
                    atom = np.random.randn(n_signals)
                    self.A[:, atom_index] = (atom /
                                             np.sqrt(atom.T @ self.K @ atom))
                    w = np.random.randn(n_classes)
                    self.W[:, atom_index] = w / np.linalg.norm(w)
                else:
                    # build selection vector
                    sel = list(range(self.A.shape[1]))
                    sel.remove(atom_index)

                    # omptize current atom
                    atom = (self.Encoding[atom_index, :].T - self.A[:, sel] @
                            (self.Encoding[np.ix_(sel, atom_usages)] @
                            self.Encoding[atom_index, atom_usages].T))
                    atom = atom / np.sqrt(atom.T @ self.K @ atom)
                    self.A[:, atom_index] = atom

                    # optimize classifier column
                    w = (H[:, atom_usages] @
                         self.Encoding[atom_index, atom_usages].T -
                         self.W[:, sel] @
                         (self.Encoding[np.ix_(sel, atom_usages)] @
                          self.Encoding[atom_index, atom_usages].T))
                    self.W[:, atom_index] = w / np.linalg.norm(w)

                    # optimize reprezentation
                    v = atom.T @ self.K
                    x_1 = (v[atom_usages] -
                           (v @ self.A) @ self.Encoding[:, atom_usages])
                    x_2 = (w.T @ H[:, atom_usages] -
                           (w.T @ self.W) @ self.Encoding[:, atom_usages])
                    self.Encoding[atom_index,
                                  atom_usages] = ((x_1 + self.alpha * x_2) /
                                                  (1 + self.alpha))

    def fit(self, X, y, max_iter=1, batches=1, verbose=0):
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
        # init label array
        positions = np.zeros(X.shape[1])
        
        # compute kernelized scalar product with training signals
        K_test = self.kernel_function(
            X,
            self.X_train,
            self.params
        )

        for n_test in range(X.shape[1]):
            k = K_test[n_test, :].reshape(K_test.shape[1], 1)
            
            # compute representation of test signal
            x, _ = sparse_encode(
                self.A.T @ k,
                self.A.T @ self.K @ self.A,
                self.transform_algorithm,
                self.n_nonzero_coefs,
            )

            # compute label vector
            positions[n_test] = np.argmax(self.W @ x)
        return positions

    def predict_proba(self, X):
        # init W array
        W = np.zeros((X.shape[1], self.W.shape[0]))

        # compute kernelized scalar product with training signals
        K_test = self.kernel_function(
            X,
            self.X_train,
            self.params
        )

        for n_test in range(X.shape[1]):
            k = K_test[n_test, :].reshape(K_test.shape[1], 1)

            # compute representation of test signal
            x, _ = sparse_encode(
                self.A.T @ k,
                self.A.T @ self.K @ self.A,
                self.transform_algorithm,
                self.n_nonzero_coefs
            )

            # compute error vector
            W[n_test, :] = self.W @ x

        proba = (np.exp(W) / np.sum(np.exp(W), axis=0))
        return proba
