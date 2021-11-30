import os
import re
import pathlib
import datetime

import numpy as np

import lsmtool
lsmtool.logger.setLevel('warning')

from libpipe import worker, futils

from . import utils, flagutils, msutils
from .settings import TEMPLATE_DIR

cwd = os.getcwd()


def get_cal_config(name):
    return pathlib.Path(__file__).absolute().parent / 'cal_config' / name


class SkyModel(object):

    def __init__(self, sky_model_name='app_sky_model'):
        self.sky_model_name = sky_model_name
        self.stat_cache = dict()

    def get_sky_model(self, msin):
        return f'{msin}/sky_model/{self.sky_model_name}.sourcedb'

    def get_sky_model_bbs(self, msin):
        return f'{msin}/sky_model/{self.sky_model_name}.skymodel'

    def get_stat(self, msin):
        if msin not in self.stat_cache:
            model = lsmtool.load(self.get_sky_model_bbs(msin))
            s = dict(zip(model.getPatchNames(), model.getColValues('I', aggregate='sum'))), model.getPatchPositions()
            self.stat_cache[msin] = s
        return self.stat_cache[msin]

    def get_patch_i(self, msin, patch):
        if isinstance(patch, str):
            return self.get_stat(msin)[0][patch]
        return sum(self.get_patch_i(msin, k) for k in patch)

    def get_patch_coord(self, msin, patch):
        return self.get_stat(msin)[1][patch]

    def get_patchs(self, msin, include_main=True, exclude=None):
        ateams = self.get_stat(msin)[0]
        patches = sorted(ateams, key=ateams.get, reverse=True)
        if 'Main' in patches:
            patches.remove('Main')
            if include_main:
                patches.append('Main')
        if exclude:
            for patch in exclude:
                if patch in patches:
                    patches.remove(patch)
        return patches

    def get_directions(self, msin, dir_name_or_idx):
        patchs = self.get_patchs(msin)
        dirs = []
        if isinstance(dir_name_or_idx, (list, np.ndarray, tuple)):
            dirs = list(set(patchs).intersection(set(dir_name_or_idx)))
            if len(dirs) != len(dir_name_or_idx):
                print(f'Warning: not all directions were recognized: {dir_name_or_idx} != {dirs}')
        elif isinstance(dir_name_or_idx, (int, np.int64, slice)):
            dirs = patchs[dir_name_or_idx]
        elif dir_name_or_idx == 'all':
            dirs = patchs
        elif isinstance(dir_name_or_idx, str) and dir_name_or_idx in patchs:
            dirs = [dir_name_or_idx]
        elif isinstance(dir_name_or_idx, str) and dir_name_or_idx.startswith('!'):
            if dir_name_or_idx[1:] in patchs:
                dirs = patchs.copy()
                dirs.remove(dir_name_or_idx[1:])
        return dirs

    def copy(self, msins, msouts):
        futils.zip_copytree(msins, msouts, self.get_sky_model(''))
        futils.zip_copy(msins, msouts, self.get_sky_model_bbs(''))


class CalSettings(object):

    def __init__(self, parmdb='instrument.h5', sol_int=1, sol_int_flux_per_slot_per_sec=0,
                 sol_int_min=2, sol_int_max=120, mode='fulljones', uv_min=None, smoothnessconstraint=4e6,
                 extra={}, **kargs):
        self.parmdb = parmdb
        self.sol_int = sol_int
        self.cal_mode = mode
        self.uv_min = uv_min
        self.extra_params = extra
        self.sol_int_min = sol_int_min
        self.sol_int_max = sol_int_max
        self.sol_int_flux_per_slot_per_sec = sol_int_flux_per_slot_per_sec
        self.smoothnessconstraint = smoothnessconstraint
        self.freq_cache = {}
        self.interval_cache = {}

    def get_time_interval(self, msin):
        if msin not in self.interval_cache:
            self.interval_cache[msin] = msutils.get_ms_time_interval(msin)
        return self.interval_cache[msin]

    def get_freq(self, msin):
        if msin not in self.freq_cache:
            self.freq_cache[msin] = msutils.get_ms_freqs(msin)[0].mean()
        return self.freq_cache[msin]

    def get_uv_min(self, msin):
        if not self.uv_min:
            return self.uv_min
        if isinstance(self.uv_min, (float, int)):
            return self.uv_min
        fmhz = self.get_freq(msin) * 1e-6
        fmhzs, lims = list(zip(*sorted(self.uv_min.items())))
        fmhzs = [int(k) for k in fmhzs]
        i = np.where(np.array(fmhzs) - fmhz >= 0)[0][0]
        return lims[i]

    def get_sol_int(self, msin, patch_i):
        if self.sol_int_flux_per_slot_per_sec is 0:
            return int(self.sol_int)

        int_time = self.get_time_interval(msin)
        b = (self.sol_int_flux_per_slot_per_sec / patch_i / int_time)
        if b >= self.sol_int_max:
            return self.sol_int_max
        f = utils.factors(self.sol_int_max)
        c = f[(f - b) > 0][0]
        return int(max(self.sol_int_min, c))


