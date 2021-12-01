import os
from pathlib import Path
import numpy as np
import pandas as pd
import functools as ft

import matplotlib.pyplot as plt
import matplotlib.ticker as mticks
import matplotlib.image as mimage

from finstat.style import grc

def returner(func):
    @ft.wraps(func)
    def wrapper(self, *args, return_fig=False, **kwargs):
        fig, fname = func(self, *args, **kwargs)

        plt.savefig(self.IMG_PATH / fname, bbox_inches='tight')
        
        if return_fig:
            return fig

    return wrapper

class Plots:
    FREQKEY = {'Q-DEC': 'Quarterly', 'A-DEC': 'Annual', 'M': 'Monthly'}
    names = ['istat', 'cap_struct', 'wocap', 'revpie']

    def __init__(self, fstat, figsize=(12,8), root='', data=''):
        import builtins

        self.ROOT_DIR = Path(root) if root else Path(builtins.DATA_DIR)
        self.fstat = fstat
        self.figsize = figsize

    @property
    def LOGO_PATH(self):
        return self.ROOT_DIR / 'logo.png'
    
    @property
    def IMG_PATH(self):
        chart_dir = Path(self.ROOT_DIR / 'charts')
        if not chart_dir.is_dir():
            chart_dir.mkdir(parents=True)

        return chart_dir

    def _insert_logo(self, ax, bbox):
        im = mimage.imread(self.LOGO_PATH)
        imax = ax.inset_axes(bbox, transform=ax.transAxes, zorder=10)
        imax.axis('off')
        imax.imshow(im, aspect='auto', extent=(0.4, 0.6, .5, .7), zorder=10)

    def make_all(self, return_figs=True):
        self._plots = {}
        for name in self.names:
            self._plots[name] = getattr(self, name)(return_fig=return_figs)

        return self

    @property
    def plots(self):
        if not hasattr(self, '_plots'):
            raise AttributeError('You must call `make_all` first')
        else:
            return self._plots

    @returner
    def istat(self, stat=None, return_fig=False):
        self.fstat.istat.update(refresh=True)
        stat = self.fstat.istat.utils.resample('Q', accts=True, aggfunc='sum', clip_rng=True) if stat == None else stat

        fig, ax = plt.subplots(figsize=self.figsize)

        xindex = np.arange(stat.columns.size)
        ax.plot(stat.loc['Revenue'].values, lw=4, c=grc.blue.data, label='Revenue')
        ax.plot(stat.loc['Gross Profit'].values, lw=4, c=grc.lblue.data, label='Gross Profit')
        ax.plot(stat.loc['Net Income'].values, lw=4, c=grc.green.data, label='Net Income')

        ax.set_xticks(np.arange(stat.columns.size))
        ax.set_xticklabels([stat.columns[i].strftime('%b\n%Y') if not i%4 else None for i in range(xindex.size)])

        ax.yaxis.set_major_formatter('${x:,.0f}')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.legend(title='\n')
        self._insert_logo(ax, [.025, .93, .1, .045])

        freq = stat.T.resample('Q').sum().T.columns.freqstr
        ax.set_title(f'Income Statement\n{self.FREQKEY[freq]}', y=1, size=32)

        return fig, 'istat.jpg'

    @returner
    def cap_struct(self, bsheet=None, show_d2cap=True, return_fig=False):
        bsheet = self.fstat.bsheet.utils.quarterly(clip_rng=True) if bsheet == None else bsheet

        fig, ax = plt.subplots(figsize=self.figsize)

        xindex = np.arange(bsheet.columns.size)
        bar1 = ax.bar(
            xindex, 
            bsheet.loc["Shareholders' Equity"].values[0], 
            width=.9, 
            color=grc.green.data,
            label='Equity     ',
            tick_label=bsheet.columns.strftime('%Y-%m'),
        )
        bar2 = ax.bar(
            xindex,
            bsheet.loc['Indebtedness'].values[0],
            width=.9,
            color=grc.blue.data,    
            bottom=bsheet.loc["Shareholders' Equity"].values[0],
            label='Debt    '
        )

        ax.set_xticklabels([bsheet.columns[i].strftime('%b\n%Y') if not (i + 1) % 4 else None for i in range(xindex.size)])
        ax.yaxis.set_major_formatter('{x:,.0f}')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if show_d2cap:
            twinx = ax.twinx()
            dcline, = twinx.plot(xindex, bsheet.loc['Debt-to-Capital'].values[0], lw=4, color='r', label='Debt-to-Capital')

            twinx.yaxis.set_major_formatter('{x:.0%}')
            twinx.spines['top'].set_visible(False)
            twinx.legend([bar1, bar2, dcline], ['Equity', 'Debt', 'Debt-to-Cap'], loc='upper left', framealpha=1, title='\n')
            self._insert_logo(twinx, [.02825, .93, .1, .045])
        else:
            ax.legend(title='\n')
            self._insert_logo(ax, [.02, .93, .1, .045])

        ax.set_title('Capital Structure \nMonthly', y=1, size=32)

        return fig, 'capstruct.jpg'

    @returner
    def wocap(self, bsheet=None, show_crat=True, return_fig=False):
        bsheet = self.fstat.bsheet.utils.quarterly(clip_rng=True) if bsheet == None else bsheet

        fig, ax = plt.subplots(figsize=self.figsize)

        xindex = np.arange(bsheet.columns.size)
        w = 0.35

        rects1 = ax.bar(xindex - w/2, bsheet.loc['Current Assets'].values[0], w, color=grc.blue, label='Current Assets')
        rects2 = ax.bar(xindex + w/2, bsheet.loc['Current Liabilities'].values[0], w, color=grc.green, label='Current Liabilities')

        ax.set_xticks(np.arange(bsheet.columns.size))
        ax.set_xticklabels([bsheet.columns[i].strftime('%b\n%Y') if not i%4 else None for i in range(xindex.size)])

        ax.yaxis.set_major_formatter(mticks.FuncFormatter(lambda x, p: f'${x/1e6:,.0f}M'))

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if show_crat:
            twinx = ax.twinx()
            cratline, = twinx.plot(xindex[4:], bsheet.loc['Current Ratio'].values[0][4:], lw=4, color='r', label='Current Ratio')

            twinx.spines['top'].set_visible(False)
            twinx.yaxis.set_major_formatter('{x:.1f}x')

            twinx.legend([rects1, rects2, cratline], ['Current Assets', 'Current Liabilities', 'Current Ratio'], loc='upper left', title='\n')
            self._insert_logo(twinx, [.0475, .93, .1, .045])
        else:
            ax.legend(title='\n')
            self._insert_logo(ax, [.02, .93, .1, .045])

        freq = bsheet.columns.freqstr    
        ax.set_title(f'Working Capital\n{self.FREQKEY[freq]}', y=1, size=32)

        return fig, 'wocap.jpg'

    @returner
    def revpie(self, istat=None, return_fig=False):
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        istat = self.fstat.istat if istat is None else istat

        rev_by_sgmt = istat.rev.utils.resample('A', sgmts=True).loc[pd.IndexSlice[:, 'Revenue'], :]
        rev_by_sgmt = rev_by_sgmt.reset_index().set_index('Segment').drop(columns='Account')
        rev_by_sgmt = rev_by_sgmt / rev_by_sgmt.sum(axis=0)

        labels = rev_by_sgmt.index.values
        sizes1 = rev_by_sgmt.loc[:, rev_by_sgmt.columns[0]]
        sizes2 = rev_by_sgmt.loc[:, rev_by_sgmt.columns[1]]

        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,8))
        ax1.pie(
            sizes1, labels=labels, autopct='%1.0f%%', colors=[grc.blue, grc.green, grc.lblue],
            startangle=90, textprops={'size': 14}
        )
        ax2.pie(
            sizes2, labels=labels, autopct='%1.0f%%', colors=[grc.blue, grc.green, grc.lblue],
            startangle=90, textprops={'size': 14}
        )

        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax2.axis('equal')

        ax1.set_title('2022', y=.85, fontsize=24)
        ax2.set_title('2023', y=.85, fontsize=24)
        plt.suptitle('Revenue by Region', y=.9, fontsize=32)
        
        return fig, 'revpie.jpg'

    @returner
    def multibar(self, istat=None, values=[], style='', return_fig=False):
        istat = self.fstat.istat if istat is None else istat

        opex_accts = istat._wages.ACCOUNTS + istat._opex.ACCOUNTS
        segopex = istat.annually().loc[opex_accts.names, :].groupby('Segment').sum()

        if style == 'per_rev':
            segopex /= istat.annually().loc['Total Revenue'].values
        elif style == 'hc':
            segopex = istat.wages._headcount.T.resample('A-DEC').last().T.groupby('Segment').sum()

        mid = segopex.shape[0] / 2
        spreads = np.arange(-np.floor(mid), np.ceil(mid))

        x = np.arange(segopex.shape[1])  # the label locations
        w = 0.15  # the width of the bars

        fig, ax = plt.subplots()
        rects = {}
        colors = grc.colors()
        for i, (sgmt, row) in enumerate(segopex.iloc[::-1].iterrows()):
            rects[sgmt] = ax.bar(x - w*spreads[i], row, w, label=sgmt, color=colors[i].data, zorder=5)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_xticks(x)
        ax.set_xticklabels(segopex.columns)

        import matplotlib.ticker as mticks
        @mticks.FuncFormatter
        def mil_fmt(x, pos):
            return f'${x/1e6:,.0f}M'

        if style == 'per_rev':
            ax.yaxis.set_major_formatter(mticks.PercentFormatter(1, decimals=0))
            title = 'Opex by Segment \n(as % of Total Revenue)'
        elif style == 'hc':
            title = 'Headcount by Segment'       
        else:
            title = 'Opex by Segment \n(including Salaries & Bonuses)'
            ax.yaxis.set_major_formatter(mil_fmt)

        ax.tick_params('y', width=0)

        ax.set_title(title)
        ax.legend(framealpha=1)

        for spine in ax.spines:
            ax.spines[spine].set_visible(False)

        ax.grid(axis='y', zorder=1, alpha=.5)

        filename = f'multi_{style}.jpeg'
        return fig, filename
