from pywyse.sales import Opportunity
import pytest 

def test_sales(): 

    opps = Opportunity().get_opportunities(pageSize = 32)
    assert isinstance(opps, list)
    assert len(opps) == 32

    opp = Opportunity().get_opportunity(opps[30]['id'])
    assert isinstance(opp, list)
    assert len(opp) == 1

    