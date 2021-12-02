# Function and class to estimate experiments sensitivity
#
# Authors: F.Mertens


import os
import itertools

import numpy as np

import scipy.interpolate

import astropy.constants as const

from fast_histogram import histogram2d

INSTRU_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instru')


class TelescopeSimu(object):

    name = 'none'
    pb_name = name
    n_elements_per_stations = 1

    def __init__(self, freqs, dec_deg, hal, har, umin=None, umax=None, timeres=100, remove_intra_baselines=True):
        self.freqs = freqs
        self.dec_deg = dec_deg
        self.hal = hal
        self.har = har
        if umin is not None:
            self.umin = umin
        if umax is not None:
            self.umax = umax
        self.timeres = timeres
        self.remove_intra_baselines = remove_intra_baselines

    @staticmethod
    def from_name(instru, freqs, dec_deg, hal, har, umin=None, umax=None, timeres=100, remove_intra_baselines=True):
        klasses = TelescopeSimu.__subclasses__()
        [klasses.extend(k.__subclasses__()) for k in klasses[:]]

        for klass in klasses:
            if hasattr(klass, 'name') and klass.name == instru:
                return klass(freqs, dec_deg, hal, har, umin, umax, timeres, remove_intra_baselines=remove_intra_baselines)

        raise ValueError('No instrument with name: %s' % instru)

    @staticmethod
    def from_dict(d, freqs):
        def get_d_value(name, default=None):
            if default is None and not name in d:
                raise ValueError(f'{name} missing to initialize TelescopeSimu')
            return d.get(name, default)

        instru = get_d_value('PEINSTRU')
        dec_deg = get_d_value('PEOBSDEC')
        hal = get_d_value('PEOBSHAL')
        har = get_d_value('PEOBSHAR')
        default_telescop = TelescopeSimu.from_name(instru, freqs, dec_deg, hal, har)
        umin = get_d_value('PEOBSUMI', default_telescop.umin)
        umax = get_d_value('PEOBSUMA', default_telescop.umax)
        timeres = get_d_value('PEOBSRES', default_telescop.timeres)
        remove_intra_baselines = get_d_value('PEREMINT', default_telescop.remove_intra_baselines)

        return TelescopeSimu.from_name(instru, freqs, dec_deg, hal, har, umin=umin, umax=umax, 
                                       timeres=timeres, remove_intra_baselines=remove_intra_baselines)

    def to_dict(self):
        return {'PEINSTRU': self.name, 'PEOBSDEC': self.dec_deg, 'PEOBSHAL': self.hal, 'PEOBSHAR': self.har,
                'PEOBSUMI': self.umin, 'PEOBSUMA': self.umax, 'PEOBSRES': self.timeres, 
                'PEREMINT': self.remove_intra_baselines}

    def get_stat_pos_file(self):
        pass

    def get_sefd(self, freq):
        pass

    def get_primary_beam(self):
        pass

    def simu_uv(self, include_conj=True):
        from ps_eor import psutil

        def m2a(m): return np.squeeze(np.asarray(m))

        lambs = const.c.value / self.freqs
        umin_meter = (self.umin * lambs).min()
        umax_meter = (self.umax * lambs).max()

        timev = np.arange(self.hal * 3600, self.har * 3600, self.timeres)

        statpos = np.loadtxt(self.get_stat_pos_file())
        nstat = statpos.shape[0]

        print('Simulating UV coverage ...')

        # All combinations of nant to generate baselines
        stncom = np.array(list(itertools.combinations(np.arange(0, nstat), 2)))
        print(f'Number of elements: {nstat}')
        print(f'Number of baselines: {stncom.shape[0]}')

        if self.remove_intra_baselines and self.n_elements_per_stations > 1:
            station_id = np.repeat(np.arange(0, nstat / self.n_elements_per_stations, dtype=int), self.n_elements_per_stations)
            stncom_stations = np.array(list(itertools.combinations(station_id, 2)))
            idx = np.array([a == b for a, b, in stncom_stations]).astype(bool)
            stncom = stncom[~idx]
            print(f'Discarding {idx.sum()} intra-baselines')

        b1, b2 = zip(*stncom)

        uu = []
        vv = []
        ww = []

        pr = psutil.progress_report(len(timev))
        i = 0

        for tt in timev:
            pr(i)
            HA = (tt / 3600.) * (15. / 180) * np.pi - (6.8689389 / 180) * np.pi
            dec = self.dec_deg * (np.pi / 180)
            RM = np.matrix([[np.sin(HA), np.cos(HA), 0.0],
                            [-np.sin(dec) * np.cos(HA), np.sin(dec) * np.sin(HA), np.cos(dec)],
                            [np.cos(dec) * np.cos(HA), - np.cos(dec) * np.sin(HA), np.sin(dec)]])
            statposuvw = np.dot(RM, statpos.T).T
            bu = m2a(statposuvw[b1, 0] - statposuvw[b2, 0])
            bv = m2a(statposuvw[b1, 1] - statposuvw[b2, 1])
            bw = m2a(statposuvw[b1, 2] - statposuvw[b2, 2])

            ru = np.sqrt(bu ** 2 + bv ** 2)
            idx = (ru > umin_meter) & (ru < umax_meter)

            uu.extend(bu[idx])
            vv.extend(bv[idx])
            ww.extend(bw[idx])

            if include_conj:
                uu.extend(- bu[idx])
                vv.extend(- bv[idx])
                ww.extend(bw[idx])

            i += 1

        return np.array(uu), np.array(vv), np.array(ww)

    def simu_gridded_uv(self, uu_meter, vv_meter, fov, oversampling_factor=4, min_weight=10):
        from ps_eor import psutil, datacube

        du = 1 / np.radians(fov)
        res = 1 / (oversampling_factor * self.umax)
        n_u = int(np.ceil(1 / (res * du)))
        shape = (n_u, n_u)

        g_uu, g_vv = psutil.get_uv_grid(shape, res)

        ranges = [g_uu.min() - du / 2, g_uu.max() + du / 2]

        print('Gridding UV coverage ...')
        weights = []
        pr = psutil.progress_report(len(self.freqs))
        for i, lamb in enumerate(const.c.value / self.freqs):
            pr(i)
            w = histogram2d(uu_meter / lamb, vv_meter / lamb, bins=n_u, range=[ranges] * 2)
            weights.append(w)

        weights = np.array(weights)
        weights = weights.reshape(len(self.freqs), -1)
        g_uu = g_uu.flatten()
        g_vv = g_vv.flatten()
        ru = np.sqrt(g_uu ** 2 + g_vv ** 2)

        idx = (weights.min(axis=0) >= min_weight) & (ru >= self.umin) & (ru <= self.umax)
        weights = weights[:, idx]
        g_uu = g_uu[idx]
        g_vv = g_vv[idx]

        meta = datacube.ImageMetaData.from_res(res, shape)
        meta.wcs.wcs.cdelt[2] = psutil.robust_freq_width(self.freqs)
        meta.set('PEINTTIM', self.timeres)
        meta.set('PETOTTIM', (self.har - self.hal) * 3600)
        w_cube = datacube.CartWeightCube(weights, g_uu, g_vv, self.freqs, meta)

        return TelescopGriddedUV(w_cube, self)


