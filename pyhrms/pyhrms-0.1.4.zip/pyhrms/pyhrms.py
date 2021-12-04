import pandas as pd
import matplotlib.pyplot as plt
import time
import pymzml
import scipy.signal
from numpy import where, argmin, median, std, zeros, argmax, mean
from numba import jit
from numba.typed import List
from glob import glob
import numpy as np
import scipy.interpolate as interpolate
import multiprocessing as mp
from molmass import Formula
import os
import json
import shutil
import sys
from tqdm import tqdm
# %config InlineBackend.figure_format = 'retina'


def peak_picking(df1, ms_error=50, threshold=15, rt_range=[0, 20], i_threshold=200):
    '''
    Perform peak picking for a whole LC-MS file, and return the result.
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param ms_error: The ms difference between two selected masses (for extraction), this parameter may not affect the final result, but 50 is recommended.
    :param threshold: This parameter is used for the function of peak_finding(eic, threhold)
    :return:
    '''
    index = ms_locator(df1, ms_error)  ### 获得ms locator
    start_t = time.time()
    RT = np.array(df1.columns)
    l = len(index)
    num = 0
    num_p = 0
    data = []
    for i in tqdm(range(l - 1),desc='Finding peaks'):
        df2 = df1.iloc[index[i]:index[i + 1]]
        a = np.array(df2).T  ### 将dataframe转换成np.array
        if len(a[0]) != 0:  ### 判断切片结果是否为0
            extract_c = a.sum(axis=1)
            peak_index, left, right = peak_finding(extract_c, threshold)  ## 关键函数，峰提取
            if len(peak_index) != 0:  ### 判断是否找到峰
                df3 = df2[df2.columns[peak_index]]
                rt = np.round(RT[peak_index], 2)
                intensity = np.round(np.array(df3.max().values), 0)
                mz = np.round(np.array(df3.idxmax().values), 4)
                name = 'peak' + str(num_p)
                locals()[name] = np.array([rt, mz, intensity]).T
                data.append(locals()[name])
      
    peak_info = np.concatenate(data)
    peak_info_df = pd.DataFrame(data=peak_info, columns=['rt', 'mz', 'intensity'])
    peak_all = peak_info_df[peak_info_df['intensity'] > i_threshold]
    peak_all = peak_all[(peak_all['rt'] < rt_range[1]) & (peak_all['rt'] > rt_range[0])].sort_values(
        by='intensity').reset_index(drop=True)
    return peak_all


def ms_locator(df1, ppm=50):
    '''
    For pick picking, selecting a series of mass locators for 50-1000.
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param ppm: the mass difference between two locators
    :return: mass locators
    '''

    @jit(nopython=True)
    def find_locator(list1, error):
        locators = []
        locator = list1[0]
        for i in range(len(list1)):
            if list1[i] > locator:
                locators.append(i)
                locator *= (1 + error * 1e-6)
        return locators

    ms_list = list(df1.index)
    typed_a = List()
    [typed_a.append(x) for x in ms_list]
    locators = find_locator(typed_a, ppm)
    return locators


def sep_scans(path, company):
    '''
    To separate scan for MS1, MS2 and lockspray. Only supported for Waters .raw and Agilent .d file
    :param path: The path for mzML files
    :return: ms1, ms2 and lockspray
    '''
    if company == 'Waters':
        a = time.time()
        print('\r Reading files...             ', end="")
        run = pymzml.run.Reader(path)
        ms1, ms2 = [], []
        lockspray = []
        for scan in run:
            if scan.id_dict['function'] == 1:
                ms1.append(scan)
            if scan.id_dict['function'] == 2:
                ms2.append(scan)
            if scan.id_dict['function'] == 3:
                lockspray.append(scan)
        b = time.time()
        time1 = round(b - a, 2)
        print(f'\r Reading files finished! Total time: {time1} s           ', end='')
        return ms1, ms2, lockspray
    elif company == 'Agilent':
        a = time.time()
        print('\r Reading files...             ', end="")
        run = pymzml.run.Reader(path)
        ms1, ms2 = [], []
        for i, scan in enumerate(run):
            if scan.ms_level == 1:
                ms1.append(scan)
            else:
                ms2.append(scan)
        b = time.time()
        time1 = round(b - a, 2)
        print(f'\r Reading files finished! Total time: {time1} s           ', end='')

        return ms1, ms2


def peak_finding(eic, threshold=15):
    '''
    finding peaks in a single extracted chromatogram,and return peak index, left valley index, right valley index.
    :param eic: extracted ion chromatogram data; e.g., [1,2,3,2,3,1...]
    :param threshold: define the noise level for a peak, 6 is recommend
    :return:peak index, left valley index, right valley index.
    '''
    peaks, _ = scipy.signal.find_peaks(eic, width=2)
    prominence = scipy.signal.peak_prominences(eic, peaks)
    peak_prominence = prominence[0]
    left = prominence[1]
    right = prominence[2]
    ### peak_picking condition 1: value of peak_prominence must be higher than
    len_pro = len(peak_prominence)
    if len(peak_prominence) == 0:
        peak_index, left, right = np.array([]), np.array([]), np.array([])
    else:
        median_1 = np.median(peak_prominence)  ### 获得中位数的值
        index_pos2 = where(prominence[0] > threshold * median_1)[0]
        peak_index = peaks[index_pos2]
        left = left[index_pos2]
        right = right[index_pos2]
    return peak_index, left, right


def extract(df1, mz, error=50):
    '''
    Extracting chromatogram based on mz and error.
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param mz: Targeted mass for extraction.
    :param error: mass error for extraction
    :return: rt,eic
    '''
    low = mz * (1 - error * 1e-6)
    high = mz * (1 + error * 1e-6)
    low_index = argmin(abs(df1.index.values - low))
    high_index = argmin(abs(df1.index.values - high))
    df2 = df1.iloc[low_index:high_index]
    rt = df1.columns.values
    if len(np.array(df2)) == 0:
        intensity = np.zeros(len(df1.columns))
    else:
        intensity = np.array(df2).T.sum(axis=1)
    return rt, intensity  ### 只返回RT和EIC


