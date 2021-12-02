"""Help classes for distribution of latent sensory variable
used in EmaCalc.EmaModel

* Version history:
2021-10-29, copied from PairedCompCalc.pc_model, slightly modified for EmaCalc
2021-11-10, moodified Bradley variant for EMA model
2021-11-21, tested Bradley, Thurstone variants for EMA model
"""
import numpy as np
from scipy.special import expit, ndtr

RNG = np.random.default_rng()
# = default module-global random generator


# ------------------------------------------------------------------
class Bradley:
    """Distribution of latent ordinal-decision variable in the Bradley-Terry-Luce model,
    with distribution function = standard logistic
    cdf(x) = 1 / (1 + exp(-x)) = expit(x)
    """
    unit_label = 'BTL unit'
    # for axis label in quality plots
    scale = np.pi / np.sqrt(3.)
    # = st.dev. of standard logistic distribution
    # may be used to standardize result scale in displays

    @staticmethod
    def log_cdf_diff(a, b):
        """log prob( a < Z <= b)
        where Z is a standard logistic random variable
        :param a: = array with LOWER interval limits
        :param b: = arrays with UPPER interval limits
            a.shape == b.shape
            all( a < b )
        :return: log_p = array with log probabilities, element-wise
            log_p.shape == a.shape == b.shape
        """
        return np.log(expit(b) - expit(a))

    @staticmethod
    def d_log_cdf_diff(a, b):
        """Element-wise partial derivatives of log_cdf_diff(a, b)
        :param a: = array with LOWER interval limits
        :param b: = arrays with UPPER interval limits
            a.shape == b.shape
            all( a < b )
        :return: tuple (dll_da, dll_db) of arrays, where
            dll_da[...] = d log_cdf_diff(a[...], b[...]) / d a[...]
            dll_db[...] = d log_cdf_diff(a[...], b[...]) / d b[...]
            dll_da.shape == dll_db.shape == a.shape == b.shape
        2017-12-08, tested by finite-diff comparison
        """
        return (1. / np.expm1(a - b) + expit(-a),
                1. / np.expm1(b - a) + expit(-b))

    def __repr__(self):
        return f'<class {self.__class__.__name__}>'

    @staticmethod
    def rvs(loc, size=None):
        """Draw random variables from self
        :param loc: scalar or array-like location
        :param size: (optional) size of result
        :return: x = scalar or array
            x.shape == loc.shape
        """
        return RNG.logistic(loc, size=size)


class Thurstone:
    """Distribution of decision variable in the Thurstone Case V model.
    with distribution function
    cdf(x) = Phi(x / sqrt(pi))
    NOTE: Thurstone.scale is now included in all calculations.
    This is different from corresponding MatLab code.
    """
    unit_label = 'd-prime unit'

    sqrt_2pi = np.sqrt(2. * np.pi)
    scale = 1.

    @classmethod
    def cdf_diff(cls, a, b):  # *********** check scale factor
        """prob( a < Z <= b)
        where Z is a Gaussian standard random variable with variance = 2.
        :param a: = array with LOWER interval limits
        :param b: = arrays with UPPER interval limits
            a.shape == b.shape
            all( a < b )
        :return: log_p = array with log probabilities, element-wise
            log_p.shape == a.shape == b.shape
        2018-04-24, include Thurstone.scale factor
        """
        a_s = a / cls.scale
        b_s = b / cls.scale
        cdf_diff = ndtr(b_s) - ndtr(a_s)
        ch_sign = a_s >= 0.  # and (b > a) always
        cdf_diff[ch_sign] = ndtr(-a_s[ch_sign]) - ndtr(-b_s[ch_sign])
        # better precision of difference in case of large positive a, b
        return cdf_diff

    @classmethod
    def log_cdf_diff(cls, a, b):
        """log cdf_diff(a, b)
        :param a: = array with LOWER interval limits
        :param b: = arrays with UPPER interval limits
            a.shape == b.shape
            all( a < b )
        :return: log_p = array with log probabilities, element-wise
            log_p.shape == a.shape == b.shape
        """
        return np.log(cls.cdf_diff(a, b))

    @classmethod
    def d_log_cdf_diff(cls, a, b):
        """Element-wise partial derivatives of log_cdf_diff(a, b)
        :param a: = array with LOWER interval limits
        :param b: = arrays with UPPER interval limits
            a.shape == b.shape
            all( a < b )
        :return: tuple (dll_da, dll_db), where
            dll_da[...] = d log_cdf_diff[a[...], b[...]) / d a[...]
            dll_db[...] = d log_cdf_diff[a[...], b[...]) / d b[...]
            dll_da.shape == dll_db.shape == a.shape == b.shape
        Arne Leijon, 2017-12-08, tested by finite-diff comparison
        2018-04-24, include Thurstone.scale factor
        """
        # *** scale may be omitted == 1. anyway
        def norm_pdf(x):
            """Gaussian density function = derivative of ndtr(x / scale)
            """
            return np.exp(- (x / cls.scale)**2 / 2) / cls.sqrt_2pi / cls.scale
        # ----------------------------------------------------
        cdf_diff = cls.cdf_diff(a, b)
        return - norm_pdf(a) / cdf_diff, norm_pdf(b) / cdf_diff

    def __repr__(self):
        return f'<class {self.__class__.__name__}>'

    @staticmethod
    def rvs(loc, size=None):
        """Draw random variables from self
        :param loc: scalar or array-like location
        :param size: (optional) size of result
        :return: x = scalar or array
            x.shape == loc.shape, if no size is given
        """
        loc = np.asarray(loc)
        if size is None:
            size = loc.shape
        return loc + RNG.standard_normal(size=size)


# ------------------------------------------------- TEST:
if __name__ == '__main__':
    from scipy.optimize import approx_fprime, check_grad

    print('*** Testing Bradley and Thurstone gradients')

    # --------------------------------------------------
    for cls in (Bradley, Thurstone):

        print(f'\nTesting {cls}.d_log_cdf_diff() with 1D (a, b) args')
        tau = np.array([0., 2.])
        th = np.array([1.5])
        (a, b) = (tau[0] - th, tau[1] - th)

        def fun_a(da):
            return cls.log_cdf_diff(a + da, b)

        def jac_a(da):
            return cls.d_log_cdf_diff(a + da, b)[0]


        def fun_b(db):
            return cls.log_cdf_diff(a, b + db)

        def jac_b(db):
            return cls.d_log_cdf_diff(a, b + db)[1]

        d = np.array([0.1])
        print(f'a ={a}. b = {b}. d = {d}')
        print(f'{cls}.fun_a_b({d}) = {(fun_a(d), fun_b(d))}')

        print('approx d_log_cdf_diff_da = ', approx_fprime(d, fun_a, epsilon=1e-6))
        print('exact  d_log_cdf_diff_da = ', jac_a(d))
        err = check_grad(fun_a, jac_a, d, epsilon=1e-6)
        print('check_grad err = ', err)

        print('')
        print('approx d_log_cdf_diff_db = ', approx_fprime(d, fun_b, epsilon=1e-6))
        print('exact  d_log_cdf_diff_db = ', jac_b(d))
        err = check_grad(fun_b, jac_b, d, epsilon=1e-6)
        print('check_grad err = ', err)