class TelescopGriddedUV(object):

    def __init__(self, weights, telescope_simu):
        from ps_eor import psutil

        self.weights = weights
        self.telescope_simu = telescope_simu
        self.name = self.telescope_simu.name
        self.z = psutil.freq_to_z(self.weights.freqs.mean())

    def save(self, filename):
        self.weights.meta.update(self.telescope_simu.to_dict())
        self.weights.save(filename)

    def get_slice(self, freq_start, freq_end):
        return TelescopGriddedUV(self.weights.get_slice(freq_start, freq_end), self.telescope_simu)

    @staticmethod
    def load(filename):
        from ps_eor import datacube

        weights = datacube.CartWeightCube.load(filename)
        telescope_simu = TelescopeSimu.from_dict(weights.meta.kargs, weights.freqs)

        return TelescopGriddedUV(weights, telescope_simu)

    def get_sefd(self):
        return np.atleast_1d(self.telescope_simu.get_sefd(self.weights.freqs))

    def get_ps_gen(self, filter_kpar_min=None, filter_wedge_theta=0):
        from ps_eor import pspec, datacube

        du = 0.75 / self.weights.meta.theta_fov

        el = 2 * np.pi * (np.arange(self.weights.ru.min(), self.weights.ru.max(), du))

        ps_conf = pspec.PowerSpectraConfig(el, window_fct='boxcar')
        ps_conf.filter_kpar_min = filter_kpar_min
        ps_conf.filter_wedge_theta = filter_wedge_theta
        ps_conf.du = self.telescope_simu.du
        ps_conf.weights_by_default = True

        eor_bin_list = pspec.EorBinList(self.weights.freqs)
        eor_bin_list.add_freq(1, self.weights.freqs.min() * 1e-6, self.weights.freqs.max() * 1e-6)
        eor = eor_bin_list.get(1, self.weights.freqs)
        pb = datacube.PrimaryBeam.from_name(self.telescope_simu.pb_name)

        return pspec.PowerSpectraCart(eor, ps_conf, pb)

    def get_noise_std_cube(self, total_time_hour, sefd=None, min_weight=1):
        if sefd is None:
            sefd = self.get_sefd()
        noise_std = self.weights.get_noise_std_cube(sefd, total_time_hour)
        noise_std.filter_min_weight(min_weight)

        return noise_std