def gen_df_to_centroid(ms1, ms_round=4):
    '''
    Convert mzml data to a dataframe in centroid mode.
    :param ms1: ms scan list generated by the function of sep_scans(), or directed from pymzml.run.Reader(path).
    :return: A Dataframe
    '''
    t1 = time.time()
    l = len(ms1)
    num = 0
    print('\r Generating dataframe...             ', end="")
    ###将所有的数据转换成centroid格式，并将每个scan存在一个独立的变量scan(n)中
    for i in range(l):
        name = 'scan' + str(i)
        peaks, _ = scipy.signal.find_peaks(ms1[i].i.copy())
        locals()[name] = pd.Series(data=ms1[i].i[peaks], index=ms1[i].mz[peaks].round(ms_round),
                                   name=round(ms1[i].scan_time[0], 3))
        t2 = time.time()
        total_t = round(t2 - t1, 2)
        p = round(num / l * 100, 2)
        print(f'\r Reading each scans：{total_t} s, {num}/{l}, {p} %     ', end="")
        num += 1
    ### 将所有的变量汇总到一个列表中
    data = []
    for i in range(l):
        name = 'scan' + str(i)
        data.append(locals()[name])
    t3 = time.time()
    ## 开始级联所有数据
    print('\r Concatenating all the data...                   ', end="")
    df1 = pd.concat(data, axis=1)
    df2 = df1.fillna(0)
    t4 = time.time()
    t = round(t4 - t1, 2)
    print(f'\r Concat finished, Consumed time: {t} s            ', end='')
    return df2


def gen_df_raw(ms1, ms_round=4):
    '''
    Convert mzml data to a dataframe in profile mode.
    :param ms1: ms scan list generated by the function of sep_scans(), or directed from pymzml.run.Reader(path).
    :return: A Dataframe
    '''
    t1 = time.time()
    l = len(ms1)
    ###将每个scan存在一个独立的变量scan(n)中
    data = []
    for i in tqdm(range(l),desc='Reading each scans'):
        name = 'scan' + str(i)
        locals()[name] = pd.Series(data=ms1[i].i, index=ms1[i].mz.round(ms_round), name=round(ms1[i].scan_time[0], 3))
        data.append(locals()[name])
    ### 将所有的变量汇总到一个列表中
    ## 开始级联所有数据
    print('\r Concatenating all the data...                             ', end="")
    df1 = pd.concat(data, axis=1)
    df2 = df1.fillna(0)
    t4 = time.time()
    t = round(t4 - t1, 2)
    print(f'\r Concat finished, Consumed time: {t} s                     ', end='')
    return df2


def B_spline(x, y):
    '''
    Generating more data points for a mass peak using beta-spline based on x,y
    :param x: mass coordinates
    :param y: intensity
    :return: new mass coordinates, new intensity
    '''
    t, c, k = interpolate.splrep(x, y, s=0, k=4)
    N = 300
    xmin, xmax = x.min(), x.max()
    new_x = np.linspace(xmin, xmax, N)
    spline = interpolate.BSpline(t, c, k, extrapolate=False)
    return new_x, spline(new_x)


def cal_bg(data):
    '''
    :param data: data need to calculate the background
    :return: background value
    '''
    if len(data) > 5:
        Median = median(data)
        Max_value = max(data)
        STD = std(data)
        Mean = mean(data)
        if Median == 0:
            bg = Mean + STD
        elif Mean <= Median * 3:
            bg = Max_value
        elif Mean > Median * 3:
            bg = Median
    else:
        bg = 1000000
    return bg + 1


def peak_checking_plot(df1, mz, rt1, Type='profile', path=None):
    '''
    Evaluating/visulizing the extracted mz
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param mz: Targetd mass for extraction
    :param rt1: expected rt for peaks
    :return:
    '''

    fig = plt.figure(figsize=(12, 4))
    ### 检查色谱图ax
    ax = fig.add_subplot(121)
    rt, eic = extract(df1, mz, 50)
    rt2 = rt[where((rt > rt1 - 3) & (rt < rt1 + 3))]
    eic2 = eic[where((rt > rt1 - 3) & (rt < rt1 + 3))]
    ax.plot(rt2, eic2)
    ax.set_xlabel('Retention Time(min)', fontsize=12)
    ax.set_ylabel('Intensity', fontsize=12)
    peak_index = np.argmin(abs(rt - rt1))
    peak_height = max(eic[peak_index - 2:peak_index + 2])
    ax.scatter(rt1, peak_height * 1.05, c='r', marker='*', s=50)
    ##计算背景
    cut = int(len(eic2) / 3)
    bg_left, bg_right = cal_bg(eic2[:cut]), cal_bg(eic2[-cut:])
    rt3 = rt2[:cut]
    rt4 = rt2[-cut:]
    bg1 = zeros(cut) + bg_left
    bg2 = zeros(cut) + bg_right
    ax.plot(rt3, bg1)
    ax.plot(rt4, bg2)
    SN1 = round(peak_height / bg_left, 1)
    SN2 = round(peak_height / bg_right, 1)
    ax.set_title(f'SN_left:{SN1},         SN_right:{SN2}')
    ax.set_ylim(top=peak_height * 1.1, bottom=-peak_height * 0.05)

    ### 检查质谱图ax1
    ax1 = fig.add_subplot(122)
    width = 0.02
    spec = spec_at_rt(df1, rt1)  ## 提取到特定时间点的质谱图
    new_spec = target_spec(spec, mz, width=0.04)

    if Type == 'profile':
        mz_obs, error1, mz_opt, error2, resolution = evaluate_ms(new_spec, mz)
        ax1.plot(new_spec)
        ax1.bar(mz, max(new_spec.values), color='r', width=0.0005)
        ax1.bar(mz_opt, max(new_spec.values), color='g', width=0.0005)
        ax1.text(min(new_spec.index.values) + 0.005, max(new_spec.values) * 0.8,
                 f'mz_obs: {mz_obs},{error1} \n mz_opt:{mz_opt}, {error2}')
    else:
        ax1.bar(mz, max(new_spec.values), width=0.0002)

    ax1.set_title(f'mz_exp: {mz}')
    ax1.set_xlabel('m/z', fontsize=12)
    ax1.set_ylabel('Intensity', fontsize=12)
    ax1.set_xlim(mz - 0.05, mz + 0.05)

    if path == None:
        pass
    else:
        plt.savefig(path, dpi=1000)
        plt.close('all')


