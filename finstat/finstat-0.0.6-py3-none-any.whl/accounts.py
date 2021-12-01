import numpy as np
import pandas as pd

def slicer(vals, nlevels, acctpos, expand_with=''):
    expand_with = expand_with if expand_with else slice(None, None, None)
    
    slicearr = np.repeat(None, nlevels)
    slicearr[acctpos] = [vals] if isinstance(vals, str) else vals
    
    if nlevels > 1:
        slicearr[np.arange(nlevels) != acctpos] = expand_with
    
    return tuple(slicearr)

### ACCOUNT OBJECTS and MAIN LIST ###
class Account:
    ALLOWED_TYPES = ['Account', 'Prior', 'Equal', 'Sum', 'Sub', 'Metric']
    CORE = ALLOWED_TYPES[:-1]
    TABS = ALLOWED_TYPES[1:-1]

    def __init__(self, 
        name:str, 
        statclass:str='',  
        type_:str='Account',
        feeders=None, 
        has_levels=True,
        hide=False,
        short:str=''
    ):
        if type_ not in self.ALLOWED_TYPES:
            raise ValueError(f'`type_` not supported. Require one of {self.ALLOWED_TYPES}')
        
        self.name = name
        self.statclass = statclass
        self.type = type_
        self.feeders = feeders
        self.has_levels = has_levels if self.statclass != 'BSheet' else False
        self.hide = hide
        self._short = short

    def __repr__(self):
        return f'Account: {self.name} {self.statclass} {self.type} {self.feeders}'

    @property
    def short(self):
        if self._short:
            return self._short
        if len(self.name.split(' ')) > 1:
            return ''.join(s[0].lower() for s in self.name.split(' '))
        else:
            return self.name.lower()

    @property
    def show(self):
        return not self.hide

    @property
    def is_sum(self):
        return self.type == 'Sum'

    @property
    def is_sub(self):
        return self.type == 'Sub'

    @property
    def is_divide(self):
        return self.type == 'Divide'

    @property
    def is_metric(self):
        return self.type == 'Metric'

    @property
    def is_prior(self):
        return self.type == 'Prior'

    @property
    def is_equal(self):
        return self.type == 'Equal'

    # Append Func and Calc Funcs #
    def append(self, stat):
        if self.name in stat.index.get_level_values('Account'):
            stat = stat.drop(self.name, level='Account')

        metric = self.calc(stat)
        if not self.has_levels:
            metric = metric if metric.ndim > 1 else metric.reshape(1,-1)
            newindex = stat.index.to_frame().iloc[:1, :]
            newindex.Segment = '---'
        else:
            acct_slice = slicer(self.feeders[0], stat.index.nlevels, self._acctpos(stat))
            newindex = stat.loc[acct_slice].index.to_frame()

        newindex.Account = self.name
        newindex = pd.MultiIndex.from_frame(newindex.reset_index(drop=True))
        newframe = pd.DataFrame(metric, index=newindex, columns=stat.columns)
        
        stat = stat.append(newframe)

        return stat

    def calc(self, *args, **kwargs):
        if self.is_sum:
            res = self.sum(*args, **kwargs)
        elif self.is_sub:
            res = self.subtract(*args, **kwargs)
        elif self.is_prior:
            res = self.calc_prior(*args, **kwargs)
        elif self.is_equal:
            res = self.equal(*args, **kwargs)
        else:
            res = None

        return res
    
    def _acctpos(self, stat):
        return stat.index.names.index('Account')

    def sum(self, stat):
        add_slice = slicer(self.feeders, stat.index.nlevels, self._acctpos(stat))
        add_ = stat.loc[add_slice]
        
        if not self.has_levels:
            loop = stat.index.nlevels if stat.index.nlevels > 1 else 2
            for i in range(loop - 1):
                add_ = add_.sum()

        return add_.values

    def subtract(self, stat):
        add_slice = slicer(self.feeders[0], stat.index.nlevels, self._acctpos(stat))
        sub_slice = slicer(self.feeders[1:], stat.index.nlevels, self._acctpos(stat))
        
        add_ = stat.loc[add_slice]
        sub_ = stat.loc[sub_slice]

        if not self.has_levels:
            loop = stat.index.nlevels if stat.index.nlevels > 1 else 2
            for i in range(stat.index.nlevels - 1):
                add_ = add_.sum()
                sub_ = sub_.sum()

        return add_.values - sub_.values

    def divide(self, stat):
        num_slice = slicer(self.feeders[0], stat.index.nlevels, self._acctpos(stat))
        denom_slice = slicer(self.feeders[1], stat.index.nlevels, self._acctpos(stat))
        
        num = stat.loc[num_slice]
        denom = stat.loc[denom_slice]

        if not self.has_levels:
            loop = stat.index.nlevels if stat.index.nlevels > 1 else 2
            for i in range(stat.index.nlevels - 1):
                num = num.sum()
                denom = denom.sum()

        return np.divide(num.values, denom.values)

    def calc_prior(self, stat):
        return stat.loc[self.feeders[0], :].shift(1, axis=1).fillna(0).values

    def equal(self, stat):
        return stat.loc[self.feeders[0], :].fillna(0).values

