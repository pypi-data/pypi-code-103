#Pip installierbar und als executable
import itertools
import numpy as np
import gseapy as gp
import pandas as pd
import plotly.express as px
import argparse
import os.path

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def coverageScore(pathway, universe, pvalue):
    if len(intersection(pathway, universe)) == 0:
        v = 0
    else:
        v = (1 - pvalue)

    return v
def preProcess(data):
    data = pd.read_csv(data, sep=",")
    data['geneID'] = data['geneID'].map(lambda x: x.lstrip('SV:'))
    data = data[data.AltType == 'mutation']
    data = data[data.fisher_q_withinCluster <= 0.1]
    data.sort_values(by=['fisher_q_withinCluster'])
    #data.to_csv('/content/sample_data/gene_list.csv', index=False)
    return data
def genelistGen(data):
    genelist = data['geneID'].tolist()

    dirName = 'lists/'
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

    with open(dirName + "glist.txt", "w") as output:
        output.write(str(genelist))

    with open(dirName + "glist.txt", 'r') as f:
        lines = f.readlines()

    lines = [line.replace(',', '\n') for line in lines]
    lines = [line.replace('[', '') for line in lines]
    lines = [line.replace(']', '') for line in lines]
    lines = [line.replace("'", "") for line in lines]

    with open(dirName + "glist.txt", 'w') as f:
        f.writelines(lines)
    return genelist

def processGmt(gmtfile):
    with open(gmtfile) as f:
        gmtlines = f.readlines()
    #gmtfile = pd.read_csv(gmtfile, delimiter = "name:", names=['Term','Name'])
    #gmtfile['Term'] = gmtfile['Term'].map(lambda x: x.rstrip('\t'))
    #gmtfile['Name'] = gmtfile['Name'].map(lambda x: x.rstrip('\t'))

    return gmtlines

def dbSelect(gmtlines, db):
    upgmtlines = []
    if db == 'ALL':
        upgmtlines = gmtlines
    else:
        for i in range(len(gmtlines)):
          if (gmtlines[i].find(db,0,15) != -1):
              upgmtlines.append(gmtlines[i])
          else:
              continue
    with open('upgmt.gmt', 'w') as f:
        for item in upgmtlines:
            f.write(item)
    return 'upgmt.gmt'


def enrichmentAnalysis(gmtfile, genelist, gene_list, ranked, tab_out):
    if ranked == False:
        enr = gp.enrichr(gene_list=genelist,
                         gene_sets=[gmtfile],
                         organism='Human',
                         description='test_name',
                         outdir='plots/list',
                         # no_plot=True,
                         cutoff=0.5  # test dataset, use lower value from range(0,1)
                         )

    # enr.results.head(10)

        enr.results.sort_values(by='Adjusted P-value', ascending=True)

        #listnames = pd.merge(enr.results, gmtdf, how="inner", on='Term')
        #listnames = listnames.sort_values(by='Adjusted P-value', ascending=True).head(20)
        #listnames["-log(p)"] = -np.log(listnames["Adjusted P-value"])
        #listnames['Overlap_per'] = listnames['Overlap'].apply(lambda x: [float(n) for n in x.split('/')[0:2]])
        #listnames['Overlap_per'] = listnames['Overlap_per'].apply(lambda x: x[0] / x[1] if x[1] != 0 else np.nan)
        #listnames = listnames.round({'Overlap_per': 2})
        #listnames['size'] = listnames['Overlap'].apply(lambda x: [float(n) for n in x.split('/')[0:2]])
        #listnames['size'] = listnames['size'].apply(lambda x: 1 / x[1])
        #listnames['Genes'] = listnames['Genes'].apply(lambda x: x.split(";"))

        listnames = enr.results
        listnames = listnames.sort_values(by='Adjusted P-value', ascending=True).head(20)
        listnames["-log(p)"] = -np.log(listnames["Adjusted P-value"])
        listnames['Overlap_per'] = listnames['Overlap'].apply(lambda x: [float(n) for n in x.split('/')[0:2]])
        listnames['Overlap_per'] = listnames['Overlap_per'].apply(lambda x: x[0] / x[1] if x[1] != 0 else np.nan)
        listnames = listnames.round({'Overlap_per': 2})
        listnames['size'] = listnames['Overlap'].apply(lambda x: [float(n) for n in x.split('/')[0:2]])
        listnames['size'] = listnames['size'].apply(lambda x: (1000 / x[1]))
        listnames['Genes'] = listnames['Genes'].apply(lambda x: x.split(";"))
        filename= 'enrTable.csv'



    else:
        gene_list.columns = range(gene_list.shape[1])
        gen_list = gene_list[[4, 3]]
        gen_list = gen_list.iloc[1:]
        gen_list[3] = gen_list[3].astype(float)
        gen_list[3] = -np.log(gen_list[3])
        gen_list = gen_list.sort_values(3, ascending=False)
        pre_res = gp.prerank(rnk=gen_list,
                             gene_sets=gmtfile,
                             min_size=5,
                             processes=-1,
                             permutation_num=100,  # reduce number to speed up testing
                             outdir='plots/prerank_report', format='png', seed=6)
        #listnames = pd.merge(pre_res.res2d, gmtfiledf, how="inner", on='Term')
        listnames = pre_res.res2d

        #listnames = pd.merge(listnames,gmtdf,how="inner", on='Term')
        listnames = listnames.sort_values(by='pval', ascending=True).head(20)
        listnames["-log(p)"] = -np.log(listnames["pval"])
        listnames['Overlap_per'] =listnames['matched_size']/listnames['geneset_size']
        listnames = listnames.round({'Overlap_per': 2})
        listnames['genes'] = listnames['genes'].apply(lambda x: x.split(";"))
        listnames.index.name = 'Term'
        listnames.reset_index(inplace=True)
        listnames = listnames.drop(['es', 'nes'], axis=1)
        listnames.replace([np.inf, -np.inf], 1000, inplace=True)
        for i in listnames['-log(p)']:
            max_val=i
            if max_val != 1000:
                break

        listnames.replace(1000, max_val*2, inplace=True)
        filename = 'rankEnrTable.csv'


    if tab_out == True:
        dirName = 'EnrTables/'
        try:
            # Create target Directory
            os.mkdir(dirName)
            print("Directory ", dirName, " Created ")
        except FileExistsError:
            print("Directory ", dirName, " already exists")
        listnames.to_csv(os.getcwd() + "/" + dirName + filename)

    return listnames

