from pywyse.client import Client 

class Company(Client): 

    def __init__(self): 
        super(Company, self).__init__()
        
    def get_companies(self, endpoint='/company/companies', **kwargs): 
        return self.cw_get(endpoint=endpoint, **kwargs).json()
      
    def get_company(self, id=2, **kwargs): 
        endpoint = '/company/companies/' + str(id)
        return self.cw_get(endpoint, **kwargs).json()

    def get_sites(self, company_id, **kwargs):
        endpoint = '/company/companies/' + str(company_id) + '/sites'
        return self.cw_get(endpoint, **kwargs).json() 

    def get_site(self, company_id, site_id, **kwargs):
        endpoint = '/company/companies/' + str(company_id) + '/sites/' + str(site_id)
        return self.cw_get(endpoint, **kwargs).json()