### ACCOUNT CHILDS ###

class Metric(Account):
    def __init__(self, *args, **kwargs):
        self.type = 'Metric'
        super().__init__(*args, **kwargs)

class TotalRevenue(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'Total Revenue', 
            *args, 
            feeders=['Revenue'], 
            has_levels=False, 
            hide=True,
            **kwargs
        )

    def calc(self, stat):
        return self.sum(stat)

class TotalGrossProfit(Account):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'Total Gross Profit', 
            feeders=['Gross Profit'], 
            has_levels=False,
            hide=True,
            *args, 
            **kwargs
        )

    def calc(self, stat):
        return self.sum(stat)

class GrossMargin(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__('Gross Margin', *args, **kwargs)

    def calc(self):
        pass

class EBIT(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'EBIT', 
            *args,
            feeders=['EBITDA', 'Amortization'],
            has_levels=False,
            hide=True,
            **kwargs,
        )

    def calc(self, stat):
        return self.subtract(stat)

class EBT(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'EBT', 
            *args, 
            feeders=['EBIT', 'Interest'],
            has_levels=False,
            hide=True,
            **kwargs
        )

    def calc(self, stat):
        return self.subtract(stat)

class StockSaleProceeds(Account):
    FULL_NAME = 'Stock Sale Proceeds'

    def __init__(self, *args, **kwargs):
        super().__init__(self.FULL_NAME, *args, **kwargs)

class DeltaWoCap(Metric):
    FULL_NAME = 'Change in Non-Cash Working Capital'

    def __init__(self, *args, **kwargs):
        super().__init__(self.FULL_NAME, short='wocap', *args, **kwargs)

    def calc(self, stat):
        from .finstat import BSheet

        delta_wocass = stat.loc[BSheet.WOCASS[1:].names.tolist()].sum().diff().fillna(0).values
        delta_woclia = stat.loc[BSheet.WOCLIA[1:].names.tolist()].sum().diff().fillna(0).values
        
        return delta_woclia - delta_wocass

class PurchasePPE(Account):
    FULL_NAME = 'Purchases of PPE'

    def __init__(self, *args, **kwargs):
        super().__init__(self.FULL_NAME, short='ppe', *args, **kwargs)

class Ratio(Metric):
    def __init__(self, *args, **kwargs):
        super().__init__(
            self.FULL_NAME, 
            *args, 
            has_levels=False,
            hide=True,
            **kwargs
        )
    
    def calc(self, stat):
        return self.divide(stat)    

class WagesPerRev(Ratio):
    FULL_NAME = 'Salaries per Rev'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            short='sal_per_rev',
            feeders=['Salaries and Payroll Taxes', 'Total Revenue'],
            **kwargs)

class OthOpexPerRev(Ratio):
    FULL_NAME = 'Other Opex per Rev'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            short='oth_opex_per_rev',
            feeders=['Other Expenses', 'Total Revenue'],
            **kwargs)

class TOpexPerRev(Ratio):
    FULL_NAME = 'Total Opex per Rev'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            short='topex_per_rev',
            feeders=['Total Operating Expenses', 'Total Revenue'],
            **kwargs
        )

class WagesPerTOpex(Ratio):
    FULL_NAME = 'Salary-Opex Mix'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            short='sal_v_topex',
            feeders=['Salaries and Payroll Taxes', 'Total Operating Expenses'],
            **kwargs)