class SkaLow(TelescopeSimu):

    name = 'ska_low'
    umin = 30
    umax = 250
    fov = 3
    du = 8
    pb_name = name

    def get_stat_pos_file(self):
        return os.path.join(INSTRU_DIR, 'skalow_enu_statpos.data')

    def get_sefd(self, freq, tsys_sky=60):
        # Specification extracted from SKA LFAA Station design report document (https://arxiv.org/pdf/2003.12744v2.pdf).
        # See Page 22 of the report. SKALA v4 is actually expected to be better than the spec.
        freqs_spec = np.array([50, 80, 110, 140, 160, 220]) * 1e6
        a_eff_over_tsys_spec = 1 * np.array([0.14, 0.46, 1.04, 1.15, 1.2, 1.2])
        def t_sky_fct(freqs): return tsys_sky * (3e8 / freqs) ** 2.55
        a_eff_fct = scipy.interpolate.interp1d(freqs_spec, a_eff_over_tsys_spec * t_sky_fct(freqs_spec), 
                                               kind='slinear', bounds_error=False, fill_value='extrapolate')

        return 2 * const.k_B.value * 1e26 * t_sky_fct(freq) / a_eff_fct(freq)


class LofarHBA(TelescopeSimu):

    name = 'lofar_hba'
    umin = 50
    umax = 250
    fov = 4
    du = 8
    n_elements_per_stations = 2
    pb_name = name

    def get_stat_pos_file(self):
        return os.path.join(INSTRU_DIR, 'lofar_statpos.data')

    def get_sefd(self, freq):
        # Typical observed SEFD ~ 130-160 MHz @ NCP (see https://old.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti)
        return 4000


class A12HBA(TelescopeSimu):

    name = 'a12_hba'
    umin = 10
    umax = 200
    fov = 24
    du = 2
    pb_name = name
    n_elements_per_stations = 48

    def get_stat_pos_file(self):
        return os.path.join(INSTRU_DIR, 'aartfaac_a12_hba_statpos.data')

    def get_sefd(self, freq):
        # Typical observed SEFD of LOFAR-HBA between ~ 130-160 MHz @ NCP (see https://old.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti)
        # LOFAR-HBA core is composed of 24 tiles. So S_tile = S_station * 24
        return 4000 * 24



class NenuFAR(TelescopeSimu):

    name = 'nenufar'
    umin = 6
    umax = 60
    fov = 16
    du = 4
    pb_name = name

    def get_stat_pos_file(self):
        return os.path.join(INSTRU_DIR, 'nenufar52_statpos.data')

    def sky_temperature(self, freq, tsys_sky=60):
        lamb = const.c.value / freq
        return tsys_sky * lamb ** 2.55

    def inst_temperature(self, freq):
        """ Instrument temperature at a given frequency ``freq``.

            From: https://github.com/AlanLoh/nenupy/blob/master/nenupy/instru/instru.py
        """
        lna_sky = np.array([
            5.0965, 2.3284, 1.0268, 0.4399, 0.2113, 0.1190, 0.0822, 0.0686,
            0.0656, 0.0683, 0.0728, 0.0770, 0.0795, 0.0799, 0.0783, 0.0751,
            0.0710, 0.0667, 0.0629, 0.0610, 0.0614, 0.0630, 0.0651, 0.0672,
            0.0694, 0.0714, 0.0728, 0.0739, 0.0751, 0.0769, 0.0797, 0.0837,
            0.0889, 0.0952, 0.1027, 0.1114, 0.1212, 0.1318, 0.1434, 0.1562,
            0.1700, 0.1841, 0.1971, 0.2072, 0.2135, 0.2168, 0.2175, 0.2159,
            0.2121, 0.2070, 0.2022, 0.1985, 0.1974, 0.2001, 0.2063, 0.2148,
            0.2246, 0.2348, 0.2462, 0.2600, 0.2783, 0.3040, 0.3390, 0.3846,
            0.4425, 0.5167, 0.6183, 0.7689, 1.0086, 1.4042, 2.0732
        ])
        lna_freqs = (np.arange(71) + 15) * 1e6
        return self.sky_temperature(freq) * scipy.interpolate.interp1d(lna_freqs, lna_sky,
                                                                       bounds_error=False,
                                                                       fill_value='extrapolate')(freq)

    def get_sefd(self, freq, tsys_sky=60):
        d = 5.5
        lamb = const.c.value / freq
        tsys = self.sky_temperature(freq, tsys_sky) + self.inst_temperature(freq)
        a_eff = 19 * np.min([lamb ** 2 / 3., np.ones_like(lamb) * np.pi * d ** 2 / 4.], axis=0)

        return 2 * const.k_B.value / a_eff * 1e26 * tsys



class NenuFARFull(NenuFAR):

    name = 'nenufar_full'
    pb_name = 'nenufar'


    def get_stat_pos_file(self):
        return os.path.join(INSTRU_DIR, 'nenufar_full_statpos.data')

