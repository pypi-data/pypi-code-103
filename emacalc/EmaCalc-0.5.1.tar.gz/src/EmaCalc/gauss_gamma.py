"""This module implements a multivariate Gaussian distribution of a random vector
with INDEPENDENT ELEMENTS, i.e., diagonal covariance matrix,
and extends the scipy.stats implementations by including Bayesian learning.

*** Classes:
GaussianRV: a trainable Gaussian distribution of a random vector with independent elements,
    defined by a Gaussian mean, and gamma-distributed precision parameters

GaussianGivenPrecisionRV: model for the random mean vector of a GaussianRV object
PrecisionRV: model for the random precision vector of a GaussianRV object

StudentRV: a multivariate Student-t distribution for a vector with independent elements,
used for predictive distributions derived from a GaussianRV instance.

Arne Leijon, 2018-08-10
2018-11-27, minor fix for easier sub-classing
2021-10-22, copied PairedCompCalc -> EmaCalc, unchanged
2021-10-22, modified for use in EmaCalc
"""
import numpy as np
from scipy.special import gammaln, psi

from scipy.stats import t as scipy_t


# -------------------------------------------
class GaussianRV:
    """Gaussian distribution of a random 1D (row) array
    with independent elements.
    The probability density function is
    p(x | mu, Lambda) propto prod_d Lambda_d^0.5 exp(- 0.5 (x_d - mu_d)^2 Lambda_d ), where
    mu = (..., mu_d, ...) is the mean array, and
    Lambda=(..., Lambda_d, ...) is the vector of precision values,
        = inverse variance
        = inverse diagonal of covariance matrix.

    To allow Bayesian learning, mu and Lambda are random variables, with
    p(mu, Lambda) = p(mu | Lambda) p(Lambda), where
    p(mu | Lambda) is implemented by a GaussGivenGammaV instance, and
    p(Lambda) is implemented by a PrecisionRV instance.
    """
    log_2_pi = np.log(2 * np.pi)  # class constant for mean_logpdf calc

    def __init__(self, mean=None, prec=None,
                 loc=None, scale=None, learned_weight=0.001):
        """
        # *** use separate cls.initialize constructor ? ****Ä
        :param mean: (optional) GaussianGivenPrecisionRV instance
        :param prec: (optional) PrecisionRV instance
        :param loc: (optional) location vector = mean of mean attribute
            required if mean is not specified
        :param scale: (optional) scale vector
            required if prec is not specified
            len(loc) == len(scale)
        :param learned_weight: (optional) scalar effective number of observations
            learned_weight = 0. gives a non-informative improper prior density
        """
        if loc is None:
            loc = [0.]
        if scale is None:
            scale = np.ones_like(loc)
        if prec is None:  # **********************
            self.prec = PrecisionRV(b=np.asarray(scale)**2 / 2,
                                    a=learned_weight / 2)
        else:
            self.prec = prec
        if mean is None:
            self.mean = GaussianGivenPrecisionRV(loc, learned_weight, self.prec)
        else:
            self.mean = mean
            self.mean.prec = self.prec

    def __repr__(self):
        property_sep = ',\n\t'
        return (self.__class__.__name__ + '(\n\t'
                + property_sep.join(f'{k}={repr(v)}'
                                    for (k, v) in vars(self).items())
                + ')')

    @property
    def loc(self):
        return self.mean.loc

    @property
    def size(self):
        return len(self.loc)

    @property
    def var(self):
        """Predictive variance = E{ |x - self.loc|^2 | self.mean, self.prec }
        with expectation across self, mean and prec.
        :returns: 1D array with elements
            v_d = int (x_d - m_d)^2 p(x_d | mu_d, Lambda_d) p(mu_d | Lambda_d) (Lambda_d) dx dmu dLambda
            where m = self.loc, mu=self.mean, Lambda=self.prec
        NOTE: this result is equal to cov of self.predictive Student distribution
        """
        return (1. + 1. / self.mean.learned_weight) * self.prec.mean_inv

    # @property
    # def cov(self):
    #     return np.diag(self.var)

    def mean_logpdf(self, x):
        """E{ ln pdf( x | self ) }, expectation across all parameters of self
        :param x: 1-dim OR M-dim array or array-like list of sample vectors assumed drawn from self
            x[..., :] = ...-th sample row vector
        :return: scalar or array LL, with
            LL[...] = E{ ln pdf( x[..., :] | self ) }
            LL.shape == x.shape[:-1]

        Arne Leijon, 2018-07-08, seems OK,
        slightly less than self.predictive.logpdf, as expected by Jensen's inequality
        """
        x = np.asarray(x)
        if self.mean.learned_weight <= 0.:
            return np.full(x.shape[:-1], -np.inf)
        z2 = np.dot((x - self.loc)**2, self.prec.mean)
        # = Mahanalobis distance, z2.shape == x.shape[:-1]
        return (- z2 - self.size / self.mean.learned_weight
                + np.sum(self.prec.mean_log) - self.size * self.log_2_pi  # np.log(2 * np.pi)
                ) / 2

    def grad_mean_logpdf(self, x):
        """First derivative of self.mean_logpdf(x) w.r.t x
        :param x: 1D OR 2D array or array-like list of sample vectors assumed drawn from self
            x[n, :] = n-th sample row vector
        :return: array dLL, with
            dLL[..., i] = d E{ ln pdf( x[..., :] | self ) / d x[..., i]
            dLL.shape == x.shape

        Arne Leijon, 2018-07-09
        """
        d = np.asarray(x) - self.loc
        return - d * self.prec.mean

    def relative_entropy(self, othr):
        """
        Kullback-Leibler divergence between self and othr
        :param othr: single instance of same class as self
        :return: scalar KLdiv(q || p) = E_q{ln q(x) / p(x)},
            where q = self and p = othr
        """
        return (self.mean.relative_entropy(othr.mean) +
                self.prec.relative_entropy(othr.prec))

    @property
    def predictive(self):
        """Predictive distribution of random vector, integrated over parameters.
        :return: rv = single StudentRV instance with independent elements

        Scalar Student pdf(x) propto (1 + (1/df) (x-m)^2 / scale^2 )^(- (df + 1) / 2)
        where scale = sqrt{ (1+beta) self.prec.inv_scale / (beta self.prec.shape)
        and Student df = 2* self.prec.shape
        See Leijon EmaCalc report Appendix, or JASA PairedComp paper appendix

        Arne Leijon, 2018-07-07
        """
        beta = self.mean.learned_weight
        return StudentRV(loc=self.loc,
                         scale=np.sqrt(self.prec.b * (1. + beta) / (beta * self.prec.a)),
                         df=2 * self.prec.a)

    def adapt(self, x, x_2, w, prior):  # *** special for EmaCalc, not general ***
        """Update distribution parameters using observed data and prior.
        :param x: 2D array with samples assumed drawn from self.
        :param x_2: 2D array with squared sample elements.
        :param w: 1D array with weights of observed samples
        :param prior: prior conjugate distribution, same class as self
        :return: - KLdiv{self || prior)

        Result: updated internal parameters of self
        Method: Leijon EmaCalc report Appendix: sec:GaussGammaUpdate
        """
        self.mean.adapt(x, w, prior=prior.mean)
        self.prec.adapt(x_2, w, prior=prior.prec,
                        new_mean_2=(self.mean.learned_weight * self.mean.loc**2 -
                                    prior.mean.learned_weight * prior.mean.loc**2))
        return - self.relative_entropy(prior)


