from pywyse.company import Company
import pytest 

def test_company(): 
    companies = Company().get_companies(pageSize=32)
    assert isinstance(companies, list)
    assert len(companies) == 32

    company = Company().get_company(companies[30]['id'])
    assert isinstance(company, dict)
    # assert len(company) == 1

    site = Company().get_sites(company['id'])
    assert company.get('billingSite').get('id') in [c['id'] for c in site]
     
    billing_site = Company().get_site(company['id'], company['billingSite']['id'])
    assert isinstance(billing_site, dict)