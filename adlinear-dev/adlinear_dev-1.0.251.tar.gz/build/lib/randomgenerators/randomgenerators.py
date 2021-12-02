import itertools
import os

import numpy as np
import pandas as pd
from nptyping import NDArray
from typing import Callable, Any, Union, Tuple, Dict
from typing import Dict
from adlinear import testers as tst
from adlinear import utilities as utl
from adlinear import nmfmodel as nmf
from pathlib import Path
import root_path
import dotenv
dotenv.load_dotenv()


class RandomVariable:

    def __init__(self, npmethod: Callable = np.random.normal, *args, **kwargs):
        """ Specifies a random variable according to a preset distribution and given parameters.

          REVIEW : chacha

          NOTE :

          Parameters
          ----------
          npmethod: distribution

          Returns
          -------

          """
        if not isinstance(npmethod, Callable):
            if isinstance(npmethod, tuple):
                args = sum((npmethod, args), ())
            else:
                args = sum(((npmethod,), args), ())
            npmethod = np.random.normal
        self._method = npmethod
        self._args = args
        self._kwargs = kwargs

    def __call__(self, size: Union[int, Tuple[int, int]] = 1,
                 ) -> Union[Any, NDArray[Any]]:
        """ Generate instances of a random variable.

          REVIEW : chacha

          NOTE :

          Parameters
          ----------
          size: an integer or a pair of integers

          Returns
          -------
          A dataframe of instances
          """
        res = self._method(*self._args, size=size, **self._kwargs)
        if len(res) == 1:
            return res[0]
        return res

    def get_mean(self):
        m = self._kwargs.get("Mean", None)
        if m is None:
            m = self._args[0] if len(self._args) > 0 else 0
        return m

    def apply_bias(self, **kwargs: object) -> Union[Any, NDArray[Any]]:
        """
        apply_bias:
        Applies an additive bias to a random proportion of a index of realizations
        :param kwargs:
        size: integer, total number of realizations
        bias: float, the value of the bias
        coeff: a multiplicative coefficient applied to the deviation between the variable and its mean
        min: a floor applied to the realizations
        max: a ceiling applied to the realizations
        signal_prop: the proportion of biased realizations as a propotion of total size
        :return:
        A vector of realizations with the specified bias applied to an index of realizations
        """
        size = kwargs.pop('size', None)
        if size is None:
            return None
        elif type(size) is list:
            nrows = size[0]
        else:
            nrows = size
        signal_prop = kwargs.pop('signal_prop', None)
        signal_index = kwargs.pop('signal_index', range(nrows))
        bias = kwargs.pop('bias', None)
        std_coeff = kwargs.pop('coeff', None)
        lbound = kwargs.pop('min', None)
        ubound = kwargs.pop('max', None)
        res = self._method(*self._args, size, **kwargs)

        rndg = np.random.default_rng()
        if signal_prop is not None:
            signal_size = min(int(nrows * signal_prop), len(signal_index))
            biased_indices = rndg.choice(signal_index, signal_size, replace=False)
        else:
            biased_indices = range(nrows)
        if std_coeff is not None and std_coeff != 1.0 and len(biased_indices) > 0:
            m = self.get_mean()
            res[biased_indices] = m + std_coeff * (res[biased_indices] - m)
        if bias is not None and bias != 0 and len(biased_indices) > 0:
            res[biased_indices] += bias

        if lbound is not None:
            res = np.maximum(lbound, res)
        if ubound is not None:
            res = np.minimum(ubound, res)
        return res, biased_indices


class RandomGroup:
    def __init__(self, variable: RandomVariable = RandomVariable()):
        self.variable = variable

    def __call__(self, rows: int = 10, columns: int = 10):
        return self.variable((rows, columns))