# ----------------------------------------------------------------------
class GaussianGivenPrecisionRV:
    """Conditionally Gaussian distribution of the mean of a Gaussian random vector,
    given the precision array.
    The probability density function is
    p(mu | Lambda) propto prod_d (beta Lambda_d)^0.5 exp(- 0.5 (mu_d - m_d)^2 beta Lambda_d
    where
    mu is a row vector, sample of random vector self
    m is the location of self,
    beta is the learned_weight property
    Lambda is the precision vector (= diagonal of covariance matrix).
    """
    def __init__(self, loc, learned_weight, prec):
        """
        Conditional Gaussian vector, given precision matrix
        :param loc: location vector
        :param learned_weight: scalar effective number of learning data
        :param prec: single PrecisionRV instance
        2018-11-27, store loc as np.array
        """
        self.loc = np.asarray(loc)
        self.learned_weight = learned_weight
        self.prec = prec

    def __repr__(self):
        return ('GaussianGivenPrecisionRV(' +
                f'loc= {repr(self.loc)}, ' +
                f'learned_weight= {repr(self.learned_weight)}, ' +
                'prec= prec)')

    def adapt(self, x, w, prior):
        """
        Update distribution parameters using observed data and prior.
        :param x: 2D array or array-like list of sample vectors assumed drawn from self
        :param w: 1D array of weights
            len(w) == x.shape[0]
        :param prior: prior conjugate distribution, same class as self
        :return: None
        Result: updated internal parameters of self
        """
        self.learned_weight = prior.learned_weight + np.sum(w)
        sx = prior.learned_weight * prior.loc + np.dot(w, x)
        self.loc = sx / self.learned_weight

    def relative_entropy(self, othr):
        """
        Kullback-Leibler divergence between self and othr
        :param othr: single instance of same class as self
        :return: scalar KLdiv[q || p] = E_q{ln q(x) / p(x)}, where q = self and p = othr

        Arne Leijon, 2018-07-07
        """
        d = len(self.loc)
        md = self.loc - othr.loc
        beta_pq_ratio = othr.learned_weight / self.learned_weight
        return (othr.learned_weight * np.dot(md**2, self.prec.mean)
                + d * (beta_pq_ratio - np.log(beta_pq_ratio) - 1.)
                ) / 2

    @property
    def predictive(self):
        """Predictive distribution of self, integrated over self.prec
        p(mu) = int{ p(mu | prec) p(prec) d_prec, where
        p(prec) is represented by the WishartRV instance self.prec
        :return: rv = single StudentRV instance

        Method: see JASA PairedComp paper Appendix
        """
        beta = self.learned_weight
        return StudentRV(loc=self.loc,
                         scale=np.sqrt(self.prec.b / (self.prec.a * beta)),
                         df=2 * self.prec.a
                         )


