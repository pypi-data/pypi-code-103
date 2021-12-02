import os
import re
import sys
import fnmatch
from functools import lru_cache

import numpy as np

import scipy.interpolate
import scipy.stats as stats
from scipy.integrate import trapz as trapezoid

import matplotlib.pyplot as plt

import astropy.stats as astats

import GPy
import paramz

import emcee
import corner

import joblib
import progressbar

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from sklearn.decomposition import PCA

from libpipe import settings

from . import psutil, datacube, pspec, fgfit


CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')


class BetaVAE(nn.Module):
    ''' Base on https://github.com/AntixK/PyTorch-VAE/blob/master/models/beta_vae.py'''

    num_iter = 0

    def __init__(self, in_dim, latent_dim, hidden_dims=[20, 20, 20], beta=1, warmup_iters=100, warmup_gamma=0.001, loss_type='H', **kwargs):
        super(BetaVAE, self).__init__()

        self.latent_dim = latent_dim
        self.beta = beta
        self.warmup_iters = warmup_iters
        self.warmup_gamma = warmup_gamma
        self.loss_type = loss_type

        modules = []

        # Build Encoder
        for i_d, o_d in zip([in_dim] + hidden_dims[:-1], hidden_dims):
            modules.append(
                nn.Sequential(
                    nn.Linear(i_d, o_d),
                    nn.LeakyReLU(),
                    nn.BatchNorm1d(o_d),
                )
            )

        self.encoder = nn.Sequential(*modules)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_var = nn.Linear(hidden_dims[-1], latent_dim)

        # Build Decoder
        modules = []

        self.decoder_input = nn.Linear(latent_dim, hidden_dims[-1])

        hidden_dims.reverse()

        for i in range(len(hidden_dims) - 1):
            modules.append(
                nn.Sequential(
                    nn.Linear(hidden_dims[i], hidden_dims[i + 1]),
                    nn.LeakyReLU(),
                )
            )

        modules.append(nn.Sequential(nn.Linear(hidden_dims[-1], in_dim), nn.Sigmoid()))

        self.decoder = nn.Sequential(*modules)
        self.iter_changed = False

    def encode(self, input):
        """
        Encodes the input by passing through the encoder network
        and returns the latent codes.
        :param input: (Tensor) Input tensor to encoder [N x C x H x W]
        :return: (Tensor) List of latent codes
        """
        result = self.encoder(input)

        # Split the result into mu and var components
        # of the latent Gaussian distribution
        mu = self.fc_mu(result)
        log_var = self.fc_var(result)

        return [mu, log_var]

    def decode(self, z):
        result = self.decoder_input(z)
        result = self.decoder(result)
        return result

    def reparameterize(self, mu, logvar):
        """
        :param mu: (Tensor) Mean of the latent Gaussian
        :param logvar: (Tensor) Standard deviation of the latent Gaussian
        :return:
        """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return eps * std + mu

    def forward(self, input, **kwargs):
        mu, log_var = self.encode(input)
        z = self.reparameterize(mu, log_var)
        return  [self.decode(z), input, mu, log_var]

    def step(self):
        self.num_iter += 1
        self.iter_changed = True

    def loss_function(self, *args, **kwargs):
        recons = args[0]
        input = args[1]
        mu = args[2]
        log_var = args[3]
        n = recons.shape[0]

        recons_loss = n * torch.nn.functional.mse_loss(recons, input)
        kld_loss = n * torch.mean(-0.5 * torch.sum(1 + log_var - mu ** 2 - log_var.exp(), dim = 1), dim = 0)

        if self.loss_type == 'H': # https://openreview.net/forum?id=Sy2fzU9gl
            loss = recons_loss + self.beta * kld_loss
        elif self.loss_type == 'W':
            beta = self.beta
            if self.num_iter < self.warmup_iters:
                beta = self.beta * (self.warmup_gamma + (1 - self.warmup_gamma) * self.num_iter / self.warmup_iters)
            loss = recons_loss + beta * kld_loss
        else:
            raise ValueError('Undefined loss type.')
        self.iter_changed = False

        return loss, recons_loss, kld_loss

    def generate(self, x, **kwargs):
        """
        Given an input image x, returns the reconstructed image
        :param x: (Tensor) [B x C x H x W]
        :return: (Tensor) [B x C x H x W]
        """

        return self.forward(x)[0]

    def generate_m(self, x):
        mu, log_var = self.encode(x)
        return self.decode(mu)


class AbstractFitter(object):

    def __init__(self, n_dim, k_mean):
        self.n_dim = n_dim
        self.k_mean = k_mean

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def reconstruct(self, data):
        raise NotImplementedError()

    def save(self, filename):
        joblib.dump(self, filename)
        
    @staticmethod
    @lru_cache(maxsize=10)
    def _cache_load(filename, mtime):
        return joblib.load(filename)

    @staticmethod
    def load(filename):
        sys.modules['ml_gpr'] = sys.modules[__name__]
        return AbstractFitter._cache_load(filename, os.stat(filename).st_mtime)


class VAEFitter(AbstractFitter):

    def __init__(self, model, optimizer, k_mean):
        self.model = model
        self.optimizer = optimizer
        self.loss = []
        self.val_loss = []
        self.all_rec_loss = []
        AbstractFitter.__init__(self, model.latent_dim, k_mean)

    def fit(self, dataloader):
        self.model.train()
        # total loss, reconstruction loss, KL loss
        running_loss = np.array([0., 0., 0.])
        for data in dataloader:
            self.optimizer.zero_grad()
            reconstruction, inp, mu, logvar = self.model.forward(data)
            loss, recons_loss, kld_loss = self.model.loss_function(reconstruction, inp, mu, logvar)
            running_loss += np.array([loss.data, recons_loss.data, kld_loss.data])
            self.all_rec_loss.append(recons_loss.data)
            loss.backward()
            self.optimizer.step()
        train_loss = running_loss / len(dataloader.dataset)
        return train_loss

    def validate(self, dataloader):
        self.model.eval()
        # total loss, reconstruction loss, KL loss
        running_loss = np.array([0., 0., 0.])
        with torch.no_grad():
            for data in dataloader:
                reconstruction, inp, mu, logvar = self.model.forward(data)
                loss, recons_loss, kld_loss = self.model.loss_function(reconstruction, inp, mu, logvar, M_N=1)
                running_loss += np.array([loss.data, recons_loss.data, kld_loss.data])
        val_loss = running_loss / len(dataloader.dataset)
        return val_loss

    def train(self, epochs, train_loader, val_loader):
        widgets = [
            "VAE Fitter ", progressbar.Percentage(), ' (',
            progressbar.SimpleProgress(), ')'
            ' ', progressbar.Bar(marker='|', left='[', right=']'),
            ' ', progressbar.ETA(),
            ' ', progressbar.DynamicMessage('Loss')
        ]
        with progressbar.ProgressBar(max_value=epochs, widgets=widgets, redirect_stdout=True) as bar:
            current_loss = np.nan
            for i in range(epochs):
                self.loss.append(self.fit(train_loader))
                self.val_loss.append(self.validate(val_loader))
                if i % 10 == 0:
                    current_loss = self.loss[-1][0]
                bar.update(i, Loss=current_loss)
                self.model.step()
        self.model.eval()

    def ensure_tensor(self, data):
        if not torch.is_tensor(data):
            return torch.DoubleTensor(data)
        return data

    def ensure_np(self, data):
        if torch.is_tensor(data):
            return data.data.numpy()
        return data

    def encode(self, data):
        return self.ensure_np(self.model.reparameterize(*self.model.encode(self.ensure_tensor(data))))

    def decode(self, latent_data):
        return self.ensure_np(self.model.decode(self.ensure_tensor(latent_data)))

    def reconstruct(self, data):
        return self.ensure_np(self.model.generate_m(self.ensure_tensor(data)))


