import numpy as np

from sklearn.base import BaseEstimator
from dictlearn import sparse_encode


class KLCDL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\min _{D, W, \\boldsymbol{A}, X} \\|\\boldsymbol{\\varphi}
        (\\boldsymbol{Y})-\\boldsymbol{\\varphi}(\\boldsymbol{Y})
        \\boldsymbol{A} \\boldsymbol{X}\\|_{F}^{2} +\\alpha\\|\\boldsymbol{H}-
        \\boldsymbol{W} \\boldsymbol{X}\\|_{F}^{2}+\\beta\\|\\boldsymbol{Q}-
        \\boldsymbol{A} \\boldsymbol{X}\\|_{F}^{2}
    
    Parameters
    ----------
    transform_algorithm : {'omp'}, default='omp'
        AAlgorithm for computing the sparse representation:
        
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

    beta : scalar constant


    Example::

        import numpy as np

        from dictlearn.models import KLCDL
        from dictlearn.datasets import yaleb
        from dictlearn.kernels import dl_rbf_kernel


        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()

        alpha = 0.01             # classification penalty
        beta = 0.01              # label consistent penalty
        n_components = 200       # number of atoms
        n_nonzero_coefs = 4      # sparsity constraint

        # define general parameters
        params = {}
        params['sigma'] = 100

        # train model
        klcdl = KLCDL('omp', n_components, n_nonzero_coefs, dl_rbf_kernel, params,
                      alpha, beta)
        klcdl.fit(X_train, y_train, max_iter=10, batches=1)

        # test model
        y_pred = klcdl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = klcdl.predict_proba(X_test)
    """
    def __init__(
        self,
        transform_algorithm,
        n_components,
        n_nonzero_coefs,
        kernel_function,
        params,
        alpha,
        beta
    ):
        self.transform_algorithm = transform_algorithm
        self.n_components = n_components
        self.n_nonzero_coefs = n_nonzero_coefs
        self.kernel_function = kernel_function
        self.params = params
        self.alpha = alpha
        self.beta = beta

    def _fit(self, X, y, max_iter=1, verbose=0):
        # save training data
        self.X_train = X

        # initialize one hot encoding matrix
        unique_labels = np.unique(y)
        n_classes = len(unique_labels)
        H = np.zeros((n_classes, len(y)))

        # initialize label consistency matrix
        n_atoms_per_class = int(np.floor(self.n_components / n_classes))
        Q = np.zeros((n_atoms_per_class*n_classes, X.shape[1]))

        # create label -> position dict
        self.label_pos = {}
        for index, label in enumerate(unique_labels):
            self.label_pos[label] = index

        # populate one hot encoding matrix
        for index, label in enumerate(y):
            H[self.label_pos[label], index] = 1
            Q[n_atoms_per_class * self.label_pos[label]:
              n_atoms_per_class * (self.label_pos[label] + 1), index] = 1

        # init dictionary and kernel
        n_signals = X.shape[1]
        self.K = np.zeros((n_signals, n_signals))
        if not hasattr(self, 'A'):
            self.A = np.random.randn(n_signals, self.n_components)
            self.A = self.A / np.linalg.norm(self.A, axis=0)
            self.W = np.zeros((n_classes, self.n_components))
            self.V = np.zeros((n_atoms_per_class*n_classes, self.n_components))

        self.K = self.kernel_function(X, X, self.params)

        for iter in range(max_iter):
            # sparse coding
            self.Encoding, _ = sparse_encode(
                self.A.T @ self.K + self.alpha * self.W.T @ H + self.beta * self.V.T @ Q,
                self.A.T @ self.K @ self.A + self.alpha * self.W.T @ self.W + self.beta * self.V.T @ self.V,
                self.transform_algorithm,
                self.n_nonzero_coefs
            )
            # update each column from dictionary
            for atom_index in range(self.n_components):
                atom_usages = np.nonzero(self.Encoding[atom_index, :])[0]

                if len(atom_usages) == 0:
                    # replace with the new atom
                    atom = np.random.randn(n_signals)
                    w = np.random.randn(n_classes)
                    v = np.random.randn(n_atoms_per_class*n_classes)
                    norm_aw = np.sqrt(
                        atom.T @ self.K @ atom + self.alpha * w.T @ w +
                        self.beta * v.T @ v
                    )

                    self.W[:, atom_index] = w / norm_aw
                    self.A[:, atom_index] = atom / norm_aw
                    self.V[:, atom_index] = v / norm_aw
                else:
                    # build selection vector
                    sel = list(range(self.A.shape[1]))
                    sel.remove(atom_index)

                    # omptize current atom
                    atom = (self.Encoding[atom_index, :].T - self.A[:, sel] @
                            (self.Encoding[np.ix_(sel, atom_usages)] @
                            self.Encoding[atom_index, atom_usages].T))

                    # optimize classifier column
                    w = (H[:, atom_usages] @
                         self.Encoding[atom_index, atom_usages].T -
                         self.W[:, sel] @
                         (self.Encoding[np.ix_(sel, atom_usages)] @
                          self.Encoding[atom_index, atom_usages].T))

                    # optimize label transformer
                    v = (Q[:, atom_usages] @
                         self.Encoding[atom_index, atom_usages].T -
                         self.V[:, sel] @
                         (self.Encoding[np.ix_(sel, atom_usages)] @
                          self.Encoding[atom_index, atom_usages].T))

                    # normalize all current columns
                    norm_aw = np.sqrt(atom.T @ self.K @ atom +
                                      self.alpha * w.T @ w +
                                      self.beta * v.T @ v)
                    self.A[:, atom_index] = atom / norm_aw
                    self.W[:, atom_index] = w / norm_aw
                    self.V[:, atom_index] = v / norm_aw

                    # optimize reprezentation
                    u = atom.T @ self.K
                    x_1 = (u[atom_usages] -
                           (u @ self.A) @ self.Encoding[:, atom_usages])
                    x_2 = (w.T @ H[:, atom_usages] -
                           (w.T @ self.W) @ self.Encoding[:, atom_usages])
                    x_3 = (v.T @ Q[:, atom_usages] -
                           (v.T @ self.V) @ self.Encoding[:, atom_usages])
                    self.Encoding[atom_index, atom_usages] = (
                        (x_1 + self.alpha * x_2 + self.beta * x_3) /
                        (1 + self.alpha + self.beta)
                    )

        # normalize atoms
        for atom_index in range(self.n_components):
            atom_norm = np.sqrt(self.A[:, atom_index].T @
                                self.K @ self.A[:, atom_index])
            self.A[:, atom_index] = self.A[:, atom_index] / atom_norm
            self.W[:, atom_index] = self.W[:, atom_index] / atom_norm
            self.V[:, atom_index] = self.V[:, atom_index] / atom_norm
            self.Encoding[:, atom_index] = (self.Encoding[:, atom_index] /
                                            atom_norm)

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
                self.n_nonzero_coefs
            )

            # compute label vector
            positions[n_test] = np.argmax(self.W @ x)

        # create position -> label dict
        pos_label = {pos: label for label, pos in self.label_pos.items()}

        for index, value in enumerate(positions):
            positions[index] = pos_label[value]
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
