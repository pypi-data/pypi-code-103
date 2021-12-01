import numpy as np
import functools as ft

from numpy.lib.utils import deprecate_with_doc

def testit(func):
    @ft.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            left, right = func(self, *args, **kwargs)
            assertion = np.isclose(left, right, atol=1e-3) 
            assert assertion.all()
            self._results[func.__name__] = True
        except AssertionError as e:
            self._results[func.__name__] = False
            self._fails.append(FailContainer(func.__name__, assertion, left, right))
        except Exception as e:
            print (func.__name__)
            raise e

    return wrapper

class BaseTests:
    def __init__(self):
        self._results = {}
        self._fails = []

    @property
    def results(self):
        return self._results
    
    @property
    def fails(self):
        return self._fails
    
    # MAIN TESTING METHODS #
    @property
    def tests(self):
        return [f for f in self.__dir__() if 'test_' in f]
    
    def run(self):
        resprint = ''
        for i in range(len(self.tests)):
            test = self.tests[i]
            testfunc = getattr(self, test)
            testfunc()
            
            if self.results[testfunc.__name__]:
                resprint += '.'
            else:
                resprint += 'F'

            if i == len(self.tests) - 1:
                print (resprint)
            else:
                print (resprint, end='\r')
        
        n_failed = len(self.results) - np.array(list(self.results.values())).sum()
        n_passed = len(self.results) - n_failed

        print (f'Passed: {n_passed}  Failed: {n_failed}')

        if not all(self.results.values()):
            print ('Follwing tests were failed: ' + ' '.join([f.__repr__() for f in self.fails]))

class FailContainer:
    def __init__(self, func_name, boolarr, left, right):
        self.func_name = func_name
        self.boolarr = boolarr
        self.left = left
        self.right = right
        self.diff = left - right
        self.results = [func_name, boolarr, left, right]
    
    def __repr__(self):
        return self.func_name

class IStatTests(BaseTests):
    name = 'IStatTests'
    def __init__(self, istat):
        self.istat = istat
        super().__init__()
    
    # Test EBIT #
    @property
    def ebitda(self):
        return self.istat.stat.loc[('EBITDA', '---'), :].values 

    @property
    def amort(self):
        return self.istat.stat.loc['Amortization', :].sum().values 

    @property
    def ebit(self):
        return self.istat.stat.loc[('EBIT', '---'), :].values 

    @testit
    def test_ebit(self):
        return self.ebitda - self.amort, self.ebit

    @property
    def ebt(self):
        return self.istat.stat.loc[('EBT', '---'), :].values

    @property
    def interest(self):
        return self.istat.stat.loc[('Interest', '---'), :].values

    @testit
    def test_ebt(self):
        return self.ebit - self.interest, self.ebt

    @property
    def taxes(self):
        return self.istat.stat.loc[('Taxes', '---'), :].values

    @property
    def net_income(self):
        return self.istat.stat.loc[('Net Income', '---'), :].values

    @testit
    def test_ni(self):
        return self.ebt - self.taxes, self.net_income