def peak_alignment(files_excel, rt_error=0.1, mz_error=0.015):
    '''
    Generating peaks information with reference mz/rt pair
    :param files_excel: files for excels of peak picking and peak checking;
    :param rt_error: rt error for merge
    :param mz_error: mz error for merge
    :return: Export to excel files
    '''
    print('\r Generating peak reference...        ', end='')
    peak_ref = gen_ref(files_excel, rt_error=rt_error, mz_error=mz_error)
    pd.DataFrame(peak_ref, columns=['rt', 'mz']).to_excel(os.path.split(files_excel[0])[0] + r'\\peak_ref.xlsx')
    j = 1
    for file in files_excel:
        print(f'\r for {j} files, generating alignment results...', end='')
        peak_p = pd.read_excel(file, index_col='Unnamed: 0').loc[:, ['rt', 'mz']].values
        peak_df = pd.read_excel(file, index_col='Unnamed: 0')
        new_all_index = []
        for i in range(len(peak_p)):
            rt1, mz1 = peak_p[i]
            index = np.where((peak_ref[:, 0] <= rt1 + rt_error) & (peak_ref[:, 0] >= rt1 - rt_error)
                             & (peak_ref[:, 1] <= mz1 + mz_error) & (peak_ref[:, 1] >= mz1 - mz_error))
            new_index = str(peak_ref[index][0][0]) + '_' + str(peak_ref[index][0][1])
            new_all_index.append(new_index)
        peak_df['new_index'] = new_all_index
        peak_df = peak_df.set_index('new_index')
        peak_df.to_excel(file.replace('.xlsx', '_alignment.xlsx'))
        j += 1





def peak_checking(peak_df, df1, error=50,profile=True,
                  i_threshold=200, SN_threshold=3):
    '''
    Processing extracted peaks, remove those false positives.
    :param peak_df: Extracted peaks generated by the function of peak_picking
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param error: For the function of extract(df,mz, error)
    :param i_threshold: filter peaks with intensity<i_threshold
    :param SN_threshold: filter peaks with sn<SN_threshold
    :return:
    '''
    if profile == True:
    
        final_result = pd.DataFrame()
        peak_num = len(peak_df['rt'])
        SN_all_left, SN_all_right, area_all, mz_obs_all, mz_opt_all, resolution_all = [], [], [], [], [], []
        for i in tqdm(range(peak_num),desc= 'Checking each peaks'):
            mz = peak_df.iloc[i]['mz']
            rt = peak_df.iloc[i]['rt']
            ### 第一步：处理色谱峰
            rt_e, eic_e = extract(df1, mz, error=error)
            peak_index = np.argmin(abs(rt_e - rt))  ## 找到特定时间点的索引
            rt_left = rt - 3
            rt_right = rt + 3
            peak_index_left = np.argmin(abs(rt_e - rt_left))  ## 找到 ±0.2min的索引
            peak_index_right = np.argmin(abs(rt_e - rt_right))
            try:
                peak_height = max(eic_e[peak_index - 2:peak_index + 2])
                other_peak = max(eic_e[peak_index - 5:peak_index + 5])
            except:
                peak_height = 1
                other_peak = 3
            rt_t, eic_t = rt_e[peak_index_left:peak_index_right], eic_e[peak_index_left:peak_index_right]
            try:
                area = scipy.integrate.simps(eic_e[peak_index - 40:peak_index + 40])
            except:
                area = scipy.integrate.simps(eic_e)
            if other_peak - peak_height > 1:
                bg_left, bg_right = 10000000, 10000000
            else:
                bg_left = cal_bg(eic_t[:int(len(eic_t) / 3)])
                bg_right = cal_bg(eic_t[-int(len(eic_t) / 3):])

            SN_left = round(peak_height / bg_left, 1)
            SN_right = round(peak_height / bg_right, 1)
            SN_all_left.append(SN_left)
            SN_all_right.append(SN_right)
            area_all.append(area)

            ### 第二步：处理质谱峰
            spec = spec_at_rt(df1, rt)
            new_spec = target_spec(spec, mz, width=0.04)

            mz_obs, error1, final_mz_opt, error2, resolution = evaluate_ms(new_spec, mz)
            mz_obs_all.append(mz_obs)
            mz_opt_all.append(final_mz_opt)
            resolution_all.append(resolution)
    
        final_result['SN_left'] = SN_all_left
        final_result['SN_right'] = SN_all_right
        final_result['area'] = list(map(int, area_all))
        final_result['mz'] = mz_obs_all
        final_result['intensity'] = peak_df['intensity'].values
        final_result['rt'] = peak_df['rt'].values
        final_result['resolution'] = resolution_all
        final_result['mz_opt'] = mz_opt_all
        ### 筛选条件，峰强度> i_threshold; 左边和右边SN至少一个大于SN_threshold
        final_result = final_result[(final_result['intensity'] > i_threshold) &
                                    ((final_result['SN_left'] > SN_threshold) | (final_result['SN_right'] > SN_threshold))]
        final_result = final_result.loc[:,
                       ['rt', 'mz', 'intensity', 'SN_left', 'SN_right', 'area', 'mz_opt', 'resolution']].sort_values(
            by='intensity').reset_index(drop=True)

        return final_result
    
    elif profile == False:
        final_result = pd.DataFrame()
        peak_num = len(peak_df['rt'])
        SN_all_left, SN_all_right, area_all = [], [], []
        for i in tqdm(range(peak_num),desc= 'Checking each peaks'):
            mz = peak_df.iloc[i]['mz']
            rt = peak_df.iloc[i]['rt']
            ### 第一步：处理色谱峰
            rt_e, eic_e = extract(df1, mz, error=error)
            peak_index = np.argmin(abs(rt_e - rt))  ## 找到特定时间点的索引
            rt_left = rt - 3
            rt_right = rt + 3
            peak_index_left = np.argmin(abs(rt_e - rt_left))  ## 找到 ±0.2min的索引
            peak_index_right = np.argmin(abs(rt_e - rt_right))
            try:
                peak_height = max(eic_e[peak_index - 2:peak_index + 2])
                other_peak = max(eic_e[peak_index - 5:peak_index + 5])
            except:
                peak_height = 1
                other_peak = 3
            rt_t, eic_t = rt_e[peak_index_left:peak_index_right], eic_e[peak_index_left:peak_index_right]
            try:
                area = scipy.integrate.simps(eic_e[peak_index - 40:peak_index + 40])
            except:
                area = scipy.integrate.simps(eic_e)
            if other_peak - peak_height > 1:
                bg_left, bg_right = 10000000, 10000000
            else:
                bg_left = cal_bg(eic_t[:int(len(eic_t) / 3)])
                bg_right = cal_bg(eic_t[-int(len(eic_t) / 3):])

            SN_left = round(peak_height / bg_left, 1)
            SN_right = round(peak_height / bg_right, 1)
            SN_all_left.append(SN_left)
            SN_all_right.append(SN_right)
            area_all.append(area)
        final_result['SN_left'] = SN_all_left
        final_result['SN_right'] = SN_all_right
        final_result['area'] = list(map(int, area_all))
        final_result['mz'] = peak_df['mz'].values
        final_result['intensity'] = peak_df['intensity'].values
        final_result['rt'] = peak_df['rt'].values

        ### 筛选条件，峰强度> i_threshold; 左边和右边SN至少一个大于SN_threshold
        final_result = final_result[(final_result['intensity'] > i_threshold) &
                                    ((final_result['SN_left'] > SN_threshold) | (final_result['SN_right'] > SN_threshold))]
        final_result = final_result.loc[:,
                       ['rt', 'mz', 'intensity', 'SN_left', 'SN_right', 'area']].sort_values(
            by='intensity').reset_index(drop=True)

        return final_result


