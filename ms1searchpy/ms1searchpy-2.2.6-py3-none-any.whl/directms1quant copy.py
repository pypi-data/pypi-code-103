from __future__ import division
import argparse
import pkg_resources
import pandas as pd
import ast
import subprocess
import numpy as np
from scipy.stats import binom, ttest_ind
from collections import defaultdict
import itertools
from pyteomics import auxiliary as aux

def calc_sf_all(v, n, p):
    sf_values = -np.log10(binom.sf(v-1, n, p))
    sf_values[np.isinf(sf_values)] = max(sf_values[~np.isinf(sf_values)]) * 2
    sf_values[n == 0] = 0
    # sf_values = binom.sf(v-1, n, p)
    # sf_values[np.isneginf(sf_values)] = min(sf_values[~np.isinf(sf_values)])
    # sf_values[n <= 3] = 1.0
    return sf_values

def run():
    parser = argparse.ArgumentParser(
        description='run DirectMS1quant for ms1searchpy results',
        epilog='''

    Example usage
    -------------
    $ directms1quant -S1 sample1_1_proteins_full.tsv sample1_n_proteins_full.tsv -S2 sample2_1_proteins_full.tsv sample2_n_proteins_full.tsv
    -------------
    ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-S1', nargs='+', help='input files for S1 sample', required=True)
    parser.add_argument('-S2', nargs='+', help='input files for S2 sample', required=True)
    # parser.add_argument('-allowed_prots', help='path to allowed prots', default='')
    parser.add_argument('-out', help='name of DirectMS1quant output file', default='directms1quant_out')
    parser.add_argument('-use_filt', help='use_filt', action='store_true')
    parser.add_argument('-use_qfilt', help='use_qfilt', action='store_true')

    # parser.add_argument('-norm', help='normalization method. Can be average, median, GMM or None', default='None')
    # parser.add_argument('-impute_threshold', help='impute_threshold for missing values fraction', default='0.75')
    parser.add_argument('-min_samples', help='minimum number of samples for peptide usage', default=4)
    # parser.add_argument('-new', help='new algo', action='store_true')
    args = vars(parser.parse_args())

    replace_label = '_proteins_full.tsv'

    df_final = False
    # protsN = False

    all_s_lbls = {}

    allowed_prots = set()
    all_peptides = set()
    allowed_peptides = set()

    for i in range(1, 3, 1):
        sample_num = 'S%d' % (i, )
        if args[sample_num]:
            for z in args[sample_num]:
                if args['use_filt']:
                    df0 = pd.read_table(z.replace('_proteins_full.tsv', '_proteins.tsv'))
                    allowed_prots.update(df0['dbname'])
                    allowed_prots.update(['DECOY_' + z for z in df0['dbname'].values])
                else:
                    df0 = pd.read_table(z)
                    allowed_prots.update(df0['dbname'])

                df0 = pd.read_table(z.replace('_proteins_full.tsv', '_PFMs_ML.tsv'))

                all_peptides.update(df0['seqs'])
                if args['use_qfilt']:
                    df0 = df0[df0['qpreds'] <= 10]
                    allowed_peptides.update(df0['seqs'])
                else:
                    allowed_peptides = all_peptides
                # if not protsN:
                #     df0 = pd.read_table(z)
                #     protsN = df0.set_index('dbname')['theoretical peptides'].to_dict()

    print(len(allowed_prots)/2)
    print(len(allowed_peptides), len(all_peptides))
    # else:
    #     for prot in open(args['allowed_prots'], 'r'):
    #         allowed_prots.add(prot.strip())


    for i in range(1, 3, 1):
        sample_num = 'S%d' % (i, )
        if args.get(sample_num, 0):
            all_s_lbls[sample_num] = []
            for z in args[sample_num]:
                label = z.replace(replace_label, '')
                all_s_lbls[sample_num].append(label)
                df1 = pd.read_table(z)
                df3 = pd.read_table(z.replace(replace_label, '_PFMs.tsv'))
                print(z)

                df3 = df3[df3['sequence'].apply(lambda x: x in allowed_peptides)]

                df3 = df3[df3['proteins'].apply(lambda x: any(z in allowed_prots for z in x.split(';')))]
                df3['proteins'] = df3['proteins'].apply(lambda x: ';'.join([z for z in x.split(';') if z in allowed_prots]))

                df3['sequence'] = df3['sequence'] + df3['charge'].astype(int).astype(str)

                df3 = df3.sort_values(by='Intensity', ascending=False)
                # df3 = df3.sort_values(by='nScans', ascending=False)

                df3 = df3.drop_duplicates(subset='sequence')
                # df3 = df3.explode('proteins')

                # df3['Intensity'] = np.log2(df3['Intensity'])
                # df3['Intensity'] = df3['Intensity'] - df3['Intensity'].median()

                # df3['Intensity'] = df3['Intensity'] / df3['Intensity'].median()

                df3[label] = df3['Intensity']
                df3['protein'] = df3['proteins']
                df3['peptide'] = df3['sequence']
                df3 = df3[['peptide', 'protein', label]]
                    
                if df_final is False:
                    label_basic = label
                    df_final = df3.reset_index(drop=True)
                else:
                    df_final = df_final.reset_index(drop=True).merge(df3.reset_index(drop=True), on='peptide', how='outer')
                    df_final.protein_x.fillna(value=df_final.protein_y, inplace=True)
                    df_final['protein'] = df_final['protein_x']

                    df_final = df_final.drop(columns=['protein_x', 'protein_y'])

            
    df_final = df_final.assign(protein=df_final['protein'].str.split(';')).explode('protein').reset_index(drop=True)

    df_final = df_final.set_index('peptide')
    df_final['proteins'] = df_final['protein']
    df_final = df_final.drop(columns=['protein'])
    # cols = df_final.columns.tolist()
    cols = [z for z in df_final.columns.tolist() if not z.startswith('mz_')]
    cols.remove('proteins')
    cols.insert(0, 'proteins')
    df_final = df_final[cols]

    all_lbls = all_s_lbls['S1'] + all_s_lbls['S2']

    max_missing = len(all_lbls) - int(args['min_samples'])

    df_final['nonmissing'] = df_final.isna().sum(axis=1) <= max_missing

    df_final = df_final[df_final.isna().sum(axis=1) <= max_missing]

    for cc in all_lbls:
        df_final[cc] = df_final[cc] / df_final[cc].median()

    for cc in all_lbls:
        df_final[cc] = df_final[cc].fillna(df_final[cc].min() / 2)

    df_final['p-value'] = list(ttest_ind(df_final[all_s_lbls['S1']].values.astype(float), df_final[all_s_lbls['S2']].values.astype(float), axis=1, nan_policy='omit', equal_var=True)[1])
    df_final['p-value'] = df_final['p-value'].astype(float)
    df_final['p-value'] = df_final['p-value'].fillna(1.0)

    df_final['S2_mean'] = df_final[all_s_lbls['S2']].mean(axis=1)
    df_final['S1_mean'] = df_final[all_s_lbls['S1']].mean(axis=1)

    df_final['FC'] = np.log2(df_final['S2_mean']/df_final['S1_mean'])
    # df_final['FC'] = (df_final['S2_mean']-df_final['S1_mean'])

    FC_max = df_final['FC'].max()
    FC_min = df_final['FC'].min()

    df_final.loc[(pd.isna(df_final['S2_mean'])) & (~pd.isna(df_final['S1_mean'])), 'FC'] = FC_min * 2
    df_final.loc[(~pd.isna(df_final['S2_mean'])) & (pd.isna(df_final['S1_mean'])), 'FC'] = FC_max * 2

    df_final['decoy'] = df_final['proteins'].apply(lambda x: all(z.startswith('DECOY_') for z in x.split(';')))

    # t_p = [0.01, 0.05, 0.25, 0.5]
    # t_fc = [0.3, 1.0, 2.0]


    from scipy.stats import scoreatpercentile
    from scipy.optimize import curve_fit
    from scipy import exp
    def noisygaus(x, a, x0, sigma, b):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + b

    def calibrate_mass(bwidth, mass_left, mass_right, true_md):

        bbins = np.arange(-mass_left, mass_right, bwidth)
        H1, b1 = np.histogram(true_md, bins=bbins)
        b1 = b1 + bwidth
        b1 = b1[:-1]


        popt, pcov = curve_fit(noisygaus, b1, H1, p0=[1, np.median(true_md), 1, 1])
        mass_shift, mass_sigma = popt[1], abs(popt[2])
        return mass_shift, mass_sigma, pcov[0][0]

    df_final_tmp = df_final[df_final['nonmissing']]

    FC_mean = np.mean(df_final_tmp['FC'])
    FC_std = np.std(df_final_tmp['FC'])
    print(FC_mean, FC_std)

    try:
        FC_mean, FC_std, covvalue_cor = calibrate_mass(0.1, -df_final_tmp['FC'].min(), df_final_tmp['FC'].max(), df_final_tmp['FC'])
    except:
        FC_mean, FC_std, covvalue_cor = calibrate_mass(0.3, -df_final_tmp['FC'].min(), df_final_tmp['FC'].max(), df_final_tmp['FC'])
    print(FC_mean, FC_std)

    FC_r = FC_mean + 2 * FC_std
    FC_l = FC_mean - 2 * FC_std
    # FC_l = -0.5
    # FC_r = 0.5

    df_final.to_csv(path_or_buf=args['out']+'_final_unfilt.tsv', sep='\t', index=False)

    # df_final.loc[~df_final['nonmissing'], 'FC'] = FC_mean

    t_p = [0.05, ]
    t_fc = [0.5, ]

    total_up = defaultdict(float)
    total_down = defaultdict(float)

    for p_val_threshold, FC_threshold in itertools.product(t_p, t_fc):
        print(p_val_threshold, FC_threshold)
        
        df_final['sign'] = df_final['p-value'] <= p_val_threshold
        
        df_final['up'] = df_final['sign'] * df_final['FC'] >= FC_r#FC_threshold
        df_final['down'] = df_final['sign'] * df_final['FC'] <= FC_l#-FC_threshold

        up_dict = df_final.groupby('proteins')['up'].sum().to_dict()
        down_dict = df_final.groupby('proteins')['down'].sum().to_dict()
        df_final['up'] = df_final.apply(lambda x: x['up'] if up_dict.get(x['proteins'], 0) >= down_dict.get(x['proteins'], 0) else x['down'], axis=1)

        # df_final['up'] = df_final['sign'] * (df_final['FC']-FC_mean).abs() >= FC_r#FC_threshold
        
        protsN = df_final.groupby('proteins')['up'].count().to_dict()
        # protsN_up = df_final[df_final['FC'] > 0].groupby('proteins')['up'].count().to_dict()
        # protsN_down = df_final[df_final['FC'] < 0].groupby('proteins')['up'].count().to_dict()

        prots_up = df_final.groupby('proteins')['up'].sum()
        prots_down = df_final.groupby('proteins')['down'].sum()

        # N_decoy_total_up = df_final[df_final['FC'] > 0]['decoy'].sum()
        # N_decoy_total_down = df_final[df_final['FC'] < 0]['decoy'].sum()

        N_decoy_total = df_final['decoy'].sum()
        changed_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy'])].shape[0]
        # upreg_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy']) & (df_final['FC'] >= FC_threshold)].shape[0]
        # downreg_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy']) & (df_final['FC'] <= -FC_threshold)].shape[0]
        upreg_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy']) & (df_final['FC'] >= FC_r)].shape[0]
        downreg_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy']) & (df_final['FC'] <= FC_l)].shape[0]

        upreg_decoy_total = df_final[df_final['decoy']]['up'].sum()
        # upreg_decoy_total = df_final[(df_final['p-value'] <= p_val_threshold) & (df_final['decoy']) & (df_final['FC'].abs() >= FC_r)].shape[0]


        p_up = upreg_decoy_total / N_decoy_total
        p_down = downreg_decoy_total / N_decoy_total
        # p_up = upreg_decoy_total / N_decoy_total_up
        # p_down = downreg_decoy_total / N_decoy_total_down
        print(N_decoy_total, changed_decoy_total, upreg_decoy_total, downreg_decoy_total, p_up, p_down)
        # print(N_decoy_total_up, N_decoy_total_down, changed_decoy_total, upreg_decoy_total, downreg_decoy_total, p_up, p_down)
        
        
        names_arr = np.array(list(protsN.keys()))
        v_arr = np.array(list(prots_up.get(k, 0) for k in names_arr))
        n_arr = np.array(list(protsN.get(k, 0) for k in names_arr))

        all_pvals = calc_sf_all(v_arr, n_arr, p_up)
        
        v_arr = np.array(list(prots_down.get(k, 0) for k in names_arr))
        all_pvals_down = calc_sf_all(v_arr, n_arr, p_up)
        
        for z, dbname in zip(all_pvals, names_arr):
            total_up[dbname] += z
        for z, dbname in zip(all_pvals_down, names_arr):
            total_down[dbname] += z

    all_pvals = [total_up[dbname] for dbname in names_arr]
    all_pvals_down = [total_down[dbname] for dbname in names_arr]

    total_set = set()

    FC_up_dict = df_final[df_final['up']].groupby('proteins')['FC'].median().to_dict()
    FC_down_dict = df_final[df_final['down']].groupby('proteins')['FC'].median().to_dict()

    # FC_up_dict_sign = df_final[df_final['sign']].groupby('proteins')['FC'].median().to_dict()
    # FC_down_dict_sign = df_final[df_final['sign']].groupby('proteins')['FC'].median().to_dict()

    # FC_up_dict = df_final.groupby('proteins')['FC'].median().to_dict()
    # FC_down_dict = df_final.groupby('proteins')['FC'].median().to_dict()

    df_out = pd.DataFrame()
    df_out['score'] = all_pvals
    df_out['dbname'] = names_arr
    df_out['FC'] = df_out['dbname'].apply(lambda x: FC_up_dict.get(x))
    # df_out['FC_sign'] = df_out['dbname'].apply(lambda x: FC_up_dict_sign.get(x))
    df_out['decoy'] = df_out['dbname'].str.startswith('DECOY_')

    print(np.mean(df_out['FC']))
    print(np.std(df_out['FC']))
    df_out.to_csv(path_or_buf=args['out']+'_upreg_unfilt.tsv', sep='\t', index=False)

    print((df_out['decoy']).sum(), (~df_out['decoy']).sum())


    # try:
    #     FC_mean, FC_std, covvalue_cor = calibrate_mass(0.1, -df_out['FC'].min(), df_out['FC'].max(), df_out['FC'])
    # except:
    #     FC_mean, FC_std, covvalue_cor = calibrate_mass(0.3, -df_out['FC'].min(), df_out['FC'].max(), df_out['FC'])
    # print(FC_mean, FC_std)

    # FC_r = FC_mean + 2 * FC_std
    # FC_l = FC_mean - 2 * FC_std

    # df_out = df_out[df_out['FC'].apply(lambda x: x >= FC_r)]

    df_out_f = aux.filter(df_out, fdr=0.05, key='score', is_decoy='decoy', reverse=True)
    # df_out_f = df_out[(df_out['score'] >= 3.0) & (~df_out['decoy'])]
    # df_out_f = df_out[(df_out['score'] >= -np.log10(0.05)) & (~df_out['decoy'])]
    # df_out = df_out.sort_values(by='score')
    # df_out = df_out[~df_out['decoy']]
    # df_out['qval'] = df_out['score']*np.arange(1, len(df_out)+1, 1)
    # df_out_f = df_out[df_out['qval'] <= 0.05]

    df_out_f.to_csv(path_or_buf=args['out']+'_upreg.tsv', sep='\t', index=False)
    print(df_out_f)


    total_set.update([z.split('|')[1] for z in set(df_out_f['dbname'])])

    # df_out = pd.DataFrame()
    # df_out['score'] = all_pvals_down
    # df_out['dbname'] = names_arr
    # df_out['FC'] = df_out['dbname'].apply(lambda x: FC_down_dict.get(x))
    # # df_out['FC_sign'] = df_out['dbname'].apply(lambda x: FC_down_dict_sign.get(x))
    # df_out['decoy'] = df_out['dbname'].str.startswith('DECOY_')


    # print(np.mean(df_out['FC']))
    # print(np.std(df_out['FC']))
    # df_out.to_csv(path_or_buf=args['out']+'_downreg_unfilt.tsv', sep='\t', index=False)


    # # df_out = df_out[df_out['FC'].apply(lambda x: x <= FC_l)]

    # df_out_f = aux.filter(df_out, fdr=0.05, key='score', is_decoy='decoy', reverse=True)
    # # df_out_f = df_out[(df_out['score'] >= 3.0) & (~df_out['decoy'])]
    # # df_out_f = df_out[(df_out['score'] >= -np.log10(0.05)) & (~df_out['decoy'])]
    # # df_out = df_out.sort_values(by='score')
    # # df_out = df_out[~df_out['decoy']]
    # # df_out['qval'] = df_out['score']*np.arange(1, len(df_out)+1, 1)
    # # df_out_f = df_out[df_out['qval'] <= 0.05]
    # # df_out_f.to_csv(path_or_buf=args['out']+'_downreg.tsv', sep='\t', index=False)
    # print(df_out_f)

    # total_set.update([z.split('|')[1] for z in set(df_out_f['dbname'])])

    f1 = open(args['out'] + '_total.txt', 'w')
    for z in total_set:
        f1.write(z + '\n')
    f1.close()

if __name__ == '__main__':
    run()
