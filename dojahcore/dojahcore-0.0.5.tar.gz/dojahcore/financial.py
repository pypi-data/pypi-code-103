"""
The financial services APIs are available to retrieve financial information of users from various banks via internet banking.
To make use of these APIs, you must have been verified on the Dojah app.

The widget is the interface your users see when they need to submit the internet details. 
You can set up the widget here https://api-docs.dojah.io/docs/financial-widget.

Our financial widget process flow:

Your application allows your end users to launch the widget
The end user fills the registration process which includes selecting financial institution etc.

After successful completion, the widget returns a secret key in your Dojah application which would be used to make APIs calls

"""

from dojahcore.core import DojahBase

class Financial(DojahBase):
    """
 



    """

    @classmethod
    def account_information(cls,account_id):
        """
            Retrieves the bank account information of a customer.

            params :
                    account_id : str -> required - Gotten from the financial widget
        """

        response  = cls().requests.get('/api/v1/financial/account_information',query =[('account_id',account_id)])

        return response

    @classmethod
    def account_transactions(cls, account_id, last_transaction_id=None, start_date=None, end_date=None, trans_type=None, response_mode=None, callback_url=None):
        """
            This endpoint allows users retrieve customer's transaction details from their bank accounts. 
            Transaction details include the bank name linked to the transaction, amount, location, transaction type (credit or debit), time,
            and date of occurrence.
        
            params :
                    account_id : str -> required - Gotten from the financial widget
                    last_transaction_id : str -> optional  - the oldest transaction ID you want to start with
                    start_date : str -> optional - the start date of transaction you want to get
                    end_date : str -> optional - the end date of transaction you want to get
                    trans_type : str -> optional - (debit or credit)
                    response_mode : str -> optional - Your preferred mode of results. (paginated, not_paginated, or webhook) Defaults to paginated
                    callback_url : str -> optional - callback url used as webhook
            
            returns :
                    Json data from Dojah API


        """

        query  = {
            'account_id': account_id
        }

        if last_transaction_id:
            query['last_transaction_id'] = last_transaction_id
        if start_date:
            query['start_date'] = start_date
        if end_date:
            query['end_date'] = end_date
        
        trans_types  = ['credit','debit']

        if trans_type:
            if  trans_type in trans_types:
                query['trans_type']= trans_type
            else:
                raise ValueError('transaction type should be credit or debit')

        response_modes  = ['paginated', 'not_paginated', 'webhook']

        if response_mode:
            if response_mode in response_modes:
                query['response_mode'] = response_mode
            else:
                raise ValueError("response_mode should be paginated, not_paginated or webhook")
        
        if response_mode == 'webhook' and not callback_url:
            raise ValueError('Callback Url required for webhook response type')
        
        if callback_url:
            query['callback_url'] =  callback_url
        
        response  =  cls().requests.get('/api/v1/financial/account_transactions',query=query)

        return response

    

    @classmethod
    def account_subscription(cls, account_id, start_date=None, end_date=None, status=None):
        """
         This endpoint allows you to retrieve recurring payments that occur daily,
         weekly, monthly, or yearly from transactions. 
         The endpoint returns the transaction date, amount, the name of the service that the service subscribed to (e.g. Netflix), 
         the subscription duration (i.e. yearly or monthly subscription), etc.

        params : 
                account_id : str -> required - account ID gotten from the widget
                start_date : str -> optional - the start date of transaction you want to get
                end_date : str -> optional - the end date of transaction you want to get
                status : str -> optional -  (expired or not_expired)

        returns:
                Json data from Dojah API
        
        """

        query = {
            'account_id': account_id
        }

        statuses  = ['expired','not_expired']
        if status:
            if status in statuses:
                query['status'] =  status
            else:
                raise ValueError('Status should be either of expired or not_expired')
        
        if start_date:
            query['start_date'] = start_date
        if end_date:
            query['end_date'] = end_date
        

        response = cls().requests.get('/api/v1/financial/account_subscription', query=query)

        return response

    
    @classmethod
    def earning_structure(cls,account_id,duration):
        """
        This endpoint allows developers to determine if a customer is a salary earner, and to determine the amount of employer's income.

        params : 
                account_id : str -> required - account id gotten from the widget
                duration : str -> optional - (6_months,12_months,24_months)

        returns :
                Json data from Dojah API
        
        """

        query = {
            'account_id': account_id
        }

        durations = ['6_moonths','12_months','24_months']

        if duration in durations:
            query['duration'] =  duration

        response =  cls().requests.get('/api/v1/financial/earning_structure',query=query)


        return response

    @classmethod
    def spending_pattern(cls, account_id, duration):
        """
        This endpoint gives insights on users' spending habits based on transactions, and it comes in percentages.

        params : 
                account_id : str -> required - account id gotten from the widget
                duration : str -> optional - (6_months,12_months,24_months)

        returns :
                Json data from Dojah API
        
        """

        query = {
            'account_id': account_id
        }

        durations = ['6_moonths','12_months','24_months']

        if duration in durations:
            query['duration'] =  duration

        response =  cls().requests.get('/api/v1/financial/spending_pattern',query=query)


        return response


    @classmethod
    def categorize_transactions(cls, description, trans_type):
        """
        This endpoint allows you to categorize your transactions 
        using our machine learning model and merchant validation system.

        params :
                description : str -> required - description of the transaction
                trans_type : str -> required -  (debit or credit)
        
        returns :
                Json data from Dojah API

        """

        if not description:
            raise ValueError('Description can not be None')
        

        body = {
            'description': description
        }
        trans_types = ['credit','debit']
        if trans_type:
            if trans_type in trans_types:
                body['trans_type'] = trans_type
            else:
                raise ValueError('trans_type must be either of credit or debit')
        else:
            raise ValueError('trans_type can not be None')


        response  =  cls().requests.post('/api/v1/ml/categorize_transaction',body=body) 

        return response


    @classmethod
    def send_transactions(cls, transactions):
        """This endpoint will post the transactions and return an account_id.

            params : 
                    transactions : array of transactions
                    sample :
                    [
                        {
                             "transaction_date":"2021-04-30",
                             "transaction_type":"credit",
                             "transaction_amount":"2016.4",
                             "reference_number":"12345tgfnde",
                             "transaction_description":"0033199479:Int.Pd:01-04-2021 to 30-04-2 |"
                        }
                    ]
            
            returns :
                    Json Data from Dojah API
        
        """

        body ={
            'transactions': transactions
        }
        
        response  =  cls().requests.post('/api/v1/financial/transactions',body=body)

        return response

    
    @classmethod
    def update_transactions(cls, account_id, transactions):
        """
        This endpoint will update transactions
            params : 
                    transactions : array of transactions
                    sample :
                    [
                        {
                             "transaction_date":"2021-04-30",
                             "transaction_type":"credit",
                             "transaction_amount":"2016.4",
                             "reference_number":"12345tgfnde",
                             "transaction_description":"0033199479:Int.Pd:01-04-2021 to 30-04-2 |"
                        }
                    ]
            
            returns :
                    Json Data from Dojah API
        
        """

        body ={
            'transactions': transactions
        }

        response  =  cls().requests.put('/api/v1/financial/transactions/{}'.format(account_id),body=body)

        return response




        