def spec_at_rt(df1, rt):
    '''
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param rt:  rentention time for certain ms spec
    :return: ms spec
    '''
    index = argmin(abs(df1.columns.values - rt))
    spec = df1.iloc[:, index]
    return spec


def concat_alignment(files_excel):
    '''
    Concatenate all data and return
    :param files_excel: excel files
    :param mode: selected 'area' or 'intensity' for each sample
    :return: dataframe
    '''
    align = []
    data_to_concat = []
    for i in tqdm(range(len(files_excel)),desc='Finding all area files'):
        if 'area' in files_excel[i]:
            align.append(files_excel[i])
    for i in tqdm(range(len(align)),desc='Concatenating all areas'):
        name = 'data' + str(i)
        locals()[name] = pd.read_excel(align[i], index_col='Unnamed: 0')
        data_to_concat.append(locals()[name])
    final_data = pd.concat(data_to_concat, axis=1)
    return final_data


def formula_to_distribution(formula, adducts='+H', num=3):
    '''
    :param formula: molecular formula, e.g., ‘C13H13N3’
    :param adducts: ion adducts, '+H', '-H'
    :return: mz_iso, i_iso (np.array)
    '''
    f = Formula(formula)
    a = f.spectrum()
    mz_iso, i_iso = np.array([a for a in a.values()]).T
    i_iso = i_iso / i_iso[0] * 100
    if adducts == '+H':
        mz_iso += 1.00727647
    elif adducts == '-H':
        mz_iso -= 1.00727647
    mz_iso = mz_iso.round(4)
    i_iso = i_iso.round(1)
    return mz_iso[:num], i_iso[:num]


def add_ms_values(new_spec):
    '''
    :param new_spec: the spectrum (pandas.Series)
    :return:  peak_mz,peak_i
    '''
    peaks, _ = scipy.signal.find_peaks(new_spec.values)
    peak3 = new_spec.iloc[peaks].sort_values().iloc[-3:]
    peak_mz = peak3.index.values
    peak_i = peak3.values
    return peak_mz, peak_i


def KMD_cal(mz_set, group='Br/H'):
    if '/' in group:
        g1, g2 = group.split('/')
        f1, f2 = Formula(g1), Formula(g2)
        f1, f2 = f1.spectrum(), f2.spectrum()
        f1_value, f2_value = [x for x in f1.values()][0][0], [x for x in f2.values()][0][0]
        values = [abs(f1_value - f2_value), round(abs(f1_value - f2_value), 0)]
        KM = mz_set * (max(values) / min(values))
        KMD_set = KM - np.floor(KM)

        print(f1_value, f2_value)
        print(min(values), max(values))
        print(values)
    else:
        g1 = Formula(group)
        f1 = g1.spectrum()
        f1_value = [x for x in f1.values()][0][0]
        KM = mz_set * (int(f1_value) / f1_value)
        KMD_set = KM - np.floor(mz_set)
    return KMD_set