# ---------------------------------------------------------------------------
class PrecisionRV:  # ********** might be subclass of scipy.stats.gamma ??? **********
    """Distribution of the precision vector Lambda of a Gaussian vector
    The probability density function is
    p(Lambda) = prod_d C_d Lambda_d^(a_d - 1) exp(- b_d Lambda_d), where
        a = scalar or 1D array of shape parameters,
        b = 1D array of inverse-scale parameters
        Lambda.shape == b.shape
        a and b must have broadcast-compatible shapes
        C_d = b_d^a_d / Gamma(a_d) is the normalization factor

    Arne Leijon, 2018-07-07
    """
    def __init__(self, a=0., b=1.):
        """
        :param a: scalar or 1D array or array-like list with shape parameters
        :param b: 1D array or array-like list with inverse scale parameters
        """
        self.a = np.array(a)
        self.b = np.array(b)

    def __repr__(self):
        return f'PrecisionRV(a= {repr(self.a)}, b= {repr(self.b)})'

    @property
    def size(self):
        return self.mean.size

    @property
    def scale(self):
        return 1./self.b

    @property
    def inv_scale(self):
        return self.b

    @property
    def mean(self):
        """E{self}"""
        return self.a / self.b

    @property
    def mean_inv(self):
        """E{ inv(self) }, where
        inv(self) has an inverse-gamma distribution
        """
        if np.all(self.a > 1):
            return self.b / (self.a - 1)
        else:
            return np.full_like(self.b, np.nan)  # OR raise error?

    @property
    def mean_log(self):
        """E{ ln self| } = 1D array"""
        return psi(self.a) - np.log(self.b)

    def logpdf(self, x):  # ******* not needed in Ema ?  ********
        """ln pdf(x | self)
        :param x: array or array-like list of 2D arrays
        :return: lp = scalar or array, with
            lp[...] = ln pdf(x[..., :] | self)
            lp.shape == x.shape[:-1]
        """
        bx = self.b * np.asarray(x)
        return np.sum((self.a - 1.) * np.log(bx) - bx
                      + np.log(self.b) - gammaln(self.a),
                      axis=-1)

    def adapt(self, x2, w, prior, new_mean_2):
        """Update distribution parameters using observed data and prior.
        :param x2: 2D array or array-like list of squared samples
            for vectors assumed drawn from distribution with precision == self.
        :param w: 1D array with sample weights
        :param prior: prior conjugate distribution, same class as self
        :param new_mean_2: weighted difference (nu * new_loc^2 - nu' * prior_loc^2)
            where nu is the new and prior sum-weight
        :return: None
        Result: updated internal parameters of self
        Method: Leijon EmaCalc report: sec:GaussGammaUpdate
        """
        self.a = prior.a + np.sum(w) / 2
        # eq:GammaUpdateA
        self.b = prior.b + (np.dot(w, x2) - new_mean_2) / 2
        # eq:GammaUpdateB

    def relative_entropy(q, p):
        """Kullback-Leibler divergence between PrecisionRV q and p,
        KLdiv( q || p ) = E{ ln q(x)/p(x) }_q

        Arne Leijon, 2018-07-07 copied from gamma.py 2015-10-16
        """
        pb_div_qb = p.b / q.b
        return np.sum(gammaln(p.a) - gammaln(q.a)
                      - p.a * np.log(pb_div_qb)
                      + (q.a - p.a) * psi(q.a)
                      - q.a * (1. - pb_div_qb)
                      )