class MultiCommands(object):

    def __init__(self, worker_settings, name, exec_name, max_time=None):
        self.worker_settings = worker_settings
        self.exec_name = exec_name
        self.name = name
        self.max_time = max_time
        if self.max_time == 0:
            self.max_time = None

    def build_command(self, msin):
        parameters = self.get_parameters(msin)
        if parameters is None:
            return None
        cmd = f'cd {cwd}; {self.exec_name} {" ".join(parameters)}'
        return cmd

    def get_parameters(self, msin):
        return []

    def get_out_file(self, msin):
        return msin

    def get_log_file(self, msin):
        return None

    def run(self, in_files):
        print(f'Starting {self.name} ...')
        kargs = self.worker_settings.copy()
        del kargs['run_on_file_host']
        del kargs['run_on_file_host_pattern']
        pool = worker.get_worker_pool(self.name, max_time=self.max_time, **kargs)
        out_files = []

        for in_file in in_files:
            host = None
            if self.worker_settings.run_on_file_host and self.worker_settings.run_on_file_host_pattern:
                r = re.search(self.worker_settings.run_on_file_host_pattern, in_file)
                if r is not None:
                    host = r.group(1)
            in_file = os.path.normpath(in_file)
            out_file = self.get_out_file(in_file)
            cmd = self.build_command(in_file)
            if cmd is None:
                print(f'Skipping {in_file}')
                continue
            pool.add(cmd, output_file=self.get_log_file(in_file), run_on_host=host)
            out_files.append(out_file)

        pool.execute()

        return out_files


class AoQuality(MultiCommands):

    def __init__(self, worker_settings, corrected_data=True, max_time=None):
        MultiCommands.__init__(self, worker_settings, 'AoQuality', 'aoquality collect', max_time=max_time)
        self.corrected_data = corrected_data

    def get_parameters(self, msin):
        p = [msin]
        if self.corrected_data:
            p.append('-d CORRECTED_DATA')
        return p


class MakeAppSkyModel(MultiCommands):

    def __init__(self, worker_settings, app_sky_model_name, int_sky_models,
                 build_sky_model_settings):
        MultiCommands.__init__(self, worker_settings, 'MakeAppSkyModel', 'modeltool attenuate')
        self.app_sky_model_name = app_sky_model_name
        self.int_sky_models = int_sky_models
        self.s_bsm = build_sky_model_settings

    def get_parameters(self, msin):
        out_file = SkyModel(self.app_sky_model_name).get_sky_model_bbs(msin)
        futils.mkdir(os.path.dirname(out_file))

        p = [msin, " ".join(self.int_sky_models),
             f'-m {self.s_bsm.min_flux}',
             f'-p {self.s_bsm.min_flux_path}',
             f'-e {self.s_bsm.ateam_min_elevation}',
             f'-o {out_file}']

        for patch in self.s_bsm.ateam_always_keep:
            p.append(f'-k {patch}')

        for patch in self.s_bsm.ateam_remove:
            p.append(f'-r {patch}')

        return p