class DependentLocalizedSignals:
    def __init__(self, signal_dist: Tuple[Dict], noise_dist: dict, non_overlapping_obs=True, cloning_mult: int = 1,
                 n_crossproducts: int = 0, n_noisecolumns: int = 0, nsamples: int = 100, lbound: float = 0.0,
                 ubound: float = 1.0):

        self._signal_dist = signal_dist
        self._nsignals = len(signal_dist)
        self._noise_dist = noise_dist
        self._cloning_mult = cloning_mult
        self._n_crossproducts = n_crossproducts
        self._n_noisecolumns = n_noisecolumns
        self._non_overlapping_signals = non_overlapping_obs
        # self._random_columns = random_columns
        self._nsamples = nsamples
        self._lbound = lbound
        self._ubound = ubound
        self._ncolumns = len(self._signal_dist) * self._cloning_mult + \
            self._n_crossproducts + self._n_noisecolumns
        self._samples = None
        # for distrib
        pass

    def __repr__(self):
        return f"Random_{self._nsamples}x[{self._nsignals}SIG_INDEP={self._non_overlapping_signals}x" \
               f"{self._cloning_mult}_" \
               f"{self._n_crossproducts}CP_{self._n_noisecolumns}Noise] "

    def _make_frame(self):
        n_sig = len(self._signal_dist)
        cols = []
        sig_cols = ["S" + str(i) + "(" + str(j) + ")" for i in range(n_sig) for j in range(self._cloning_mult)]
        cols += sig_cols
        if self._n_crossproducts > 0:
            prod_cols = ["P" + str(i) for i in range(self._n_crossproducts)]
            cols += prod_cols
        noise_cols = ["N" + str(i) for i in range(self._n_noisecolumns)]
        cols += noise_cols
        cols.append("Group")
        self._samples = pd.DataFrame(index=range(self._nsamples),
                                     columns=cols)
        return self

    def get_samples(self):
        if self._samples is None or utl.count_not_nans(self._samples) == 0:
            self.__call__()
        return self._samples

    def get_sub_frame(self, obs_prop=0.5,
                      feat_prop=0.5):
        pass

    def __call__(self):
        self._make_frame()
        m = self._cloning_mult
        # create signal data
        signal_index = range(self._nsamples)
        n_sig = len(self._signal_dist)
        n_prod = self._n_crossproducts
        rndg = np.random.default_rng(seed=42)
        for isig, sig_dict in enumerate(self._signal_dist):
            rvar: RandomVariable = sig_dict.get("Variable", None)
            signal_prop: float = sig_dict.get('Signal_prop', 0.0)
            bias: float = sig_dict.get('Bias', 0.0)
            coeff: float = sig_dict.get('Coeff', 1.0)
            size = [self._nsamples, self._cloning_mult]
            if rvar is not None:
                rvar_clones, rvar_index = rvar.apply_bias(size=size,
                                                          signal_index=signal_index,
                                                          coeff=coeff,
                                                          min=self._lbound,
                                                          max=self._ubound,
                                                          bias=bias,
                                                          signal_prop=signal_prop)
                cloned_cols = [i for i in range(isig * m, (isig + 1) * m)]
                self._samples.iloc[:, cloned_cols] = rvar_clones
                self._samples.loc[rvar_index, "Group"] = isig + 1
                if self._non_overlapping_signals:
                    signal_index = list(set(signal_index).difference(set(rvar_index)))
        # create cross-products
        if n_prod > 0:
            pairs = [i for i in filter(lambda x: x[0] < x[1], itertools.product(range(n_sig * m), range(n_sig * m)))]
            # select random pairs
            rnd_pairs = rndg.choice(pairs, n_prod, replace=False)

            for ipair, pair in enumerate(rnd_pairs):
                col = f"CP{pair[0]}x{pair[1]}"
                self._samples.rename(columns={f"P{ipair}": col}, inplace=True)
                try:
                    self._samples.loc[:, col] = self._samples.iloc[:, pair[0]] * self._samples.iloc[:, pair[1]]
                except ValueError:
                    pass
            pass

        # create noise data
        nvar: RandomVariable = self._noise_dist.get("Variable", None)
        signal_prop = 0.0
        bias = 0.0
        size = [self._nsamples, self._n_noisecolumns]
        noise_col0 = len(self._signal_dist) * self._cloning_mult + self._n_crossproducts

        if nvar is not None and self._n_noisecolumns > 0:
            nvar_clones, _ = nvar.apply_bias(size=size,
                                             min=self._lbound,
                                             max=self._ubound,
                                             bias=bias,
                                             signal_prop=signal_prop)
            self._samples.iloc[:, noise_col0: noise_col0 + self._n_noisecolumns] = nvar_clones

        self._samples.loc[:, "Group"].fillna(value=0.0, inplace=True)
        return self


