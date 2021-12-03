import base64
import requests
import json

from . import config

from inktool.endpoints.orders import OrderMethods
from inktool.endpoints.neprinters import NEPrinterMethods

class InkToolAPI:

    def __init__(self, secureCode):
        self.baseUrl = config.BASE_URL
        self.secureCode = secureCode

        self.headers = {}

        self.orders = OrderMethods(self)
        self.neprinters = NEPrinterMethods(self)

    def setAuthHeader(self, secureCode):
        encodedBytes = base64.b64encode(secureCode.encode('utf-8'))
        encodedString = str(encodedBytes, 'utf-8')
        self.headers.update({'Authorization' : encodedString})

    def checkHeaderTokens(self):
        if 'Authorization' not in self.headers: self.setAuthHeader(self.secureCode)

    def doRequest(self, method, url, data=None, headers=None):

        if headers:
            mergedHeaders = self.headers
            mergedHeaders.update(headers)
            headers = mergedHeaders
        else: headers = self.headers

        reqUrl = '{base}/{url}/'.format(base=self.baseUrl, url=url)

        if method == 'GET':
            response = requests.get(reqUrl, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(reqUrl, data=json.dumps(data), headers=headers)
        elif method == 'PUT':
            response = requests.put(reqUrl, data=json.dumps(data), headers=headers)
        
        return response


    def request(self, method, url, data=None, headers=None):
        
        # Check the headers for appropriate tokens before we make a request
        self.checkHeaderTokens()

        # Make the request
        response = self.doRequest(method, url, data, headers)
        respContent = response.json()
        
        return response.status_code, response.headers, respContent
    
    def get(self, url, data=None, headers=None):
        status, headers, response = self.request('GET', url, data, headers)
        return status, headers, response
    
    def post(self, url, data=None, headers=None):
        status, headers, response = self.request('POST', url, data, headers)
        return status, headers, response
    
    def put(self, url, data=None, headers=None):
        status, headers, response = self.request('PUT', url, data, headers)
        return status, headers, response