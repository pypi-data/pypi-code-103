""" Script contains all general services """

from dojahcore.core import DojahBase


class General(DojahBase):
    """
    
    
    """

    @classmethod
    def resolve_nuban(cls, account_number, bank_code):
        """
            This endpoint returns the account name linked to an account number

            params :
                    account_number -> string - required
                    bank_code -> string - required
            
            returns :
                    Json data from Dojah API
        """

        query = {
            'account_number': account_number,
            'bank_code': bank_code
        }

        response  =  cls().requests.get('/api/v1/general/account',query=query)

        return response

    
    @classmethod
    def banks(cls):
        """
            This endpoint allow you to get Nigerian banks and their codes.
        
        """



        response =  cls().requests.get('/api/v1/general/banks')

        return response


    @classmethod
    def resolve_card_bin(cls, card_bin):
        """
            Provides the details of a card.

            params : 
                    card_bin -> str - required
            

            returns :

                    Json data from Dojah API
        
        """

        query = {
            'card_bin': card_bin
        }

        response  =  cls().requests.get('/api/v1/general/bin', query=query)

        return response

    @classmethod
    def purchase_airtime(cls, amount, destination):
        """
            Buy airtime across alll mobine network

            params : 
                    amount : str - required
                    destination : [str] - required

            returns :
                        Json data from Dojah API
            

        """

        body = {
            'amount': amount,
            'destination': destination
        }

        response  =  cls().requests.post('/api/v1/purchase/airtime',body=body)

        return response



    @classmethod
    def purchase_data(cls,plan, destination):
        """
            Buy data

            params : 
                    plan : str -> required

                    destination : number -> required
            
            returns :
                        Json data from Dojah API
        
        """

        query = {
            'plan': plan,
            'destination':destination
        }

        response  =  cls().requests.get('/api/v1/purchase/data',query=query)

        return response

    @classmethod
    def data_plans(cls):
        """
            Get data plans

        
        """

        return cls().requests.get('/api/v1/purchase/data/plans')

    @classmethod
    def my_dojah_balance(cls):
        """
            Returns your Dojah Wallet Balance
        
        """


        return cls().requests.get('/api/v1/balance')



    