def generate_nmf_reconstruction(n_comp: int,
                                min_intra_corr: float,
                                max_inter_corr: float,
                                h_avg_clust_size: int,
                                w_avg_clust_size: int,
                                epsilon: float,
                                random_norms: bool = True):
    cl_vects_H = utl.generate_clusterized_vectors(veclen=n_comp,
                                                  nclusters=n_comp,
                                                  nbvect=n_comp * h_avg_clust_size,
                                                  clusterminsize=int(h_avg_clust_size/2),
                                                  max_inter_corr=max_inter_corr,
                                                  min_intra_corr=min_intra_corr,
                                                  random_norms=random_norms)
    cl_vects_W = utl.generate_clusterized_vectors(veclen=nb_clusters,
                                                  nclusters=nb_clusters,
                                                  nbvect=nb_clusters * w_avg_clust_size,
                                                  clusterminsize=int(w_avg_clust_size/2),
                                                  max_inter_corr=max_inter_corr,
                                                  min_intra_corr=min_intra_corr,
                                                  random_norms=random_norms)
    cl_vects_W = cl_vects_W.T
    cl_vects_M = cl_vects_W @ cl_vects_H
    noise = np.random.normal(loc=0.0, scale=epsilon, size=cl_vects_M.shape)
    cl_vects_M *= 1 + noise
    cl_vects_M = np.maximum(cl_vects_M, 0)
    return cl_vects_M


if __name__ == "__main__":
    # localisation du modèle GAN
    root_path = root_path.get_root_path()

    rd_path = root_path / os.getenv("rd_subpath")
    imputation_paper_path = rd_path / os.getenv("imputation_paper_subpath")

    data_path = imputation_paper_path / os.getenv("data_subpath")
    res_path = imputation_paper_path / os.getenv("results_subpath")

    train_f_name = f"mini_scree_plots2.csv"

    if os.path.isfile(res_path / "random_nmf" / train_f_name):
        df_mini_scree_plots = pd.read_csv(res_path / "random_nmf" / train_f_name)
    else:
        df_mini_scree_plots = pd.DataFrame(index=[], columns=[])

    # train_f_name = "foo_scree.csv"
    random_norms = True
    for itrial in range(20):
        nb_clusters = np.random.randint(low=5, high=50)
        min_corr = np.random.uniform(low=0.80, high=0.95)
        max_corr = np.random.uniform(low=0.05, high=0.20)
        h_avg_csize = np.random.randint(low=10, high=20)
        w_avg_csize = np.random.randint(low=10, high=100)
        eps = np.random.uniform(low=0.05, high=0.25)
        generated_M = generate_nmf_reconstruction(n_comp=nb_clusters,
                                                  min_intra_corr=min_corr,
                                                  max_inter_corr=max_corr,
                                                  h_avg_clust_size=h_avg_csize,
                                                  w_avg_clust_size=w_avg_csize,
                                                  epsilon=eps,
                                                  random_norms=random_norms)
        rnstr = "RandNorms" if random_norms else "ConstNorms"
        generated_M.to_csv(res_path / "random_nmf" / f"M_nc{nb_clusters}_corrmin{round(min_corr,2)}_"
                                       f"corrmax{round(max_corr,2)}_noise{round(eps,2)}_{rnstr}.csv",
                           float_format="%.4f")
        df_scree_plot = nmf.generate_scree_plot(generated_M, ncmin=5, ncmax=40)
        df_mini_scree_plots = nmf.add_examples_from_scree_plot(df_mini_scree_plots, df_scree_plot, nb_clusters)
        df_mini_scree_plots.to_csv(res_path / "random_nmf" / train_f_name)

    do_read_mat = False
    if do_read_mat:
        mat_name = "M_nc36_corrmin0.92_corrmax0.13_noise0.11"
        M = pd.read_csv(res_path / "random_nmf" / f"{mat_name}.csv")
        df_scree_plot = nmf.generate_scree_plot(M, ncmin=25, ncmax=40)
        df_scree_plot.to_csv(res_path / "random_nmf" / f"{mat_name}_screeplot.csv")

    pass
