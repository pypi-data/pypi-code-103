import numpy as np
import copy
import pickle
import os
from .utils import _transform_space, MyProgressBar, mean_absolute_exp_percentage_error, accuracy_exp_01, accuracy_exp_005
from scipy import interpolate
import tensorflow
tensorflow.compat.v1.logging.set_verbosity(tensorflow.compat.v1.logging.ERROR)
from tensorflow.keras.models import load_model
gpus = tensorflow.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tensorflow.config.experimental.set_memory_growth(gpu, True)

__all__ = ["Lbias_expansion"]

class Lbias_expansion(object):
    """
    A class to load and call the baccoemu for the Lagrangian bias expansion terms.
    By default, the LPT Lagrangian bias expansion terms emulator
    (described in Aricò et al, 2021) are loaded.

    :param lpt: whether to load the LPT emulator, defaults to True
    :type lpt: boolean, optional
    :param compute_sigma8: whether to load the sigma8 emulator, defaults to True
    :type compute_sigma8: boolean, optional

    :param verbose: whether to activate the verbose mode, defaults to True
    :type verbose: boolean, optional

    """
    def __init__(self, lpt=True, compute_sigma8=True, verbose=True):


        self.verbose = verbose
        self.compute_lpt = True if lpt else False
        self.compute_sigma8 = True if compute_sigma8 else False

        self.lb_term_labels = [r'$1 1$', r'$1 \delta$', r'$1 \delta^2$', r'$1 s^2$',
                               r'$ 1 \nabla^2\delta$', r'$\delta \delta$',
                               r'$\delta \delta^2$', r'$\delta s^2$',
                               r'$\delta \nabla^2\delta$', r'$\delta^2 \delta^2$',
                               r'$\delta^2 s^2$', r'$\delta^2 \nabla^2\delta$',
                               r'$s^2 s^2$', r'$s^2 \nabla^2\delta$',
                               r'$\nabla^2\delta \nabla^2\delta$']

        self.emulator = {}
        if self.compute_lpt:
            self.emulator['lpt'] = load_lpt_emu()
        if self.compute_sigma8:
            from .matter_powerspectrum import Matter_powerspectrum
            self.matter_powerspectrum_emulator = Matter_powerspectrum(linear=False, smeared_bao=False,
            nonlinear_boost = False, baryonic_boost=False, compute_sigma8=True, verbose=verbose)

    def _get_parameters(self, coordinates, which_emu, grid=None):
        """
        Function that returns a dictionary of cosmological parameters,
        computing derived cosmological parameters, if not
        already present in the given coordinates, and checking the relevant boundaries.
        :param coordinates: a set of coordinates in parameter space
        :type coordinates: dict
        :param which_emu: kind of emulator: options are 'linear', 'nonlinear','baryon','smeared_bao','sigma8'
        :type which_emu: str
        :param grid: dictionary with parameter and vector of values where to evaluate the emulator, defaults to None
        :type grid: array_like, optional
        :return: coordinates with derived parameters
        :rtype: dict
        """
        coordinates = {key: coordinates[key] for key in set(list(coordinates.keys())) - set(['k', 'k_lin', 'pk_lin'])}

        avail_pars = [coo for coo in coordinates.keys() if coordinates[coo] is not None] #parameters currently available
        eva_pars = self.emulator[which_emu]['keys']  #parameters strictly needed to evaluate the emulator
        req_pars = self.emulator[which_emu]['keys']  #parameters needed for a computation
        comp_pars = list(set(req_pars)-set(avail_pars)) #parameters to be computed
        deriv_pars = ['omega_cold','sigma8_cold', 'A_s'] #derived parameters that can be computed
        miss_pars = list(set(comp_pars)-set(deriv_pars)) #parameters missing from coordinates
        extra_pars = list(set(req_pars)-set(eva_pars)) #requested parameters not needed for evaluation
        if miss_pars:
            print(f"{which_emu} emulator:")
            print(f"  Please add the parameter(s) {miss_pars} to your coordinates!")
            raise KeyError(f"{which_emu} emulator: coordinates need the following parameters: ", miss_pars)

        if ('omega_cold' in avail_pars) & ('omega_matter' in avail_pars):
            assert len(np.atleast_1d(coordinates['omega_cold'])) == len(np.atleast_1d(coordinates['omega_matter'])), 'Both omega_cold and omega_matter were provided, but they have different len'
            om_from_oc = coordinates['omega_cold'] + coordinates['neutrino_mass'] / 93.14 /coordinates['hubble']**2
            assert np.all(np.abs(coordinates['omega_matter'] - om_from_oc) < 1e-4), 'Both omega_cold and omega_matter were provided, but they are inconsistent among each other'

        if 'omega_cold' in comp_pars:
            if 'omega_matter' not in avail_pars:
                raise KeyError('One parameter between omega_matter and omega_cold must be provided!')

            omega_nu = coordinates['neutrino_mass'] / 93.14 /coordinates['hubble']**2
            coordinates['omega_cold'] = coordinates['omega_matter'] - omega_nu

        if ('sigma8_cold' not in avail_pars) & ('A_s' not in avail_pars):
            raise KeyError('One parameter between sigma8_cold and A_s must be provided!')

        if ('sigma8_cold' in  avail_pars) & ('A_s' in avail_pars):
            assert len(np.atleast_1d(coordinates['sigma8_cold'])) == len(atleast_1d(coordinates['A_s'])), 'Both sigma8_cold and A_s were provided, but they have different len'
            ignore_s8_pars = copy.deepcopy(coordinates)
            del ignore_s8_pars['sigma8_cold']
            s8_from_A_s = self.get_sigma8(**ignore_s8_pars)
            assert np.all(np.abs(coordinates['sigma8_cold'] - s8_from_A_s) < 1e-4), 'Both sigma8_cold and A_s were provided, but they are inconsistent among each other'

        if 'sigma8_cold' in comp_pars:
            coordinates['sigma8_cold'] = self.matter_powerspectrum_emulator.get_sigma8(**coordinates)

        if 'A_s' in comp_pars:
            tmp_coords = copy.deepcopy(coordinates)
            del tmp_coords['sigma8_cold']
            tmp_coords['A_s'] = 2e-9
            coordinates['A_s'] = (coordinates['sigma8_cold'] / self.matter_powerspectrum_emulator.get_sigma8(**tmp_coords))**2 * tmp_coords['A_s']

        pp = np.squeeze([coordinates[p] for p in eva_pars])
        coords_out = copy.deepcopy(coordinates)

        grid = {}
        for key in coordinates.keys():
            if len(np.atleast_1d(coordinates[key])) > 1:
                grid[key] = np.array(coordinates[key])

        if len(list(grid.keys()))==0:
            grid = None
        else:
            grid_structure = []
            for key in grid.keys():
                grid_structure.append(len(grid[key]))
            grid_structure = np.array(grid_structure)
            values, counts = np.unique(grid_structure, return_counts=True)
            counts_but_highest = np.delete(counts, np.argmax(counts))
            assert np.all(counts == counts[0]) | np.all(counts_but_highest == 1), 'When passing multiple coordinate sets you should either vary only on parameter, or all parameters should have the same len'

        if grid is not None:
            grid_pars = list(grid.keys()) # list of parameters that are varyied in a grid
            N = len(grid[grid_pars[0]])
            pp = np.tile(pp, (N, 1))
            for par in grid_pars:
                if par in eva_pars:
                    index = eva_pars.index(par)
                    pp[:,index] = np.float64(grid[par])

                    coords_out[par] = grid[par]
            pp = np.float64(pp)

        for i,par in enumerate(eva_pars):
            val = pp[i] if grid is None else pp[:,i]
            message = 'Param {}={} out of bounds [{}, {}]'.format(
                par, val, self.emulator[which_emu]['bounds'][i][0], self.emulator[which_emu]['bounds'][i][1])

            assert np.all(val >= self.emulator[which_emu]['bounds'][i][0]) & np.all(val <= self.emulator[which_emu]['bounds'][i][1]), message

        if extra_pars:
            cc = np.squeeze([coords_out[p] for p in extra_pars])
            if None in cc:
                raise ValueError(f'None in parameters: {extra_pars} = {cc}!')

        return coords_out, pp, grid

    def get_lpt_pk(self, omega_cold=None, omega_matter=None, omega_baryon=None,
                            sigma8_cold=None, A_s=None, hubble=None, ns=None, neutrino_mass=None,
                            w0=None, wa=None, expfactor=None, k=None, **kwargs):

        """Compute the prediction of the 15 LPT Lagrangian bias expansion terms.


        :param omega_cold: omega cold matter (cdm + baryons), either omega_cold
                           or omega_matter should be specified, if both are specified
                           they should be consistent
        :type omega_cold: float or array
        :param omega_matter: omega total matter (cdm + baryons + neutrinos), either omega_cold
                           or omega_matter should be specified, if both are specified
                           they should be consistent
        :type omega_matter: float or array
        :param sigma8_cold: rms of cold (cdm + baryons) linear perturbations, either sigma8_cold
                            or A_s should be specified, if both are specified they should be
                            consistent
        :type sigma8_cold: float or array
        :param A_s: primordial scalar amplitude at k=0.05 1/Mpc, either sigma8_cold
                    or A_s should be specified, if both are specified they should be
                    consistent
        :type A_s: float or array
        :param hubble: adimensional Hubble parameters, h=H0/(100 km/s/Mpc)
        :type hubble: float or array
        :param ns: scalar spectral index
        :type ns: float or array
        :param neutrino_mass: total neutrino mass
        :type neutrino_mass: float or array
        :param w0: dark energy equation of state redshift 0 parameter
        :type w0: float or array
        :param wa: dark energy equation of state redshift dependent parameter
        :type wa: float or array
        :param expfactor: expansion factor a = 1 / (1 + z)
        :type expfactor: float or array
        :param k: a vector of wavemodes in h/Mpc at which the nonlinear boost will be computed, if None
                the default wavemodes of the nonlinear emulator will be used, defaults to None
        :type k: array_like, optional
        :return: k and P(k), a list of the emulated 15 LPT Lagrangian bias expansion terms
        :rtype: tuple
        """
        _kwargs = locals()
        kwargs = {key: _kwargs[key] for key in set(list(_kwargs.keys())) - set(['self'])}

        if not self.compute_lpt:
            raise ValueError("Please enable the lpt emulator!")

        emulator = self.emulator['lpt']
        coordinates, pp, grid = self._get_parameters(kwargs, 'lpt')

        sub = emulator['sub']
        scaler = emulator['scaler']

        P_nn = []
        for n in range(15):
            pred = emulator['model'][n](pp.reshape(-1,9), training=False)
            prediction = np.squeeze(scaler[n].inverse_transform(pred))
            P_nn.append(prediction)

        if k is not None:
            if max(k) > 0.75:
                raise ValueError(f"""
            The maximum k of the l-bias lpt emulator must be 0.75 h/Mpc:
            the current value is {max(k)} h/Mpc""")
            if (min(k) < 1.e-2)&(self.verbose):
                print("WARNING: the l-bias lpt emulator is extrapolating to k < 0.01 h/Mpc!")

            for n in range(15):
                p_interp = interpolate.interp1d(np.log(emulator['k']), P_nn[n],
                kind='cubic', axis = 0 if grid is None else 1, fill_value='extrapolate')
                P_nn[n] = p_interp(np.log(k))

        P_nn = np.array([np.exp(P_nn[n])-sub[n] for n in range(15) ])
        return k, P_nn

