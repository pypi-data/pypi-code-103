import os
import pendulum
from requests import Session
from io import BytesIO
from .globals import APPHUB_PROD_HOST
from .decorators import jsonify_response, validate_search, one_of_keyword_only, check_names


from urllib.parse import urljoin


class AppHubObject(object):

    def __init__(self, ah, content_type):
        """
        Initializes an AppHub Content Object with default owner of `swimlane`
        Args:
            ah: (AppHub) Object
            content_type: (str) One of `swimbundles`, `apps`, or `applets`. not enduser exposed
        """
        self.content_type = content_type
        self._api_base = "api/{}".format(content_type)
        self._ah = ah

    def make_endpoint(self, endpoint):
        """
        Args:
            endpoint: (str) API endpoint

        Returns: (str) full endpoint

        """
        return self._api_base + '/' + endpoint


class AppHubLogos(AppHubObject):

    def get(self, _id=None):
        """
        Get Content from AppHub
        Args:
            _id: (str) id of logos

        Returns: (dict)

        """
        return self._ah.request("GET", self.make_endpoint(_id)).json()

class AppHubFeeds(AppHubObject):
    def get(self, date=None, dateObj=pendulum.today()):
        """
        Get content feed from AppHub
        
        Args:
            date: (str)
        """
        if date:
            dateObj = pendulum.parse(date)
        return self._ah.request("GET", self.make_endpoint("content"), params={'date': dateObj.to_iso8601_string()})

class AppHubGeneral(AppHubObject):

    def get(self):
        """
        Get Content from AppHub
        Args:
            _id: (str) id of logos

        Returns: (dict)

        """
        return self._ah.request("GET", self.make_endpoint("release")).json()
    
    def post(self, version, date, new_features=[], improvements=[],bug_fixes=[]):
        """
        Add Content to AppHub
        Args:
            version: Version of document
            date: string date
            new_featurs/improvements/bug_fixes: list of string notes

        Returns: (dict)

        """
        return self._ah.request("POST", self.make_endpoint("release"), json={
            "version": version, 
            "date": date, 
            "new_features": new_features, 
            "improvements": improvements, 
            "bug_fixes": bug_fixes
            }).json()

    def update(self, version, date=None, new_features=[], improvements=[],bug_fixes=[]):
        """
        Update Content in AppHub
        Args:
            version: Version of document
            date: string date
            new_featurs/improvements/bug_fixes: list of string notes

        Returns: (dict)

        """
        json_obj = {
            "date": date, 
            "new_features": new_features, 
            "improvements": improvements, 
            "bug_fixes": bug_fixes
            }
        
        return self._ah.request("POST", self.make_endpoint("release/{}".format(version)), json={k: v for k, v in json_obj.items() if v}).json()

    def delete(self, version):
        """
        Delete Content in AppHub
        Args:
            version: version of document

        Returns: (dict)

        """
        return self._ah.request("DELETE", self.make_endpoint("release/{}".format(version))).json()