class ConcatenateSkyModel(MultiCommands):

    def __init__(self, worker_settings, output_sky_model_name, input_sky_model_names,
                 build_sky_model_settings):
        MultiCommands.__init__(self, worker_settings, 'ConcatenateSkyModel', 'modeltool concatenate')
        self.output_sky_model_name = output_sky_model_name
        self.input_sky_model_names = input_sky_model_names
        self.s_bsm = build_sky_model_settings

    def get_parameters(self, msin):
        out_file = SkyModel(self.output_sky_model_name).get_sky_model_bbs(msin)
        inp_files = [SkyModel(name).get_sky_model_bbs(msin) for name in self.input_sky_model_names]
        futils.mkdir(os.path.dirname(out_file))

        p = [msin, " ".join(inp_files),
             f'-m {self.s_bsm.min_flux}',
             f'-p {self.s_bsm.min_flux_path}',
             f'-e {self.s_bsm.ateam_min_elevation}',
             f'-o {out_file}']

        for patch in self.s_bsm.ateam_always_keep:
            p.append(f'-k {patch}')

        for patch in self.s_bsm.ateam_remove:
            p.append(f'-r {patch}')

        return p


class MakeSourceDB(MultiCommands):

    def __init__(self, worker_settings, app_sky_model_name):
        MultiCommands.__init__(self, worker_settings, 'MakeSourceDB', 'makesourcedb')
        self.app_sky_model_name = app_sky_model_name

    def get_parameters(self, msin):
        sky_model = SkyModel(self.app_sky_model_name)
        return [f'in={sky_model.get_sky_model_bbs(msin)}', f'out={sky_model.get_sky_model(msin)}', 'append=false']


class PlotSolutions(MultiCommands):

    def __init__(self, worker_settings, parmdb_in_name, clip=False):
        self.parmdb_in_name = parmdb_in_name
        self.clip = clip
        MultiCommands.__init__(self, worker_settings, 'PlotSol', 'soltool plot')

    def get_parameters(self, msin):
        parmdb = f'{msin}/{self.parmdb_in_name}'
        if not os.path.exists(parmdb):
            return None
        p = [parmdb, f'--plot_dir=plots_{os.path.basename(self.parmdb_in_name.split(".")[0])}']
        if self.clip:
            p.append('--clip')
        return p


class SmoothSolutions(MultiCommands):

    def __init__(self, worker_settings, parmdb_in_name, time_min=15, freq_mhz=2, main_time_min=None,
                 main_freq_mhz=None, clip_nsigma=4):
        self.parmdb_in_name = parmdb_in_name
        self.fwhm_time = time_min
        self.fwhm_freq = freq_mhz
        self.main_fwhm_time = main_time_min
        self.main_fwhm_freq = main_freq_mhz

        if self.main_fwhm_freq is None:
            self.main_fwhm_freq = freq_mhz
        if self.main_fwhm_time is None:
            self.main_fwhm_time = freq_mhz

        self.clip_nsigma = clip_nsigma
        MultiCommands.__init__(self, worker_settings, 'SmoothSol', 'soltool smooth')

    def get_parameters(self, msin):
        parmdb = f'{msin}/{self.parmdb_in_name}'
        if not os.path.exists(parmdb):
            return None

        p = [parmdb, f'--fwhm_time={self.fwhm_time}', f'--fwhm_freq={self.fwhm_freq}',
             f'--main_fwhm_time={self.main_fwhm_time}', f'--main_fwhm_freq={self.main_fwhm_freq}',
             f'--clip_nsigma={self.clip_nsigma}']
        return p


class CopyFlag(MultiCommands):

    def __init__(self, worker_settings, in_postfix, out_postfix):
        self.in_postfix = in_postfix
        self.out_postfix = out_postfix
        MultiCommands.__init__(self, worker_settings, 'CopyFlag', 'flagtool copy')

    def get_parameters(self, msin):
        ms_flag = f'_{self.in_postfix}.MS'.join(msin.rsplit(f'_{self.out_postfix}.MS', 1))
        return [ms_flag, msin]


class RestoreOrBackupFlag(MultiCommands):

    def __init__(self, worker_settings, flag_name='pre_cal_flags.h5'):
        self.flag_name = flag_name
        MultiCommands.__init__(self, worker_settings, 'RestoreOrBackupFlag', 'flagtool')

    def get_parameters(self, msin):
        flag_file = os.path.join(msin, self.flag_name)
        if os.path.exists(flag_file):
            return ['restore', msin, flag_file]
        return ['backup', msin, flag_file]