def sep_result(result, replicate=4, batch=5):
    a = 0
    sep_result = []
    for i in range(batch):
        name = 'b' + str(i)
        sep_result.append(result[result.columns[a:a + replicate]])
        a += replicate

    return sep_result


def peak_checking_area(ref_all, df1, name):
    '''
    Based on referece pairs, extract all peaks and integrate the peak area.
    :param ref_all: all referece pairs (dataframe)
    :param df1: LC-MS dataframe, genrated by the function gen_df()
    :param name: name for area
    :return: peak_ref (dataframe)
    '''
    area_all = []
    peak_index = np.array(
        ref_all['rt'].map(lambda x: str(round(x, 2))).str.cat(ref_all['mz'].map(lambda x: str(round(x, 4))), sep='_'))
    num = len(ref_all)
    for i in range(num):
        rt, mz = ref_all.loc[i, ['rt', 'mz']]
        rt1, eic1 = extract(df1, mz, 50)
        rt_ind = argmin(abs(rt1 - rt))
        left = argmin(abs(rt1 - (rt - 0.2)))
        right = argmin(abs(rt1 - (rt + 0.2)))
        rt_t, eic_t = rt1[left:right], eic1[left:right]
        area = round(scipy.integrate.simps(eic_t, rt_t), 0)
        area_all.append(area)
        print(f'\r {i}/{num}', end='')
    sample_area = pd.DataFrame(area_all, index=peak_index, columns=[name])
    return sample_area


def JsonToExcel(path):
    with open(path, 'r', encoding='utf8')as fp:
        json_data = json.load(fp)
    Inchikey, precursor, frag, formula, smiles = [], [], [], [], []
    num = len(json_data)
    for i in range(num):
        try:
            cmp_info = json_data[i]['compound'][0]['metaData']
            Inchikey.append([x['value'] for x in cmp_info if x['name'] == 'InChIKey'][0])
            formula.append([x['value'] for x in cmp_info if x['name'] == 'molecular formula'][0])
            precursor.append([x['value'] for x in cmp_info if x['name'] == 'total exact mass'][0])
            smiles.append([x['value'] for x in cmp_info if x['name'] == 'SMILES'][0])
        except:
            Inchikey.append(None)
            formula.append(None)
            precursor.append(None)
            smiles.append(None)
        spec1 = r'{' + json_data[i]['spectrum'].replace(' ', ',') + r'}'
        spec2 = pd.Series(eval(spec1)).sort_values()
        spec3 = spec2[spec2.index[-50:]].to_dict()
        frag.append(spec3)
        print(f'\r {round(i / num * 100, 2)}%', end='')
    database = pd.DataFrame(np.array([Inchikey, precursor, frag, formula, smiles]).T,
                            columns=['Inchikey', 'Precursor', 'Frag', 'Formula', 'Smiles'])
    return database


def target_spec(spec, target_mz, width=0.04):
    '''
    :param spec: spec generated from function spec_at_rt()
    :param target_mz: target mz for inspection
    :param width: width for data points
    :return: new spec and observed mz
    '''
    index = argmin(abs(spec.index.values - target_mz))
    index_left = argmin(abs(spec.index.values - (target_mz - width)))
    index_right = argmin(abs(spec.index.values - (target_mz + width)))
    new_spec = spec.iloc[index_left:index_right]
    return new_spec


def gen_ref(files_excel, mz_error=0.015, rt_error=0.1):
    '''
    For alignment, generating a reference mz/rt pair
    :param files_excel: excel files path for extracted peaks
    :return: mz/rt pair reference
    '''
    data = []
    for i in range(len(files_excel)):
        name = 'peaks' + str(i)
        locals()[name] = pd.read_excel(files_excel[i], index_col='Unnamed: 0').loc[:, ['rt', 'mz']].values
        data.append(locals()[name])
        print(f'\r Reading excel files... {i}/{len(files_excel)}                   ', end="")
    print(f'\r Concatenating all peaks...                 ', end='')
    pair = np.concatenate(data, axis=0)
    peak_all_check = pair
    peak_ref = []
    while len(pair) > 0:
        rt1, mz1 = pair[0]
        index1 = np.where((pair[:, 0] <= rt1 + rt_error) & (pair[:, 0] >= rt1 - rt_error)
                          & (pair[:, 1] <= mz1 + mz_error) & (pair[:, 1] >= mz1 - mz_error))
        peak = np.mean(pair[index1], axis=0).tolist()
        peak = [round(peak[0], 2), round(peak[1], 4)]
        pair = np.delete(pair, index1, axis=0)
        peak_ref.append(peak)
        print(f'\r  {len(pair)}                        ', end='')

    peak_ref2 = np.array(peak_ref)

    ### 检查是否有漏的
    peak_lost = []
    for peak in peak_all_check:
        rt1, mz1 = peak
        check = np.where((peak_ref2[:, 0] <= rt1 + rt_error) & (peak_ref2[:, 0] >= rt1 - rt_error)
                         & (peak_ref2[:, 1] <= mz1 + mz_error) & (peak_ref2[:, 1] >= mz1 - mz_error))
        if len(check[0]) == 0:
            peak_lost.append([rt1, mz1])
    peak_lost = np.array(peak_lost)
    while len(peak_lost) > 0:
        rt1, mz1 = peak_lost[0]
        index1 = np.where((peak_lost[:, 0] <= rt1 + rt_error) & (peak_lost[:, 0] >= rt1 - rt_error)
                          & (peak_lost[:, 1] <= mz1 + mz_error) & (peak_lost[:, 1] >= mz1 - mz_error))
        peak = np.mean(peak_lost[index1], axis=0).tolist()
        peak = [round(peak[0], 2), round(peak[1], 4)]
        peak_lost = np.delete(peak_lost, index1, axis=0)
        peak_ref.append(peak)
        print(f'\r  {len(pair)}                        ', end='')

    return np.array(peak_ref)


