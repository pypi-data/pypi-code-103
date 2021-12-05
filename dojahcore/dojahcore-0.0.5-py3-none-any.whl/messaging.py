""" Script contains all messaging services"""

from dojahcore.core import DojahBase


class Messaging(DojahBase):
    """
    
    """

    @classmethod
    def send_message(cls,sender_id, channel, destination,message, priority=False):
        """
        This endpoint allows you to deliver transactional messages to your customer

        params :
                sender_id : str -> required - your sender ID
                channel : str -> required - sms or whatsapp
                destination : str -> required - phone number of recipient
                message : str -> required - body of message
                priority : bool -> optional - indicates if you want to send in priority mode

        
        returns :
                Json data from Dojah API
        
        """

        body = {
            'sender_id': sender_id,
            'channel': channel,
            'destination': destination,
            'message': message,
            'priority': priority
        }

        response  = cls().requests.post('/api/v1/messaging/sms',body=body)

        return response


    @classmethod
    def register_sender_id(cls, sender_id):
        """
        Register your Sender ID with this endpoint, 
        you will get an email once it has been approved, 
        all messages sent before then will be delivered with the default sender ID
        
        params : 
                sender_id : str -> required - less than 11 characters

        returns :
                Json data from Dojah API

        """

        if len(sender_id) >= 11 :
            raise ValueError("sender id should be less than 11 characters")

        body = {
            'sender_id': sender_id
        }

        response  =  cls().requests.post('/api/v1/messaging/sender_id', body=body)

        return response

    @classmethod
    def fetch_sender_ids(cls):
        """
        Fetches all sender Ids associated with your account

        params :


        returns :
                Json data from Dojah API
        
        """

        response =  cls().requests.get('/api/v1/messaging/sender_ids')

        return response

    @classmethod
    def get_status(cls, message_id):
        """
        This endpoint allows you get the delivery status of messages
        
        params :
                message_id : str -> required - reference ID of the message
        
        returns :
                Json data from Dojah API
        
        """


        response  =  cls().requests.get('/api/v1/messaging/sms/get_status',query=[('message_id',message_id)])

        return response


    @classmethod
    def send_otp(cls, sender_id,destination,channel,expiry=10,length=6, priority=False, otp=None):
        """
        Deliver OTPs to your users via multiple channels such as whatsapp, voice, and sms 

        params :
                sender_id :	str ->	required - registered Sender ID
                destination : str -> required  - phone number of recipient
                channel :	str	  -> required - can be either whatsapp, sms, or voice
                expiry :	number -> optional -	number of minutes before token becomes Invalid. Default is 10
                length :	number -> optional - length of token(4 to 10 characters), default is 6 characters
                priority :	boolean	-> optional - indicate if you want to send in priority mode. Default is false
                otp	 :	    number  -> optional -length of token should be between 4-10 digits which is optional
        returns :
                Json data from Dojah API
        """

        body = {
            'sender_id': sender_id,
            'destination': destination,
            'expiry': expiry,
            'length': length,
            'priority':priority,
        }

        if otp:
            if len(otp) < 4 or len(otp) > 10:
                raise ValueError('Length of token should be between 4-10 digits')

        channels  = ['sms','whatsapp','voice']

        if channel not in channels:
            raise ValueError('Channel should be either of sms, whatsapp or voice')

        body['channel'] =  channel
        body['otp'] = otp

        response  =  cls().requests.post('/api/v1/messaging/otp', body=body)    

        return response
    
    @classmethod
    def validate_otp(cls,code, reference_id):
        """
        Validates OTP received from user
        
        params : 
                code : str -> required - OTP received from user
                reference_id : str -> required - ID to identify the OTP

        returns :
                Json data from Dojah API

        """

        query = [('code',code),('reference_id',reference_id)]

        response = cls().requests.get('/api/v1/messaging/otp/validate',query=query)

        return response
     