class PCAFitter(AbstractFitter):

    def __init__(self, n_cmpt, k_mean):
        self.pca = PCA(n_components=n_cmpt)
        self.y_min = [0, 0]
        self.y_max = [0, 0]
        AbstractFitter.__init__(self, n_cmpt, k_mean)

    def train(self, train_set):
        Y = self.pca.fit_transform(train_set)
        self.y_min = Y.min(axis=0)
        self.y_max = Y.max(axis=0)

    def encode(self, data):
        return self.pca.transform(data)

    def decode(self, latent_data):
        return self.pca.inverse_transform(latent_data)

    def reconstruct(self, data):
        return self.pca.inverse_transform(self.pca.transform(data))


class FitterResult(AbstractFitter):

    def __init__(self, fitter, train_data, test_data):
        self.fitter = fitter
        if isinstance(train_data, DataLoader):
            train_data = train_data.dataset
        if isinstance(test_data, DataLoader):
            test_data = test_data.dataset
        self.train_data = train_data
        self.test_data = test_data

    def plot_loss(self):
        if not hasattr(self.fitter, 'loss'):
            return None

        fig, ax = plt.subplots()
        ax.plot(np.array(self.fitter.loss)[:, 1], label='reconstruction loss')
        ax.plot(np.array(self.fitter.val_loss)[:, 1], label='reconstruction loss (val)')
        ax.plot(np.array(self.fitter.loss)[:, 2] * self.fitter.model.beta, label='KL loss')
        ax.set_yscale('log')
        ax.set_xlabel('Epochs')
        ax.set_ylabel('Loss')
        ax.legend()

        return fig

    def plot_latent_qq(self):
        fig, ax = plt.subplots()
        for data, data_label in zip([self.train_data, self.test_data], ['training', 'validation']):
            latent_params = self.fitter.encode(data).T

            ((osm, osr), _) = stats.probplot(latent_params[0], dist="norm")
            ax.scatter(osm, osr, s=10, label=f'Dim 0 ({data_label})')

            ((osm, osr), _) = stats.probplot(latent_params[1], dist="norm")
            ax.scatter(osm, osr, s=10, label=f'Dim 1 ({data_label})')

        ax.set_xlabel('Theoretical Quantile')
        ax.set_ylabel('Observed Quantile')
        ax.plot(osm, osm, c=psutil.red, lw=2)
        ax.legend()

        return fig

    def get_reco_ratio_train(self):
        rec = self.fitter.reconstruct(self.train_data)
        return (rec / self.train_data)

    def get_reco_ratio_val(self):
        rec = self.fitter.reconstruct(self.test_data)
        return (rec / self.test_data)

    def plot_ratio(self):
        fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(9, 3), sharey=True)
        ratio_train = self.get_reco_ratio_train()
        ratio_val = self.get_reco_ratio_val()

        ax1.boxplot(ratio_train, sym='')
        ax2.boxplot(ratio_val, sym='')

        med, rms = np.median(ratio_train), ratio_train.std()
        ax1.text(0.05, 0.97, f'Training set:median:{med:.3f} rms:{rms:.3f}', 
                 transform=ax1.transAxes, va='top', ha='left')

        med, rms = np.median(ratio_val), ratio_val.std()
        ax2.text(0.05, 0.97, f'Validation set:median:{med:.3f} rms:{rms:.3f}', 
                 transform=ax2.transAxes, va='top', ha='left')

        fig.tight_layout()

        return fig


def make_new_vis_cube(res, n_pix, freqs, umin, umax, kern=None, K=None, uv_bins_du=None):
    ''' Make a datacube.CartDataCube object with data generated 
        from the frequency-frequency covariance kern.

        Either a GPy Kern object (kern) or a frequency-frequency covariance (K) can be given.

        In case of multi baselines kernels (MultiKern), you can either set
        the uv bins steps (uv_bins_du) or if the covariance is defined by a MultiKern, 
        you can set the uv bins with kern.set_uv_bins(...) before calling this function.'''
    uu, vv, _ = psutil.get_ungrid_vis_idx((n_pix, n_pix), res, umin, umax)

    meta = datacube.ImageMetaData.from_res(res, (n_pix, n_pix))
    meta.wcs.wcs.cdelt[2] = np.diff(freqs).mean()

    c = datacube.CartDataCube(np.zeros((len(freqs), len(uu)), dtype=np.complex128), uu, vv, freqs, meta)

    return make_new_from_cube(c, kern=kern, K=K, uv_bins_du=uv_bins_du)


def make_new_from_cube(i_cube, kern=None, K=None, uv_bins_du=None):
    ''' Make a datacube.CartDataCube object using a template from an other datacube
        and with data generated from the GPy kern object or the frequency-frequency covariance (K).

        In case of multi baselines kernels (MultiKern), you can either set
        the uv bin width (uv_bins_du) or if the covariance is defined by a MultiKern, 
        you can set the uv bins with kern.set_uv_bins(...) before calling this function.'''
    c = i_cube.new_with_data(np.zeros_like(i_cube.data))

    assert (kern is None) ^ (K is None), 'both kern and K should not be set'

    uv_bins = None
    fmhz = c.freqs * 1e-6
    if uv_bins_du is not None:
        uv_bins = get_uv_bins(c.ru.min(), c.ru.max(), uv_bins_du)

    if kern is not None:
        if hasattr(kern, 'uv_bins'):
            if (uv_bins_du is not None):
                kern.set_uv_bins(uv_bins)
            uv_bins = kern.uv_bins
        K = kern.K(fmhz[:, None])

    if K is not None:
        if uv_bins is None:
            c.data = get_samples(fmhz, len(c.ru), K)
        else:
            for (umin, umax), Ki in zip(uv_bins, K):
                idx = (c.ru >= umin) & (c.ru <= umax)
                c.data[:, idx] = get_samples(fmhz, np.sum(idx), Ki)

    return c


def get_uv_bins(umin, umax, du):
    '''Return uv bins from umin to umax with a bin width of du'''
    return psutil.pairwise(np.arange(umin, umax + du, du))


def get_samples(X, n, K, complex_type=True, nearest_pd=True, method='cholesky'):
    '''Return n samples from the freq-freq covariance K'''
    if nearest_pd and not is_positive_definite(K):
        K = nearest_postive_definite(K)
    rg = np.random.default_rng()
    d = rg.multivariate_normal(np.zeros_like(X).squeeze(), K, n, method=method).T
    if complex_type:
        d = d + 1j * np.random.multivariate_normal(np.zeros_like(X).squeeze(), K, n).T
    return d


