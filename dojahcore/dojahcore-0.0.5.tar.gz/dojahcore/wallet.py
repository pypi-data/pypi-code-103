"""Script contains all services in the wallet category """
from dojahcore.core import DojahBase

class Wallet(DojahBase):
    """
    
    """
    @classmethod
    def create(cls,dob,phone_number,last_name,first_name,bvn=None,middle_name=None,):
        """
            This endpoint allows you to create a virtual wallet with a NUBAN

            params : 
                    dob -> string - required (07-Aug-1958)
                    phone_number -> string - required
                    bvn -> string - optional
                    middle_name -> string - optional
                    last_name -> string  - required
                    first_name -> string - required
            returns :
                    Json data from Dojah API
                    
        """

        body = {
            "dob": dob,
            "phone_number":phone_number,
            "last_name": last_name,
            "first_name": first_name
        }

        if bvn:
            body['bvn'] =  bvn
        if middle_name:
            body['middle_name'] = middle_name

        response  =  cls().requests.post('/api/v1/wallet/ngn/create',body=body)

        return response


    @classmethod
    def transaction(cls, transaction_id):
        """
            Get details of a transaction

            params :
                    transaction_id -> str - required
            
            returns:
                    Json data from Dojah API
        
        """


        if not transaction_id:
            raise ValueError("Transaction Id can not be None")

        query ={
            'transaction_id' : transaction_id
        }

        response  =  cls().requests.get('/api/v1/wallet/ngn/transaction',query=query)


        return response
    

    @classmethod
    def details(cls, wallet_id):
        """
           With this endpoint, you can easily retrieve information and details of a created wallet.

           params : 
                    wallet_id : str - required

            returns :
                        Json Data from Dojah API 
        """


        query ={
            'wallet_id': wallet_id
        }
        response  =  cls().requests.get('/api/v1/wallet/ngn/retrieve',query=query)

        return response

    @classmethod
    def transfer_funds(cls,amount,recipient_bank_code,recipient_account_number,wallet_id):
        """
            An endpoint that allows your user to transfer funds
            from wallet created to any Nigerian Bank Account

            params :
                    amount -> str - required
                    recipient_bank_code -> str - required
                    recipient_account_number -> str - required
                    wallet_id -> str - required
            returns :
                         Json response from Dojah API
        """
        body = {
            'wallet_id': wallet_id,
            'amount': amount,
            'recipient_bank_code': recipient_bank_code,
            'recipient_account_number': recipient_account_number,

        }

        response  = cls().requests.post('api/v1/wallet/ngn/transfer',body=body)

        return response

    @classmethod
    def transactions(cls, wallet_id):
        """
            Get all transactions in a wallet

            params : 
                    wallet_id -> str - required

            returns:
                    Json data from Dojah API

        """

        query ={
            'wallet_id': wallet_id
        }

        response  =  cls().requests.get('/api/v1/wallet/ngn/transactions',query=query)

        return response