from __future__ import division
import argparse
# from . import main, utils
import pkg_resources
import pandas as pd
import ast
import numpy as np
from itertools import chain
from pyteomics import fasta
from collections import Counter
import os

def read_table(z, allowed_peptides, allowed_prots, label=None):
    if label is None:
        label = z.replace('_proteins.csv', '')
    if isinstance(z, str):
        df = pd.read_csv(z.replace('_proteins.csv', '_PFMs.csv'), sep='\t')
    else:
        df = pd.concat([pd.read_csv(f.replace('_proteins.csv', '_PFMs.csv'), sep='\t') for f in z])

    df = df[df['sequence'].apply(lambda z: z in allowed_peptides)]
    df['count'] = df.groupby('sequence')['Intensity'].transform('max')
    df = df.sort_values('Intensity', ascending=False).drop_duplicates(['sequence'])
    df[label] = df['count']
    df['protein'] = df['proteins'].apply(lambda z: [u for u in z.split(';') if u in allowed_prots])
    df = df[df['protein'].apply(lambda z: len(z)>0)]
    df = df[['sequence', 'protein', label]]
    return df

def run():
    parser = argparse.ArgumentParser(
        description='calculate NSAF for scavager results',
        epilog='''

    Example usage
    -------------
    $ scav2nsaf -S1 sample1_1_proteins.tsv sample1_n_proteins.tsv -S2 sample2_1_proteins.tsv sample2_n_proteins.tsv
    -------------
    ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-S1', nargs='+', metavar='FILE', help='input files for S1 sample', required=True)
    parser.add_argument('-S2', nargs='+', metavar='FILE', help='input files for S2 sample')
    parser.add_argument('-S3', nargs='+', metavar='FILE', help='input files for S3 sample')
    parser.add_argument('-S4', nargs='+', metavar='FILE', help='input files for S4 sample')
    parser.add_argument('-min_samples', help='minimum number of samples for protein usage', default='3')
    parser.add_argument('-u', '--union',  help='pool the files together for the samples', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--autolabel', help='in union mode, derive sample labels from common name prefixes',
        action='store_true')
    group.add_argument('--labels', nargs='+', metavar='LABEL',
        help='labels for samples in union mode (same number as samples)')
    parser.add_argument('-db', metavar='FILE', help='path to fasta file', required=True)
    parser.add_argument('-out', metavar='FILE', help='name of nsaf output file', default='nsaf_out.txt')
    parser.add_argument('-version', action='version', version='%s' % (pkg_resources.require("ms1searchpy")[0], ))
    args = vars(parser.parse_args())

    samples = ['S1', 'S2', 'S3', 'S4']
    labels = args['labels'] if args['labels'] else samples

    min_samples = int(args['min_samples'])

    df_final = False

    allowed_prots = set()
    allowed_peptides = set()
    allowed_prots_c = Counter()

    for sample_num in samples:
        if args[sample_num]:
            for z in args[sample_num]:
                df0 = pd.read_csv(z, sep='\t')
                for dbname in df0['dbname'].values:
                    allowed_prots_c[dbname] += 1
                # allowed_prots.update(df0['dbname'])
    for k, v in allowed_prots_c.items():
        if v >= min_samples:
            allowed_prots.add(k)

    for sample_num in samples:
        if args[sample_num]:
            for z in args[sample_num]:
                df0 = pd.read_csv(z.replace('_proteins.csv', '_PFMs.csv'), sep='\t')
                allowed_peptides.update(df0['sequence'])



    for sample_num, label in zip(samples, labels):
        if args[sample_num]:
            if not args['union']:
                for z in args[sample_num]:
                    df1 = read_table(z, allowed_peptides, allowed_prots)
                    if df_final is False:
                        df_final = df1
                    else:
                        df_final = df_final.reset_index().merge(df1.reset_index(), on='sequence', how='outer')#.set_index('peptide')
                        df_final.protein_x.fillna(value=df_final.protein_y, inplace=True)
                        df_final['protein'] = df_final['protein_x']
                        df_final = df_final.drop(columns=['protein_x', 'protein_y', 'index_x', 'index_y'])
            else:
                if args['autolabel']:
                    label = os.path.commonprefix(args[sample_num]).rstrip('_')
                df1 = read_table(args[sample_num], allowed_peptides, allowed_prots, label=label)
                if df_final is False:
                    df_final = df1
                else:
                    df_final = df_final.reset_index().merge(df1.reset_index(), on='sequence', how='outer')#.set_index('peptide')
                    df_final.protein_x.fillna(value=df_final.protein_y, inplace=True)
                    df_final['protein'] = df_final['protein_x']
                    df_final = df_final.drop(columns=['protein_x', 'protein_y', 'index_x', 'index_y'])


    df_final = df_final.set_index('sequence')
    df_final['proteins'] = df_final['protein']
    df_final = df_final.drop(columns=['protein'])
    cols = df_final.columns.tolist()
    cols.remove('proteins')
    cols.insert(0, 'proteins')
    df_final = df_final[cols]
    df_final.fillna(value='')

    cols = df_final.columns.difference(['proteins'])
    genres = df_final['proteins']#.str.split(';')
    df_final =  (df_final.loc[df_final.index.repeat(genres.str.len()), cols]
         .assign(dbname=list(chain.from_iterable(genres.tolist()))))


    df_final.to_csv(args['out']+'test', sep='\t', index=False)

    df_final = df_final.groupby('dbname').sum()
    df_final.reset_index(level=0, inplace=True)

    protsL = {}
    for p in fasta.read(args['db']):
        dbn = p[0].split()[0]
        protsL[dbn] = len(p[1])

    df_final['Length'] = df_final['dbname'].apply(lambda z: protsL[z])
    for cc in df_final.columns:
        if cc not in ['dbname', 'Length']:
            df_final[cc] = df_final[cc]# / df_final['Length']
    for cc in df_final.columns:
        if cc not in ['dbname', 'Length']:
            df_final[cc] = df_final[cc] / df_final[cc].sum()
            df_final[cc] = df_final[cc].replace(0, np.nan)
            min_val = np.nanmin(df_final[cc].values)
            df_final[cc] = df_final[cc].replace(np.nan, min_val)
    df_final.drop(columns=['Length', ], inplace=True)
    df_final.to_csv(args['out'], sep='\t', index=False)

if __name__ == '__main__':
    run()