def get_multi_samples(X, ns, Ks):
    '''Return ns samples from the freq-freq multi-baselines covariance Ks'''
    return [get_samples(X, n, K) for n, K in zip(ns, Ks)]


def nearest_postive_definite(A, maxtries=10):
    """Find the nearest positive-definite matrix to input

    A Python/Numpy port of John D'Errico's `nearestSPD` MATLAB code [1], which
    credits [2].

    [1] https://www.mathworks.com/matlabcentral/fileexchange/42885-nearestspd

    [2] N.J. Higham, "Computing a nearest symmetric positive semidefinite
    matrix" (1988): https://doi.org/10.1016/0024-3795(88)90223-6
    """
    B = (A + A.T) / 2
    _, s, V = np.linalg.svd(B)

    H = np.dot(V.T, np.dot(np.diag(s), V))

    A2 = (B + H) / 2

    A3 = (A2 + A2.T) / 2

    if is_positive_definite(A3):
        return A3

    spacing = np.spacing(np.linalg.norm(A))
    I = np.eye(A.shape[0])
    k = 1
    while not is_positive_definite(A3):
        mineig = np.min(np.real(np.linalg.eigvals(A3)))
        A3 += I * (-mineig * k**2 + spacing)
        k += 1
        if k > maxtries:
            break

    return A3


def is_positive_definite(B):
    """Returns true when input is positive-definite, via Cholesky"""
    try:
        _ = GPy.util.linalg.jitchol(B, 0)
        return True
    except np.linalg.LinAlgError:
        return False


