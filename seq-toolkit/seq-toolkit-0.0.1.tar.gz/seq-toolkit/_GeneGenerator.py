
import vinplots
import pandas as pd
import matplotlib.pyplot as plt


from ._SequenceGenerator import _SequenceGenerator

def _define_gene_exons(n_bases, n_boundaries, boundary_spacing):
    
    """"""
    
    ExonDict = {}
    ExonDict['Start'] = []
    ExonDict['End'] = []
    
    exon_bounds = np.sort(np.random.choice(n_bases, n_boundaries))
    
    for i in range(len(exon_bounds)-1):
        if i % boundary_spacing == 0:
            Exon['Start'].append(exon_bounds[i])
            Exon['End'].append(exon_bounds[i + 1])
           
    exon_df = pd.DataFrame.from_dict(Exon)
    
    return exon_df

def _construct_gene_plot():

    fig = vinplots.Plot()
    fig.construct(nplots=1, ncols=1, figsize_width=2.5)
    fig.modify_spines(ax="all", spines_to_delete=['top', 'right', 'left'])
    ax = fig.AxesDict[0][0]
    xt = ax.set_xticks(np.linspace(0, 50000, 11))
    yt = ax.set_yticks([])
    
    return fig, ax

def _plot_gene(exon_df, color="navy"):
    
    """"""
    
    fig, ax = _construct_gene_plot()
    
    plt.hlines(1, exon_bounds.min(), exon_bounds.max(), color=color, zorder=2)
    plt.ylim(.95, 1.1)
    
    for i, exon in exon_df.iterrows():
        plt.vlines(exon.Start, 0.95, 1.025, color="lightgrey", linestyle="--", lw=1)
        plt.vlines(exon.End, 0.95, 1.025, color="lightgrey", linestyle="--", lw=1)
        plt.text(x=exon_start + 200, y=1.03, s="{}-{}".format(exon.Start, exon.End), rotation=25)
        plt.hlines(1, exon.Start, exon.End, color=color, lw=15, zorder=2)


class _GeneGenerator:
    
    def __init__(self, A=1, C=1, G=1, T=1):
        
        """"""
        
        self.Gene = {}
        self.SeqGen = _SequenceGenerator(A, C, G, T)
        
        
    def create(self, n_bases, n_boundaries=30, boundary_spacing=5, return_gene=True):
        
        self.n_bases = n_bases
        self.Gene["seq"] = self.seq = self.SeqGen.simulate(n_bases, return_seq=True)
        self.Gene["exons"] = self.exon_df = _define_gene_exons(n_bases, n_boundaries, boundary_spacing)
        
        
        if return_gene:
            return self.seq
        
    def plot(self, color="navy"):
        
        _plot_gene(self.exon_df, color)