class StudentRV:  # ***** might be subclass of scipy.stats.t ???
    """Frozen Student distribution of 1D random vector with INDEPENDENT elements
    generalizing scipy.stats.t for vector-valued random variable
    """
    def __init__(self, df, loc=np.array(0.), scale=1.):
        """Create a StudentRV instance
        :param df: scalar degrees of freedom, SAME for all vector elements
        :param loc: 1D array or array-like list of location elements
        :param scale: scalar or 1D array or array-like list of scale parameter(s)
            loc and scale must have broadcast-compatible shapes
        """
        self.df = df
        self.loc = np.asarray(loc)
        self.scale = np.asarray(scale)

    def __repr__(self):
        return f'StudentRV(df= {repr(self.df)}, loc= {repr(self.loc)}, scale= {repr(self.scale)})'

    @property
    def size(self):
        return len(self.loc)

    @property
    def mean(self):
        if self.df > 1:
            return self.loc
        else:
            return np.full_like(self.loc, np.nan)

    @property
    def var(self):
        """Variance array"""
        if self.df > 2:
            return self.scale**2 * self.df / (self.df - 2)
        elif self.df > 1:
            return np.full_like(self.loc, np.inf)
        else:
            return np.full_like(self.loc, np.nan)

    def logpdf(self, x):
        """
        ln pdf(x | self)
        :param x: array or array-like list of sample vectors
        :return: lp = scalar or array of logpdf values
            lp[...] = ln pdf[x[..., :] | self)
            lp.shape == x.shape[:-1]
        Arne Leijon, 2018-07-08, **** checked by comparison to scipy.stats.t
        """
        d = (x - self.loc) / self.scale
        return np.sum(- np.log1p(d**2 / self.df) * (self.df + 1) / 2
                      - np.log(self.scale)
                      + gammaln((self.df + 1) / 2) - gammaln(self.df / 2)
                      - 0.5 * np.log(np.pi * self.df),
                      axis=-1)

    def rvs(self, size=1):
        """Random vectors drawn from self.
        :param size: scalar or sequence with number of sample vectors
        :return: x = array of samples
            x.shape == (*size, self.size)

        Method: use scipy.stats.t.rvs  ****** use numpy.default_rng() ? ***********
        """
        if np.isscalar(size):
            s = (size, self.size)
        else:
            s = (*size, self.size)
        z = scipy_t.rvs(df=self.df, size=s)
        # = standardized samples
        return self.loc + self.scale * z


# ------------------------------------------------ Help functions

# def multi_psi(a, d):
#     """Multivariate psi function
#     = first derivative of scipy.special.multigammaln
#     = sum( psi( a + (1-j)/2) for j = 1,...,d (Wikipedia)
#     = sum( psi( a - (j-1)/2) for j = 1,...,d
#     """
#     return sum(psi(a - j/2) for j in range(d))
#