class BSheetTests(BaseTests):
    name = 'BSheetTests'
    def __init__(self, bsheet):
        self.bsheet = bsheet
        
        super().__init__()
    
    def roller(self, arr, rolls:int):
        arrs = np.tile(arr, (rolls, 1))

        for i in np.arange(arrs.shape[0]):
            if i > 0:
                arrs[i] = np.roll(arrs[i], i)
                arrs[i, :i] = 0

        return arrs
    
    # TEST FOR AR #
    @property
    def ar_new(self):
        return self.bsheet._isprox.loc['Total Revenue'].values
    
    @property
    def ar(self):
        return self.bsheet.stat.loc['Accounts Receivable', :].values
    
    @property
    def ar_n(self):
        return self.bsheet.AR_COLLECTION.n
    
    @testit
    def test_ar(self):
        ars = self.roller(self.ar_new, self.ar_n)
        return ars.sum(axis=0), self.ar

    # TEST FOR INV #
    @property
    def inv_n(self):
        return self.bsheet.INVENTORY_LEAD.n
    
    @property
    def cogs_for_inv(self):
        return self.bsheet._isprox.loc['COGS'].shift(-self.inv_n).fillna(0)
    
    @property
    def inv(self):
        return self.bsheet.stat.loc['Inventory', :].values[0]
    
    @testit
    def test_inv(self):
        invs = self.roller(self.cogs_for_inv, self.inv_n)
        return invs.sum(axis=0)[:-2], self.inv[:-2]
    
    # Test for AP #
    @property
    def ap_n(self):
        return self.bsheet.AP_COLLECTION.n

    @property
    def ap(self):
        return self.bsheet.stat.loc['Accounts Payable', :].values[0]
    
    @testit
    def test_ap(self):
        aps = self.roller(self.cogs_for_inv, self.ap_n)
        return aps.sum(axis=0)[:-2], self.ap[:-2]

    # Test Cash #
    @property
    def shadow_cash(self):
        return self.bsheet.stat.loc['Shadow Cash', :].values[0]

    @property
    def cash(self):
        return self.bsheet.stat.loc['Cash', :].values[0]

    @property
    def indebt(self):
        return self.bsheet.stat.loc['Indebtedness', :].values[0]

    @testit
    def test_cash(self):
        cash_diff = self.shadow_cash - self.cash + self.indebt
        return cash_diff, np.zeros(cash_diff.shape[0])

    # Test Current Assets #
    @property
    def ca_from_wocass(self):
        return self.bsheet.stat.loc[self.bsheet.WOCASS[:-1].names].sum().values
    
    @property
    def ca(self):
        return self.bsheet.stat.loc['Current Assets'].values[0]

    @testit
    def test_ca(self):
        return self.ca_from_wocass, self.ca

    # Test Current Liabilities #
    @property
    def cl_from_woclia(self):
        return self.bsheet.stat.loc[self.bsheet.WOCLIA.names].sum().values

    @property
    def cl(self):
        return self.bsheet.stat.loc['Current Liabilities'].values[0]

    @testit
    def test_ca(self):
        return self.cl_from_woclia, self.cl

    # Test Balance #
    @property
    def bal(self):
        return self.bsheet.stat.loc['bal', :].values[0]
    
    @testit
    def test_bal(self):
        return np.round(self.bal[:-2], -2), np.zeros(self.bsheet.stat.columns[:-2].size)

    # Test Taxes #
    @property
    def ebt(self):
        return self.bsheet._isprox.loc['EBT']
        
    @testit
    def test_taxes(self):
        return self.ebt.values*self.bsheet.TAX_RATE, self.bsheet.stat.loc['Taxes'].values

    # Test TaxFwd #
    @property
    def cumtax(self):
        return self.bsheet.stat.loc['Taxes'].cumsum(axis=1).values[0]

    @property
    def taxfwd(self):
        return self.bsheet.stat.loc['Tax Carry-Forward'].values[0]

    @testit
    def test_taxfwd(self):
        black_tax_mask = self.cumtax > 0
        return self.taxfwd[black_tax_mask], 0

    # Test Amortization and Capital Assets #
    @property
    def capass(self):
        return self.bsheet.stat.loc['Capital Assets'].values[0]

    @property
    def ppe(self):
        return self.bsheet.stat.loc['Purchases of PPE'].values[0]

    @property
    def amort(self):
        return self.bsheet.istat._amort.stat.sum(axis=0).values

    @testit
    def test_amort(self):
        return self.capass[self.bsheet._ledge:], self.ppe[self.bsheet._ledge:].cumsum() - self.amort.cumsum()[:self.ppe[self.bsheet._ledge:].size]

class CFlowTests(BaseTests):
    name = 'CFlowTests'
    def __init__(self, cflow):
        self.cflow = cflow
        
        super().__init__()

    # Test Start / End Cash #
    @property
    def cash_start(self):
        return self.cflow.stat.loc['Cash - Start'].values[0]
    
    @property
    def cash_end(self):
        return self.cflow.stat.loc['Cash - End'].values[0]

    @property
    def delta_cash(self):
        return self.cflow.stat.loc['Change in Cash'].values[0]

    @testit
    def test_cash_ends(self):
        return self.cash_start[:-2] + self.delta_cash[:-2], self.cash_end[:-2]

class FStatTests:
    def __init__(self, istat=None, bsheet=None, eqstat=None, cflow=None):
        self.istat = IStatTests(istat) if istat is not None else istat
        self.bsheet = BSheetTests(bsheet) if bsheet is not None else bsheet
        # self.eqstat = EQStatTestseqstat
        self.cflow = CFlowTests(cflow) if cflow is not None else cflow
    
    @property
    def tests(self):
        return [self.istat, self.bsheet, self.cflow] # self.eqstat,

    def run(self):
        for t in self.tests:
            print (t.name)
            t.run()
            print ('')
