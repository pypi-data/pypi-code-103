import pytest 
from pywyse import Client 

def test_package_import():
    import pywyse 
    pywyse.client 
    pywyse.service
    pywyse.procurement
    
    with pytest.raises(AttributeError):
        pywyse.someerror

def test_function_import(): 
    from pywyse.procurement import Procurement
    from pywyse import procurement
    procurement.Procurement
    import pywyse 
    pywyse.procurement.Procurement

    # from pywyse import service 
    # service.get_ticket
    from pywyse import company
    company.Company
    from pywyse.company import Company

def test_build_url(): 
    resp = Client.build_url('/hello/world', 'myname/is')
    assert isinstance(resp, str)
    assert resp == '/hello/world/myname/is'