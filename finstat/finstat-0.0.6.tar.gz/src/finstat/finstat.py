import numpy as np
import pandas as pd
import functools as ft

from finstat.accounts import ISTAT_ACCOUNTS, BSHEET_ACCOUNTS, EQ_ACCOUNTS, CFLOW_ACCOUNTS
from finstat.fincalcs import expon, expon_fit
from finstat.extensions import UtilsMixin, IStatUtils
from finstat.visuals import Plots

# UTILITIES, ASSIGNORS, AND METRIC FUNCS
def set_assumps(func):
    # Sets constants for object if 'assumps' key passed
    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        if 'assumps' in kwargs and isinstance(kwargs['assumps'], pd.DataFrame):
            assumps = self.constants_as_records(kwargs['assumps'])
            for name, value in assumps.items():
                if name in self.INT_ASSUMPS:
                    value = int(value['Factor'])
                elif name in self.FREQ_ASSUMPS:
                    value = int(value['Factor'])
                    value = pd.tseries.frequencies.to_offset(f'{value}M')
                else:
                    value = value['Factor']

                setattr(self, name, value)
            
        return func(self, *args, **kwargs)
    
    return wrapper

def set_projrng(func):
    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        if 'projrng' in kwargs and kwargs['projrng'] is not None:
            self._projrng = kwargs['projrng']
        
        return func(self, *args, **kwargs)
    
    return wrapper

### INDEX MIXIN ###
class IndexMix:
    """Mixin for index sublcass of each statement"""
    def __init__(self, obj):
        self.obj = obj
        self._levels = self._set_levels()
        self._base = self._make_base()

    @property
    def nlevels(self):
        return len(self.levels)
    
    @property
    def acctpos(self):
        return self.names.index('Account')
    
    @property
    def levels(self):
        return self._levels
    
    @property
    def names(self):
        return list(self.levels.keys())
    
    @property
    def base(self):
        return self._base

    def _set_levels(self):
        levels = {k:v for k, v in self.__class__.__dict__.items() if '__' not in k}
        if 'Account' not  in levels:
            levels['Account'] = ISTAT_ACCOUNTS.names
        return levels
    
    def _make_base(self):
        idxs = {}
        for name, cats in self.levels.items():
            if name == 'Segment' and self.obj.is_istat:
                cats = self.obj.sgmt_categories()

            any_cats = cats.size if isinstance(cats, np.ndarray) else cats
            if any_cats:
                idxs[name] = pd.Categorical([], cats, ordered=True)
            else:
                idxs[name] = cats

        codes = [[] for i in range(len(idxs))]

        return pd.MultiIndex(levels=idxs.values(), codes=codes, names=idxs.keys())
 
### BASE STATEMENTS ###
class BaseStat(UtilsMixin):
    _START = '2022-01'
    _END = '2025-12'
    _projrng = pd.period_range(start=_START, end=_END, freq='Q')
    FREQKEY = {'H': '2Q', 'Q': 'Q', 'M': 'M', 'A': 'A'}
    ZERO_ROWS = []
    INT_ASSUMPS = ['AMORT_YEARS']
    FREQ_ASSUMPS = ['AR_COLLECTION', 'AP_COLLECTION', 'INVENTORY_LEAD']

    CONSTANTS_KEY = {
        'Interest Rate': 'INT_RATE',
        'Income Tax Rate': 'TAX_RATE',
        'AR Terms': 'AR_COLLECTION',
        'AP Terms': 'AP_COLLECTION',
        'Inventory Lead Time': 'INVENTORY_LEAD',
        'Amortization Schedule': 'AMORT_YEARS',
        'Payroll Taxes': 'PAYROLL_TAXES',
        'Wage Inflation': 'WAGE_INFLATION',
        'Benefits': 'ANNUAL_BENEFITS',
        'Payroll Fees': 'ANNUAL_PAYROLL_FEES',
        'Unemployment Fees': 'ANNUAL_UNEMPLOYMENT',
        "Workers' Compensation": 'ANNUAL_WORKERS_COMP',
        '401K Contributions': 'ANNUAL_401K'
    }

    def __repr__(self):
        if hasattr(self, 'FULL_NAME'):

            freqstr = self.projrng.freq.__str__()
            if ':' in freqstr:
                freqstr = freqstr.split(':')[0]
            
            freqstr = freqstr.strip('<').strip('>')
            start = self.projrng[0].strftime('%b-%y')
            end = self.projrng[-1].strftime('%b-%y')
            return f'{self.FULL_NAME}: {freqstr} {start} to {end}'
        else:
            return super().__repr__()

    @property
    def is_istat(self):
        return hasattr(self, '_is_istat') and self._is_istat

    @property
    def projrng(self):
        return self._projrng
        
    @property
    def index(self):
        return self._index
    
    @property
    def frame(self):
        return self._frame

    @property
    def stat(self):
        return self.statement

    @property
    def statement(self):
        return self._statement

    def update(self, *args, refresh=False):
        if refresh:
            self._statement = self._base.copy()

    def _make_frame(self, projrng):
        self._frame = pd.DataFrame(columns=projrng, index=self.index.base)
        return self._frame

    @classmethod
    def from_schedule(cls, *args, projrng=None, **kwargs):
        if projrng is not None:
            cls._projrng = projrng

    @classmethod
    def constants_as_records(cls, assumps):
        assumps.index = [cls.CONSTANTS_KEY[idx] if idx in cls.CONSTANTS_KEY else idx for idx in assumps.index]

        return assumps[~assumps.isna().all(axis=1)].to_dict('index')

    def _add_zero_row(self, acct_name, stat):
        if stat.index.nlevels == 2:
            stat.loc[(acct_name, '---'), :] = 0
        elif stat.index.nlevels == 1:
            stat.loc[acct_name, :] = 0

class BaseIStat(BaseStat):
    """
    Base class to provide unique features to 
    Income Statement based classes.

    In particular, UtilsMixin differentiates between BaseIStat and BaseBSheet
    """
    @set_projrng
    def __init__(self, *args, **kwargs):
        """
        All income statement components set `projrng` using the
        set_projrng decorator.
        The `super()` call then integrates the UtilsMixin
        """
        super().__init__(*args, **kwargs)

class BaseBSheet(BaseStat):
    """
    Base class to provide unique features to 
    Balance Sheet based classes.

    Currently, this base is used only to allow UtilsMixin to 
    support unique Balance Sheet utilities

    Each Balance Sheet statement determines `projrng` uniquely and so `set_projrng` is not needed
    """
    pass

