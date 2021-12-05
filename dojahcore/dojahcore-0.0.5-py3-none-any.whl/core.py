""" Script contains all the core implementation """
import requests
import dojahcore as core
from dojahcore.server_error import ServerError
class DojahBase:
    """ Base class"""

    def __init__(self, **kwargs) -> None:
        """ Prepare the requests """

        api_key  =  kwargs.get('api_key',core.API_KEY)
        api_url  =  core.API_URL
        api_id  =  kwargs.get('app_id',core.APP_ID)
        
         
        headers  =  {'Authorization': api_key, 'AppId': api_id}
        arguments  = {"headers":headers, "api_url": api_url}

        self.requests  =  DojahRequests(**arguments)

class DojahRequests(object):
    """" Contains request implementation """

    def __init__(self, api_url, headers=None) -> None:
        """ Initialize requests object 
        params:
                api_url: str
                headers : dict

        """
        self.BASE_URL  =  api_url
        self.headers  =  headers
        

    def _request(self, method, uri, **kwargs):

        """ Call a method on the specified resource uri
        
        params:
                method: GET | POST | PUT
                uri : endpoint
        Raises :
                HTTPError
        Returns :
                JSON
         """

        body  =  kwargs.get('body')
        query =  kwargs.get('query')
        response   = method(self.BASE_URL + uri, json=body,headers=self.headers, params=query)

        if response.status_code != 200:
                raise ServerError(
                        "Failed to complete request, status={}, error_message={}".format(response.status_code, response.json()['error'])
                )
        return response.json()['entity']
    

    def get(self, endpoint,**kwargs):
        """ GET request method
        
        params :
                endpoint : uri pointing to the resource

        """

        return self._request(requests.get,endpoint,**kwargs)
    def put(self,endpoint,**kwargs):
            """ PUT request method

            params :
                      endpoint : uri pointing to the resource
            
            """

            return self._request(requests.put,endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        """ POST request method
        
        params :
                endpoint : uri for the resource
        
        """

        return self._request(requests.post,endpoint,**kwargs)