def c_nu_from_ps21_fct(ps3d_fct, freqs, uv_bins, delta_kpar=0.05, normalize=True):
    ''' Return frequency-frequency covariance for the given baselines bins and frequency 
        given the spherically averaged power-spectra P(k) (and not delta(k)). 
        Assume isotropie of the signal, which is true to some extend for the 21-cm signal.

        See https://arxiv.org/abs/astro-ph/0605546'''
    z = psutil.freq_to_z(freqs.mean())

    uu = np.array(uv_bins).mean(axis=1)
    k_per = psutil.l_to_k(2 * np.pi * uu, z)

    r = psutil.angular_to_comoving_distance(psutil.freq_to_z(freqs))
    delta_r = abs(r - r[0])

    d_delta_r = np.diff(delta_r).mean()
    k_par = 2 * np.pi * np.fft.fftshift(np.fft.fftfreq(len(r), d_delta_r))
    k_par = k_par[k_par >= 0]

    k_pers, k_pars = np.meshgrid(k_per, k_par)
    ks = np.sqrt(k_pers ** 2 + k_pars ** 2)
    
    y = ps3d_fct(ks)[:, :, None] * np.cos(delta_r[None, None, :] * k_par[:, None, None])

    c_nu_nu = np.abs(trapezoid(y, k_par, axis=0))
    c_nu_nu[:, len(delta_r) // 2:] = 0

    if normalize:
        c_nu_nu = c_nu_nu / c_nu_nu.max()

    return c_nu_nu


def c_nu_from_ps21(k_mean, ps3d, freqs, uv_bins, delta_kpar=0.05, normalize=True):
    '''Return frequency-frequency covariance for the given baselines bins and frequency 
       given the spherically averaged power-spectra delta(k) (and not P(k)).
       Assume isotropic of the signal, which is true to some extend for the 21-cm signal.

       See https://arxiv.org/abs/astro-ph/0605546'''
    def ps_fct(k): return 1 / k ** 3 * scipy.interpolate.interp1d(k_mean, ps3d,
                                                                  bounds_error=False,
                                                                  kind='quadratic',
                                                                  fill_value='extrapolate')(k)

    return np.clip(c_nu_from_ps21_fct(ps_fct, freqs, uv_bins, delta_kpar=delta_kpar,
                                      normalize=normalize), 1e-20, 1e20)


def c_nu_to_K(freqs, c_nu_nu):
    ''' return a covariance matrix K from freq-freq covariance c_nu_nu'''
    X = (freqs * 1e-6)[:, None]
    dnu_mhz = np.diff(X.squeeze()).mean()
    r_1d = dnu_mhz * np.arange(c_nu_nu.shape[1])

    Xsq = np.sum(np.square(X), 1)
    r2 = -2. * np.dot(X, X.T) + (Xsq[:, None] + Xsq[None, :])
    r2[np.diag_indices(X.shape[0])] = 0.
    r2 = np.clip(r2, 0, np.inf)
    r = np.sqrt(r2)

    return scipy.interpolate.interp1d(r_1d, c_nu_nu, kind='quadratic', axis=1,
                                      bounds_error=False, fill_value=0)(r)


def make_new_vis_cube_from_ps(k_mean, ps3d, res, n_pix, freqs, umin, umax, uv_bins_du=15):
    ''' Make a datacube.CartDataCube object with given power-spectra ((delta(k))).

        See also c_nu_from_ps21() and make_new_vis_cube() '''
    uv_bins = get_uv_bins(umin, umax, uv_bins_du)
    c_nu_nu = c_nu_from_ps21(k_mean, ps3d, freqs, uv_bins, delta_kpar=0.025, normalize=False)
    K = c_nu_to_K(freqs, c_nu_nu)

    z = psutil.freq_to_z(freqs.mean())
    r_z = psutil.cosmo.comoving_distance(z).value / psutil.cosmo.h
    norm = 0.16 / (res * n_pix) ** 4 * 1 / (np.pi * r_z ** 2)
    K = norm * K

    return make_new_vis_cube(res, n_pix, freqs, umin, umax, K=K, uv_bins_du=uv_bins_du)


class MultiKern(object):
    ''' Multi Baseline Kernel. '''

    def __init__(self, *args, **kargs):
        self.uv_bins = [[0, 1e4]]

    def set_uv_bins(self, uv_bins):
        ''' Set the uv bins for this kernel. '''
        self.uv_bins = uv_bins
        self.parameters_changed()

    def add(self, other, name='sum'):
        assert isinstance(other, MultiKern), "only kernels can be added to kernels..."
        return MultiAdd([self, other], name=name)

    def copy_params(self, other):
        [self.unlink_parameter(k) for k in self.params]
        self.params = [k.copy() for k in other.params]
        self.link_parameters(*self.params)
        self._connect_parameters()
        self._connect_fixes()
        self._notify_parent_change()
        self.uv_bins = other.uv_bins

    @staticmethod
    def _parse_set_prior_from_dict(param, d):
        all_priors_classes = {k.__name__: k for k in GPy.core.parameterization.priors.Prior.__subclasses__()}
        if 'prior' in d:
            re_match = re.match(r'(\w+)\s*\((.*)\)', d['prior'])
            if not re_match or len(re_match.groups()) != 2:
                raise ValueError(f"Error parsing prior: {d['prior']}")
            prior_class, args = re_match.groups()
            if prior_class == 'Fixed':
                param.constrain_fixed(value=float(args))
            elif prior_class in all_priors_classes:
                param.unconstrain()
                klass = all_priors_classes[prior_class]
                param.set_prior(klass(*[float(k.strip()) for k in args.split(',')]))
                if klass == Log10Uniform:
                    param.constrain(Exponent10())
            else:
                raise ValueError(f"Error parsing prior, unknown class name: {d['prior']}")
        return param

    @staticmethod
    def _parse_set_params_from_dict(params, d):
        for param in params.parameters:
            if param.name not in d:
                raise ValueError(f"Error parameter missing from configuration: {param.hierarchy_name()}")
            MultiKern._parse_set_prior_from_dict(param, d[param.name])
        return params

    @staticmethod
    def load_from_dict(name, d):
        raise NotImplementedError()


class MultiAdd(MultiKern, GPy.kern.Add):

    def __init__(self, sub_kerns, name='sum'):
        for kern in sub_kerns:
            assert isinstance(kern, MultiKern)
            assert sub_kerns[0].uv_bins == kern.uv_bins
        GPy.kern.Add.__init__(self, sub_kerns)
        MultiKern.__init__(self)
        self.set_uv_bins(sub_kerns[0].uv_bins)

    def set_uv_bins(self, uv_bins):
        for k_part in self.parts:
            k_part.set_uv_bins(uv_bins)
        MultiKern.set_uv_bins(self, uv_bins)


class AbstractMLKern(MultiKern, GPy.kern.Kern):
    ''' ML Kernel implementation '''

    def __init__(self, latent_dim, name='ml_kern', param_values=[]):
        ''' Initialize a VAE kernel with ml_decoder given the dimension of the latent space latent_dim, 
            and the k_mean of the traing sets (ps3d_k_mean).'''
        from paramz.transformations import Logexp

        GPy.kern.Kern.__init__(self, 1, 0, name)
        self.latent_dim = latent_dim
        self.params = [GPy.core.parameterization.Param(f'x{i + 1}', 0, ) for i in range(self.latent_dim)]
        self.params.append(GPy.core.parameterization.Param('variance', 1, Logexp()))
        self.link_parameters(*self.params)
        for i, pvalue in zip(range(self.latent_dim), param_values):
            setattr(self, f'x{i + 1}', pvalue)
        self.params_call = []
        MultiKern.__init__(self)

    def set_latent_space_normal_prior(self):
        ''' Convenient function to set a Gaussian prior on the latent space parameters '''
        for param in self.parameters[:-1]:
            param.set_prior(GPy.core.parameterization.priors.Gaussian(0, 1))

    def set_variance_log10_prior(self, lower, upper):
        ''' Convenient function to set a Log10 prior on the variance parameters '''
        self.variance.unconstrain()
        self.variance.set_prior(Log10Uniform(lower, upper))
        self.variance.constrain(Exponent10())

    def copy(self):
        raise NotImplementedError()

    def get_norm_cov_1d(self, freqs, params):
        raise NotImplementedError()

    def K(self, X, X2=None):
        freqs = X.squeeze() * 1e6
        dnu_mhz = np.diff(X.squeeze()).mean()
        norm_cov_1d = self.get_norm_cov_1d(freqs, np.array(self.params[:-1]).T)
        r_1d = dnu_mhz * np.arange(norm_cov_1d.shape[1])

        Xsq = np.sum(np.square(X), 1)
        r2 = -2. * np.dot(X, X.T) + (Xsq[:, None] + Xsq[None, :])
        r2[np.diag_indices(X.shape[0])] = 0.
        r2 = np.clip(r2, 0, np.inf)
        r = np.sqrt(r2)

        cov = scipy.interpolate.interp1d(r_1d, norm_cov_1d, kind='quadratic', axis=1,
                                         bounds_error=False, fill_value=0)(r)

        return self.params[-1][0] * cov


class VAEKern(AbstractMLKern, MultiKern):
    ''' ML Kernel implementation '''

    def __init__(self, ml_decoder, latent_dim, ps3d_k_mean, name='vae_kern', param_values=[]):
        ''' Initialize a VAE kernel with ml_decoder given the dimension of the latent space latent_dim, 
            and the k_mean of the traing sets (ps3d_k_mean).'''
        self.ml_decoder = ml_decoder
        self.ps3d_k_mean = ps3d_k_mean
        AbstractMLKern.__init__(self, latent_dim, name=name, param_values=param_values)

    def copy(self):
        c = VAEKern(self.ml_decoder, self.latent_dim, self.ps3d_k_mean, name=self.name)
        c.copy_params(self)

        return c

    def get_norm_cov_1d(self, freqs, params):
        ps3d = self.ml_decoder.predict(params).squeeze()
        ps3d = self.ps3d_k_mean ** 1 * ps3d

        return c_nu_from_ps21(self.ps3d_k_mean, ps3d, freqs, self.uv_bins, delta_kpar=0.05)

    @staticmethod
    def load_from_dict(name, d):
        from tensorflow import keras

        decoder = keras.models.load_model(d['decoder_filename'])
        kern = VAEKern(decoder, d['latent_dim'], d['ps3d_k_mean'], name=name)
        return MultiKern._parse_set_params_from_dict(kern, d)


class VAEKernTorch(AbstractMLKern, MultiKern):
    ''' ML Kernel implementation '''

    def __init__(self, vae_fitter, name='vae_kern', param_values=[]):
        ''' Initialize a VAE kernel with ml_decoder given the dimension of the latent space latent_dim, 
            and the k_mean of the traing sets (ps3d_k_mean).'''
        self.fitter_res = vae_fitter
        self.ps3d_k_mean = vae_fitter.k_mean
        AbstractMLKern.__init__(self, vae_fitter.n_dim, name=name, param_values=param_values)

    def copy(self):
        c = VAEKernTorch(self.fitter_res, name=self.name)
        c.copy_params(self)

        return c

    def get_norm_cov_1d(self, freqs, params):
        ps3d = self.fitter_res.decode(params).squeeze()
        ps3d = self.ps3d_k_mean ** 1 * ps3d

        return c_nu_from_ps21(self.ps3d_k_mean, ps3d, freqs, self.uv_bins, delta_kpar=0.05)

    @staticmethod
    def load_from_dict(name, d):
        vae_fitter = VAEFitter.load(d['fitter_filename'])
        kern = VAEKernTorch(vae_fitter, name=name)
        return MultiKern._parse_set_params_from_dict(kern, d)


class PCAKern(AbstractMLKern, MultiKern):
    ''' ML Kernel implementation '''

    def __init__(self, pca_fitter, name='pca_kern', param_values=[]):
        ''' Initialize a VAE kernel with ml_decoder given the dimension of the latent space latent_dim, 
            and the k_mean of the traing sets (ps3d_k_mean).'''
        self.fitter_res = pca_fitter
        self.ps3d_k_mean = pca_fitter.k_mean
        AbstractMLKern.__init__(self, pca_fitter.n_dim, name=name, param_values=param_values)

    def copy(self):
        c = PCAKern(self.fitter_res, name=self.name)
        c.copy_params(self)

        return c

    def set_latent_space_prior(self):
        ''' Convenient function to set a Gaussian prior on the latent space parameters '''
        for param, mini, maxi in zip(self.parameters[:-1], self.fitter_res.y_min, self.fitter_res.y_max):
            param.set_prior(Uniform(mini, maxi))

    def get_norm_cov_1d(self, freqs, params):
        ps3d = self.fitter_res.decode(params).squeeze()
        ps3d = self.ps3d_k_mean ** 1 * ps3d

        return c_nu_from_ps21(self.ps3d_k_mean, ps3d, freqs, self.uv_bins, delta_kpar=0.05)

    @staticmethod
    def load_from_dict(name, d):
        pca_fitter = PCAKern.load(d['fitter_filename'])
        kern = PCAKern(pca_fitter, name=name)
        return MultiKern._parse_set_params_from_dict(kern, d)


class MutliStationaryKern(MultiKern):
    ''' extension of kernel for regression in multiple baselines range'''

    def __init__(self, kern_class, variance=1, lengthscale=1, ls_alpha=0, var_alpha=0, name='mkern'):
        MultiKern.__init__(self)
        self.kern_class = kern_class
        self.kerns = None
        kern_class.__init__(self, 1, variance=variance, lengthscale=lengthscale, name=name)
        self.ls_alpha = GPy.core.parameterization.Param('ls_alpha', ls_alpha)
        self.ls_alpha.constrain_fixed(ls_alpha)
        self.var_alpha = GPy.core.parameterization.Param('var_alpha', var_alpha)
        self.var_alpha.constrain_fixed(var_alpha)
        self.link_parameters(self.ls_alpha)
        self.link_parameters(self.var_alpha)
        self.ls_alpha = ls_alpha
        self.var_alpha = var_alpha

    @classmethod
    def load_from_dict(cls, name, d):
        kern = cls(name=name)
        return MultiKern._parse_set_params_from_dict(kern, d)

    def set_var_alpha_prior(self, lower, upper):
        ''' Convenient function to set a Uniform prior on the var_alpha parameters '''
        self.var_alpha.unconstrain()
        self.var_alpha.set_prior(Uniform(lower, upper))

    def set_ls_alpha_prior(self, lower, upper):
        ''' Convenient function to set a Uniform prior on the ls_alpha parameters '''
        self.ls_alpha.unconstrain()
        self.ls_alpha.set_prior(Uniform(lower, upper))

    def set_variance_prior(self, lower, upper):
        ''' Convenient function to set a Uniform prior on the variance parameters '''
        self.variance.unconstrain()
        self.variance.set_prior(Uniform(lower, upper))

    def set_variance_log10_prior(self, lower, upper):
        ''' Convenient function to set a Log10 prior on the variance parameters '''
        self.variance.unconstrain()
        self.variance.set_prior(Log10Uniform(lower, upper))
        self.variance.constrain(Exponent10())

    def set_lengthscale_prior(self, lower, upper):
        ''' Convenient function to set a Uniform prior on the lengthscale parameters '''
        self.lengthscale.unconstrain()
        self.lengthscale.set_prior(Uniform(lower, upper))

    def parameters_changed(self):
        if self.kerns is None or len(self.uv_bins) != len(self.kerns):
            self.kerns = [self.kern_class(1) for i in range(len(self.uv_bins))]
        u_min = np.clip(self.uv_bins[0][0], 10, 1e3)
        u_means = np.array([(umax + umin) / 2 for umin, umax in self.uv_bins])
        l_m = self.lengthscale[0]
        var_norm = 1 / np.mean((u_means / u_min) ** self.var_alpha * u_means / u_means.mean())
        for i, u_mean in enumerate(u_means):
            ll = l_m / (1 + self.ls_alpha * 1e-3 * l_m * (u_mean - u_min))
            self.kerns[i].lengthscale = np.clip(abs(ll), 1e-8, 1e8)
            self.kerns[i].variance = self.variance[0] * var_norm * (u_mean / u_min) ** self.var_alpha

    def K(self, X, X2=None):
        return np.array([k.K(X, X2) for k in self.kerns])


class MRBF(MutliStationaryKern, MultiKern, GPy.kern.RBF):

    def __init__(self, variance=1, lengthscale=1, ls_alpha=0, var_alpha=0, name='mrbf'):
        MutliStationaryKern.__init__(self, GPy.kern.RBF, variance=variance, lengthscale=lengthscale,
                                     ls_alpha=ls_alpha, var_alpha=var_alpha, name=name)


class MMat32(MutliStationaryKern, MultiKern, GPy.kern.Matern32):

    def __init__(self, variance=1, lengthscale=1, ls_alpha=0, var_alpha=0, name='mmat32'):
        MutliStationaryKern.__init__(self, GPy.kern.Matern32, variance=variance, lengthscale=lengthscale,
                                     ls_alpha=ls_alpha, var_alpha=var_alpha, name=name)


class MMat52(MutliStationaryKern, MultiKern, GPy.kern.Matern52):

    def __init__(self, variance=1, lengthscale=1, ls_alpha=0, var_alpha=0, name='mmat52'):
        MutliStationaryKern.__init__(self, GPy.kern.Matern52, variance=variance, lengthscale=lengthscale,
                                     ls_alpha=ls_alpha, var_alpha=var_alpha, name=name)


class MExponential(MutliStationaryKern, MultiKern, GPy.kern.Exponential):

    def __init__(self, variance=1, lengthscale=1, ls_alpha=0, var_alpha=0, name='mexp'):
        MutliStationaryKern.__init__(self, GPy.kern.Exponential, variance=variance, lengthscale=lengthscale,
                                     ls_alpha=ls_alpha, var_alpha=var_alpha, name=name)


class MWhiteHeteroscedastic(MultiKern, GPy.kern.Kern):

    def __init__(self, variance=1, name='noise'):
        MultiKern.__init__(self)
        GPy.kern.Kern.__init__(self, 1, 0, name)
        self.set_variance(variance)
        self.alpha = GPy.core.parameterization.Param('alpha', 1)
        self.alpha.constrain_fixed()
        self.link_parameters(self.alpha)

    def set_variance(self, variance):
        assert np.isscalar(variance) or (len(self.uv_bins) == len(variance))
        self.variance = variance

    def K(self, X, X2=None):
        if np.isscalar(self.variance):
            Ks = np.array([np.eye(X.shape[0]) * self.variance] * len(self.uv_bins))
        else:
            Ks = np.array([np.diag(v) for v in self.variance])
        return self.alpha[0] * Ks


class Uniform(GPy.core.parameterization.priors.Prior):
    ''' Uniform prior '''

    domain = GPy.priors._REAL

    def __new__(cls, *args):
        return object.__new__(cls)

    def __init__(self, l, u):
        self.lower = l
        self.upper = u

    def __str__(self):
        return "[{:.2g}, {:.2g}]".format(self.lower, self.upper)

    def lnpdf(self, x):
        region = (x >= self.lower) * (x <= self.upper)
        return np.log(region * np.e)

    def lnpdf_grad(self, x):
        return np.zeros(x.shape)

    def rvs(self, n):
        return np.random.uniform(self.lower, self.upper, size=n)


class Log10Uniform(GPy.core.parameterization.priors.Prior):
    ''' Log10 prior '''

    domain = GPy.priors._POSITIVE

    def __new__(cls, *args):
        return object.__new__(cls)

    def __init__(self, l, u):
        self.lower = l
        self.upper = u

    def __str__(self):
        return "Log10[{:.2g}, {:.2g}]".format(self.lower, self.upper)

    def lnpdf(self, x):
        region = (x >= 10 ** self.lower) * (x <= 10 ** self.upper)
        return np.log(region * np.e)

    def lnpdf_grad(self, x):
        return np.zeros(x.shape)

    def rvs(self, n):
        return 10 ** np.random.uniform(self.lower, self.upper, size=n)


class Exponent10(paramz.transformations.Transformation):
    domain = paramz.transformations._POSITIVE

    def f(self, x):
        return 10 ** x

    def finv(self, x):
        return np.log10(x)

    def initialize(self, f):
        return np.abs(f)

    def log_jacobian(self, model_param):
        return 0

    def __str__(self):
        return 'exp10'


class GPRegressor:
    ''' Simple GPR. See e.g. http://www.gaussianprocess.org/gpml/chapters/RW2.pdf'''

    def __init__(self, X, Y, K):
        self.X = X
        self.K = K
        self.Y = Y
        self.fit()

    def fit(self):
        self.L_ = GPy.util.linalg.jitchol(self.K, maxtries=100)
        self.alpha_, _ = GPy.util.linalg.dpotrs(self.L_, self.Y, lower=1)

    def predict(self, K_star):
        y_mean = K_star.dot(self.alpha_)
        v, _ = GPy.util.linalg.dpotrs(self.L_, K_star.T, lower=1)
        y_cov = K_star - K_star.dot(v)
        return y_mean, y_cov

    def log_marginal_likelihood(self):
        return - 0.5 * (self.Y.size * np.log(2 * np.pi) + 2 * self.Y.shape[1] * np.sum(np.log(np.diag(self.L_)))
            + np.sum(self.alpha_ * self.Y))


class MultiData(object):
    ''' Object encapsulating a CartDataCube for use in MultiGPRegressor.
        Optionally, you can also set the corresponding noise_cube, the uv_bin width
        (or alternatively the uv_bins), and the normalization factor. If the later is not 
        set it will be computed so that the variance of the real part of the data is 1. '''

    def __init__(self, i_cube, noise_cube=1, uv_bins_du=25, norm_factor=None, uv_bins=None):
        self.i_cube = i_cube
        self.X = (i_cube.freqs * 1e-6)[:, None]
        if norm_factor is None:
            norm_factor = np.sqrt(1 / i_cube.data.real.var())
        self.norm_factor = norm_factor
        if uv_bins is None:
            uv_bins = get_uv_bins(i_cube.ru.min(), i_cube.ru.max(), uv_bins_du)
        self.uv_bins = uv_bins
        self.noise_cube = noise_cube

    def c2f(self, c):
        return np.concatenate([c.real, c.imag], axis=1)

    def f2c(self, f):
        return f[:, :f.shape[1] // 2] + 1j * f[:, f.shape[1] // 2:]

    def split(self, i_cube=None):
        if i_cube is None:
            i_cube = self.i_cube
        idxs = [(i_cube.ru >= umin) & (i_cube.ru <= umax) for umin, umax in self.uv_bins]
        Ys = [i_cube.data[:, idx] for idx in idxs]

        return [self.c2f(Y * self.norm_factor) for Y in Ys]

    def variance_split(self, v_cube, axis=1):
        return [Y.var(axis=axis) for Y in self.split(v_cube)]

    def noise_variance_split(self):
        if np.isscalar(self.noise_cube):
            return self.noise_cube * self.norm_factor ** 2
        else:
            return self.variance_split(self.noise_cube)

    def gen_cube(self, Ys_and_covYs):
        cube = self.i_cube.copy()
        idxs = [(cube.ru >= umin) & (cube.ru < umax) for umin, umax in self.uv_bins]
        for (Y, covY), idx in zip(Ys_and_covYs, idxs):
            cube.data[:, idx] = self.f2c(Y) + get_samples(self.X, idx.sum(), covY)
        return 1 / self.norm_factor * cube


class MultiGPRegressor(GPy.core.model.Model):
    ''' Extension of GPRegressor to support multi-baselines.'''

    def __init__(self, multi_data, kern_model, kern_noise=None, name='mgp'):
        ''' Initialze a MultiGPRegressor. Inputs:

            multi_data: a MultiData object
            kern_model: the covariance model for the underlying signal (including foregrounds but without noise)
            kern_noise (optional): the noise Kern object. If not set, it will be set to a MWhiteHeteroscedastic.

            The uv_bins of kern_model and kern_noise will be set to the uv_bins of multi_data.
            Also, the noise variance will be set using the noise_cube of multi_data.
            '''
        super(MultiGPRegressor, self).__init__(name=name)

        if kern_noise is None:
            kern_noise = MWhiteHeteroscedastic(name='noise')

        kern_model.set_uv_bins(multi_data.uv_bins)
        kern_noise.set_uv_bins(multi_data.uv_bins)
        kern_noise.set_variance(multi_data.noise_variance_split())

        self.multi_data = multi_data
        self.kern_model = kern_model
        self.kern_noise = kern_noise
        self.update_kern()

        self.X = multi_data.X
        self.Ys = multi_data.split()

        self.gp_regressors = None
        self.link_parameters(self.kern)
        self.kern_noise.add_observer(self, self.update_kern)
        self.kern_model.add_observer(self, self.update_kern)

    def update_kern(self, *args, **kargs):
        self.kern = self.kern_model + self.kern_noise

    def fit(self):
        Ks = self.kern.K(self.X)
        if Ks.ndim == 2 and self.Ys.ndim == 2:
            self.gp_regressors = [GPRegressor(self.X, self.Ys, Ks)]
        else:
            self.gp_regressors = [GPRegressor(self.X, Y, K) for K, Y in zip(Ks, self.Ys)]

    def predict(self, kern=None):
        assert self.gp_regressors is not None
        if kern is None:
            kern = self.kern_model
        Ks = kern.K(self.X)
        if Ks.ndim == 2:
            Ks = np.repeat(Ks[None], len(self.Ys), axis=0)
        return self.multi_data.gen_cube([gp_regressor.predict(K) for K, gp_regressor in zip(Ks, self.gp_regressors)])

    def log_marginal_likelihood(self):
        assert self.gp_regressors is not None
        return np.sum([gp_regressor.log_marginal_likelihood() for gp_regressor in self.gp_regressors])


def get_kern_part(kern, name):
    if kern.name == name:
        return kern

    kern_list = []
    for k in kern.parts:
        if fnmatch.fnmatch(k.name, name):
            kern_list.append(k)
    if len(kern_list) == 0:
        return None
    elif len(kern_list) == 1:
        return kern_list[0]
    return GPy.kern.Add(kern_list)


class MCMCSampler(object):
    ''' MCMC sampler for GPR '''

    def __init__(self, gp):
        '''gp: a MultiGPRegressor object'''
        self.gp = gp
        self.sampler = None

    def get_parameter_names(self):
        self.gp.kern._ensure_fixes()
        return ['.'.join(s.split('.')[2:]) for s in self.gp.kern.parameter_names_flat().squeeze()]
    
    def get_n_params(self):
        return self.sampler.get_chain().shape[-1]

    def run_mcmc(self, n_steps, n_walkers, lower_bound=None, upper_bound=None,
                 verbose=False, debug=False, save_file=None, live_update=False):
        ''' Run the MCMC smapler. If lower_bound/upper_bound is not set, 
            initial values will be sampled from the parameters priors.'''

        def lnprob(p):
            self.gp.kern.optimizer_array = p
            if not np.isfinite(self.gp.kern.log_prior()):
                return - np.inf

            self.gp.fit()

            log_marginal_likelihood = self.gp.log_marginal_likelihood()
            log_prior = self.gp.kern.log_prior()

            if debug:
                print(self.gp.kern.param_array, log_marginal_likelihood, log_prior)

            return log_marginal_likelihood + log_prior

        ndim = len(self.gp.kern.optimizer_array)

        if lower_bound is None and upper_bound is None:
            print('No lower/upper bound given, using prior ranges.')
            pos = []
            for i in range(n_walkers):
                self.gp.kern.randomize()
                pos.append(self.gp.kern.optimizer_array.tolist())
        else:
            pos = np.random.uniform(low=np.array(lower_bound)[:, None],
                                    high=np.array(upper_bound)[:, None],
                                    size=(ndim, n_walkers)).T

        moves = emcee.moves.StretchMove(a=1.75)
        if save_file is not None:
            backend = emcee.backends.HDFBackend(save_file)
            backend.reset(n_walkers, ndim)
            self.sampler = emcee.EnsembleSampler(n_walkers, ndim, lnprob, backend=backend, moves=moves)
        else:
            self.sampler = emcee.EnsembleSampler(n_walkers, ndim, lnprob, moves=moves)

        if live_update:
            from IPython import display

            ncols = 4
            nrows = int(np.ceil((ndim + 1) / ncols))

            fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(12, 1 + 2.2 * nrows), sharex=True)
            hdisplay = display.display("", display_id=True)
            p_names = self.get_parameter_names() + ['likelihood']

            for i, ax in zip(range(ndim + 1), axs.flatten()):
                for k in range(n_walkers):
                    ax.plot([], c='tab:orange', alpha=0.6)
                ax.text(0.05, 0.97, f'{p_names[i]}:', transform=ax.transAxes, va='top', ha='left')
            fig.tight_layout(pad=0.15)

        try:
            pr = psutil.progress_report(n_steps)
            for i, _ in enumerate(self.sampler.sample(pos, iterations=n_steps)):
                pr(i)
                if verbose and i % 20 == 0 and i != 0:
                    log_prob = self.sampler.get_log_prob()[:, -20:]
                    chain = self.sampler.chain[:, -20:]
                    print('Last 20:')
                    print('Median:', ', '.join([f'{k:.3f}' for k in np.median(chain, axis=(0, 1))]))
                    print('Mean:', ', '.join([f'{k:.3f}' for k in np.mean(chain, axis=(0, 1))]))
                    print('Min:', ', '.join([f'{k:.3f}' for k in np.min(chain, axis=(0, 1))]))
                    print('Max:', ', '.join([f'{k:.3f}' for k in np.max(chain, axis=(0, 1))]))
                    print('Rms:', ', '.join([f'{k:.3f}' for k in np.std(chain, axis=(0, 1))]))
                    print(f'Likelihood: {log_prob.mean():.2f} +-{log_prob.std():-2f}')

                if live_update and i % 10 == 0:  # and i != 0:
                    chain = self.sampler.get_chain()

                    for j in range(ndim + 1):
                        if j < ndim:
                            data = chain[:, :, j]
                        else:
                            data = self.sampler.get_log_prob()
                        for k in range(n_walkers):
                            fig.axes[j].lines[k].set_data((np.arange(chain.shape[0]), data[:, k]))
                        if (np.median(data) < 1) and np.all(data.flatten() > 1e-8):
                            fig.axes[j].set_yscale('log')

                        fig.axes[j].relim()
                        fig.axes[j].autoscale_view()
                        fig.axes[j].texts[0].set_text(f'{p_names[j]}: med:{np.median(data[:, -20:]):.4f}')
                    hdisplay.update(fig)

        except KeyboardInterrupt:
            print('KeyboardInterrupt')

        if live_update:
            plt.close(fig)

    def load_mcmc(self, save_file):
        self.sampler = emcee.backends.HDFBackend(save_file)

    def get_samples(self, n_burn=50, clip_nsigma=6, discard_walkers_nsigma=10, return_log_prob=False):
        samples = self.sampler.get_chain(discard=n_burn)
        log_prob = self.sampler.get_log_prob(discard=n_burn)
        max_log_prob = log_prob.max(axis=0)
        mask = max_log_prob > np.median(max_log_prob) - discard_walkers_nsigma * np.median(log_prob.std(axis=0))
        if (~mask).sum() > 0:
            print(f'Discarding {(~mask).sum()} walkers')

        samples = samples[:, mask, :].reshape(-1, samples.shape[-1])
        
        if return_log_prob:
            log_prob = log_prob[:, mask].flatten()

        samples_outliers = np.zeros_like(samples)
        for i in range(samples.shape[1]):
            m = np.median(samples[:, i])
            s = psutil.robust_std(samples[:, i])
            samples_outliers[abs(samples[:, i] - m) > clip_nsigma * s, i] = 1
            
        mask = (samples_outliers.sum(axis=1) == 0)

        if return_log_prob:
            return samples[mask], log_prob[mask]

        return samples[mask]

    def get_parameter_samples(self, param_name, n_burn=50, clip_nsigma=6, discard_walkers_nsigma=10):
        names = self.get_parameter_names()
        if not param_name in names:
            raise ValueError(f'Parameter name {param_name} not valid.')
        samples = self.get_samples(n_burn, clip_nsigma=clip_nsigma, discard_walkers_nsigma=discard_walkers_nsigma)

        return samples[:, names.index(param_name)]

    def plot_samples(self):
        n_params = self.get_n_params()

        ncols = 4
        nrows = int(np.ceil(n_params / ncols))

        fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(12, 1 + 2.2 * nrows), sharex=True)

        auto_cors = self.sampler.get_autocorr_time(tol=0)
        chain = self.sampler.get_chain()

        names = self.get_parameter_names()

        for j, ax in zip(range(n_params), axs.flatten()):
            y = chain[:, :, j]
            ax.plot(y, c='tab:orange', alpha=0.6)
            ax.axvline(auto_cors[j], c=psutil.black, ls=':')
            ax.axvline(5 * auto_cors[j], c=psutil.black, ls='--')
            if (np.median(y) < 1) and np.all(y.flatten() > 1e-8):
                ax.set_yscale('log')

            txt = f'{names[j]}\nmed:{np.median(y):.4f} std:{astats.mad_std(y):.4f}'
            ax.text(0.05, 0.97, txt, transform=ax.transAxes, va='top', ha='left')

        fig.tight_layout(pad=0.15)

        return fig

    def plot_samples_likelihood(self, p_true=None, n_burn=0, clip_nsigma=6, discard_walkers_nsigma=10):
        _, n_walkers, n_params = self.sampler.get_chain().shape

        ncols = 4
        nrows = int(np.ceil(n_params / ncols))

        fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(12, 1 + 2.5 * nrows), sharey=True)

        samples, log_prob = self.get_samples(n_burn, clip_nsigma=clip_nsigma, return_log_prob=True,
                                   discard_walkers_nsigma=discard_walkers_nsigma)
        i = np.arange(samples.shape[0])

        names = self.get_parameter_names()

        for j, ax in zip(range(n_params), axs.flatten()):
            x = samples[:, j]
            ax.scatter(x, - log_prob, marker='+', c=i, cmap='viridis')
            if p_true is not None:
                ax.axvline(p_true[j], c='tab:orange', ls='--')
            txt = f'{names[j]}\nmed:{np.median(x):.4f} std:{astats.mad_std(x):.4f}'
            ax.text(0.05, 0.97, txt, transform=ax.transAxes, va='top', ha='left')
        fig.tight_layout(pad=0.15)

        return fig

    def plot_corner(self, n_burn, clip_nsigma=6, discard_walkers_nsigma=10):
        samples = self.get_samples(n_burn, clip_nsigma=clip_nsigma, 
                                   discard_walkers_nsigma=discard_walkers_nsigma)

        return corner.corner(samples, plot_datapoints=False, smooth=0.8, 
                             quantiles=(0.16, 0.84), labels=self.get_parameter_names())

    def get_ps_stack(self, ps_gen, kbins, n_burn, n_pick=100, kern_name='eor',
                     subtract_from=None, verbose=False, clip_nsigma=6, discard_walkers_nsigma=10):
        ps_stacker = pspec.PsStacker(ps_gen, kbins)
        samples = self.get_samples(n_burn=n_burn, clip_nsigma=clip_nsigma, 
                                   discard_walkers_nsigma=discard_walkers_nsigma)
        pick = np.random.randint(0, samples.shape[0], n_pick)
        pr = psutil.progress_report(len(pick))
        
        # Determine the parameters index of the portion of the kernel that will be predicted
        k = self.gp.kern.copy()
        k.optimizer_array = np.arange(len(k.optimizer_array))
        k_part = get_kern_part(k, kern_name)
        k_part_idx = k_part.optimizer_array.astype(int)

        for j, i in enumerate(pick):
            pr(j)
            m_oa = samples[i].copy()
            self.gp.kern.optimizer_array = m_oa
            k_part.optimizer_array = m_oa[k_part_idx]
            self.gp.fit()
            if verbose:
                print(m_oa)
            c_rec = self.gp.predict(k_part)
            if subtract_from is not None:
                c_rec = subtract_from - c_rec
            ps_stacker.add(c_rec)

        return ps_stacker