### INCOME STATEMENT and SUPPORTING ###
class RevStat(BaseIStat):
    FULL_NAME = 'Sales Statement'
    ACCOUNTS = ISTAT_ACCOUNTS.by_stat('RevStat')
    _projrng = pd.period_range(start='2022-01', end=pd.Period('2025Q4', freq='Q'), freq='Q')
    
    class Index(IndexMix):
        Segment = ['APAC', 'EMEA', 'AM', '---']
        PipeType = []
        Name = []
        Confidence = ['High', 'Low', '---']
    
    def __init__(self, rev, projrng=None):
        super().__init__(self)
            
        self._index = self.Index(self)
        self._base = self._make_base(rev)
        self.update(refresh=True)
    
    def _make_base(self, rev):
        rev = self._reindex_booking(rev)
        base = self._make_frame(self.projrng)
        base = base.append(rev.stack())
        
        return base.apply(pd.to_numeric, downcast='float').sort_index()
    
    def _reindex_booking(self, rev):
        rev = rev.set_index(self.index.names[:-1])
        rev.columns = pd.MultiIndex.from_product((self.projrng, rev.columns.unique()), names=['Period', 'Account'])
        rev = rev[~rev.index.get_level_values(1).isna()]
        return rev
    
    def update(self, metrics=[], conf=[], refresh=False):
        super().update(refresh=refresh)
        
        for acct in self.ACCOUNTS.tabs:
            if acct.is_sub:
                self._statement = acct.append(self._statement)
        
        if conf:
            high_conf_mask = self._statement.index[self._statement.index.get_level_values('Confidence').isin(conf)]
            self._statement = self._statement.loc[high_conf_mask]

        self._statement = self._statement.fillna(0).sort_index()
        
        return self
    
    @classmethod
    def from_schedule(cls, rev, projrng=None):
        super().from_schedule(rev, projrng=projrng)

        rev.columns = rev.iloc[1]
        idx_start = rev.Name[rev.Name.str.find('  ') == 0].index[0] - 1
        idx_end = rev.Name[rev.Name == 'GAPP REVENUE PROJECTIONS'].index[0] - 1
        rev = rev.iloc[idx_start:idx_end]
        rev = rev[~rev.isna().all(axis=1).T]

        sgmt_brks = rev.index[rev.Name.str.find('  ') == -1]
        rev.insert(0, 'PipeType', '')
        for i in range(sgmt_brks.size):
            last = rev.index[-1] if i == len(sgmt_brks) - 1 else sgmt_brks[i + 1]
            rev.loc[sgmt_brks[i]+1:last, 'PipeType'] = rev.Name[sgmt_brks[i]]
        rev = rev.loc[rev.index.difference(sgmt_brks)]

        rev.loc[:, 'Segment'] = rev.loc[:, 'Segment'].fillna('---')
        rev.insert(2, 'Confidence', '---')

        rev = rev.T[~rev.isna().all()].T

        skiprevs = np.arange(12,4+5*4*2,10)
        skipcols = skiprevs + 1
        skips = np.sort(np.concatenate([skiprevs, skipcols]))
        keeps = np.setdiff1d(np.arange(rev.shape[1]), skips)

        rev = rev.iloc[:, keeps].fillna(0)
        
        return cls(rev)
    