class AppHubContentObject(AppHubObject):

    # The following dict will contain data in the form of {"bundle_name": ["list", "of", "versions"]} 
    # to allow "did you mean?" when end users fat finger things. Eventually this functionality will come from
    # the API
    CONTENT_MAP = {}

    def __init__(self, ah, content_type, is_versioned=False, owner="swimlane"):
        """
        Initializes an AppHub Content Object with default owner of `swimlane`
        Args:
            ah: (AppHub) Object
            content_type: (str) One of `swimbundles`, `apps`, or `applets`. not enduser exposed
            is_versioned: (bool) Is content versioned.
            owner: (str) content owner for building endpoint.
        """
        super(AppHubContentObject, self).__init__(ah, content_type)

        self.__is_versioned = is_versioned
        self.__owner = owner


    @jsonify_response
    def get(self, name=None, version='latest', _id=None):
        """
        Get Content from AppHub
        Args:
            name: (str) Content name
            version: (str) content version

        Returns: (dict)

        """
        return self._ah.paginated_request("GET", self.make_endpoint(name, version))

    def upload(self, file_path='', f=None):
        """
        Upload a file to AppHub (Admin Only)
        Args:
            file_path: (str) Path to file that will upload to AppHub
            f: (file) File-like object to upload.

        Returns: (requests.Response)

        """
        files = {"file": open(os.path.join(file_path), 'rb') if file_path else f}
        return self._ah.request("POST", '{}/upload'.format(self._api_base), files=files)

    def download(self, name=None, version='latest', f=BytesIO):
        """
        Download a file from AppHub (Authenticated user only)
        Args:
            name: (str) Content name
            version: (str) content version
            f: (file obj) Optional file object to write download zipfile to

        Returns: (BytesIO) Downloaded file from AppHub

        """
        return f(self._ah.request("GET", self.make_endpoint(name, version) + "/download").content)

    @jsonify_response
    def delete(self, name=None, version=None):
        """
        Delete a file from AppHub (Admin Only)
        Args:
            name: (str) Content name
            version: (str) content version

        Returns:  (requests.Response)

        """
        return self._ah.request("DELETE", self.make_endpoint(name, version))

    @jsonify_response
    def update_description(self, description, name=None):
        """
        Update description in AppHub (Admin Only)
        Args:
            description: (str) Description/Markdown for content
            name: Name of content

        Returns: (requests.Response)

        """
        return self._ah.request("PUT", self.make_endpoint(name), json={
            "description": description
        })

    @validate_search
    @one_of_keyword_only('fields', 'text')
    def search(self, kw, val):
        """
        Search AppHub
        Args:
            kw: (str) one of `fields` or `text`
            val: value for kw, either a dict of fields/vals or a string

        Returns: (requests.Response)

        """
        return self._ah.request("POST", 'api/' + self.content_type, json={kw: val})

    @check_names
    def make_endpoint(self, name=None, version=None):
        """

        Args:
            name: (str) Content name
            version: (str) content version

        Returns: (str) endpoint

        """
        endpoint = self._api_base
        if self.content_type != 'logos':
            endpoint += '/' + self.__owner
        if name:
            endpoint += '/' + name
        if version and self.__is_versioned:
            endpoint += '/v/' + version
        return endpoint


class AppHub(object):

    def __init__(self, username, password, host=APPHUB_PROD_HOST, ignore_dup_error=True, verify_ssl=True, proxies=None):
        """
        AppHub Client initializer
        Args:
            host: (str) AppHub Host defaults to production environment
            username: (str) AppHub Username
            password: (str) AppHub Password
            ignore_dup_error: (Bool) Ignore 409 Duplicate errors from AppHub (no dups will be uploaded)
            verify_ssl: (Bool) Verify SSL in requests
        """
        self.__host = host
        self.__session = Session()
        self.__session.verify = verify_ssl
        self.__ignore_dup_error = ignore_dup_error
        self.__session.proxies = proxies
        self.authorize(username, password)
        self.swimbundles = AppHubContentObject(self, 'swimbundles', is_versioned=True)
        self.logos = AppHubLogos(self, 'logos')
        self.general = AppHubGeneral(self, 'general')
        self.feeds = AppHubFeeds(self, "feeds")


    def authorize(self, username, password):
        r = self.request("post", "api/auth/signin", json={"username": username, "password": password})
        self.__session.headers.update(
            {
                'Authorization': "Bearer {}".format(r.json()['data']['accessToken']['jwtToken']),
                "X-Forwarded-Proto": "https"
            }
        )

    def request(self, method, endpoint, **kwargs):
        """
        Request wrapper for session.
        Args:
            method: (str) Request method
            endpoint: (str) AppHub API endpoint
            **kwargs: (dict) kwargs to pass to `requests.request`

        Returns: (requests.Response)

        """
        resp = self.__session.request(method, urljoin(self.__host, endpoint), **kwargs)
        try:
            resp.raise_for_status()
        except Exception as e:
            if resp.status_code != 409 or not self.__ignore_dup_error:
                raise Exception(resp.content, e)
        return resp

    def paginated_request(self, method, endpoint, **kwargs):
        """
        Paginate wrapper for request.
        Args:
            method: (str) Request method
            endpoint: (str) AppHub API endpoint
            **kwargs: (dict) kwargs to pass to `requests.request`

        Returns: (dict) paginated data

        """
        next_page = True
        responses = []
        while next_page:
            response = self.request(method, endpoint, **kwargs)
            response_json = response.json()
            responses.append(response)
            if response_json.get('data'):
                if isinstance(response_json['data'], dict):
                    return response
                meta = response_json.get('meta')
                if not meta:
                    break
                next_page = meta.get('next')
                kwargs['params'] = {'page': next_page}
        return responses