class MLGPRConfigFile(settings.BaseSettings):

    DEFAULT_SETTINGS = os.path.join(CONFIG_DIR, 'default_ml_gpr_settings.toml')

    def _load_kerns_from_dict(self, k_names, label_prefix):
        all_kern_class = {k.__name__: k for k in MultiKern.__subclasses__()}
        kerns = []
        for name in k_names:
            if not name in self:
                raise ValueError(f'{name} not defined in {self.get_file()}')
            assert self[name]['type'] in all_kern_class, f"Kernel type {self[name]['type']} unknown"
            label = name
            if not label.startswith(label_prefix + '_'):
                label = f'{label_prefix}_{name}'
            k = all_kern_class[self[name]['type']].load_from_dict(label, self[name])
            kerns.append(k)

        return MultiAdd(kerns)

    def get_kern(self):
        k_fg = self._load_kerns_from_dict(self.kern.fg, 'fg')
        k_eor = self._load_kerns_from_dict(self.kern.eor, 'eor')
        k_noise = MultiKern._parse_set_params_from_dict(MWhiteHeteroscedastic(), self.kern.noise)

        return k_fg, k_eor, k_noise

    @staticmethod
    def load_from_string_with_defaults(string):
        config = MLGPRConfigFile.get_defaults()
        config += MLGPRConfigFile.load_from_string(string, check_args=False)

        return config


