import os
import numpy as np
import pandas as pd
import itertools as it

import xlwings as xw

from finstat.style import tabs
from finstat.finstat import FinStat

IMG_KWARGS = {
    'istat': {
        'left': 0,
        'top': 0,
    },
    'revpie': {
        'left': 800,
        'top': 0
    },
    'cap_struct': {
        'left': 0,
        'top': 600
    },
    'wocap': {
        'left': 800,
        'top': 600
    },
}

@xw.sub
def main():
    wb = xw.Book.caller()
    args = compile_sheets(wb)
    cash = 1620209
    ar = 89511
    # inventory = 720712
    capass = 76380
    ap = 221100 + 60554 + 20023 + 223133 + 58034
    nols = 15380552
    taxcrryfwd = nols * .35
    plug = 595173
    eq = 14756919 + 1447777 + 2000000 + 1441094 - plug + taxcrryfwd - ar
    re = -16417861 - 1505880
    opening = pd.DataFrame.from_dict({
        'Shadow Cash': cash,
        'Tax Carry-Forward': taxcrryfwd,
        'Accounts Payable': ap,
        'Equity Capital': eq,
        'Retained Earnings': re,
    }, orient='index')
    fstat = FinStat(*args, opening=opening, make_plots=True)
    print ('Add Spacers')
    add_spacers(wb)
    print ('Add Summary')
    add_summary(wb, fstat)
    print ('Expense Analysis')
    add_exp_anal(wb, fstat)
    print ('Write Data')
    write_data(wb, fstat)
    print ('Write Expense Schedules')
    add_exp_schedule(wb, fstat)
    print ('Color Tabs')
    color_tabs(wb)
    print ('Complete')

def compile_sheets(wb):
    pipeline = wb.sheets['Pipeline'].range('A1:BA200').options(pd.DataFrame, index=False, header=False, numbers=float).value
    pipeline = pipeline.fillna(np.nan)

    assumps = wb.sheets['Assumptions'].range('A1').expand().options(pd.DataFrame).value
    assumps = assumps.fillna(np.nan)

    wages = wb.sheets['Wages - Raw'].range('A1').expand().options(pd.DataFrame, index=False, header=False).value
    wages = wages.fillna(np.nan)

    hcraw = wb.sheets['Headcount - Raw'].range('A1').expand().options(pd.DataFrame, index=False, header=False).value

    opex = wb.sheets['Opex'].range('A1:R100').options(pd.DataFrame, index=False, header=False).value
    idxs = np.argwhere(opex.isna().all(axis=1).values).flatten()
    last = idxs[(idxs - np.roll(idxs, 1)) == 1][0]
    opex = opex.iloc[:last-1]
    opex = opex.loc[:, ~opex.isna().all(axis=0)]
    opex = opex.fillna(np.nan)

    capex = wb.sheets['Capex'].range('A1').expand().options(pd.DataFrame, index=False, header=False).value
    capex = capex.fillna(np.nan)

    capital = wb.sheets['Capital'].range('A1').expand().options(pd.DataFrame, index=False).value
    capital = capital.fillna(np.nan)

    return pipeline, wages, hcraw, opex, capex, capital, assumps

# Add Spacers if Required
def add_spacers(wb):
    for name in tabs.spacers:
        if name not in [s.name for s in wb.sheets]:
            after = tabs.before_after.loc[name, 'after']
            wb.sheets.add(name, after=after)

def add_exp_anal(wb, fstat):
    if 'Expenses' not in [s.name for s in wb.sheets]:
        exp = wb.sheets.add('Expenses', after=tabs.spacers[1])
    else:
        exp = wb.sheets['Expenses']

    exp.range('A2').expand('table').value = fstat.istat.opex.top10()

def add_summary(wb, fstat):
    if 'Charts' not in [s.name for s in wb.sheets]:
        summ = wb.sheets.add('Charts', after=tabs.spacers[1])
    else:
        summ = wb.sheets['Charts']

    for plot, fig in fstat.plots.plots.items():
        kws = IMG_KWARGS[plot]
        summ.pictures.add(fig, name=plot, update=True, **kws)

def write_data(wb, fstat):
    for period, stat in it.product(['A', 'Q'], fstat.STAT_NAMES):
        statobj = getattr(fstat, stat.lower())
        
        update_kws = {'hide': True}
        if stat.lower() == 'istat':
            update_kws = {'ops': ['_merge_benefits'], **update_kws}

        if stat.lower() == 'istat':
            frame = fstat.istat.update(refresh=True, **update_kws).resample(period, accts=True, str_cols=False, clip_rng=fstat.istat.stat.columns.tolist())
        else:
            frame = statobj.update(refresh=True, **update_kws).resample(period, accts=True, str_cols=False, clip_rng=fstat.istat.stat.columns.tolist())

        strf = '%Y' if period == 'A-DEC' else '%b-%y'
        frame.columns = frame.columns.strftime(strf)
        wb.sheets[f'{stat} - {period}'][:frame.shape[1] + 1 , :frame.shape[0] + 1].options(index=True, header=True).value = frame

def add_exp_schedule(wb, fstat):
    if 'Expense Schedule - A' not in [s.name for s in wb.sheets]:
        exp = wb.sheets.add('Expense Schedule - A', before=tabs.spacers[-2])
    else:
        exp = wb.sheets['Expense Schedule - A']

    annual = fstat.istat._opex.exp_schedule().isutils.annually()
    annual.columns = annual.columns.strftime('%b-%y')

    exp.range('A1').expand('table').value = annual

    if 'Expense Schedule - Q' not in [s.name for s in wb.sheets]:
        exp = wb.sheets.add('Expense Schedule - Q', before=tabs.spacers[-1])
    else:
        exp = wb.sheets['Expense Schedule - Q']

    quarterly = fstat.istat._opex.exp_schedule()
    quarterly.columns = quarterly.columns.strftime('%b-%y')

    exp.range('A1').expand('table').value = quarterly

def color_tabs(wb):
    for sheet in wb.sheets:
        tabs.set_color(sheet)
        