class OthOpexPerTOpex(Ratio):
    FULL_NAME = 'Other-Opex Mix'

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            short='oth_v_topex',
            feeders=['Other Expenses', 'Total Operating Expenses'],
            **kwargs)

### ACCOUNT CONTAINERS ###
class Accounts(np.ndarray, Account):
    def __new__(cls, accounts:list):
        obj = np.asarray(accounts).view(cls)
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return

    def __init__(self, accounts:list):
        for acct in accounts:
            setattr(self, acct.name, acct)

    def __repr__(self):
        return f'Accounts Type: {self}'

    def __add__(self, accounts):
        return Accounts([acct for acct in self] + [acct for acct in accounts])

    def get(self, acct_name):
        if acct_name in self.__dict__:
            return self.__dict__[acct_name]
        elif acct_name in self.shortkey:
            return self.__dict__[self.shortkey[acct_name]]

    def get_from_list(self, acct_names):
        return Accounts([self.get(acct_name) for acct_name in acct_names])

    # Properties that return another Accounts instance
    @property
    def accounts(self):
        return Accounts([item for item in self if item.type == 'Account'])

    @property
    def core(self):
        return Accounts([item for item in self if item.type in self.CORE])

    @property
    def tabs(self):
        return Accounts([acct for acct in self if acct.type in self.TABS])

    @property
    def metrics(self):
        return Accounts([item for item in self if item.type == 'Metric'])

    # Properties that return list
    @property
    def names(self):
        return np.array([item.name for item in self])

    # Properties that return list
    @property
    def shorts(self):
        return np.array([item.short for item in self])

    @property
    def shortkey(self):
        return {k:v for k,v in zip(self.shorts, self.names)}

    def by_stat(self, statclass):
        return Accounts([item for item in self if item.statclass in statclass])

class BSheetAccounts(Accounts):
    def __new__(cls, accounts:list):
        for acct in accounts:
            acct.statclass = 'BSheet'
            acct.has_levels = False

        obj = np.asarray(accounts).view(cls)

        return obj

class EQStatAccounts(Accounts):
    def __new__(cls, accounts:list):
        for acct in accounts:
            acct.statclass = 'EQStat'
            acct.has_levels = False

        obj = np.asarray(accounts).view(cls)

        return obj

class CFlowAccounts(Accounts):
    def __new__(cls, accounts:list):
        for acct in accounts:
            acct.statclass = 'CFlow'
            acct.has_levels = False

        obj = np.asarray(accounts).view(cls)

        return obj

class Capital(Metric):
    FULL_NAME = 'Capital'

    def __init__(self, *args, **kwargs):
        super().__init__(
            self.FULL_NAME,
            feeders=['Indebtedness', "Shareholders' Equity"],
            has_levels=False, 
            short='cap',
            hide=True,
            *args,
            **kwargs
        )

    def calc(self, stat):
        return self.sum(stat)    

class Debt2Cap(Metric):
    FULL_NAME = 'Debt-to-Capital'
    def __init__(self, *args, **kwargs):
        super().__init__(
            self.FULL_NAME,
            *args, 
            feeders=['Indebtedness', 'Capital'], 
            has_levels=False, 
            short='d2cap',
            hide=True,
            **kwargs
        )

    def calc(self, stat):
        return self.divide(stat)

class CurrentRatio(Metric):
    FULL_NAME = 'Current Ratio'
    def __init__(self, *args, **kwargs):
        super().__init__( 
            self.FULL_NAME,
            *args, 
            feeders=['Current Assets', 'Current Liabilities'], 
            has_levels=False, 
            short='crat',
            hide=True,
            **kwargs
        )

    def calc(self, stat):
        return self.divide(stat)



ISTAT_ACCOUNTS = Accounts([
    Account('Revenue', 'RevStat'),
    TotalRevenue('RevStat'), 
    Account('COGS', 'RevStat'), 
    Account('Gross Profit', 'RevStat', type_='Sub', feeders=['Revenue', 'COGS']), 
    TotalGrossProfit('IStat'), 
    Account('Gross Margin', 'RevStat', type_='Metric'),
    Account('Salaries and Payroll Taxes', 'WageStat'),
    Account('Benefits', 'WageStat'),
    Account('Other Expenses', 'OpexStat'),
    Account('Total Operating Expenses', 'IStat', type_='Sum', feeders=['Salaries and Payroll Taxes', 'Benefits', 'Other Expenses'], has_levels=False),
    Account('EBITDA', 'IStat', type_='Sub', feeders=['Gross Profit', 'Total Operating Expenses'], has_levels=False),
    Account('Amortization', 'AmortSched'),
    EBIT('IStat'),
    Account('Interest', 'IStat'),
    EBT('IStat'),
    Account('Taxes', 'IStat'),
    Account('Net Income', 'IStat', type_='Sub', feeders=['EBITDA', 'Amortization', 'Interest', 'Taxes'], has_levels=False),
    # WagesPerRev('IStat'),
    # OthOpexPerRev('IStat'),
    # TOpexPerRev('IStat'),
    # WagesPerTOpex('IStat'),
    # OthOpexPerTOpex('IStat'),
])

