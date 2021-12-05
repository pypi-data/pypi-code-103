""" Script contains all ID verification resources """

from dojahcore.core import DojahBase

class Verification(DojahBase):
    """
        This class contains all KYC/KYB identification endpoints
        To ensure that your customer is who they say they are, you can allow them take a selfie photo which you can pass on to the Dojah for verification process
        This helps to significantly reduce the possibility of fraud by confirming the person using your product is the account owner at the validated bank.
        Note that; Confidence value is used to verify match and values from 90 are considered false.

        TODO : 1. Wrap the response, raise error as appropriate or not
               2. Clean endpoint
    """   

    @classmethod
    def verify_age(cls, mode,mode_value,first_name,last_name,strict=False):
        """Age Identity and Verification allows you to confirm and ascertain information summitted by your end users.
            With this endpoint, Dojah can help you verify first name, middle name by simply adding it to the request body
            Information Required; Phone Number OR Account Number OR BVN


            params :
                    mode : str -> required (phone_number,account_number or bvn)
                    strict : bool -> default is False
                    mode_value : str -> required (value of the mode specified)
                    first_name : str 
                    last_name : str

            returns :
                    Json response from Dojah API
            
        """

        query = [('mode',mode),(mode,mode_value),('first_name',first_name),('last_name',last_name)]
        response = cls().requests.get('/api/v1/kyc/age_verification',query=query)

        return response
    
    @classmethod
    def verify_bvn_selfie(cls, bvn, selfie_image):
        """
        This endpoint allows you to verifies your customers with their selfie images and their valid BVN
        
        params  : 
                bvn : str  -> required
                selfie_image : base64 value of the selfie image -> required
        
        returns :
                Json response from Dojah API


        """

        body  = {
            'bvn': bvn,
            'selfie_image': selfie_image
        }

        response  =  cls().requests.post('/api/v1/kyc/bvn/verify',body=body)

        return response
    

    @classmethod
    def verify_nin_selfie(cls, nin, selfie_image):
        """
        This endpoint identify and verifies a person using their selfie image and their valid NIN

        params :
                nin : str -> required
                selfie_image : base64 value of the selfie image -> required
        
        returns :
                Json response from Dojah API
        
        """

        body = {
            'nin': nin,
            'selfie_image': selfie_image

        }

        response = cls().requests.post('/api/v1/kyc/nin/verify', body=body)

        return response

    @classmethod
    def verify_photoid_selfie(cls, photo_id, selfie_image, last_name=None, first_name=None):
        """
        This endpoint verifies an individual's identity using their photo id and a selfie image

        params :
                photo_id : str -> photo image in base64 -> required
                selfie_image : str -> base64 value of the selfie image -> required
                last_name : str -> optional
                first_name : str -> optional
            
        returns :
                Json response from Dojah API

        """

        body = {
            'photo_id': photo_id,
            'selfie_image': selfie_image
        }

        if last_name:
            body['last_name'] =  last_name
        if first_name:
            body['first_name'] =  first_name
        
        response  =  cls().requests.post('/api/v1/kyc/photoid/verify',body=body)

        return response

