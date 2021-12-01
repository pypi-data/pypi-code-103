import datetime as dt
import numpy as np
import pandas as pd

import xlwings as xw

WAGE_INFLATION = .03
IDX_COL_NAMES = ['Role', 'Segment', 'Focus', 'Salary']



def wagemaker(plan):
    headix, = np.where((plan.iloc[:, :4] == IDX_COL_NAMES).all(axis=1))
    splits = np.split(plan, headix)
    sgmts = []
    for df_sgmt in splits[1:]:
        df_sgmt.columns = df_sgmt.iloc[0]

        df_sgmt = df_sgmt.iloc[1:]
        footidx, = np.where(df_sgmt.Role == 'Total')

        df_sgmt = df_sgmt.iloc[:footidx[0]]
        df_sgmt = df_sgmt[df_sgmt.columns[~df_sgmt.columns.astype('str').str.contains('202')]]

        df_sgmt.Focus = df_sgmt.Focus.fillna('')

        front = np.arange(4)
        back = np.arange(df_sgmt.shape[1] - 16, df_sgmt.shape[1])
        other = np.array([df_sgmt.columns.get_loc('Current')])

        icols = np.concatenate((front, other, back))
        df_sgmt = df_sgmt.iloc[:, icols].set_index(IDX_COL_NAMES).fillna(0)
        df_sgmt.columns.name = 'Period'
        sgmts.append(df_sgmt)

    df = pd.concat(sgmts)

    df_starts = df.iloc[:, 1:].applymap(type_sched)
    expands = []
    for i in range(df_starts.shape[1]):
        df_exp = df_starts.iloc[:, i].apply(pd.Series)
        expands.append(df_exp)

    df_starts = pd.concat(expands, axis=1).astype('int')
    df_starts.columns = pd.period_range(start='2022-01', periods=df_starts.shape[1], freq='M')
    df = pd.concat((df.iloc[:, :1], df_starts), axis=1).astype('int')

    factors = _wage_factors(*df.shape)
    factors = np.hstack((factors[:, :1], factors))
    wo_inf = _wages_wo_inf(df.columns, df.index.get_level_values('Salary').astype('float')/12)
    wages_w_inf = np.multiply(wo_inf.astype('float'), factors)
    df_wages = np.multiply(wages_w_inf, df.cumsum(axis=1))

    return df, df_wages

def make_raw(plan, type_=''):
    df, df_wages = wagemaker(plan)

    if type_ == 'wages':
        df_wages = df_wages.rename(columns={'Current': '2021-12'})
        df_wages.columns = pd.PeriodIndex(df_wages.columns)
        df_wages.columns = df_wages.columns.strftime('%b-%y')

        return df_wages
    elif type_ == 'hc':
        df = df.rename(columns={'Current': '2021-12'})
        df.columns = pd.PeriodIndex(df.columns)
        df.columns = df.columns.strftime('%b-%y')
        
        return df

def resamp(df, type_='', freq=''):
    rsamp_str = '%b-%y' if freq == 'Q' else '%Y'
    aggfunc = 'sum' if type_ == 'wages' else 'last'
    df.columns = pd.PeriodIndex([dt.datetime.strptime(s, '%b-%y') for s in df.columns], freq='M')
    resampled = df.T.resample(freq).agg(aggfunc).T.groupby('Segment').sum()
    resampled.loc['Total'] = resampled.sum()
    resampled.columns = resampled.columns.strftime(rsamp_str)
    return resampled

@xw.func
def quarterly_rev():
    wb = xw.Book.caller()
    pipeline = wb.sheets['Pipeline']
    pipeline = pipeline['A1:AU120'].options(pd.DataFrame, index=False).value
    rev = RevStat.from_schedule(pipeline)
    rev = rev._base.isutils.accts().loc['Revenue']

    return rev.values

@xw.func
def annual_rev():
    wb = xw.Book.caller()
    pipeline = wb.sheets['Pipeline']
    pipeline = pipeline['A1:AU120'].options(pd.DataFrame, index=False).value
    rev = RevStat.from_schedule(pipeline)
    rev = rev._base.isutils.resample('A', accts=True).loc['Revenue']

    return rev.values

@xw.func
@xw.arg('plan', pd.DataFrame, index=False, header=False, ndim=2)
@xw.ret(expand='table')
def raw_wages(plan):
    return make_raw(plan, 'wages')