def ms_bg_removal(background, target_spec, mz_error=0.01):
    '''
    Only support for centroid data, please convert profile data to centroid
    :param background:  background spec
    :param target_spec:  target spec
    :param mz_error: ms widow
    :return: spec after bg removal
    '''
    bg = []
    if len(target_spec) ==0:
        return None
    else: 
        for i in target_spec.index.values:
            index = argmin(abs(background.index.values - i))
            if background.index.values[index] - i < mz_error:
                bg.append([i, background.values[index]])
            else:
                bg.append([i, 0])
        bg_spec = pd.Series(np.array(bg).T[1], np.array(bg).T[0],name=target_spec.name)
        spec_bg_removal = target_spec - bg_spec
        return spec_bg_removal[spec_bg_removal > 100].sort_values()


def gen_frag(df1, df2, rt, company='Waters', mode='profile'):
    if company == 'Waters':
        if mode == 'profile':
            spec1 = ms_to_centroid(spec_at_rt(df1, rt))
            spec2 = ms_to_centroid(spec_at_rt(df2, rt))
            spec_bg_removal = ms_bg_removal(spec1, spec2)
        elif mode == 'centroid':
            spec1 = spec_at_rt(df1, rt)
            spec2 = spec_at_rt(df2, rt)
            spec_bg_removal = ms_bg_removal(spec1, spec2)
        else:
            new_frag = None
            print('please check the mode input, only accept profile or centroid')
    return spec_bg_removal


def ms_to_centroid(spec):
    '''
    :param spec: profile spec ready to convert into centroid data
    :return: converted centroid data
    '''
    peaks, _ = scipy.signal.find_peaks(spec.values.copy())
    new_index = spec.index.values[peaks]
    new_values = spec.values[peaks]
    new_spec = pd.Series(new_values, new_index,name=spec.name)
    return new_spec

def spec_similarity(spec_obs, suspect_frag, error=0.005):
    '''
    :param spec_obs: observed spec
    :param suspect_frag: frag in database
    :param error: mz window
    :return: 
    '''
    fragments = suspect_frag.index.values[-10:]
    score = 0
    for i in fragments:
        if min(abs(spec_obs.index.values - i)) < error:
            score += 1
    return score / len(fragments)

def massbank_match(mz, spec_obs, database1, mode='pos', ms1_error=0.015, ms2_error=0.005, vis=False):
    '''
    :param mz: parent compound mz
    :param spec_obs: observed spec
    :param database1: selected database 
    :param mode: 'pos' or 'neg'
    :param ms1_error: ms1 error
    :param ms2_error:ms2 error
    :param vis: visulization option
    :return: massbank result (DataFrame)
    '''
    data = {}
    if mode == 'pos':
        error = abs(database1['Precursor'].values - (mz - 1.0078))
        suspect_ind = where(error < ms1_error)[0]
    else:
        error = abs(database1['Precursor'].values - (mz + 1.0078))
        suspect_ind = where(error < ms1_error)[0]
    if len(suspect_ind) == 0:
        msbank_result = pd.DataFrame(data, columns=data.keys(), index=['Inchikey', 'score']).T
    else:
        for num, i in enumerate(suspect_ind):
            suspect_frag = pd.Series(eval(database1['Frag'][i])).sort_values()
            cmp_info = database1['Inchikey'][i]
            score = spec_similarity(spec_obs, suspect_frag, error=ms2_error)
            data[num] = [i, cmp_info, score]
        msbank_result = pd.DataFrame(data, columns=data.keys(), index=['index', 'Inchikey', 'score']).T
        msbank_result = msbank_result.sort_values(by='score').reset_index(drop=True)
    if vis == True:
        if len(msbank_result) != 0:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.bar(spec_obs.index.values, spec_obs.values / max(spec_obs.values) * 100)
            index = msbank_result['index'].values[-1]
            suspect_frag = pd.Series(eval(database1['Frag'][index])).sort_values()
            ax.bar(suspect_frag.index.values, -suspect_frag.values)
            ax.set_xlabel('m/z')
            ax.set_ylabel('Relative intensity')
            plt.xlim(50, mz * 1.2)
        else:
            pass
    else:
        pass
    return msbank_result


def evaluate_ms(new_spec, mz_exp):
    '''
    :param new_spec: target ms spec wiht width ± 0.04
    :param mz_exp:  expected mz
    :return: mz_obs, error1, final_mz_opt, error2, resolution
    '''
    peaks, _ = scipy.signal.find_peaks(new_spec.values)
    if len(peaks) == 0:
        mz_obs, error1, mz_opt, error2, resolution = mz_exp, 0, mz_exp, 0, 0
    else:
        mz_obs = new_spec.index.values[peaks][argmin(abs(new_spec.index.values[peaks] - mz_exp))]
        x, y = B_spline(new_spec.index.values, new_spec.values)
        peaks, _ = scipy.signal.find_peaks(y)
        max_index = peaks[argmin(abs(x[peaks] - mz_exp))]
        half_height = y[max_index] / 2
        mz_left = x[:max_index][argmin(abs(y[:max_index] - half_height))]
        mz_right = x[max_index:][argmin(abs(y[max_index:] - half_height))]
        resolution = int(mz_obs / (mz_right - mz_left))
        mz_opt = round(mz_left + (mz_right - mz_left) / 2, 4)
        error1 = round((mz_obs - mz_exp) / mz_exp * 1000000, 1)
        error2 = round((mz_opt - mz_exp) / mz_exp * 1000000, 1)
    return mz_obs, error1, mz_opt, error2, resolution


