import numpy as np

from sklearn import preprocessing
from sklearn.base import BaseEstimator


class KDPL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\begin{array}{r}
            \\displaystyle\\min_{\\boldsymbol{P}, \\boldsymbol{A},
            \\boldsymbol{D}} \\sum_{k=1}^{\\mathrm{N}}\\left\\|
            \\boldsymbol{\\Phi}\\left(\\boldsymbol{X}_{\\boldsymbol{k}}\\right)
            -\\boldsymbol{\\Phi}(\\boldsymbol{X}) \\boldsymbol{D}_{k}
            \\boldsymbol{A}_{k}\\right\\|_{F}^{2}+\\tau\\left\\|\\boldsymbol{P}_{k}
            \\boldsymbol{\\Phi}^{T}(\\boldsymbol{X}) \\boldsymbol{\\Phi}
            \\left(\\boldsymbol{X}_{k}\\right)-\\boldsymbol{A}_{k}\\right\\|_{F}^{2} \\\\
            +\\theta\\left\\|\\boldsymbol{P}_{k} \\boldsymbol{\\Phi}^{T}(\\boldsymbol{X})
            \\Phi\\left(\\overline{\\boldsymbol{X}}_{k}\\right)\\right\\|_{F}^{2},
            \\quad \\text { s.t. }\\left\\|\\boldsymbol{d}_{i}\\right\\|_{2}^{2} \\leq 1
        \\end{array}

    :param n_components: dictionary size (number of atoms)
    :param tau: scalar constant
    :param theta: scalar constant
    :param gamma: scalar constant
    :param alpha: scalar constant
    :param kernel_function: kernel method
    :param params: dictionary learning parameters

    Example::

        import numpy as np
        
        from sklearn import preprocessing
        from dictlearn.models import KDPL
        from dictlearn.datasets import yaleb
        from dictlearn.kernels import dl_rbf_kernel
        
        
        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()
        
        # data normalization
        X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
        X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
        
        # define dl parameters
        params = {}
        params['gamma'] = 0.5
        
        # train model
        kdpl = KDPL(n_components=30, tau=0.05, theta=0.003, gamma=1e-4,
                    alpha=1e-4, kernel_function=dl_rbf_kernel, params=params)
        kdpl.fit(X_train, y_train, max_iter=10)
        
        # test model
        y_pred = kdpl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = kdpl.predict_proba(X_test)
    """
    def __init__(
        self,
        n_components,
        tau,
        theta,
        gamma,
        alpha,
        kernel_function,
        params
    ):
        self.n_components = n_components
        self.tau = tau
        self.theta = theta
        self.gamma = gamma
        self.alpha = alpha
        self.kernel_function = kernel_function
        self.params = params

        self.D = []
        self.P = []
        self.A = []
        self.InvData = []
        self.n_classes = None

    def _init_dictionaries(self, X, y):
        # save training data
        self.X_train = X

        unique_classes = np.unique(y)
        self.n_classes = len(unique_classes)

        # initialize identity matrix and kernel
        n_signals = X.shape[1]
        I_mat = np.eye(n_signals, dtype=float)
        self.K = self.kernel_function(X, X, self.params)

        # initialize matrices
        for i in range(self.n_classes):
            randn_mat = np.random.randn(n_signals, self.n_components)
            self.D.append(preprocessing.normalize(randn_mat,
                                                  norm='l2',
                                                  axis=0))

            randn_mat = np.random.randn(n_signals, self.n_components)
            self.P.append(preprocessing.normalize(randn_mat,
                                                  norm='l2',
                                                  axis=0).T)

            self.A.append(np.empty([self.n_components,
                                    self.n_components],
                                   dtype=float))

            self.InvData.append(np.linalg.inv(self.tau * self.K[:, y == i] @
                                self.K[y == i, :] +
                                self.theta * self.K[:, y != i] @
                                self.K[y != i, :] + self.gamma * I_mat))

        # initialize A matrices
        self.update_A(X, y)

    def update_D(self, X, y):
        for i in range(0, self.n_classes):
            rho = 1
            rate_rho = 1.2
            tmp_S = self.D[i]
            tmp_T = np.zeros(self.D[i].shape)
            prev_D = self.D[i]
            iteration = 0
            error = 1

            B = np.linalg.solve(
                self.K + self.alpha * np.eye(X.shape[1]),
                self.K[:, y == i] + self.alpha * self.D[i] @ self.A[i]
            )

            while (error > 1e-8 and iteration < 100):
                tmp_D = np.linalg.solve(
                    (rho * np.eye(self.n_components) +
                     self.alpha * self.A[i] @ self.A[i].T).T,
                    (rho * (tmp_S - tmp_T) + self.alpha * B @ self.A[i].T).T
                ).T
                tmp_S = preprocessing.normalize(tmp_D + tmp_T,
                                                norm='l2',
                                                axis=0)
                tmp_T = tmp_T + tmp_D - tmp_S
                rho = rho * rate_rho
                error = np.mean((tmp_D - prev_D)**2)
                prev_D = tmp_D
                iteration += 1

            self.D[i] = tmp_D

    def update_P(self, X, y):
        for i in range(0, self.n_classes):
            self.P[i] = (self.tau * self.A[i] @
                         self.K[y == i, :] @ self.InvData[i])

    def update_A(self, X, y):
        I_mat = np.eye(self.n_components, dtype=float)

        for i in range(0, self.n_classes):
            self.A[i] = np.linalg.solve(
                self.D[i].T@self.K@self.D[i] + self.tau*I_mat,
                (self.D[i].T + self.tau * self.P[i]) @ self.K[:, y == i]
            )

    def fit(self, X, y, max_iter=1, verbose=0):
        # initialize matrices
        self._init_dictionaries(X, y)

        # train dictionaries
        for i in range(max_iter):
            self.update_P(X, y)
            self.update_D(X, y)
            self.update_A(X, y)

    def predict(self, X):
        # build test kernel
        n_train_signals = self.X_train.shape[1]
        n_test_signals = X.shape[1]
        K_test = np.zeros((n_train_signals, n_test_signals))

        # init prediction array and test kernel
        y_pred = np.empty(n_test_signals, dtype=np.uint8)
        K_test = self.kernel_function(self.X_train, X, self.params)

        for j in range(0, n_test_signals):
            K_y_y = self.kernel_function(X[:, j].reshape(-1, 1),
                                         X[:, j].reshape(-1, 1),
                                         self.params)
            K_y_X = K_test[:, j]

            error = np.Inf
            for i in range(0, self.n_classes):
                tmp_mat_1 = K_y_X @ self.P[i].T @ self.D[i].T
                tmp_mat_2 = (K_y_X @ self.D[i]) @ (self.P[i] @ K_y_X.T)
                eps = (K_y_y - tmp_mat_2 - tmp_mat_2.T +
                       tmp_mat_1 @ self.K @ tmp_mat_1.T)
                if error > eps:
                    error = eps
                    y_pred[j] = i

        return y_pred

    def predict_proba(self, X):
        # build test kernel
        n_train_signals = self.X_train.shape[1]
        n_test_signals = X.shape[1]
        K_test = np.zeros((n_train_signals, n_test_signals))

        # init prediction aray
        error = np.zeros([self.n_classes, X.shape[1]], dtype=float)
        K_test = self.kernel_function(self.X_train, X,
                                      self.params)

        for j in range(0, n_test_signals):
            K_y_y = self.kernel_function(X[:, j].reshape(-1, 1),
                                         X[:, j].reshape(-1, 1),
                                         self.params)
            K_y_X = K_test[:, j]

            for i in range(0, self.n_classes):
                tmp_mat_1 = K_y_X @ self.P[i].T @ self.D[i].T
                tmp_mat_2 = (K_y_X @ self.D[i]) @ (self.P[i] @ K_y_X.T)
                error[i, j] = (K_y_y - tmp_mat_2 - tmp_mat_2.T +
                               tmp_mat_1 @ self.K @ tmp_mat_1.T)

        proba = (np.exp(-error) / np.sum(np.exp(-error), axis=0)).T
        return proba