@xw.func
@xw.arg('plan', pd.DataFrame, index=False, header=False, ndim=2)
@xw.ret(expand='table')
def raw_headcount(plan):
    hc = make_raw(plan, 'hc')
    return hc.cumsum(axis=1)
    
@xw.func
@xw.arg('wages', pd.DataFrame, index=False, header=True, expand='table', ndim=2)
def annual_wages(wages):
    ### Split, sort, and recombine
    wages = wages.set_index(IDX_COL_NAMES)
    return resamp(wages, 'wages', 'A').iloc[:, 1:]

@xw.func
@xw.arg('wages', pd.DataFrame, index=False, header=True, expand='table', ndim=2)
def quarterly_wages(wages):
    ### Split, sort, and recombine
    wages = wages.set_index(IDX_COL_NAMES)
    return resamp(wages, 'wages', 'Q').iloc[:, 1:]

@xw.func
@xw.arg('hc', pd.DataFrame, index=False, header=True, expand='table', ndim=2)
def annual_hc(hc):
    hc = hc.set_index(IDX_COL_NAMES)
    return resamp(hc, 'hc', 'A')

@xw.func
@xw.arg('hc', pd.DataFrame, index=False, header=True, expand='table', ndim=2)
def quarterly_hc(hc):
    hc = hc.set_index(IDX_COL_NAMES)
    return resamp(hc, 'hc', 'Q')

@xw.func
@xw.arg('existing', pd.DataFrame, index=True, header=True, ndim=2)
def existing_counts(existing):
    existing.Focus = existing.Focus.fillna('')
    counts = existing.groupby(['Segment', 'Role', 'Focus', 'Salary']).size()
    counts.columns = ['Count']
    return counts

@xw.func
@xw.arg('counts', pd.DataFrame, index=False, header=True, ndim=2)
def existing_lookup(sgmt, role, focus, salary, counts):
    focus = '' if focus is None else focus
    counts = counts.set_index(['Segment', 'Role', 'Focus', 'Salary'])
    if counts.index.isin([(sgmt, role, focus, salary)]).any():
        return counts.loc[(sgmt, role, focus, salary)].iloc[0]
    else:
        return 0

@xw.func
@xw.arg('hires', pd.Series, index=False, header=False, ndim=1)
def find_schedule(hires):
    hires = pd.DataFrame(hires.fillna(0).values.reshape(-1, 4)).T
    cumsched = hires.apply(sum_sched_for_series).values.cumsum()
    if (cumsched == 0).all():
        return None
    else:
        return ', '.join([f'{v:.0f}' for v in cumsched])

def type_sched(x):
    if isinstance(x, str):
        splitter = x.split(', ') if ', ' in x else x.split(' ')
        x = np.array([int(h) for h in x.split(' ') if h])
        if x.size > 3:
            x[2] = x[2:].sum()
            x = x[:3]
        elif x.size < 3:
            x = np.concatenate((x, np.zeros(x.size - 1)))
    elif isinstance(x, (int, float)):
        x = np.array([x, 0 , 0])
    else:
        raise

    return x

def sum_sched(x):
    if isinstance(x, str):
        x = sum([int(h) for h in x.split(' ') if h])
    elif isinstance(x, (int, float)):
        pass
    else:
        raise

    return x

def sum_sched_for_series(ser):
    ser = ser.apply(sum_sched)
    return ser.sum()

def _wage_factors(hcsize, projsize):
    wage_factors = np.array([(1 + WAGE_INFLATION)**i for i in np.arange(projsize//12)])
    wage_factors = np.repeat(wage_factors, 12)

    return np.tile(wage_factors, (hcsize,1))

def _wages_wo_inf(projrng, wages):
    return np.repeat(wages, projrng.size).values.reshape((wages.size, projrng.size))

@xw.func
@xw.arg('recruits', pd.DataFrame, index=False, header=True, ndim=2, expand='table')
@xw.ret(expand='table')
def recruit_fees(recruits):
    # plan = wb.sheets['Headcount - Plan'].range('A10').expand().options(pd.DataFrame, index=False).value

    recruits = recruits.set_index(recruits.columns[:9].tolist()).fillna(0)
    recruits = recruits[recruits.columns[recruits.columns.str.contains('Q')]]
    fees = recruits.index.get_level_values('Recruiting Fee').fillna(0).values.astype('float').reshape(-1,1)
    recruits.loc[:, :] = fees * recruits.values
    return recruits.sum(axis=0).values