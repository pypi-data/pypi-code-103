from .main import final_iteration
import pandas as pd
from collections import defaultdict
import argparse
from pyteomics import auxiliary as aux


def run():
    parser = argparse.ArgumentParser(
        description='Combine DirectMS1 search results',
        epilog='''

    Example usage
    -------------
    $ ms1combine.py file1_PFMs_ML.tsv ... filen_PFMs_ML.tsv
    -------------
    ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file', nargs='+', help='input tsv PFMs_ML files')
    parser.add_argument('-out', help='prefix output file names', default='combined')
    parser.add_argument('-prots_full', help='path to any of *_proteins_full.tsv file. By default this file will be searched in the folder with PFMs_ML files', default='')
    parser.add_argument('-fdr', help='protein fdr filter in %%', default=1.0, type=float)
    parser.add_argument('-prefix', help='decoy prefix', default='DECOY_')
    parser.add_argument('-nproc',   help='number of processes', default=1, type=int)
    args = vars(parser.parse_args())

    prefix = args['prefix']
    isdecoy = lambda x: x[0].startswith(prefix)
    isdecoy_key = lambda x: x.startswith(prefix)
    escore = lambda x: -x[1]
    fdr = float(args['fdr']) / 100

    outlist = []

    df1 = False
    prots_order = False
    for idx, filen in enumerate(args['file']):
        df3 = pd.read_csv(filen, sep='\t')
        df3['ids'] = df3['ids'].apply(lambda x: '%d:%s' % (idx, str(x)))
        if df1 is False:
            df1 = df3
            if args['prots_full']:
                df2 = pd.read_csv(args['prots_full'], sep='\t')
            else:
                try:
                    df2 = pd.read_csv(filen.replace('_PFMs_ML.tsv', '_proteins_full.tsv'), sep='\t')
                except:
                    print('Proteins_full file is missing!')
                    break

        else:
            df1 = df1.append(df3, ignore_index=True)

        pept_prot = defaultdict(set)
        for seq, prots in df1[['seqs', 'proteins']].values:
            for dbname in prots.split(';'):
                pept_prot[seq].add(dbname)

        protsN = dict()
        for dbname, theorpept in df2[['dbname', 'theoretical peptides']].values:
            protsN[dbname] = theorpept

        resdict = dict()

        resdict['qpreds'] = df1['qpreds'].values
        resdict['preds'] = df1['preds'].values
        resdict['seqs'] = df1['peptide'].values
        resdict['ids'] = df1['ids'].values
        resdict['iorig'] = df1['iorig'].values

        mass_diff = resdict['qpreds']
        rt_diff = resdict['qpreds']

        base_out_name = args['out']
        sortedlist_spc = final_iteration(resdict, mass_diff, rt_diff, pept_prot, protsN, base_out_name, prefix, isdecoy, isdecoy_key, escore, fdr, args['nproc'], fname=False, prots_order=prots_order, write_output=False)
        print(sortedlist_spc[:5])
        outlist.extend(sortedlist_spc)

        if not prots_order:
            prots_order = dict()
            for k, v in sortedlist_spc:
                prots_order[k] = v

        df1 = False

        print('\n\n\n')


        prots_spc = dict()
        for k, v in outlist:
            prots_spc[k] = prots_spc.get(k, 0) + v

        filtered_prots = aux.filter(prots_spc.items(), fdr=fdr, key=escore, is_decoy=isdecoy, remove_decoy=True, formula=1, full_output=True, correction=1)
        if len(filtered_prots) < 1:
            filtered_prots = aux.filter(prots_spc.items(), fdr=fdr, key=escore, is_decoy=isdecoy, remove_decoy=True, formula=1, full_output=True, correction=0)
        identified_proteins = 0

        for x in filtered_prots:
            identified_proteins += 1

        print('TOP 5 identified proteins:')
        print('dbname\tscore\tnum matched peptides\tnum theoretical peptides')
        for x in filtered_prots[:5]:
            print('\t'.join((str(x[0]), str(x[1]), '0', str(protsN[x[0]]))))
        print('results:%s;number of identified proteins = %d' % (base_out_name, identified_proteins, ))
        print('\n\n\n')

if __name__ == '__main__':
    run()
