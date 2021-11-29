
from urllib import parse
import requests
import json

class Authenticator:
    def __init__(self, username, password, region):
        """authenticator class"""
        self.url = "https://www.credit-agricole.fr"
        self.ssl_verify = True
        self.username = username
        self.password = password
        self.region = region
        self.cookies = None
        
        self.authenticate()
        
    def map_digit(self, key_layout, digit):
        """map digit with key layout"""
        i = 0
        for k in key_layout:
            if int(digit) == int(k):
                return i
            i += 1
            
    def authenticate(self):
        """authenticate user"""
        # get the keypad layout for the password
        url = "%s/ca-%s/particulier/" % (self.url, self.region)
        url += "acceder-a-mes-comptes.authenticationKeypad.json"
        r = requests.post(url=url,
                          verify=self.ssl_verify)
        if r.status_code != 200:
            raise Exception( "[error] keypad: %s - %s" % (r.status_code, r.text) )

        self.cookies = r.cookies 
        rsp = json.loads(r.text)
        self.keypadId = rsp["keypadId"]
        
        # compute the password according to the layout
        j_password = []
        for d in self.password:
            k = self.map_digit(key_layout=rsp["keyLayout"], digit=d)
            j_password.append( "%s" % k)


        # authenticate the user
        url = "%s/ca-%s/particulier/" % (self.url, self.region)
        url += "acceder-a-mes-comptes.html/j_security_check"
        headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        payload = {'j_password': ",".join(j_password),
                   'path': '/content/npc/start',
                   'j_path_ressource': '%%2Fca-%s%%2Fparticulier%%2Foperations%%2Fsynthese.html' % self.region,
                   'j_username': self.username,
                   'keypadId': rsp["keypadId"],
                   'j_validate': "true"}
        r2 = requests.post(url=url,
                          data=parse.urlencode(payload),
                          headers=headers,
                          verify=self.ssl_verify,
                          cookies = r.cookies)
        if r2.status_code != 200:
            raise Exception( "[error] securitycheck: %s - %s" % (r2.status_code, r2.text) )

        # success, extract cookies and save-it
        self.cookies = requests.cookies.merge_cookies(self.cookies, r2.cookies)
