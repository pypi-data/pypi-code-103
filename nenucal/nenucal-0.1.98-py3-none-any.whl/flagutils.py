import os

import numpy as np

import astropy.stats as astats

from casacore import tables

from .msutils import mean_consecutive, diff_consecutive, MsDataCube, FlagManager

np.seterr(divide='ignore', invalid='ignore')


def ssins_flagger(m_vis, ntime_avg, config):
    m_vis_sum, m_vis_sum_n = mean_consecutive(diff_consecutive(m_vis, axis=1), axis=1, n=ntime_avg, return_n=True)
    ss_spc = np.mean(abs((m_vis_sum * np.sqrt(m_vis_sum_n))) ** 2, axis=(2, 3))
    for nsigma in config["nsigmas"][str(ntime_avg)]:
        ss_spc = ss_spc - np.ma.median(ss_spc, axis=1)[:, None]
        ss_spc = astats.sigma_clip(ss_spc, sigma=nsigma, stdfunc=astats.mad_std)

    mask = np.repeat(ss_spc.mask, 2 * ntime_avg, axis=1)[:, :m_vis.shape[1]]
    if mask.shape[1] < m_vis.shape[1]:
        mask = np.concatenate([mask, mask[:, -2:-1]], axis=1)

    mask[mask.sum(axis=1) > config["percentage_freq_full_flag"] * mask.shape[1]] = 1
    n_freq_full_flag = mask.shape[0] - mask.sum(axis=0).max()
    mask[:, mask.sum(axis=0) - n_freq_full_flag > config["percentage_time_full_flag"] *
         (mask.shape[0] - n_freq_full_flag)] = 1

    percentile_flag = 100. * mask.sum() / mask.size
    print(f'-> SSINS with {ntime_avg} time averaging: {percentile_flag:.2f} % time/freq flagged')

    return (np.zeros_like(m_vis.mask) + mask[:, :, None, None]).astype(bool)


def time_freq_threshold_flagger(mask, threshold):
    mask_time_freq = (1. * mask.sum(axis=(2, 3)) / (mask.shape[2] * mask.shape[3]) > threshold)
    percentile_flag = 100. * mask_time_freq.sum() / mask_time_freq.size
    print(f'-> Time/freq flagging with threshold {threshold}: {percentile_flag:.2f} % time/freq flagged')

    return (np.zeros_like(mask) + mask_time_freq[:, :, None, None]).astype(bool)


def baseline_threshold_flagger(mask, threshold):
    idx_freq_full_flag = (mask[:, :, :, 0].sum(axis=(1, 2)) == mask.shape[1] * mask.shape[2])

    mask_baseline = (1. * mask[~idx_freq_full_flag].sum(axis=(0, 1, 3)) /
                     (mask[~idx_freq_full_flag].shape[0] * mask.shape[1] * mask.shape[3]) > threshold)
    percentile_flag = 100. * mask_baseline.sum() / mask_baseline.size
    print(f'-> Baseline flagging with threshold {threshold}: {percentile_flag:.2f} % time/freq flagged')

    return (np.zeros_like(mask) + mask_baseline[None, None, :, None]).astype(bool)


def snapshot_threshold_flagger(mask, threshold):
    idx_freq_full_flag = (mask[:, :, :, 0].sum(axis=(1, 2)) == mask.shape[1] * mask.shape[2])
    if mask[~idx_freq_full_flag].sum() / float(mask[~idx_freq_full_flag].size) > threshold:
        print(f'-> Fully flag the MS as the flag ratio is above threshold of {threshold}')
        return np.ones_like(mask)
    return mask


def get_ss_spc(m_vis, zero_mean=False):
    ss_spc = np.mean(abs(diff_consecutive(m_vis, axis=1)) ** 2, axis=(2, 3))
    if zero_mean:
        ss_spc = ss_spc - np.ma.median(ss_spc, axis=1)[:, None]

    return ss_spc


def get_badstatsions(ms, nsigma):
    file = ms + '/QUALITY_BASELINE_STATISTIC'
    if not os.path.exists(file):
        print('Error: QUALITY_BASELINE_STATISTIC does not exits. Did you run aoquality ?')
        return []

    with tables.table(file, ack=False) as t:
        kind = t.getcol('KIND')
        a1 = t.getcol('ANTENNA1')
        a2 = t.getcol('ANTENNA2')
        v = t.getcol('VALUE')

    a_max = max(max(a1), max(a2))
    idx = kind == 7
    i = abs(v.mean(axis=1)[idx])
    aa1 = a1[idx]
    aa2 = a2[idx]
    i[aa1 == aa2] = np.nan
    stat = np.nanmedian(np.array([i[(aa1 == k) | (aa2 == k)] for k in range(a_max)]), axis=0)
    bad_statsions = np.where(astats.sigma_clip(stat, sigma=nsigma).mask > 0)[0]

    return bad_statsions


def get_badbaselines(ms, nsigma_station, nsigma_baseline):
    file = ms + '/QUALITY_BASELINE_STATISTIC'
    if not os.path.exists(file):
        print('Error: QUALITY_BASELINE_STATISTIC does not exits. Did you run aoquality ?')
        return []

    with tables.table(file, ack=False) as t:
        kind = t.getcol('KIND')
        a1 = t.getcol('ANTENNA1')
        a2 = t.getcol('ANTENNA2')
        v = t.getcol('VALUE')

    a_max = max(max(a1), max(a2))
    idx = (kind == 7)
    i = np.ma.array(abs(v[idx].mean(axis=1)))
    a1 = a1[idx]
    a2 = a2[idx]
    i[a1 == a2] = np.ma.masked
    i[i == 0] = np.ma.masked
    stat = np.median(np.array([i[(a1 == k) | (a2 == k)] for k in range(a_max)]), axis=0)
    badstations = np.where(astats.sigma_clip(stat, sigma=nsigma_station).mask > 0)[0].tolist()
    i[np.sum([(a1 == k) | (a2 == k) for k in badstations], axis=0).astype(bool) > 0] = np.ma.masked
    mask_before = i.mask
    i = astats.sigma_clip(i, sigma=nsigma_baseline)
    badbaselines = ['%s&%s' % (k, v) for k, v in zip(a1[(i.mask ^ mask_before)], a2[(i.mask ^ mask_before)])]

    return ';'.join([str(k) for k in badstations] + badbaselines)


def flag_badscans(mss, umin=20, umax=400, data_col='CORRECTED_DATA', nsigma=5):
    all_var = np.array([np.var(MsDataCube.load(ms, umin, umax, data_col, verbose=False).data_dt,
                               axis=(0, 1, 2)) for ms in mss])
    bad_scans = astats.sigma_clip(all_var, sigma=nsigma, axis=0, stdfunc=astats.mad_std).mask.sum(axis=1) > 0
    print('Flagging bad scans ...')
    for ms in np.array(mss)[bad_scans]:
        FlagManager.fully_flag(ms)
