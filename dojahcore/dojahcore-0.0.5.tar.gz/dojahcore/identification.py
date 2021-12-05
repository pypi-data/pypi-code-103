""" Script contains all identification resources """

from dojahcore import dojah
from dojahcore.core import DojahBase

class Identification(DojahBase):
    """
        This class contains all KYC/KYB identification endpoints
    
    """

    @classmethod
    def validate_bvn(cls,bvn, first_name=None, last_name=None, dob=None):
        """ Validates a bvn
        
        params :
                bvn : str -> Required 
                first_name : str -> Optional
                last_name : str -> Optional
                dob : str -> Optional
        returns :
           Json data from Dojah API

        """
        query= {
            'bvn': bvn
        }

        if first_name:
            query['first_name'] = first_name
        if last_name:
            query['last_name'] =last_name
        
        if dob:
            query['dob'] =  dob

        response  =  cls().requests.get('/api/v1/kyc/bvn', query=query)
        return response #TODO write utility function to parse response 

    @classmethod
    def lookup_bvn_basic(cls,bvn):
        """ The Lookup BVN endpoint returns details of a particular BVN

            Calls the /api/v1/kyc/bvn/full

        params :
                bvn : str -> required
        
        returns :
            Json data from Dojah API

        """
        response = cls().requests.get('/api/v1/kyc/bvn/full', query=[('bvn',bvn)])

        return response
    
    @classmethod
    def lookup_bvn_advance(cls, bvn):
        """ The Lookup BVN endpoint returns details of a particular BVN

            Calls the /api/v1/kyc/bvn/advance

        params :
                bvn : str -> required
        
        returns :
            Json data from Dojah API
        
        """

        response = cls().requests.get('/api/v1/kyc/bvn/advance', query=[('bvn',bvn)])

        return response

    @classmethod
    def lookup_nuban(cls, account_number, bank_code):
        """ The Lookup NUBAN (Nigeria Uniform Bank Account Number) endpoint provides information of users' account numbers

            params :
                    account_number : str -> required
                    bank_code : number  -> required
            
            returns :
                 Json data from Dojah API
        
        """


        response  = cls().requests.get('/api/v1/kyc/nuban', query=[('account_number',account_number),('bank_code',bank_code)])

        return response
    
    @classmethod
    def lookup_nin(cls, nin):
        """ This endpoint allows developers to fetch customers details 
            using the National Identification Number (NIN) of the customer

            params :
                    nin : str -> required

            returns :
                    Json data  from Dojah API
        """

        response = cls().requests.get('/api/v1/kyc/nin',query=[('nin',nin)])

        return response
    
    @classmethod
    def lookup_phone_number_basic(cls, phone_number):
        """ Returns the details of a phone number

            params :
                    phone_number : str -> required
            returns :
                    Json data from Dojah API
        
        """

        response = cls().requests.get('/api/v1/kyc/phone_number/basic', query=[('phone_number',phone_number)])

        return response

    
    @classmethod
    def lookup_phone_number(cls, phone_number):
        """ Returns the details of a phone number

            params :
                    phone_number : str -> required

            returns :

                    Json data from Dojah API
        """

        response = cls().requests.get('/api/v1/kyc/phone_number', query=[('phone_number',phone_number)])

        return response

    @classmethod
    def lookup_vin_dob(cls, state, first_name, last_name,dob):
        """ Lookup vin via date of birth

            params :
                    state : str -> required
                    first_name : str -> required
                    last_name : str -> required
                    dob : str -> required
            returns :
                    Json data from Dojah API
        """

        query = [('mode','dob'),('state',state),('first_name',first_name),('last_name',last_name),('dob',dob)]
        response = cls().requests.get('/api/v1/kyc/vin', query=query)

        return response
    
    @classmethod
    def lookup_vin(cls,vin, state, last_name):
        """ Lookup vin

            params :
                    vin : str -> required
                    state : str -> required
                    last_name : str -> required
            returns :
                    Json data from Dojah API
            
        """

        query =[('mode','vin'),('state',state),('last_name',last_name),('vin',vin)]

        response = cls().requests.get('/api/v1/kyc/vin', query=query)

        return response

    @classmethod
    def lookup_driver_licence(cls, license_number, dob):
        """ Returns details of a license number

            params :
                    license_number : str -> required
                    dob : yyyy-mm-dd -> required

            returns :
                    Json data from Dojah API        
        
        """

        query =  [('license_number', license_number),('dob',dob)]
        response  =  cls().requests.get('/api/v1/kyc/dl',query=query)

        return response

    @classmethod
    def lookup_cac(cls,rc_number, company_name):
        """ Fetch CAC information of customers' company/organization.
            CAC is a certificate that shows evidence of the company's existence.
        
            params :
                    rc_number : str -> required
                    company_name : str -> required
            
            returns :
                    Json data from Dojah API

        """

        query  = [('rc_number',rc_number),('company_name',company_name)]
        response  =  cls().requests.get('/api/v1/kyc/cac',query=query)

        return response

    @classmethod
    def lookup_tin(cls,tin):
        """ Fetch a person's details using the Tax Identification number
        
            params :
                    tin : str -> required
            

            returns :
                    Json data from Dojah API

        """

        response  =  cls().requests.get('/api/v1/kyc/tin',query=[('tin',tin)])

        return response
    