class WageStat(BaseIStat):
    """
    Builds expense statement for salaried employees 
    """
    FULL_NAME = 'Salaries by Role'
    ACCOUNTS = ISTAT_ACCOUNTS.by_stat('WageStat')
    _projrng = pd.period_range(start='2022-01', end=pd.Period('2025-12', freq='M'), freq='M')

    PAYROLL_TAXES = .075
    WAGE_INFLATION = .03

    ANNUAL_BENEFITS = 6000
    ANNUAL_PAYROLL_FEES = 1200
    ANNUAL_UNEMPLOYMENT = 200
  
    ANNUAL_WORKERS_COMP = .0075
    ANNUAL_401K = .1
        
    class Index(IndexMix):
        Segment = ['CE', 'G&A', 'OPS', 'Product', 'S&M']
        Role = []
        Focus = []
        Salary = []
        ID = []
        
    def __init__(self, wages, headcount, projrng=None):
        super().__init__(self, projrng=projrng)
        
        self._index = self.Index(self)
        self._base = self._make_base(wages)

        hc = headcount.T.set_index(0).T.set_index(self.index.names[:-2])
        hc.columns = pd.PeriodIndex(pd.to_datetime(hc.columns, format='%b-%y'), freq='m')

        self._headcount = hc
        
        self.update(refresh=True)

    def _make_base(self, schedule):
        if hasattr(self, '_base'):
            raise ValueError('_base has already been made')

        base = self._make_frame(self.projrng)

        wages = self._make_wages(schedule)
        base = base.append(wages)
        
        benefits = self._make_benefits(base)
        base = base.append(benefits)
        
        return base.apply(pd.to_numeric, downcast='float').sort_index()

    def _make_wages(self, schedule):
        schedule.loc[:, 'Account'] = self.ACCOUNTS.names[0]
        schedule.loc[:, 'ID'] = np.arange(schedule.shape[0])

        if self._from == 'schedule':
            schedule.Start = pd.to_datetime(schedule.Start)
            wages_w_inf = np.multiply(self._wages_wo_inf(schedule.Salary/12), self._wage_factors(schedule.shape[0]))
            values = np.multiply(wages_w_inf, self._wagemask(schedule.Start))
            index = schedule.set_index(self.index.names).index
        elif self._from == 'wages':
            schedule = schedule.set_index(['Segment', 'Role', 'Focus', 'Salary', 'ID', 'Account'])
            index = schedule.index
            values = schedule.values[:, 1:]
        
        return pd.DataFrame(values, index=index, columns=self.projrng).fillna(0)

    def _make_benefits(self, base):
        wage_benefits = np.multiply(base, self._benefits_per_wage(base.shape))
        hc_benefits = np.multiply(base > 0, self._benefits_per_hc(base.shape))
        benefits = np.add(wage_benefits, hc_benefits)

        newidx = base.index.to_frame().reset_index(drop=True)
        newidx.Account = self.ACCOUNTS[1].name
        newidx = pd.MultiIndex.from_frame(newidx)

        return pd.DataFrame(benefits.values, index=newidx, columns=self.projrng).fillna(0)
    
    @classmethod
    @property
    def headcount_benefits(cls):
        return [cls.ANNUAL_BENEFITS, cls.ANNUAL_PAYROLL_FEES, cls.ANNUAL_UNEMPLOYMENT]

    @classmethod
    @property
    def wage_benefits(cls):
        return [cls.ANNUAL_WORKERS_COMP, cls.ANNUAL_401K]
    
    def _benefits_per_hc(self, shape):
        monthly_bens = sum(self.headcount_benefits) / 12
        return np.tile(monthly_bens, shape)

    def _benefits_per_wage(self, shape):
        monthly_bens = sum(self.wage_benefits) / 12
        return np.tile(monthly_bens, shape)
        
    def _wage_factors(self, hcsize):
        wage_factors = np.array([(1 + self.WAGE_INFLATION)**i for i in np.arange(self.projrng.size//12)])
        wage_factors = np.repeat(wage_factors, 12)
        
        return np.tile(wage_factors, (hcsize,1))

    def _wages_wo_inf(self, wages):
        return np.repeat(wages, self.projrng.size).values.reshape((wages.size, self.projrng.size))

    def _startmask(self, start):
        return (self.projrng >= start.to_period('M')).astype('int')
    
    def _wagemask(self, start):
        return np.hstack(start.apply(self._startmask).values).reshape((start.size, self.projrng.size))

    @classmethod
    @set_assumps
    def from_wages(cls, wages:pd.DataFrame, headcount:pd.DataFrame, projrng:pd.PeriodIndex=None, assumps=[]):
        cls._from = 'wages'

        super().from_schedule(projrng=projrng)
        return cls(wages.T.set_index(0).T, headcount)

    @classmethod
    @set_assumps
    def from_schedule(cls, wages:pd.DataFrame, headcount:pd.DataFrame, projrng:pd.PeriodIndex=None, assumps=[]):
        """
        Process
        --------
        Assign projection range
        Create the base dataframe
        
        The split the headcount into two main types of frames:
            1) single: roles where only one hire is required
            2) multi: roles where multiple hires are required
        
        Either type is handled separately
            1) multi: 
                + find first start for each role
                + distribute the new hires evenly during the unique role range
                + assign hire at each unique start date
            2) single:
                + self explanatory
                
        Benefits are added afterwards, some allocated based on each employees wage and some on headcount
        
        Parameters
        ------------
        wages:       Dataframe of excel wages
        """        
        cls._from = 'schedule'
        super().from_schedule(projrng=projrng)
        # Split wagess into single roles or multiple roles
        wages = wages.iloc[:,1:].sort_values(by='n')
        wages.Title = wages.Title.str.strip()
        currmask = wages.Start == 'Current'
        wages.loc[currmask, 'Start'] = cls._projrng[0].to_timestamp()
        
        single, multi = wages[wages.n == 1].copy(), wages[wages.n > 1].copy()
        
        ids = np.arange(1, wages.n.sum() + 1).tolist()
        subframes = []
        for i, role in multi.iterrows():
            role_start = pd.Period(role.Start, freq='M')
            rolerng = pd.period_range(start=role_start, end=cls._projrng[-1], freq='M')

            # Linearly distribute roles thru the rolerng. the end of the rolerng is capped by 
            # the number of periods per role, so there is always a space b/w the end and the last role start
            # the linear range of floats is then floored, which will result in some roles starting on that the same time
            start_idxs = np.floor(np.linspace(0, rolerng.size*(1-(1/role.n)), role.n)).astype('int')
            
            subframe = pd.DataFrame(np.tile(role, (role.n,1)), columns=role.index)
            subframe.Start = pd.to_datetime(rolerng[start_idxs].to_timestamp())
            
            subframes.append(subframe)
                        
        single_from_multi = pd.concat(subframes)
        single_from_multi.n = 1
        
        return cls(pd.concat([single, single_from_multi]), headcount)

class AmortSched(BaseIStat):
    FULL_NAME = 'Amortization'
    ACCOUNTS = ISTAT_ACCOUNTS.by_stat('AmortSched')
    _projrng = pd.period_range(start='2022-01', end=pd.Period('2025-12', freq='M'), freq='M')
    AMORT_YEARS = 5

    class Index(IndexMix):
        Segment = []
        Item = []
        Description = []
        Account = []
        Period = []
        
    def __init__(self, capex, projrng=None):
        super().__init__(self, projrng=projrng)

        self._capex = capex

        self._index = self.Index(self)
        self._base = self._make_base(capex)
        self.update(refresh=True)   
    
    @property
    def amortrng(self):
        return pd.period_range(
            start=self.projrng[0],
            periods=self.projrng.size + self.AMORT_MONTHS, 
            freq=self.projrng.freq
        ) 
    
    @classmethod
    @property
    def capexrng(cls):
        return pd.period_range(start=cls._projrng[0], end=cls._projrng[-1], freq='Q')
         
    @property
    def amortsched(self):
        return self._statement

    @property
    def capex(self):
        return self._capex
    
    @property
    def capexsched(self):
        return self._capex

    @classmethod
    @property
    def AMORT_MONTHS(cls):
        return 12 * cls.AMORT_YEARS

    @classmethod
    @property
    def AMORT_SCHED(cls):
        return 1 / cls.AMORT_MONTHS

    @property
    def SEGMENTS(self):
        return self.stat.index.get_level_values('Segment').unique()
    
    def _make_base(self, capex):
        asched = self._expand_sched(capex)
        base = self._make_frame(self.amortrng)
        base = base.append(asched)

        return base.apply(pd.to_numeric, downcast='float')*-1
    
    def _expand_sched(self, capex):
        # 11 asset type, across 48 monthly periods of projection, across 60 amortization months
        by_purchase = np.repeat(capex.values, self.AMORT_MONTHS).reshape(-1, capex.values.shape[1], self.AMORT_MONTHS)
        amort_by_asset = np.multiply(by_purchase, self.AMORT_SCHED)
        amort_by_asset = amort_by_asset.reshape(amort_by_asset.shape[0]*amort_by_asset.shape[1], -1)
        backend = np.zeros((amort_by_asset.shape[0], by_purchase.shape[1]))
        amort = np.hstack((amort_by_asset, backend))

        # https://stackoverflow.com/questions/20360675/roll-rows-of-a-matrix-independently
        roll = np.tile(np.arange(1,by_purchase.shape[1]+1), (by_purchase.shape[0],1)).flatten()
        rowidx, colidx = np.ogrid[:amort.shape[0], :amort.shape[1]]
        colidx = colidx - roll[:, np.newaxis]
        amortarr = amort[rowidx, colidx]
        
        newidx = self._reindex(capex)
        
        asched = pd.DataFrame(amortarr, index=newidx, columns=self.amortrng)
        
        return asched
    
    def _reindex(self, capex):
        idx = capex.index.to_frame().reset_index(drop=True)
        newidx = pd.DataFrame(np.repeat(idx.values.T, capex.columns.size).reshape(3,-1).T, columns=self.index.names[:-2])
        newidx['Account'] = 'Amortization'
        newidx['Period'] = np.tile(capex.columns.values, (idx.shape[0],1)).ravel()
        newidx = pd.MultiIndex.from_frame(newidx)
        
        return newidx
    
    @classmethod
    @set_assumps
    def from_schedule(cls, capex:pd.DataFrame, projrng=None, assumps=[]):
        super().from_schedule(projrng=projrng)
        
        capex = capex.T.set_index(0).T
        capexidx = ['Asset', 'Item', 'Description']
        capex[capexidx] = capex[capexidx].fillna('')
        capex = capex.set_index(capexidx)
        capex.columns = AmortSched.capexrng

        capex = capex.fillna(0)
        capex = (capex.T.resample('M').asfreq().T / 3).ffill(axis=1)

        return cls(capex)

class OpexStat(BaseIStat):
    FULL_NAME = 'Operating Expenses'
    ACCOUNTS = ISTAT_ACCOUNTS.by_stat('OpexStat')
        
    class Index(IndexMix):
        Segment = ['CE', 'G&A', 'OPS', 'Product', 'S&M']
        Item = []
        
    def __init__(self, istat, specs, gens, projrng=None):
        super().__init__(projrng=projrng)

        self._istat = istat        
        self._index = self.Index(self)
        self._base = self._make_base(specs, gens)

        self.update(refresh=True)
    
    @property
    def istat(self):
        return self._istat

    def top10(self):
        top10 = self.stat.sum(axis=1).sort_values(ascending=False).reset_index().set_index(['Segment', 'Item']).drop(columns='Account').iloc[:10]
        top10.columns = ['4Y Sum']
        return top10

    def exp_schedule(self):
        exp_sched = self.stat.reorder_levels(['Account', 'Segment', 'Item']).droplevel('Account').sort_index()

        items = exp_sched.index.get_level_values('Item').unique().values
        totals = exp_sched.groupby('Segment').sum()

        newidx = totals.index.to_frame()
        newidx['Item'] = 'Total'
        total = totals.sum().to_frame().T
        total.index = ['Total']
        total.index.name = 'Segment'
        totals = totals.append(total)
        totidx = totals.index.to_frame()
        totidx['Item'] = ['Total']*5 + ['---']
        totals.index = pd.MultiIndex.from_frame(totidx)
        exp_sched = exp_sched.append(totals)
        newidx = exp_sched.index.to_frame()
        newidx.Segment = pd.Categorical(newidx.Segment, newidx.Segment.unique(), ordered=True)
        newcats = np.concatenate((items, np.array(['Total', '---'])))
        newidx.Item = pd.Categorical(newidx.Item, newcats, ordered=True)
        newidx = pd.MultiIndex.from_frame(newidx)
        exp_sched.index = newidx

        return exp_sched.sort_index()

    def _make_base(self, specs, gens):
        sub_frames = self._make_gens(gens)
        specs = self._clean_specs(specs)
        sub_frames = pd.concat([specs, sub_frames])
        base = self._make_frame(self.projrng)
        base = base.append(sub_frames)
        
        return base.apply(pd.to_numeric, downcast='float')

    def _clean_specs(self, specs):
        specs['Account'] = 'Other Expenses'
        specs = specs.drop('Description', axis=1).set_index(self.index.names).fillna(0)
        specs = specs.astype('str').replace(' ', '0').astype('float')
        specs.columns = self._projrng
        
        return specs

    def _make_gens(self, gens):
        opex_subs = []
        for (var, freq), gf in gens.groupby(['Variable', 'Frequency']):
            gf['Account'] = 'Other Expenses'

            if freq in ['Q', 'A']:
                startstr = '2022-12' if freq == 'A' else '2022-03'
                start = pd.Period(startstr, freq='Q-DEC')
                opexrng = pd.period_range(start=start, end=self.projrng[-1], freq=freq)
            else:
                opexrng = self.projrng

            fctrs = gf.Factor.values

            if var == 'Salaries and Payroll Taxes':
                # BONUSES
                vars_ = self.istat.wages.utils.resample(freq, sgmts=True)
                varsmask = vars_.index.get_level_values('Segment').isin(gf.Segment)
                vars_ = vars_[varsmask].loc[pd.IndexSlice[:, var], :].values
            # Employees & New Hires
            elif var in ['Employee', 'New Hire']:
                if var == 'Employee':
                    vars_ = self.istat.wages._headcount.T.resample(freq).last().T.groupby('Segment').sum().iloc[:, 1:]
                elif var == 'New Hire':
                    vars_ = self.istat.wages._headcount.diff(axis=1).fillna(0).T.resample(self.projrng.freqstr).sum().T.groupby('Segment').sum().iloc[:, 1:]

                varsmask = vars_.index.get_level_values('Segment').isin(gf.Segment)
                vars_ = vars_[varsmask].values
            elif var in ['Revenue', 'Gross Profit']:
                # Revenue & Gross Profit
                vars_ = self.istat.rev.utils.resample(freq, accts=True)
                vars_ = vars_.loc[var].values

                fltmask = gf.Factor.apply(type) == float
                floats = gf.Factor[fltmask]
                floats = np.tile(floats, (4, 1)).T

                strs = gf.Factor[~fltmask]
                strs = (pd.DataFrame(strs.str.replace('%', '').str.replace(',', '').str.split(' ').tolist()).astype('float') / 100).values

                fctrs = np.zeros((gf.Factor.shape[0], strs.shape[1]))
                fctrs[fltmask] = floats
                fctrs[~fltmask] = strs

                reps = 4 if freq == 'Q' else 1
                fctrs = np.repeat(fctrs, reps).reshape(gf.Factor.shape[0], vars_.shape[0])

            fctrs = fctrs.reshape(-1,1) if vars_.ndim > 1 else fctrs
            values = np.multiply(vars_, fctrs.astype('float'))
            timemask = self.projrng.to_timestamp(self.projrng.freqstr).isin(opexrng.to_timestamp(opexrng.freqstr))
            timemask = np.tile(timemask, (gf.shape[0],1))
            inputs = np.zeros(timemask.size)
            inputs[timemask.flatten()] = values.flatten()
            inputs = inputs.reshape(timemask.shape)

            index = gf.set_index(self.index.names).index
            gframe = pd.DataFrame(inputs, index=index, columns=self.projrng)

            opex_subs.append(gframe)

        return pd.concat(opex_subs)
    
    @classmethod
    def from_schedule(cls, istat, opex:pd.DataFrame, projrng:pd.PeriodIndex=None):
        """
        Process
        --------
        Assign projection range
        Create the base dataframe
        
        The split the headcount into two main types of frames:
            1) single: roles where only one hire is required
            2) multi: roles where multiple hires are required
        
        Either type is handled separately
            1) multi: 
                + find first start for each role
                + distribute the new hires evenly during the unique role range
                + assign hire at each unique start date
            2) single:
                + self explanatory
                
        Benefits are added afterwards, some allocated based on each employees wage and some on headcount
        
        Parameters
        ------------
        headcount:       Dataframe of excel headcount
        """
        super().from_schedule(projrng=projrng)
        
        opexs = np.split(opex, opex[opex.isnull().all(1)].index)
        gen_opexs = [p for p in opexs if p.iloc[:, 5].isna().all()]
        spec_opexs = [p for p in opexs if ~p.iloc[:, 5].isna().all()]

        # Specific opex
        clean_specs = []
        for spec_opex in spec_opexs:
            if spec_opex.iloc[0].isna().all():
                spec_opex = spec_opex.iloc[1:]

            spec_opex.insert(0, column=-1, value=spec_opex.iloc[0,0])
            spec_opex.iloc[0,0] = 'Segment'
            spec_opex.iloc[0, 1] = 'Item'
            spec_opex = spec_opex.T.set_index(spec_opex.T.columns[0]).T
            clean_specs.append(spec_opex)

        specs = pd.concat(clean_specs)
        # General Opex
        clean_gens = []
        gen_opexs = gen_opexs if len(gen_opexs) == 5 else gen_opexs[:5 - len(gen_opexs)]
        for gen_opex in gen_opexs:
            if gen_opex.iloc[0].isna().all():
                gen_opex = gen_opex.iloc[1:]
            gen_opex.insert(0, column=-1, value=gen_opex.iloc[0,0])
            gen_opex.iloc[0,0] = 'Segment'
            gen_opex.iloc[0, 1] = 'Item'
            gen_opex = gen_opex.T.set_index(gen_opex.T.columns[0]).T.iloc[:, :6]
            clean_gens.append(gen_opex)

        gens = pd.concat(clean_gens)
        gens = gens.drop('Description', axis=1)
        
        return cls(istat, specs, gens)

class IStat(BaseIStat):
    """
    Instantiates *incomplete* income statement. Requires BSheet and CStat to complete
    """
    FULL_NAME = 'Income Statement'
    ACCOUNTS = ISTAT_ACCOUNTS
    ZERO_ROWS = ['Interest', 'Taxes']
    _projrng = pd.period_range(start='2022-01', end=pd.Period('2025-12', freq='Q'), freq='Q')
    _is_istat = True
    swapped_exp = False

    OPEX_RATS = ['sal_per_rev', 'oth_opex_per_rev', 'topex_per_rev', 'sal_v_topex', 'oth_v_topex']


    class Index(IndexMix):
        Account = ISTAT_ACCOUNTS.names
        Segment = []

    @set_assumps
    def __init__(self, revenue, wages, headcount, opex, capex, assumps=[], projrng=None):
        super().__init__(self, projrng=projrng)

        self._rev = RevStat.from_schedule(revenue)
        self._wages = WageStat.from_wages(wages, headcount, assumps=assumps)
        self._amort = AmortSched.from_schedule(capex, assumps=assumps)
        self._opex = OpexStat.from_schedule(self, opex)

        self._index = self.Index(self)
        self._base = self._make_base()
        self.update(refresh=True)
        
    @property
    def rev(self):
        return self._rev
    
    @property
    def wages(self):
        return self._wages
    
    @property
    def amort(self):
        return self._amort
    
    @property
    def opex(self):
        return self._opex
    
    @property
    def components(self):
        return [self.rev, self.wages, self.amort, self.opex]
    
    @property
    def exp_accts(self):
        return np.concatenate((self._wages.ACCOUNTS.names, self._opex.ACCOUNTS.names))
    
    def sgmt_categories(self):
        cats = []
        for c in self.components:
            sgmtidx = c.stat.index.get_level_values('Segment')
            if hasattr(sgmtidx, 'categories'):
                for cat in sgmtidx: 
                    if cat not in cats:
                        cats.append(cat)
            else:
                for cat in sgmtidx.unique():
                    if cat not in cats:
                        cats.append(cat)
                
        return cats
    
    def _make_base(self):
        base = pd.concat([c.resample(self.projrng.freqstr, sgmts=True) for c in self.components])
        base = base.loc[:, self.projrng]
        base.index = self._refresh_index(base)

        return base.reorder_levels([1,0]).sort_index()

    def _refresh_index(self, base):
        sgmts = pd.Categorical(base.index.get_level_values('Segment'), self.sgmt_categories(), ordered=True)
        accts = pd.Categorical(base.index.get_level_values('Account'), self.ACCOUNTS.names, ordered=True)
        index_as_frame = pd.DataFrame({'Segment': sgmts, 'Account': accts})
        
        return pd.MultiIndex.from_frame(index_as_frame)

    def update(self, metrics=['tr', 'tgp', 'ebit', 'ebt'], ops=[], refresh=False, hide=False):
        super().update(refresh=refresh)

        if 'opex_rats' in metrics:
            metrics.pop(metrics.index('opex_rats'))
            metrics += self.OPEX_RATS

        if refresh:
            if hasattr(self, '_bsheet'):
                for acct_name in self.ZERO_ROWS:
                    self._statement.loc[(acct_name, '---'), :] = self._bsheet._base.isutils \
                        .resample(self.projrng.freqstr).loc[acct_name, self._statement.columns].values[0]
            else:
                for acct_name in self.ZERO_ROWS:
                    if acct_name not in self._statement.index.get_level_values('Account'):
                        self._add_zero_row(acct_name, self._statement)
        
        for acct in self.ACCOUNTS.tabs:
            self._statement = acct.append(self._statement)

        for metric in metrics:
            metric_acct = self.ACCOUNTS.get(metric)
            self._statement = metric_acct.append(self._statement)            

        if ops:
            ops = [ops] if isinstance(ops, str) else ops
            for op in ops:
                self._statement = getattr(self, op)(self._statement)

        self._statement = self._statement.fillna(0).sort_index()

        if hide:
            show_mask = []
            for name in self.stat.index.get_level_values('Account'):
                acct = self.ACCOUNTS.get(name)
                if not hasattr(acct, 'show') or acct.show:
                    show_mask.append(True)
                else:
                    show_mask.append(False)
            self._statement = self._statement[show_mask]

        return self

    def backpass(self, bsheet):
        self._bsheet = bsheet
        self.update(refresh=True)

    # OPERATIONS
    def _merge_and_swap(self, stat:pd.DataFrame):
        stat = self._merge_benefits(stat)
        stat = self._swap_exp_levels(stat)

        return stat

    def _merge_benefits(self, stat:pd.DataFrame):
        wages = stat.loc[pd.IndexSlice[self._wages.ACCOUNTS.names, :]].groupby('Segment').sum()
        stat.loc[pd.IndexSlice[self._wages.ACCOUNTS.names[0], :], :] = wages.values
        stat = stat.drop(self._wages.ACCOUNTS.names[1], axis=0)
        
        return stat
    
    def _swap_exp_levels(self, stat):
        begidx = np.argwhere(self.ACCOUNTS.names == 'Gross Margin')[0,0]
        endidx = np.argwhere(self.ACCOUNTS.names == 'Total Operating Expenses')[0,0]

        swapidx = stat.index.swaplevel()

        swapped = swapidx.to_frame().loc[pd.IndexSlice[:, self.exp_accts], :].values

        stat_reset = stat.reset_index().set_index(stat.index.names, drop=False)

        new_sgmt_cats = np.concatenate((
            self._rev.index.levels['Segment'],
            self.exp_accts, 
            self._amort.stat.index.get_level_values('Segment').unique()
        ))
        new_acct_cats = np.concatenate((
            self.ACCOUNTS[:begidx].names, 
            self._wages.index.Segment,
            self.ACCOUNTS[endidx:].names
        ))
        stat_reset.loc[:, 'Account'] = pd.Categorical(stat_reset.Account, new_acct_cats, ordered=True)
        stat_reset.loc[:, 'Segment'] = pd.Categorical(stat_reset.Segment, new_sgmt_cats, ordered=True)
        
        stat_reset.loc[np.unique(swapped[:, 1]), stat.index.names] = swapped

        stat_reset = stat_reset.set_index(stat.index.names)
        stat_reset.columns = self.projrng

        return stat_reset.sort_index()

### BALANCE SHEET ###
class BSheet(BaseBSheet):
    FULL_NAME = 'Balance Sheet'
    ACCOUNTS = BSHEET_ACCOUNTS

    WOCASS = BSHEET_ACCOUNTS.accounts[[0,1,2,4]]
    WOCLIA = BSHEET_ACCOUNTS.accounts[[5,6]]
    WOCAP = WOCASS + WOCLIA
    NC_WOCAP = WOCASS[1:] + WOCLIA[:-1]

    TAX_RATE = .35
    INT_RATE = .05
    AR_COLLECTION = pd.tseries.frequencies.to_offset('3M')
    AP_COLLECTION = pd.tseries.frequencies.to_offset('2M')
    INVENTORY_LEAD = pd.tseries.frequencies.to_offset('2M')

    _projrng = pd.period_range(start='2022-01', end='2025-12', freq='M')

    class Index(IndexMix):
        Account = BSHEET_ACCOUNTS.names.tolist()
    
    @set_assumps
    def __init__(self, istat, capital, projrng=None, assumps=[], opening=None):
        super().__init__(projrng=projrng)
        self._projrng = self._set_projrng(projrng)
        
        self._index = self.Index(self)
        self._istat = istat
        self._capital = self._capital_from_sched(capital)
        self._isprox = self._set_istat_proxy(istat)
        self._base = self._make_base(opening)
        
        self.update(refresh=True, hide=False)

        self._istat.backpass(self)
 
    @property
    def _redge(self):
        return max(self.AR_COLLECTION.n, self.AP_COLLECTION.n, self.INVENTORY_LEAD.n)
    
    @property
    def _ledge(self):
        return self.INVENTORY_LEAD.n
    
    @property
    def projrng(self):
        return self._projrng
    
    @property
    def istat(self):
        return self._istat

    @property
    def capital(self):
        return self._capital

    def _set_projrng(self, projrng=None):
        projrng = projrng if projrng else self._projrng
        start = projrng[0].asfreq('M') - self._ledge
        end = projrng[-1] + self._redge
        
        return pd.period_range(start=start, end=end, freq='M')
    
    def _expand_rng(self, stat):
        new_stat = pd.DataFrame(0, index=stat.index, columns=self.projrng)
        new_stat.loc[stat.index, stat.columns] = stat.values
        new_stat = new_stat.fillna(0).sort_index()

        return new_stat
    
    def _set_istat_proxy(self, istat):
        isprox = istat.stat.isutils.resample(self.projrng.freqstr, accts=True).copy()
        isprox = self._expand_rng(isprox)
        self._extrap(isprox)
        # Must recalc amortization and EBITDA from original monthly ... not resampled
        isprox.loc['Amortization', :] = self.amortsched.values[:isprox.shape[1]]
        isprox.loc['EBIT', :] = isprox.loc['EBITDA'].values - isprox.loc['Amortization'].values
        
        return isprox

    def _extrap(self, isprox):
        accts = ['Total Revenue', 'COGS']
        
        xs = np.arange(0, self.projrng.size)
        for acct in accts:
            vals = isprox.loc[acct, :].values
            params, _, _, _, _, _ = expon_fit(vals)
            extrapd = expon(xs, *params)[-self._redge:]
            isprox.loc[acct, self.projrng[-self._redge:]] = extrapd

    def _capital_from_sched(self, capital):
        capital = capital.copy().fillna(0)
        capital.insert(1, 'Account', 'Stock Sale Proceeds')
        capital = capital.set_index(['Details', 'Account'])
        capital.columns = self.istat.projrng
        capital = capital.apply(pd.to_numeric, downcast='float')
        capital = capital.isutils.resample('M', aggfunc='first').fillna(0)

        return self._expand_rng(capital)

    def _append_opening(self, base, opening):
        opening.columns = self.projrng[:1]
        acctidx = pd.Categorical(opening.index, categories=base.index.get_level_values('Account').categories, ordered=True)
        opening.index = pd.MultiIndex.from_frame(pd.DataFrame({'Account': acctidx}))
        return base.append(opening)

    @property
    def capexsched(self):
        if not hasattr(self, '_capexsched'):
            self._capexsched = self._expand_rng(self.istat._amort.capex)
        
        return self._capexsched

    @property
    def amortsched(self):
        if not hasattr(self, '_amortsched'):
            self._amortsched = self._expand_rng(self.istat._amort.stat.sum().to_frame().T)
        
        return self._amortsched.sum()
    
    def _make_base(self, opening=None):
        #         """
        #         Transactions to be captured:
        #             + Sell product / generate revenue / ship inventory
        #             + collect AR
        #             + Purchase inventory in advance of sale; 1-month lead time
        #             + pay AP
        #             + Pay opex
        #             + make capital expenditures
        #             + amortize capex
        #             + pay interest
        #             + pay tax
        #             + retain earnings
        #             + raise capital (debt and equity)
        #         """
        base = self._make_frame(self.projrng)

        for acct in self.index.Account:
            base.loc[acct, :] = 0

        if opening is not None:
            for idx, value in opening.iterrows():
                if idx == 'Tax Carry-Forward':
                    base.loc[idx, :] = [value[0]] + [0]*(self.projrng.size - 1)
                else:
                    base.loc[idx, :] = [value[0]] * self.projrng.size

        # dr AR
        #   cr Rev
        # dr Cash
        #   cr AR 
        tr = self._isprox.loc['Total Revenue']
        invoiced = tr.cumsum() + base.loc['Accounts Receivable'].iloc[0]
        collected = invoiced.shift(self.AR_COLLECTION.n).fillna(0)
        base.loc['Accounts Receivable', :] = invoiced.values - collected.values

        # dr Inv
        #   cr AP
        # cr COGS
        #   dr Inv
        # dr AP
        #   cr cash
        # Inventory built IN ADVANCE of COGS / AP recorded same time, so must shift BACKWARDS in time
        cogs = self._isprox.loc['COGS', :]
        inv_up = cogs.cumsum().shift(-self.INVENTORY_LEAD.n).fillna(0)
        inv_down = cogs.cumsum()
        billed = inv_up
        paid = billed.shift(self.AP_COLLECTION.n).fillna(0) # shift one extra; booked on last day of month
        
        base.loc['Inventory', :] = inv_up.values -  inv_down.values
        base.loc['Accounts Payable', :] = billed.values - paid.values  + base.loc['Accounts Payable'].iloc[0].values

        # Capex and Amort EASY #
        capex = -self.capexsched.sum().values
        base.loc['Purchases of PPE', :] = capex
        base.loc['Capital Assets', :] = capex.cumsum() - self.amortsched.cumsum().values[:capex.size]

        # Capital Accounts #
        stock_sales = self.capital.groupby('Account').sum().loc['Stock Sale Proceeds', :].values
        base.loc['Stock Sale Proceeds', :] = stock_sales
        base.loc['Equity Capital', :] = stock_sales.cumsum() + base.loc['Equity Capital', :].iloc[0].values

        #### FIRST CHANGE TO CASH ####
        toe = self._isprox.loc['Total Operating Expenses', :].values
        base.loc['Shadow Cash', :] = collected.values - paid.values - capex.cumsum() + stock_sales.cumsum() - toe.cumsum() + base.loc['Shadow Cash', :].iloc[0].values

        # Interest Impact #
        interest = np.zeros(self.projrng.size)
        red_cash_mask = base.loc['Shadow Cash'].iloc[0] < 0
        interest[red_cash_mask] = -base.loc['Shadow Cash'].values[0][red_cash_mask] * self.INT_RATE
        base.loc['Interest', :] = interest
        
        ebt = self._isprox.loc['EBIT', :].values - interest
        self._isprox.loc['EBT', :] = ebt

        ### TAXES ###
        # First, find taxes and find when accumulated taxes are positive and negative
        tax = ebt*self.TAX_RATE   
        cumtax = tax.cumsum() - base.loc['Tax Carry-Forward', self.projrng[0]].values[0] # cumulative tax must incorporate tax carryforwards
        red_tax_mask = cumtax < 0
        black_tax_mask = cumtax >= 0
        
        # Second, assign taxes and cumulative taxes to carry-forward; 
        # carry-forward is 0 when cumtax >= 0
        base.loc['Tax Carry-Forward', base.columns[red_tax_mask]] = -cumtax[red_tax_mask]
        base.loc['Taxes', :] = tax
        
        # Second, determine cash portion of txes
        # When cumulative taxes > 0, cash taxes == taxes
        cashtax = np.zeros(self.projrng.size)
        cashtax[black_tax_mask] = tax[black_tax_mask]

        # There are some periods where carry-fwd > 0, but cash taxes are still paid
        # this occurs when cash taxes_t > carry-fwd_t-1
        # So must find periods when carry-fwd_t-1 > 0 AND cash taxes_t > carry-fwd_t-1
        black_fwd_mask = base.loc['Tax Carry-Forward'].iloc[0].shift(1).fillna(0) > 0
        tax_gt_fwd_mask = base.loc['Taxes'].iloc[0].fillna(0) - base.loc['Tax Carry-Forward'].iloc[0].shift(1).fillna(0) > 0
        partial_cash_tax_mask = black_fwd_mask & tax_gt_fwd_mask

        # Find cashtaxes for these instances and assign
        partial_fwd = base.loc['Tax Carry-Forward'].iloc[0].shift(1).fillna(0)[partial_cash_tax_mask]
        partial_tax = base.loc['Taxes'].iloc[0][partial_cash_tax_mask]
        cashtax[partial_cash_tax_mask] = partial_tax - partial_fwd
        base.loc['Cash Taxes', :] = cashtax
        base.loc['Non-Cash Taxes', :] = tax - cashtax
        
        ni = ebt - tax
        base.loc['Net Income', :] = ni
        base.loc['Retained Earnings', :] = ni.cumsum() + base.loc['Retained Earnings'].iloc[0].values

        base.loc['Shadow Cash'] -=  interest.cumsum() + cashtax.cumsum() 

        base.loc['Cash', :] = base.loc['Shadow Cash', :].where(base.loc['Shadow Cash', :] >= 0, 0).values
        base.loc['Indebtedness', :] = -base.loc['Shadow Cash', :].where(base.loc['Shadow Cash', :] <= 0, 0).values

        return base

    def update(self, metrics=[], ops=[], refresh=False, hide=True):
        super().update(refresh=refresh)

        for acct in self.ACCOUNTS.tabs:
            self._statement = acct.append(self._statement)

        metrics += ['wocap', 'cap', 'd2cap', 'crat']
        for metric in metrics:
            metric_acct = self.ACCOUNTS.get(metric)

            if metric_acct is None:
                raise TypeError(f'{metric} is not a valid Account name. Did you include it in list?')

            self._statement = metric_acct.append(self._statement)            

        if ops:
            ops = [ops] if isinstance(ops, str) else ops
            for op in ops:
                self._statement = getattr(self, op)(self._statement)

        self._statement = self._statement.fillna(0).sort_index()
        
        if hide:
            show_mask = np.array([self.ACCOUNTS.get(acct).show for acct in self.stat.index.get_level_values('Account')])
            self._statement = self._statement[show_mask]
        
        return self

class EQStat(BaseBSheet):
    FULL_NAME = 'Statement of Changes in Equity'
    ACCOUNTS = EQ_ACCOUNTS

    first = {'first': ['Retained Earnings - Start', 'Equity Capital - Start']}
    last = {'last': [
        'Retained Earnings', 'Equity Capital', 
        "Shareholders' Equity"
    ]}
    sums = {'sum': ['Net Income', 'Stock Sale Proceeds', ]}
    aggfuncs = [first, last, sums] 

    class Index(IndexMix):
        Account = EQ_ACCOUNTS.names.tolist()

    def __init__(self, bsheet):
        super().__init__()
        self._projrng = bsheet._projrng
        
        self._index = self.Index(self)
        self._bsheet = bsheet
        self._base = self._make_base()
        self.update(refresh=True)

    def _make_base(self):
        idx_from_bsheet = self._bsheet.stat.index.get_level_values('Account').intersection(self.index.levels['Account'])
        base = self._bsheet.stat.loc[idx_from_bsheet]
        base = self._refresh_index(base, idx_from_bsheet)
        
        return base
        
    def _refresh_index(self, base, idx_from_bsheet):
        acctidx = pd.Categorical(idx_from_bsheet, categories=self.index.levels['Account'], ordered=True)
        index_as_frame = pd.DataFrame({'Account': acctidx})
        base.index = pd.MultiIndex.from_frame(index_as_frame)
        
        return base

    def update(self, metrics=[], ops=[], refresh=False, hide=True):
        super().update(refresh=refresh)

        for acct_name in self.ZERO_ROWS:
            if acct_name not in self._statement.index.get_level_values('Account'):
                self._add_zero_row(acct_name, self._statement)

        for acct in self.ACCOUNTS.tabs:
            self._statement = acct.append(self._statement)

        self._statement = self._statement.fillna(0).sort_index()

        return self

class CFlow(EQStat):
    FULL_NAME = 'Cash Flow Statement'
    ACCOUNTS = CFLOW_ACCOUNTS
    ZERO_ROWS = ['Proceeds from Sale', 'Proceeds of LTD', 'Repayment of LTD', 'Dividends Paid']

    class Index(IndexMix):
        Account = CFLOW_ACCOUNTS.names.tolist()

    @property
    def aggfuncs(self):
        first = {'first': ['Cash - Start']}
        last = {'last': [
            'Cash - End'
        ]}
        sums = {'sum': self.stat.index.get_level_values('Account').difference(['Cash - Start', 'Cash - End'])}
        return [first, last, sums] 

    def _make_base(self):
        idx_from_bsheet = self._bsheet.stat.index.get_level_values('Account').intersection(self.index.levels['Account'])
        idx_from_isprox = self._bsheet._isprox.index.get_level_values('Account').intersection(self.index.levels['Account'])
        idx_from_isprox = idx_from_isprox.difference(idx_from_bsheet)
        idx_already = idx_from_bsheet.append(idx_from_isprox)
        base = self._bsheet.stat.loc[idx_from_bsheet]
        base = base.append(self._bsheet._isprox.loc[idx_from_isprox])
        base = self._refresh_index(base, idx_already)
        base.loc['Purchases of PPE', :] *= -1
        
        base.loc['Cash - End', :] = 0

        return base

    def update(self, metrics=[], ops=[], refresh=False, hide=True):
        if refresh:
            self._statement = self._base.copy()

        for acct_name in self.ZERO_ROWS:
            if acct_name not in self._statement.index.get_level_values('Account'):
                self._add_zero_row(acct_name, self._statement)

        for acct in self.ACCOUNTS.tabs:
            self._statement = acct.append(self._statement)

        acct = self.ACCOUNTS.get('Cash - Start')
        self._statement = self._statement.drop('Cash - Start', level='Account')
        self._statement = acct.append(self._statement)

        self._statement = self._statement.fillna(0).sort_index()

        if hide:
            show_mask = np.array([self.ACCOUNTS.get(acct).show for acct in self.stat.index.get_level_values('Account')])
            self._statement = self._statement[show_mask]
        
        return self

### MAIN INTERFACE ###
class FinStat(BaseStat):
    INT_RATE = .04 / 12
    TAX_RATE = .35
    STAT_NAMES = ['IStat', 'BSheet', 'EQStat', 'CFlow']

    @set_assumps
    def __init__(self, 
        revenue, wages, headcount, opex, capex, capital,
        assumps=[],
        opening=None,
        make_plots=False,
        plot_root=''
        ):

        print ('Generating Income Statement', end='\r')
        self._istat = IStat(revenue, wages, headcount, opex, capex, assumps=assumps)
        print ('Generating Balance Sheet      ', end='\r')                
        self._bsheet = BSheet(self._istat, capital, assumps=assumps, opening=opening)
        print ('Generating Equity Statement', end='\r')        
        self._eqstat = EQStat(self._bsheet)
        print ('Generating Cash Flow Statement')
        self._cflow = CFlow(self._bsheet)
        print ('Done.                        ')
        
        if make_plots:
            self._plots = Plots(self, root=plot_root)
            self._plots.make_all()

    @property
    def _supporting(self):        
        return [
            self.istat.rev, self.istat.wages, self.istat.amort
        ]

    def supporting(self, as_dict=False):
        if as_dict:
            return {stat.FULL_NAME: stat for stat in self._supporting}
        else:
            return self._supporting
    
    @property
    def istat(self):
        return self._istat

    @property
    def bsheet(self):
        return self._bsheet
        
    @property
    def eqstat(self):
        return self._eqstat
    
    @property
    def cflow(self):
        return self._cflow

    @property
    def _stats(self):
        return [self._istat, self._bsheet, self._eqstat, self._cflow]
    
    def stats(self, as_dict=False):
        if as_dict:
            return {k: v for k, v in zip(self.STAT_NAMES, self._stats)}
        else:
            return  self._stats
    
    @property
    def annuals(self):
        return {name: stat.annually() for name, stat in self.stats(as_dict=True).items()}

    @property
    def quarterlies(self):
        return {name: stat.quarterly() for name, stat in self.stats(as_dict=True).items()}

    @property
    def assumptions(self):
        return pd.DataFrame.from_dict(
            {
                'Income Statement': ['', ''],
                'Interest Rate': [self.INT_RATE * 12, 'Annual'],
                'Income Tax Rate': [self.TAX_RATE, 'Annual'],
                'Balance Sheet': ['', ''],
                'AR Terms': [self.bsheet.AR_COLLECTION.n, 'Months'],
                'AP Terms': [self.bsheet.AP_COLLECTION.n, 'Months'],
                'Inventory Lead Time': [self.bsheet.INVENTORY_LEAD.n, 'Months'],
                'Amortization Schedule': [AmortSched.AMORT_YEARS, 'Years'],
                'Headcount Items': ['', ''],
                'Payroll Taxes': [WageStat.PAYROLL_TAXES, 'Annual'],
                'Wage Inflation': [WageStat.WAGE_INFLATION, 'Annual'],
                'Benefits': [WageStat.ANNUAL_BENEFITS, 'per person'],
                'Payroll Fees': [WageStat.ANNUAL_PAYROLL_FEES, 'per person'],
                'Unemployment Fees': [WageStat.ANNUAL_UNEMPLOYMENT, 'per person'],
                "Workers' Compensation": [WageStat.ANNUAL_WORKERS_COMP, 'Annual (per salaries)'],
                "401K Contributions": [WageStat.ANNUAL_401K, 'Annual (per salaries)']
            }, orient='index', columns=['Factor', 'Units / Period']
        )

    @property
    def plots(self):
        return self._plots
