from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from clear_s2s.APIHandler import APIHandler
from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(loader=PackageLoader("clear_s2s.CLEAR"), autoescape=select_autoescape())


class ThomsonReuters:

    def __init__(
        self,
        url,
        username,
        password,
        client_id=None,
        client_secret=None,
        s2s_scopes=None,
        cert_path=None,
        cert_key_path=None,
        logging=False
        ):
        self._api_handler = APIHandler(
            host=url,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            s2s_scopes=s2s_scopes,
            cert_path=cert_path,
            cert_key=cert_key_path,
            headers={'Content-Type': 'application/xml'},
            logging=logging,
        )

    def person_search(self, **kwargs):
        template = env.get_template("PersonSearchRequest.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/person/searchResults', payload=payload)

    def eidv_person_search(self, **kwargs):
        template = env.get_template("EIDVPersonSearch.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/eidvperson/searchResults', payload=payload)

    def business_search(self, **kwargs):
        template = env.get_template("BusinessSearchRequest.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/business/searchResults', payload=payload)

    def person_quick_analysis_search(self, **kwargs):
        template = env.get_template("PersonQuickAnalysisFlagRequest.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/person/quickanalysis/searchResults', payload=payload)

    def business_quick_analysis_search(self, **kwargs):
        template = env.get_template("CompanyQuickAnalysisFlagRequest.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/business/quickanalysis/searchResults', payload=payload)
    
    def social_media_search(self, **kwargs):
        template = env.get_template("WebAndSocialMediaSearchRequest.xml")
        payload = template.render(**kwargs)
        return self._api_handler.send_request('/v2/webandsocialmedia/searchResults', payload=payload)