def one_step_process(path, company):
    '''
    For beginers, one step process will greatly simplify this process.
    :param path: path for mzml
    :param company: compand for HRMS
    :return:
    '''
    files_mzml = glob(os.path.join(path, '*.mzML'))
    if company == 'Waters':
        mz_round = 4
    elif company == 'Agilent':
        mz_round = 3
    else:
        print('Error:Only support for Aglient or Waters files')
    for file in files_mzml:
        ms1, *_ = sep_scans(file, company)
        df1 = gen_df_raw(ms1, mz_round)
        peak_all = peak_picking(df1)
        peak_selected = peak_checking(peak_all, df1)
        peak_selected.to_excel(file.replace('.mzML', '.xlsx'))
    files_excel = glob(os.path.join(path, '*.xlsx'))
    peak_alignment(files_excel)
    ref_all = pd.read_excel(os.path.join(path, 'peak_ref.xlsx'), index_col='Unnamed: 0')
    for file in files_mzml:
        ms1, *_ = sep_scans(file, company)
        df1 = gen_df_raw(ms1, mz_round)
        final_result = peak_checking_area(ref_all, df1, name=os.path.basename(file).split('.')[0])
        final_result.to_excel(file.replace('.mzML', '_final_area.xlsx'))





def first_process(file, company,profile=True):
    '''
    For processing HRMS data, this process will do peak picking and peak checking
    :param file: single file to process
    :param company: e.g., 'Waters', 'Agilent',etc,
    :return:
    '''
    if company == 'Waters':
        mz_round = 4
    elif company == 'Agilent':
        mz_round = 3
    else:
        print('Error:Only support for Aglient or Waters files')

    ms1, *_ = sep_scans(file, company)
    df1 = gen_df_raw(ms1, mz_round)
    peak_all = peak_picking(df1)
    peak_selected = peak_checking(peak_all, df1,profile=profile)
    peak_selected.to_excel(file.replace('.mzML', '.xlsx'))


def second_process(file,ref_all, company):
    '''
    This process will reintegrate peak area
    :param file: single file to process
    :param ref_all: all reference peaks
    :param company: e.g., 'Waters', 'Agilent',etc,
    :return:
    '''
    if company == 'Waters':
        mz_round = 4
    elif company == 'Agilent':
        mz_round = 3
    else:
        print('Error:Only support for Aglient or Waters files')
    ms1, *_ = sep_scans(file, company)
    df1 = gen_df_raw(ms1, mz_round)
    final_result = peak_checking_area(ref_all, df1, name=os.path.basename(file).split('.')[0])
    final_result.to_excel(file.replace('.mzML', '_final_area.xlsx'))


def extract_tic(ms1):
    '''
    For extracting TIC data
    :param ms1: ms1
    :return: rt,tic
    '''
    rt = [scan.scan_time[0] for scan in ms1]
    tic = [scan.TIC for scan in ms1]
    return rt,tic   


def sep_dda(path,company):
    '''
    :param path: path for separate DDA data
    :return: ms1, ms2
    '''
    if company =='Waters':
        run = pymzml.run.Reader(path)
        ms1,ms2 = [],[]
        for scan in run:
            if scan.id_dict['function'] ==1:
                ms1.append(scan)
            if scan.ms_level ==2:
                ms2.append(scan)
    else:
        run = pymzml.run.Reader(path)
        ms1,ms2 = [],[]
        for scan in run:
            if scan.ms_level ==1:
                ms1.append(scan)
            if scan.ms_level ==2:
                ms2.append(scan)
    return ms1,ms2



def DDA_ms2(ms1,ms2,rt,mz_exp):
    '''
        :param ms1: ms1
        :param ms2: ms2
        :param rt: rt expected
        :param mz_exp: precursor expected
        :return: target ms2
    '''
    
    def dda_ms1_and_ms2(ms1,ms2,rt,mz_exp):
       
        for scan1 in ms1:
            if scan1.scan_time[0]>rt:
                break
        for scan2 in ms2:
            if (scan2.selected_precursors[0]['mz']> mz_exp-0.015) & (scan2.selected_precursors[0]['mz']< mz_exp+0.015)&(scan2.scan_time[0]>rt):
                break
        spec1,spec2 = pd.Series(data = scan1.i,index=scan1.mz,name=scan1.scan_time[0]),pd.Series(data = scan2.i,index=scan2.mz,name =scan2.scan_time[0])
        return spec1,spec2
    
    spec1,spec2 = dda_ms1_and_ms2(ms1,ms2,rt,mz_exp)
    spec1,spec2 = ms_to_centroid(spec1),ms_to_centroid(spec2)
    target_ms2 = ms_bg_removal(spec1,spec2)
    target_ms2 = pd.Series(data = (target_ms2.values).round(2),index = target_ms2.index.values.round(4))
    return target_ms2


def loc_database_ms1(df1, mz, rt, formula):
    '''
    Evaluate the data by suspect screening method.
    :param df1: df1 for ms1
    :param df2: df2 for ms2
    :param mz: mz expected
    :param rt: rt expected
    :param frag: fragments expected
    :param formula:  target compound formula
    :return: SN_left, SN_right, mz_obs1, mz_obs_error1, mz_opt1, mz_opt_error1, intensity1, resolution1
    '''
    
    ### 1.根据信噪比打分
    rts, eics = extract(df1, mz, 50)
    peak_index = argmin(abs(rts - rt))
    index_left = argmin(abs(rts - (rt - 3)))
    index_right = argmin(abs(rts - (rt + 3)))
    peak_height = max(eics[peak_index - 5:peak_index + 5])
    rt2, eic2 = rts[index_left:index_right], eics[index_left:index_right]
    cut = int(len(eic2) / 3)
    bg_left, bg_right = cal_bg(eic2[:cut]), cal_bg(eic2[-cut:])
    SN_left = round(peak_height / bg_left, 1)
    SN_right = round(peak_height / bg_right, 1)

    ### 2. 根据MS的峰打分，包括同位素 
    spec = spec_at_rt(df1, rt)
    new_spec1 = target_spec(spec, mz, width=0.06)
    mz_obs1, mz_obs_error1, mz_opt1, mz_opt_error1, resolution1 = evaluate_ms(new_spec1, mz)
    try:
        intensity1 = new_spec1[mz_obs1]
    except:
        intensity1 = max(new_spec1.values)
    
    isotopes,distribution = formula_to_distribution(formula,adducts = '+H')
    new_spec2 = target_spec(spec,isotopes[1],width = 0.06)
    intensity2 = max(new_spec2.values)
    
    new_spec3 = target_spec(spec,isotopes[2],width = 0.06)
    intensity3 = max(new_spec3.values)
    if intensity1 ==0:
        intensity1 +=1
        iso_value = f'{int(intensity1/intensity1*100)}:{int(intensity2/intensity1*100)}:{int(intensity3/intensity1*100)}'
    else:
        iso_value = f'{int(intensity1/intensity1*100)}:{int(intensity2/intensity1*100)}:{int(intensity3/intensity1*100)}'
    iso_exp = f'{int(distribution[0])}:{int(distribution[1])}:{int(distribution[2])}'
    return SN_left, SN_right, mz_obs1, mz_obs_error1, mz_opt1, mz_opt_error1, intensity1, iso_value,iso_exp,resolution1