def plotting(table, ranked):
    if ranked == False:
        fig = px.scatter(table.sort_values(by='Adjusted P-value', ascending=False), x='-log(p)', y=table.sort_values(by='Adjusted P-value', ascending=False).Term.str.split(';', expand=True)[0], size="size",
                         color='Overlap_per', color_continuous_scale='inferno',
                         title="Gene Enrichment",
                         labels={"Overlap_per": "Overlap"},
                         width=1600, height=700
                         )
        fig.update_layout(showlegend=False)
        fig.show()
        fig.update_layout(showlegend=False)
        fig.write_image("plots/scatterplot_unranked.png")
        fig.show()
    else:
        fig = px.scatter(table.sort_values(by='pval', ascending=False), x='-log(p)', y=table.sort_values(by='pval', ascending=False).Term.str.split(';', expand=True)[0], size="geneset_size",
                         color='Overlap_per', color_continuous_scale='inferno',
                         title="Gene Enrichment",
                         labels={"Overlap_per": "Overlap"},
                         width=1600, height=700
                         )
        fig.update_layout(showlegend=False)
        fig.write_image("plots/scatterplot_ranked.png")
        fig.show()

def setCover(table, thresh):
    r = set(itertools.chain.from_iterable(table.Genes))  # list of uncovered genes in Universe
    c = []  # list of covered genes
    sc = []  # set cover result
    u_len = len(r)  # size of Universe
   # thresh = 95  # preferably below 100
    sets = table  # datasets
    df = pd.DataFrame(columns=list(table.columns))
    discarded = pd.DataFrame(columns=list(table.columns))

    while (len(c) / u_len) * 100 < thresh:
        sets['scores'] = sets.apply(lambda x: coverageScore(x['Genes'], r, x['Adjusted P-value']), axis=1)
        delete = sets[sets['scores'] == 0].index
        sets.drop(delete, inplace=True)
        df = df.append(sets.iloc[0])
        print(sets.iloc[0])
        c.extend(intersection(sets.Genes.iloc[0], r))
        for ele in intersection(c, r):
            r.remove(ele)
        sets = sets.iloc[1:]

    #df.to_csv(dirName + "SetcoverEnr.csv")
    return df

#read in files

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def main():
    parser = argparse.ArgumentParser(description="Read .gmt file and pathway data")
    #parser.add_argument("--custom", required=True, type=bool, default=True,
    #                        help="Option of using custom .gmt file or predefined database")
    #parser.add_argument("--gmt", required=True,
    #                    help="Path to gene set file representing the pathways (e.g. PathwayCommons)")
    parser.add_argument("--db", required=True, choices=['ALL', 'BIOCARTA' ,'KEGG', 'WP', 'PID', 'NABA', 'SA', 'REACTOME'], help="Option of selecting the database.")
    #parser.add_argument("--gmt",
    #                    help="Path to gene set file representing the pathways (e.g. PathwayCommons)")
    #parser.add_argument("--db",
    #                    help="Name of predefined database")
    parser.add_argument("--gene_list", required=True,
                        help="Path to gene list we want to analyze")
    parser.add_argument("--tab_out", type=bool,default=True)
    parser.add_argument("--ranked", action="store_true") # TODO implement functionality
    parser.add_argument("--dedup_threshold", type=float, default=0.95)


    args = parser.parse_args()
    #if args.custom == True:
    gmtfile = processGmt(os.path.dirname(__file__) + '/' + 'Data/' + 'c2.cp.v7.4.symbols.gmt')
    #else:
    #    gmtfiledf = args.db
    gene_list = preProcess(args.gene_list)
    glist = genelistGen(gene_list)
    #if args.custom == True:
    gmt = dbSelect(gmtfile, args.db)
    resulttable = enrichmentAnalysis(gmtfile=gmt, genelist=glist, gene_list=gene_list, ranked=args.ranked, tab_out=args.tab_out)
    #else:
    #   resulttable = enrichmentAnalysis(gmtfile=args.db, genelist=glist, gmtdf=gmtfiledf, ranked=args.ranked, tab_out=args.tab_out, custom=args.custom)
    plotting(resulttable, ranked=args.ranked)
    #deduplicated = setCover(resulttable, args.dedup_threshold)
#    plotting(deduplicated)

if __name__ == "__main__":
    main()
