import numpy as np

from sklearn import preprocessing
from sklearn.base import BaseEstimator


class DPL(BaseEstimator):
    """Solves the following classification problem

    .. math::
        \\min _{\\boldsymbol{P}, \\boldsymbol{A}, \\boldsymbol{D}}
        \\sum_{k=1}^{K}\\left\\|\\boldsymbol{X}_{i}-\\boldsymbol{D}_{k}
        \\boldsymbol{A}_{k}\\right\\|_{F}^{2}+\\tau\\left\\|\\boldsymbol{P}_{k}
        \\boldsymbol{X}_{k}-\\boldsymbol{A}_{k}\\right\\|_{F}^{2}+
        \\theta\\left\\|\\boldsymbol{P}_{k} \\overline{\\boldsymbol{X}}_{k}
        \\right\\|_{F}^{2}, \\quad \\text { s.t. }\\left\\|\\boldsymbol{d}_{i}
        \\right\\|_{2}^{2} \\leq 1

    :param n_components: dictionary size (number of atoms)
    :param tau: scalar constant
    :param theta: scalar constant
    :param gamma: scalar constant

    Example::

        import numpy as np
        
        from sklearn import preprocessing
        from dictlearn.models import DPL
        from dictlearn.datasets import yaleb
        
        
        # load data
        (X_train, y_train), (X_test, y_test) = yaleb.load_data()
        
        # data normalization
        X_train = preprocessing.normalize(X_train, norm='l2', axis=0)
        X_test = preprocessing.normalize(X_test, norm='l2', axis=0)
        
        # train model
        dpl = DPL(n_components=30, tau=0.05, theta=0.003, gamma=0.0001)
        dpl.fit(X_train, y_train, max_iter=10)
        
        # test model
        y_pred = dpl.predict(X_test)
        accuracy = np.sum(y_test == y_pred) / len(y_test)
        y_proba = dpl.predict_proba(X_test)

    **References:**
    Gu, Shuhang, et al. "Projective dictionary pair learning for pattern classification."
    Advances in neural information processing systems 27 (2014): 793-801
    """

    def __init__(
        self,
        n_components,
        tau,
        theta,
        gamma
    ):
        self.n_components = n_components
        self.tau = tau
        self.theta = theta
        self.gamma = gamma

        self.D = []
        self.P = []
        self.A = []
        self.InvData = []
        self.n_classes = None

    def _init_dictionaries(self, X, y):
        unique_classes = np.unique(y)
        self.n_classes = len(unique_classes)

        # initialize identity matrix
        n_features = X.shape[0]
        I_mat = np.eye(n_features, dtype=float)

        # initialize matrices
        for i in range(self.n_classes):
            randn_mat = np.random.randn(n_features, self.n_components)
            self.D.append(preprocessing.normalize(randn_mat,
                                                  norm='l2',
                                                  axis=0))

            randn_mat = np.random.randn(n_features, self.n_components)
            self.P.append(preprocessing.normalize(randn_mat,
                                                  norm='l2',
                                                  axis=0).T)

            self.A.append(np.empty([self.n_components, self.n_components],
                                   dtype=float))

            self.InvData.append(
                np.linalg.inv(
                    self.tau * (X[:, y == i] @ X[:, y == i].T) +
                    self.theta * (X[:, y != i] @ X[:, y != i].T) +
                    self.gamma * I_mat
                )
            )

        # initialize A matrices
        self.update_A(X, y)

    def update_D(self, X, y):
        I_mat = np.eye(self.n_components, dtype=float)

        for i in range(self.n_classes):
            rho = 1
            rate_rho = 1.2
            tmp_S = self.D[i]
            tmp_T = np.zeros(self.D[i].shape)
            prev_D = self.D[i]
            iteration = 0
            error = 1

            while (error > 1e-8 and iteration < 100):
                tmp_D = np.linalg.solve(
                    (rho * I_mat + self.A[i] @ self.A[i].T).T,
                    (rho * (tmp_S - tmp_T) + X[:, y == i] @ self.A[i].T).T
                ).T
                tmp_S = preprocessing.normalize(tmp_D + tmp_T,
                                                norm='l2', axis=0)
                tmp_T = tmp_T + tmp_D - tmp_S
                rho = rho * rate_rho
                error = np.mean((tmp_D - prev_D)**2)
                prev_D = tmp_D
                iteration += 1

            self.D[i] = tmp_D

    def update_P(self, X, y):
        for i in range(self.n_classes):
            self.P[i] = self.tau * self.A[i] @ X[:, y == i].T @ self.InvData[i]

    def update_A(self, X, y):
        I_mat = np.eye(self.n_components, dtype=float)

        for i in range(self.n_classes):
            self.A[i] = np.linalg.solve(
                self.D[i].T@self.D[i] + self.tau*I_mat,
                self.D[i].T @ X[:, y == i] +
                self.tau * self.P[i] @ X[:, y == i]
            )

    def fit(self, X, y, max_iter=10, verbose=0):
        # initialize matrices
        self._init_dictionaries(X, y)

        # train dictionaries
        for i in range(max_iter):
            self.update_P(X, y)
            self.update_D(X, y)
            self.update_A(X, y)

        # create encoder matrix
        self.Encoder = np.vstack(self.P)

    def predict(self, X):
        predicted_coef = self.Encoder @ X
        error = np.zeros([self.n_classes, X.shape[1]], dtype=float)

        for i in range(self.n_classes):
            error[i, :] = np.sum((self.D[i] @ predicted_coef[i*self.n_components:
                                 (i+1) * self.n_components, :] - X) ** 2, axis=0)

        y_pred = np.argmin(error, axis=0)
        return y_pred

    def predict_proba(self, X):
        predicted_coef = self.Encoder @ X
        error = np.zeros([self.n_classes, X.shape[1]], dtype=float)

        for i in range(self.n_classes):
            error[i, :] = np.sum((self.D[i] @ predicted_coef[i*self.n_components:
                                 (i+1) * self.n_components, :] - X) ** 2, axis=0)

        proba = (np.exp(-error) / np.sum(np.exp(-error), axis=0)).T
        return proba