BSHEET_ACCOUNTS = BSheetAccounts([
    Account('Cash'),
    Account('Accounts Receivable'),
    Account('Inventory', short='inv'),
    Account('Current Assets', type_='Sum', feeders=['Cash', 'Accounts Receivable', 'Inventory']),
    Account('Capital Assets', short='capass'),
    Account('Tax Carry-Forward', short='taxfwd'),
    Account('Total Assets', type_='Sum', feeders=['Current Assets', 'Capital Assets', 'Tax Carry-Forward']),
    Account('Indebtedness', short='indebt'),
    Account('Accounts Payable'),
    Account('Current Liabilities', type_='Sum', feeders=['Indebtedness', 'Accounts Payable']),
    Account('Long-Term Debt', short='ltd', hide=True),
    Account('Total Liabilities', type_='Sum', feeders=['Current Liabilities', 'Long-Term Debt']),
    Account('Retained Earnings'),
    Account('Equity Capital'),
    Account("Shareholders' Equity", type_='Sum', feeders=['Retained Earnings', 'Equity Capital']),
    Account('Liabilities and Equity', type_='Sum', feeders=['Total Liabilities', "Shareholders' Equity"]),
    Account('bal',  'BSheet', type_='Sub', feeders=['Total Assets', 'Liabilities and Equity']),
    Account('Shadow Cash', hide=True),
    Account('Interest', hide=True),
    Account('Taxes', hide=True),
    Account('Cash Taxes', hide=True),
    Account('Non-Cash Taxes', hide=True),
    Account('Net Income', hide=True),
    DeltaWoCap(hide=True),
    PurchasePPE(hide=True),
    StockSaleProceeds(hide=True),
    CurrentRatio(),
    Capital(),
    Debt2Cap(),
])

EQ_ACCOUNTS = EQStatAccounts([
    Account('Retained Earnings - Start', type_='Prior', feeders=['Retained Earnings']),
    Account('Net Income'),
    Account('Dividends Paid'),
    Account('Retained Earnings', type_='Sum', feeders=['Net Income', 'Dividends Paid', 'Retained Earnings - Start']),
    Account('Equity Capital - Start', type_='Prior', feeders=['Equity Capital']),
    StockSaleProceeds(),
    Account('Equity Capital', type_='Sum', feeders=['Stock Sale Proceeds', 'Equity Capital - Start' ]),
    Account("Shareholders' Equity", type_='Sum', feeders=['Retained Earnings', 'Equity Capital']),
])

CFLOW_ACCOUNTS = CFlowAccounts([
    Account('Cash - Start', type_='Prior', feeders=['Cash - End']),
    Account('Net Income'),
    Account('Amortization'),
    DeltaWoCap(),
    Account('Cash from Operations', type_='Sum', feeders=['Net Income', 'Amortization', DeltaWoCap.FULL_NAME]),
    PurchasePPE(),
    Account('Proceeds from Sale'),
    Account('Cash from Investing', type_='Sum', feeders=[PurchasePPE.FULL_NAME, 'Proceeds from Sale']),
    Account('Proceeds of LTD'),
    Account('Repayment of LTD'),
    Account('Dividends Paid'),
    StockSaleProceeds(),
    Account('Cash from Financing', type_='Sum', feeders=['Proceeds of LTD', 'Repayment of LTD', StockSaleProceeds.FULL_NAME]),
    Account('Change in Cash', type_='Sum', feeders=['Cash from Operations', 'Cash from Investing', 'Cash from Financing']),
    Account('Shadow Cash', hide=True),
    Account('Cash - End', type_='Equal', feeders=['Shadow Cash']),  
])