def load_lpt_emu(verbose=True):
    """Loads in memory the lpt emulator described in Aricò et al. 2021.

    :return: a dictionary containing the emulator object
    :rtype: dict
    """

    if verbose:
        print('Loading l-bias lpt emulator...')

    basefold = os.path.dirname(os.path.abspath(__file__))

    old_names = [(basefold + '/' + "lpt_emulator")]
    for old_name in old_names:
        if os.path.exists(old_name):
            import shutil
            shutil.rmtree(old_name)

    emulator_name = (basefold + '/' +
                     "lpt_emulator_v2.0.0")

    if (not os.path.exists(emulator_name)):
        import urllib.request
        import tarfile
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        print('Downloading emulator data (13 Mb)...')
        urllib.request.urlretrieve(
            'https://bacco.dipc.org/lpt_emulator_v2.0.0.tar',
            emulator_name + '.tar',
            MyProgressBar())
        tf = tarfile.open(emulator_name+'.tar', 'r')
        tf.extractall(path=basefold)
        tf.close()
        os.remove(emulator_name + '.tar')

    customs={"accuracy_01": accuracy_exp_01,
             "accuracy_005": accuracy_exp_005,
             "mean_absolute_exp_percentage_error":mean_absolute_exp_percentage_error}

    emulator = {}
    emulator['model'] = []
    emulator['sub'] = []
    emulator['scaler'] = []
    for n in range(15):
        i_emulator_name = f'{emulator_name}/lpt_emu_field{n}'

        file_to_read = open(f"{i_emulator_name}/details.pickle", "rb")
        nn_details = pickle.load(file_to_read)

        emulator['model'].append(load_model(i_emulator_name, custom_objects=customs))
        emulator['scaler'].append(nn_details['scaler'])
        emulator['sub'].append(nn_details['subtract'])

    emulator['k'] = nn_details['kk']
    emulator['keys'] = ['omega_cold', 'sigma8_cold', 'omega_baryon', 'ns',
                                'hubble', 'neutrino_mass', 'w0', 'wa', 'expfactor']
    emulator['bounds'] = nn_details['bounds']

    if verbose:
        print('L-bias lpt emulator loaded in memory.')

    return emulator