class DPPP(MultiCommands):

    def __init__(self, worker_settings, name, parset, max_time=None):
        self.parset = parset
        MultiCommands.__init__(self, worker_settings, name, 'DPPP', max_time=max_time)

    def get_log_file(self, msin):
        log_dir = os.path.join(os.path.dirname(msin), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_name = self.name.replace(' ', '_').lower()
        date_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        return f'{log_dir}/{date_str}_{os.path.basename(msin)}_{log_name}.log'

    def build_command(self, msin):
        parameters = self.get_parameters(msin)
        if parameters is None:
            return None
        return f'cd {cwd}; {self.exec_name} {self.parset} msin={msin} {" ".join(parameters)}'

    def get_directions_str(self, directions):
        if isinstance(directions, str):
            return f'[[{directions}]]'
        return '[%s]' % ','.join(['[%s]' % k for k in directions])

    def get_directions_str_single_list(self, directions):
        if isinstance(directions, str):
            return f'[{directions}]'
        return '[%s]' % ','.join(['%s' % k for k in directions])


class CopyDataCol(DPPP):

    def __init__(self, worker_settings, col_in, col_out):
        self.col_in = col_in
        self.col_out = col_out
        DPPP.__init__(self, worker_settings, 'CopyCol', '')

    def get_parameters(self, msin):
        return ['numthreads=200', f'msin.datacolumn={self.col_in}',
                f'msout=.', f'msout.datacolumn={self.col_out}', 'steps=[]']


class CopyMS(DPPP):

    def __init__(self, worker_settings, col_in, ms_out_postfix):
        self.col_in = col_in
        self.postfix = ms_out_postfix
        DPPP.__init__(self, worker_settings, 'CopyMS', '')

    def get_out_file(self, msin):
        return f'_{self.postfix}.MS'.join(msin.rsplit('.MS', 1))

    def get_parameters(self, msin):
        msout = self.get_out_file(msin)
        return ['numthreads=200', 'msout.overwrite=true', f'msin.datacolumn={self.col_in}',
                f'msout={msout}', f'msout.datacolumn=DATA', 'steps=[]']


class DDEcal(DPPP):

    def __init__(self, worker_settings, cal_settings, sky_model, data_col='DATA', directions='all'):
        self.settings = cal_settings
        self.sky_model = sky_model
        self.directions = directions
        self.data_col = data_col
        self.data_col_out = data_col

        DPPP.__init__(self, worker_settings, 'DDEcal', get_cal_config('dppp_ddecal.parset'))

    def get_parameters(self, msin):
        parmdb_out = f'{msin}/{self.settings.parmdb}'

        if os.path.exists(parmdb_out):
            os.remove(parmdb_out)

        directions = self.sky_model.get_directions(msin, self.directions)

        sol_int = self.settings.get_sol_int(msin, self.sky_model.get_patch_i(msin, directions))

        p = []
        p.append(f'msin.datacolumn={self.data_col}')
        p.append(f'msout.datacolumn={self.data_col_out}')
        p.append(f'cal.sourcedb={self.sky_model.get_sky_model(msin)}')
        p.append(f'cal.directions={self.get_directions_str(directions)}')
        p.append(f'cal.h5parm={parmdb_out}')
        p.append(f'cal.solint={sol_int}')
        p.append(f'cal.mode={self.settings.cal_mode}')
        p.append(f'cal.smoothnessconstraint={self.settings.smoothnessconstraint}')

        for k, v in self.settings.extra_params.items():
            p.append(f'cal.{k}={v}')

        if self.settings.uv_min:
            p.append(f'cal.uvlambdamin={self.settings.get_uv_min(msin)}')

        return p


class DDEcalAvg(DDEcal):

    def __init__(self, worker_settings, cal_settings, sky_model, time_avg=4,
                 freq_avg=1, data_col='DATA', directions='Main'):
        DDEcal.__init__(self, worker_settings, cal_settings, sky_model, data_col=data_col, directions=directions)
        self.data_col_out = 'DATA'
        self.time_avg = time_avg
        self.freq_avg = freq_avg

    def get_out_file(self, msin):
        p = pathlib.Path(msin)
        return str(p.parent / ('tmp_' + p.name))

    def get_parameters(self, msin):
        msout = self.get_out_file(msin)

        p = DDEcal.get_parameters(self, msin)
        p.append('steps=[avg,cal]')
        p.append('avg.type=averager')
        p.append(f'avg.timestep={self.time_avg}')
        p.append(f'avg.freqstep={self.freq_avg}')
        p.append(f'msout={msout}')
        p.append(f'msout.overwrite=true')

        return p


class Predict(DPPP):

    def __init__(self, worker_settings, cal_settings, sky_model, col_out, directions='all', max_time=None):
        self.settings = cal_settings
        self.sky_model = sky_model
        self.col_out = col_out
        self.directions = directions

        if not self.settings.parmdb.strip():
            cal_file = 'dppp_predict_nocal.parset'
        else:
            cal_file = 'dppp_predict.parset'
            if self.settings.cal_mode == 'diagonal':
                cal_file = 'dppp_predict_diag.parset'

        DPPP.__init__(self, worker_settings, 'Predict', get_cal_config(cal_file), max_time=max_time)

    def get_parameters(self, msin):
        directions = self.sky_model.get_directions(msin, self.directions)
        if not directions:
            return None

        p = []
        p.append(f'msin.datacolumn={self.col_out}')
        p.append(f'msout.datacolumn={self.col_out}')
        p.append(f'predict.sourcedb={self.sky_model.get_sky_model(msin)}')
        if self.settings.parmdb.strip():
            p.append(f'predict.directions={self.get_directions_str(directions)}')
            p.append(f'predict.applycal.parmdb={msin}/{self.settings.parmdb}')
        else:
            p.append(f'predict.sources={self.get_directions_str_single_list(directions)}')

        return p


class Subtract(DPPP):

    def __init__(self, worker_settings, cal_settings, sky_model, col_in, col_out, directions='all', max_time=None):
        self.settings = cal_settings
        self.sky_model = sky_model
        self.col_in = col_in
        self.col_out = col_out
        self.directions = directions

        if not self.settings.parmdb.strip():
            cal_file = 'dppp_subtract_nocal.parset'
        else:
            cal_file = 'dppp_subtract.parset'
            if self.settings.cal_mode == 'diagonal':
                cal_file = 'dppp_subtract_diag.parset'

        DPPP.__init__(self, worker_settings, 'Subtract', get_cal_config(cal_file), max_time=max_time)

    def get_parameters(self, msin):
        directions = self.sky_model.get_directions(msin, self.directions)
        if not directions:
            return None

        p = []
        p.append(f'msin.datacolumn={self.col_in}')
        p.append(f'msout.datacolumn={self.col_out}')
        p.append(f'sub.sourcedb={self.sky_model.get_sky_model(msin)}')
        if self.settings.parmdb.strip():
            p.append(f'sub.directions={self.get_directions_str(directions)}')
            p.append(f'sub.applycal.parmdb={msin}/{self.settings.parmdb}')
        else:
            p.append(f'sub.sources={self.get_directions_str_single_list(directions)}')

        return p


class Peel(object):

    def __init__(self, sky_model):
        self.sky_model = sky_model

    def iterations(self, msins):
        n_pactchs = np.array([len(self.sky_model.get_patchs(msin, include_main=False)) for msin in msins])
        for i in np.arange(1, max(n_pactchs) + 1):
            yield i, np.array(msins)[n_pactchs >= i]


class PeelPreSubtract(Subtract):

    def __init__(self, peel_iter, worker_settings, cal_settings, sky_model, col_in='DATA', max_time=None):
        Subtract.__init__(self, worker_settings, cal_settings, sky_model, col_in, 'DATA_PEEL',
                          directions=slice(peel_iter, None), max_time=max_time)
        self.name = f'PeelPreSub {peel_iter}'
        self.peel_iter = peel_iter


class PeelCal(DDEcal):

    def __init__(self, peel_iter, worker_settings, cal_settings, sky_model, data_col='DATA_PEEL'):
        DDEcal.__init__(self, worker_settings, cal_settings, sky_model, data_col=data_col,
                        directions=peel_iter - 1)
        self.name = f'PeelCal {peel_iter}'
        self.peel_iter = peel_iter


class PeelPostSubtract(Subtract):

    def __init__(self, peel_iter, worker_settings, cal_settings, sky_model, data_col='DATA', max_time=None):
        Subtract.__init__(self, worker_settings, cal_settings, sky_model, data_col, data_col,
                          directions=peel_iter - 1, max_time=max_time)
        self.name = f'PeelPostSub {peel_iter}'
        self.peel_iter = peel_iter


class PeelPreSubtractPhaseShifted(PeelPreSubtract):

    def __init__(self, peel_iter, worker_settings, cal_settings, sky_model, col_in='DATA',
                 max_time=None, time_avg=4, freq_avg=1):
        PeelPreSubtract.__init__(self, peel_iter, worker_settings, cal_settings, sky_model,
                                 col_in=col_in, max_time=max_time)
        self.time_avg = time_avg
        self.freq_avg = freq_avg

    def get_out_file(self, msin):
        p = pathlib.Path(msin)
        return str(p.parent / ('tmp_' + p.name))

    def get_parameters(self, msin):
        coord = self.sky_model.get_patch_coord(msin, self.sky_model.get_patchs(msin)[self.peel_iter - 1])
        msout = self.get_out_file(msin)

        p = PeelPreSubtract.get_parameters(self, msin)
        p.append('steps=[sub,phaseshift,avg]')
        p.append('phaseshift.type=phaseshifter')
        p.append('avg.type=average')
        p.append(f'phaseshift.phasecenter=[{coord[0].deg}deg,{coord[1].deg}deg]')
        p.append(f'avg.timestep={self.time_avg}')
        p.append(f'avg.freqstep={self.freq_avg}')
        p.append(f'msout={msout}')
        p.append(f'msout.datacolumn=DATA')
        p.append(f'msout.overwrite=true')

        return p


class PeelPostSubtractPhaseShift(PeelPostSubtract):

    def __init__(self, peel_iter, worker_settings, cal_settings, sky_model, data_col='DATA', max_time=None,
                 coord_phase_back=None):
        PeelPostSubtract.__init__(self, peel_iter, worker_settings, cal_settings, sky_model,
                                  data_col=data_col, max_time=max_time)
        self.coord_phase_back = coord_phase_back

    def get_out_file(self, msin):
        p = pathlib.Path(msin)
        return str(p.parent / ('tmp_' + p.name))

    def get_parameters(self, msin):
        coord = self.sky_model.get_patch_coord(msin, self.sky_model.get_patchs(msin)[self.peel_iter - 1])
        msout = self.get_out_file(msin)

        if self.coord_phase_back:
            coord_phase_back = f'[{self.coord_phase_back.ra.deg}deg,{self.coord_phase_back.dec.deg}deg]'
        else:
            coord_phase_back = '[]'

        p = PeelPostSubtract.get_parameters(self, msin)
        p.append('steps=[phaseshift,sub,phaseshiftback]')
        p.append('phaseshift.type=phaseshifter')
        p.append('phaseshiftback.type=phaseshifter')
        p.append(f'phaseshift.phasecenter=[{coord[0].deg}deg,{coord[1].deg}deg]')
        p.append(f'phaseshiftback.phasecenter={coord_phase_back}')
        p.append(f'msout={msout}')
        p.append(f'msout.datacolumn=DATA')
        p.append(f'msout.overwrite=true')

        return p


class ApplyCal(DPPP):

    def __init__(self, worker_settings, cal_settings, col_in='DATA', col_out='CORRECTED_DATA', direction='Main'):
        self.col_in = col_in
        self.col_out = col_out
        self.direction = direction
        self.settings = cal_settings
        self.direction = direction
        dppp_file = 'dppp_applycal.parset'
        if self.settings.cal_mode == 'diagonal':
            dppp_file = 'dppp_applycal_diag.parset'

        DPPP.__init__(self, worker_settings, 'ApplyCal', get_cal_config(dppp_file))

    def get_parameters(self, msin):
        p = []
        p.append(f'apply.parmdb={msin}/{self.settings.parmdb}')
        p.append(f'apply.direction=[{self.direction}]')
        p.append(f'msin.datacolumn={self.col_in}')
        p.append(f'msout.datacolumn={self.col_out}')

        return p


class FlagPostCal(DPPP):

    def __init__(self, worker_settings, strategy='nenufar_1s1c'):
        if strategy == 'nenufar_1s1c':
            strategy = get_cal_config('LBAdefault_after_di.rfis')
        self.strategy = strategy
        DPPP.__init__(self, worker_settings, 'FlagPostCal', get_cal_config('dppp_flagger.parset'))

    def get_parameters(self, msin):
        p = []
        p.append(f'flag.strategy={self.strategy}')

        return p


class FlagBadStations(DPPP):

    def __init__(self, worker_settings, nsigma=5):
        self.nsigma = nsigma
        DPPP.__init__(self, worker_settings, 'FlagBadStations', get_cal_config('dppp_preflag.parset'))

    def get_parameters(self, msin):
        to_flag = flagutils.get_badstatsions(msin, self.nsigma)
        if len(to_flag) == 0:
            return None

        to_flag = ','.join([str(k) for k in to_flag])
        return [f'flag.baseline={to_flag}']


class FlagBaselines(DPPP):

    def __init__(self, worker_settings, baselines=''):
        self.baselines = baselines
        DPPP.__init__(self, worker_settings, 'FlagBaselines', get_cal_config('dppp_preflag.parset'))

    def get_baselines(self, msin):
        return self.baselines

    def get_parameters(self, msin):
        to_flag = self.get_baselines(msin)
        if len(to_flag) == 0:
            return None

        return [f'flag.baseline="{to_flag}"']


class FlagFreqs(DPPP):

    def __init__(self, worker_settings, fmhz_range):
        self.fmhz_range = fmhz_range
        DPPP.__init__(self, worker_settings, 'FlagFreqs', get_cal_config('dppp_preflag.parset'))

    def get_parameters(self, msin):
        return [f'flag.freqrange="{self.fmhz_range[0]} .. {self.fmhz_range[1]} MHz"']


class FlagBadBaselines(FlagBaselines):

    def __init__(self, worker_settings, nsigma_stations=5, nsigma_baselines=8):
        self.nsigma_stations = nsigma_stations
        self.nsigma_baselines = nsigma_baselines
        FlagBaselines.__init__(self, worker_settings)

    def get_baselines(self, msin):
        return flagutils.get_badbaselines(msin, self.nsigma_stations, self.nsigma_baselines)


class SSINSFlagger(MultiCommands):

    def __init__(self, worker_settings, config='default', plot_dir=None, data_col='CORRECTED_DATA'):
        self.config = config
        self.plot_dir = plot_dir
        self.data_col = data_col
        MultiCommands.__init__(self, worker_settings, 'SSINS', 'flagtool ssins')

    def get_parameters(self, msin):
        p = [msin, f'--data_col={self.data_col}']
        if self.plot_dir is not None:
            plot_dir = os.path.join(msin, self.plot_dir)
            futils.mkdir(plot_dir)
            p.append(f'--plot_dir={plot_dir}')
        if self.config != 'default':
            p.append(f'--config={self.config}')
        return p


def main():
    pass

    # ret = TestMulti('test').run(msins)
    # print(ret)

    # AoQuality().run(msins)
    # PostProcessSolutions('instru_test.h5').run(msins)

    # CopyDataCol('DATA', 'SUBTRACTED_DATA').run(msins)

    # for i in range(3):
    #     parmdb_iter = f'instrument_peel_iter{i + 1}.h5'
    #     PeelCalibrate(i + 1, 'instrument_smooth.h5', parmdb_iter, sol_int_fct).run(msins)
    #     PostProcessSolutions(parmdb_iter).run(msins)
    #     PeelSubtract('SUBTRACTED_DATA', 'SUBTRACTED_DATA', parmdb_iter, i + 1).run(msins)

    # ApplyCal('SUBTRACTED_DATA', 'CORRECTED_DATA', 'instrument_smooth.h5', 'Main').run(msins)
    # AoQuality().run(msins)

    # FlagPostCal().run(msins)


if __name__ == '__main__':
    main()