class MLGPRForegroundFitter(fgfit.AbstractForegroundFitter):

    def __init__(self, ml_gpr_config):
        self.config = ml_gpr_config

    def run(self, data_cube, data_cube_noise, save_name=None, save_dir='.', live_update=False, verbose=False):
        k_fg, k_eor, k_noise = self.config.get_kern()
        m_data = MultiData(data_cube, noise_cube=data_cube_noise, uv_bins_du=self.config.kern.uv_bins_du)

        gp = MultiGPRegressor(m_data, k_fg + k_eor, k_noise)
        sampler = MCMCSampler(gp)

        save_file = None

        if save_name is not None:
            save_file = f'{save_dir}/{save_name}.mcmc.h5'
            sampler.gp.multi_data.i_cube.save(os.path.join(save_dir, save_name + '.data.h5'))
            sampler.gp.multi_data.noise_cube.save(os.path.join(save_dir, save_name + '.noise.h5'))
            self.config.save(os.path.join(save_dir, save_name + '.config.parset'))

        sampler.run_mcmc(self.config.mcmc.n_steps, self.config.mcmc.n_walkers, verbose=verbose,
                         live_update=live_update, save_file=save_file)

        return MLGPRResult(sampler, self.config)


class MLGPRResult(object):

    def __init__(self, sampler, ml_gpr_config):
        self.config = ml_gpr_config
        self.sampler = sampler

    @staticmethod
    def load(save_dir, save_name):
        i_cube = datacube.CartDataCube.load(os.path.join(save_dir, save_name + '.data.h5'))
        noise_cube = datacube.CartDataCube.load(os.path.join(save_dir, save_name + '.noise.h5'))
        config = MLGPRConfigFile.load_with_defaults(os.path.join(save_dir, save_name + '.config.parset'), 
                                                    check_args=False)
        k_fg, k_eor, k_noise = config.get_kern()

        m_data = MultiData(i_cube, noise_cube, uv_bins_du=config.kern.uv_bins_du)
        gp = MultiGPRegressor(m_data, k_fg + k_eor, k_noise)
        sampler = MCMCSampler(gp)

        sampler.load_mcmc(os.path.join(save_dir, save_name + '.mcmc.h5'))

        return MLGPRResult(sampler, config)

    def get_ps(self, ps_gen, kbins, kern_name, n_pick=50, subtract_from=None):
        return self.sampler.get_ps_stack(ps_gen, kbins, self.config.mcmc.n_burn, n_pick=n_pick, 
                                         kern_name=kern_name, subtract_from=subtract_from)

    def get_ps_fg(self, ps_gen, kbins, n_pick=50):
        return self.get_ps(ps_gen, kbins, 'fg*', n_pick)

    def get_ps_eor(self, ps_gen, kbins, n_pick=50):
        return self.get_ps(ps_gen, kbins, 'eor*', n_pick)

    def get_ps_res(self, ps_gen, kbins, n_pick=50):
        return self.get_ps(ps_gen, kbins, 'fg*', n_pick, subtract_from=self.get_data_cube())

    def get_scaled_noise_cube(self):
        noise_scale = np.nanmedian(self.sampler.get_parameter_samples('noise.alpha', n_burn=self.config.mcmc.n_burn))
        return np.sqrt(noise_scale) * self.get_noise_cube()

    def get_noise_cube(self):
        return self.sampler.gp.multi_data.noise_cube

    def get_data_cube(self):
        return self.sampler.gp.multi_data.i_cube
