import pytest 
from pywyse.procurement import Procurement 
from pywyse.exceptions import PywyseException


def test_purchaseorder(): 
    p = Procurement()

    pos = p.get_purchaseorders(pageSize=1000, page=5)
    assert isinstance(pos, list)
    assert len(pos) > 0
    assert len(pos) == 1000

    po=pos[999].get('poNumber')

    with pytest.raises(PywyseException):  
        p.get_purchaseorder(po)

    po = p.get_purchaseorder(po[4:])

    assert isinstance(po, dict)
    assert 'id' in po
    # assert hasattr(po, 'id')