def loc_database_ms2(df1,df2,rt,frag,ms2_error=0.005):
    '''
    Evaluate MSMS
    :param df1: df1 for ms1
    :param df2: df2 for ms2
    :param rt:  mz expected
    :param frag: frag expected
    :param ms2_error:  ms2 error
    :return: score
    '''
    ##  根据MSMS峰打分
    if len(eval(frag)) == 0:
        score = 0
        frag_score = score/10
    else:
        spec_obs = gen_frag(df1, df2, rt, company='Waters', mode='profile')
        suspect_frag = pd.Series(eval(frag))
        fragments = suspect_frag.index.values[-10:]
        score = 0
        for i in fragments:
            if min(abs(spec_obs.index.values - i)) < ms2_error:
                score += 1
        frag_score = score/10
    return frag_score  



def fold_change_filter(path,fold_change = 5,area_threhold = 500):
    
    ### 整合blank数据，获的最大值
    print('\r Organizing blank data...         ',end = '')
    excel_path = os.path.join(path,'*.xlsx')
    files_excel = glob(excel_path)
    alignment = [file for file in files_excel if 'alignment' in file]
    area_files = [file for file in files_excel if 'final_area' in file]
    blk_files = [file for file in area_files if 'blank' in file or 'Control' in file or 'control' in file]
    blk_df = concat_alignment(blk_files)  ##生成所有blank的dataframe表
    blk_s = blk_df.max(axis=1)  ## 找到blanks中每个峰的最大值
    final_blk = blk_s.to_frame(name = 'blk')
    print('\r Start to process fold change         ',end = '')
    ###整合每个area_file与blank的对比结果，输出fold change 大于fold_change倍的值
    area_files_sample = [file for file in area_files if 'blank' not in file and 'control' not in file and 'Control' not in file]
    for i in tqdm(range(len(area_files_sample)),desc='Fold change processing'):
        ###基于峰面积的对比拿到比较数据
        sample = pd.read_excel(area_files_sample[i],index_col = 'Unnamed: 0')
        compare = pd.concat((sample,final_blk),axis=1)
        compare_result1 = compare[compare[compare.columns[0]]
                                 >fold_change*compare['blk']].sort_values(by=compare.columns[0],ascending=False)
        compare_result = compare_result1[compare_result1[compare_result1.columns[0]]>area_threhold]
        ###开始处理alignment文件
        name = os.path.basename(area_files_sample[i]).replace('_final_area.xlsx','') ## 拿到名字
        alignment_path = [file for file in alignment if name in file][0]
        alignment_df = pd.read_excel(alignment_path,index_col = 'new_index').sort_values(by = 'intensity')
        alignment_df1 = alignment_df[~alignment_df.index.duplicated(keep='last')] ## 去掉重复索引

        final_index = np.intersect1d(alignment_df1.index.values,compare_result.index.values)
        final_alignment = alignment_df1.loc[final_index,:].sort_values(by = 'intensity',ascending = False)
        new_name = area_files_sample[i].replace('_final_area','_unique_cmps')  ### 文件输出名称
        final_alignment.to_excel(new_name)

        
def classify_files(path):
    '''
    classifly the generated excel files.
    :param path: path for excel files
    :return:
    '''
    files_excel = glob(os.path.join(path, '*.xlsx'))
    step1 = os.path.join(path, 'step1_peak_picking_result')
    step2 = os.path.join(path, 'step2_peak_alignment_result')
    step3 = os.path.join(path, 'step3_all_peak_areas')
    step4 = os.path.join(path,'step4_fold_change_filter ')
    os.mkdir(step1)
    os.mkdir(step2)
    os.mkdir(step3)
    os.mkdir(step4)
    for file in files_excel:
        if 'alignment' in file:
            shutil.move(file, step2)
        elif 'final_area' in file:
            shutil.move(file, step3)
        elif 'unique_cmps' in file:
            shutil.move(file,step4)
        else:
            shutil.move(file, step1)
    files_excel = glob(os.path.join(step3, '*.xlsx'))
    all_peak_areas = concat_alignment(files_excel)
    all_peak_areas.to_excel(os.path.join(step3, 'final_result.xlsx'))

        
if __name__ == '__main__':
    pass



# path = r'D:\TOF-Ms DATA\tangting_DPG\TEST_one_step'
# company = 'Waters'
# one_step_process(path, company)
#     path = r'D:\TOF-Ms DATA\HYH-MZML\混合实验\*.mzML'
#     files_mzml = glob(path)
#     pool = Pool(processes = 5)
#     for file in files_mzml:
#         pool.apply_async(multi_process,args=(file,))
#     print('Finished')
#     pool.close()
#     pool.join()
