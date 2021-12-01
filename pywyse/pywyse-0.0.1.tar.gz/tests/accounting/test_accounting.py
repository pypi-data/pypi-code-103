import pytest 
from pywyse.accounting import Expense
from pywyse.accounting import Invoice
from pywyse.accounting import Procurement
from pywyse.client import Client

from pprint import pprint 


def test_count(): 
    resp = Procurement().count_unposted(verbose=True)
    assert isinstance(resp, dict)
    
def test_pre_batch(): 
    resp = Procurement().get_unposted(verbose = True, pageSize=1)
    assert isinstance(resp, list)
    assert len(resp) == 1
    resp

    pprint(resp)


def test_soft_batch(): 
    prod = Procurement()
    prod.get_batch_ids(ids=['7325-STOCK10012021-purchase'])
    assert len(prod.batch_ids) == 1
    assert isinstance(prod.batch_ids, list)
    

def test_soft_batch_ids(): 
    prod = Procurement()
    resp = prod.soft_batch()
    
    resp.keys()
    pprint(resp['exportSettings'])
    pprint(resp['transactions'])
    pprint(resp['purchaseTransactions'])
    len(resp['purchaseTransactions'])
    pprint(resp['purchaseTransactions'][0])