# ------------------------------------------------- TEST
if __name__ == '__main__':
    from scipy.stats import norm
    from scipy.stats import gamma
    import copy

    # --------------------------- Test PrecisionRV
    a = 10.
    b = [1., 2., 3.]
    nx = 10

    g = PrecisionRV(a=a, b=b)
    print(f'\n*** Testing {g}:')
    x = np.array([gamma(a=a, scale=1/b_i).rvs(size=nx)
                  for b_i in b]).T
    print(f'gamma samples x= {x}')
    print(f'mean(x)= {np.mean(x, axis=0)}')
    print(f'PrecisionRV.logpdf(x)= {g.logpdf(x)}')
    g_ll = np.array([np.sum([gamma(a=a, scale=1/b_i).logpdf(x_si)
                             for (b_i, x_si) in zip(b, x_s)])
                     for x_s in x])
    print(f'scipy gamma.logpdf(x)= {g_ll}')

    # --------------------------- Test StudentRV
    df = 10.
    m = [1., 2., 3.]
    s = [3., 2., 1.]
    st = StudentRV(df=df, loc=m, scale=s)
    print(f'\n*** Testing {st}')
    scipy_x = np.array([scipy_t.rvs(df=df, loc=m_i, scale=s_i, size=nx)
                        for (m_i, s_i) in zip(m, s)]).T
    print(f'scipy_t samples x= {scipy_x}')
    print(f'mean(x)= {np.mean(scipy_x, axis=0)}')
    x = st.rvs(size=[nx])
    print(f'StudentRV samples x= {x}')
    print(f'mean(x)= {np.mean(x, axis=0)}')
    print(f'StudentRV.logpdf(x)= {st.logpdf(x)}')
    st_ll = np.array([np.sum([scipy_t(df=df, loc=m_i, scale=s_i).logpdf(x_si)
                             for (m_i, s_i, x_si) in zip(m, s, x_s)])
                     for x_s in x])
    print(f'scipy_t.logpdf(x)= {st_ll}')

    # --------------------------- Test GaussianRV
    g = GaussianRV(loc=[0., 1., 2.], scale=[1., 2., 3.], learned_weight=2.01)
    print(f'\n*** Testing {g}')
    print(f'g.var = \n{g.var}')
    # print(f'g.cov = \n{g.cov}')
    print(f'g.predictive.var = \n{g.predictive.var}')

    #     print('\n*** Learn GaussianRV from data:')
    #
    # # generative distribution:
    # d = 3
    # mu = np.array([1., 2., 3.])
    # sd_within = np.array([3., 2., 1.])
    # sd_between = 3.
    #
    # nx = 10  # number of independent "subjects"
    # n_within = 100  # number of samples per subject
    # y = sd_between * np.ones(d) * norm.rvs(size=(nx, 1, 1))
    # x = mu + y + sd_within * norm.rvs(size=(nx, n_within, d))
    # # theoretical mean(x) == mu; cov(x) = sd_between * ones((d,d)) + diag(sd_within)
    # cov_within = np.diag(sd_within**2)
    # cov_between = np.ones((d, d)) * sd_between**2
    # cov_total = cov_between + cov_within
    # print('mean_within = ', mu + y)
    # print('mean_total = ', mu)
    # print('cov_within =\n', cov_within)
    # print('cov_between =\n', cov_between)
    # print('cov_total =\n', cov_total)
    #
    # x_mean_total = np.mean(x, axis=(0, 1))
    # print(f'x_mean_total = {x_mean_total}')
    # x_mean_within = np.mean(x, axis=1, keepdims=True)
    # print('x_mean_within = \n', x_mean_within)
    #
    # dx = x - x_mean_within
    # x_cov_within = np.einsum('nmi, nmj', dx, dx) / (nx * n_within)
    # print('x_cov_within:\n', x_cov_within)
    #
    # dx = x - x_mean_total
    # x_cov_total = np.einsum('nmi, nmj', dx, dx) / (nx * n_within)
    # print('x_cov_total:\n', x_cov_total)
    #
    # gw0 = GaussianRV(loc=np.zeros(d), scale=np.ones(d), learned_weight=0.1)
    # print('Prior GaussianRV:')
    # print(gw0)
    #
    # gw = copy.deepcopy(gw0)
    # gw.adapt(x, gw0)
    # print('\nLearned GaussianRV:')
    # print(gw)
    # print('prec.mean:', gw.prec.mean)
    # print('learned var:', gw.var)
    #
    # print('\nLearned ind.predictive distr:')
    # gw_pred = gw.predictive
    # print(gw_pred)
    # print(f'pred. var= {gw_pred.var}')
    # print(f'pred. std.d= {np.sqrt(gw_pred.var)}')
    # print('\nLearned mean.predictive distr:')
    # print(gw.mean.predictive)
    #
    # print('KLdiv(g_pop.mean || g_pop.mean) = ', gw.mean.relative_entropy(gw.mean))
    # print('KLdiv(g_pop.mean || gw0.mean) = ', gw.mean.relative_entropy(gw0.mean))
    # print('KLdiv(g_pop.prec || g_pop.prec) = ', gw.prec.relative_entropy(gw.prec))
    # print('KLdiv(g_pop.prec || gw0.prec) = ', gw.prec.relative_entropy(gw0.prec))
    # print('KLdiv(gw0.prec || g_pop.prec) = ', gw0.prec.relative_entropy(gw.prec))
    # print('KLdiv(gw0 || gw0) = ', gw0.relative_entropy(gw0))
    # print('KLdiv(g_pop || g_pop) = ', gw.relative_entropy(gw))
    # print('KLdiv(g_pop || gw0) = ', gw.relative_entropy(gw0))
    # print('KLdiv(gw0 || g_pop) = ', gw0.relative_entropy(gw))
    #
    # # print('mean_logpdf(x)')
    # # print(g_pop.mean_logpdf(x))
    # #
    # # print('predictive log pdf(x)')
    # # print(g_pop.predictive.logpdf(x))
    #
    # print('\nmean_logpdf(x[:, 0, :])')
    # print(gw.mean_logpdf(x[:, 0, :]))
    #
    # print('\npredictive log pdf(x[:, 0, :])')
    # print(gw.predictive.logpdf(x[:, 0, :]))
