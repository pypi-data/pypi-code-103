import re
import json
import redis
from collections.abc import Sequence
from collections.abc import MutableMapping

from data_verifier.base import BaseResposne
from data_verifier.model.ahrefs_model import AhrefsModel
from data_verifier.utils.persist_cookies import PersistCookies
from data_verifier.identities.ahrefs.templates import login_template, organic_chart_template
from data_verifier.identities.ahrefs.exceptions import SessionNotActive, GettingDetailsFailed, SessionExpired
from data_verifier.exceptions.exception import VerificationError, SessionRetrieveException, AccessDenied

class AhrefsSiteDetails(BaseResposne):
    login_url = 'https://toolszap.com/auth/login'
    toolszap_url='https://tool2.toolszap.com/site-explorer'
    get_token='https://tool2.toolszap.com/site-explorer/overview/v2/subdomains/live?target={}'

    nav_urls=[{'name':"domain_rating","url":'https://tool2.toolszap.com/site-explorer/ajax/overview/domain-rating/{}'},
              {"name":"backlink_stats","url":'https://tool2.toolszap.com/site-explorer/ajax/overview/backlinks-stats/{}'},
              {"name":"refering_domain_status","url":'https://tool2.toolszap.com/site-explorer/ajax/overview/referring-domains-stats/{}'},
              {"name":"domain_rank_history","url":'https://tool2.toolszap.com/site-explorer/ajax/overview/domain-rank-history-table/{}'},
              {"name":"anchors","url":'https://tool2.toolszap.com/site-explorer/ajax/overview/all-anchors/{}'},
              {"name":"tlds","url":'http://tool2.toolszap.com/site-explorer/ajax/overview/tlds-chart/{}'},
              {"name":"pe_stats","url":'http://tool2.toolszap.com/site-explorer/ajax/overview/PE-stats/{}?source=overview'},
              {"name":"backlink_change","url":'http://tool2.toolszap.com/site-explorer/ajax/overview/backlinks-changes-stats/{}'}]

    organic_chart='http://tool2.toolszap.com/v3/api-adaptor/seGetOrganicChartDataPhpCompat?pretty=1'

    traffic_by_country='http://tool2.toolszap.com/v3/api-adaptor/seGetMetricsByCountryPhpCompat?pretty=1'

    graph_url=[{"name":"main_chart","url":'http://tool2.toolszap.com/site-explorer/ajax/overview/main-chart/{}'},
               {"name":"position_histogram","url":'http://tool2.toolszap.com/positions-explorer/ajax/get-position-histogram/{}?region=all'},
               {"name":"position_histogram_ads","url":'http://tool2.toolszap.com/positions-explorer/ajax/get-position-histogram-ads/{}?region=all'}]

    key_word_url=[{"name":"top_keyword","url":'http://tool2.toolszap.com/positions-explorer/ajax/get-top-keywords/{}'},
                  {"name":"top_pages","url":'http://tool2.toolszap.com/positions-explorer/ajax/get-top-pages/{}'},
                  {"name":"top_ads","url":'http://tool2.toolszap.com/positions-explorer/ajax/get-top-ads/{}'}]

    INSIGNIFICANT_KEYS=['tooltip','TLDs','types','chart','pointStart','Categories','authorized_user','free_or_lite_or_standard_user','free_or_lite_user',
                        'free_user','lite_user','rows_limit_not_exceeded','serp_features','serp_structure']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Connection': 'keep-alive',
        'Host': 'toolszap.com',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    #'http://180.87.102.69:80'
    proxy_dict={}

    DEFAULT_PERSISTOR_EXPIRY = 60 * 60 * 24

    def __init__(self, to_verify, **kwargs):
        super(AhrefsSiteDetails, self).__init__(to_verify)
        self.to_verify = to_verify
        self.persistor = kwargs.get('persistor')
        self.login = kwargs.get('login',False)
        self.domain_data=kwargs.get('details',False)
        self.domain_graph=kwargs.get('graph',False)
        self.domain_keyword=kwargs.get('keyword',False)
        self.csrf=None
        self.cshash=None
        self.proxy=kwargs.get('proxy')

        if self.proxy is not None:
            self.proxy_dict[self.proxy.split('://')[0]]=self.proxy

    def save_session(self, additional_data=None):
        self.persistor.save_session(self.session, additional_data=additional_data,
                                    timeout=self.DEFAULT_PERSISTOR_EXPIRY)

    def load_sess(self):
        try:
            return self.persistor.load_session(self.session)
        except SessionRetrieveException:
            return False

    def map_nested_keys(self, mapping, function):
        for key in list(mapping):
            try:
                value = mapping[key]
            except KeyError:
                continue
            if isinstance(value, MutableMapping):
                self.map_nested_keys(value, function)
            if isinstance(value, Sequence):
                [self.map_nested_keys(m, function) for m in value if isinstance(m, MutableMapping)]
            function(mapping, key)

    def pop_insignificant_keys(self, data):
        return self.map_nested_keys(
            data, lambda dict_, key: dict_.pop(key, None) if key in self.INSIGNIFICANT_KEYS else None
        )

    def get_data(self,**kwargs):

        self.headers['Referer'] = 'https://tool2.toolszap.com/site-explorer'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['X-CSRF-Token']=self.csrf

        if kwargs.get('req','')=='POST':
            self.headers['Content-Type']='application/json'
        else:
            self.headers['Content-Type'] =''
        response = self.smart_request(kwargs.get('req'),kwargs.get('url'),headers = self.headers,json=kwargs.get('data'))

        if response.status_code!=200:
            raise GettingDetailsFailed(str(response.status_code)+' ERROR:\n'+response.text)

        if response.text.__contains__('Session Expired! Login Again.'):
            raise SessionExpired

        return response

    def pre_query(self):
        #TODO
        self.headers['host']='toolszap.com'
        response=self.smart_request('GET', self.login_url,headers=self.headers)
        hidden=self.get_hidden_payload(response)

        # return self.login_attempt(hidden)

    def login_attempt(self,hidden):
        payload = {**hidden,**login_template(self.to_verify.username,self.to_verify.password)}
        response = self.smart_request('POST',self.login_url,headers = self.headers,data=payload)

        try:
            json_data = response.json()

            if not json_data.get('ok'):
                raise VerificationError(',\n'.join(i for i in json_data.get('error')))

        except json.JSONDecodeError:
            raise VerificationError


        self.save_session()

        if self.login:
            return True

        return self.main_site()

    def main_site(self):

        self.headers['host']='tool2.toolszap.com'

        response=self.smart_request('GET',self.toolszap_url,headers=self.headers)
        if response.text.__contains__('You Are Not Logged In'):
            raise SessionNotActive

        if response.text.__contains__('Server Error'):
            raise SessionNotActive

        return self.get_tokens()

    def get_tokens(self):
        self.headers['Referer']='https://tool2.toolszap.com/site-explorer'
        self.headers['X-Requested-With']=''
        response=self.smart_request('GET',self.get_token.format(self.to_verify.domain),headers=self.headers)
        if response.text.__contains__("You dont have Access"):
            raise AccessDenied

        try:
            self.csrf=re.findall(r'name="_token"\Wcontent="(.+)"',response.text)[0]
            self.cshash=re.findall(r'CSHash = "(.+)"',response.text)[0]
        except IndexError:
            raise SessionNotActive

        return self.get_domain_info()

    def get_domain_info(self):
        details=dict()

        if self.domain_data:
            for urls in self.nav_urls:
                try:
                    response=self.get_data(req='GET',url=urls.get('url').format(self.cshash))
                    data=response.json()
                    if data.get('data') is not None:
                        data=data.get('data')
                    details[urls.get('name')]=data
                except GettingDetailsFailed as e:
                    print(e)
                    continue

            try:
                data=self.get_data(req='POST',url=self.traffic_by_country,data=organic_chart_template(self.to_verify.domain)).json()
                details['traffic_by_country']=data[1]
            except GettingDetailsFailed as e:
                print(e)

        if self.domain_graph:
            for urls in self.graph_url:
                try:
                    response=self.get_data(req='GET',url=urls.get('url').format(self.cshash))
                    data=response.json()
                    if data.get('data') is not None:
                        data=data.get('data')
                    details[urls.get('name')]=data
                except GettingDetailsFailed as e:
                    print(e)
                    continue

            try:
                data=self.get_data(req='POST',url=self.organic_chart,data=organic_chart_template(self.to_verify.domain)).json()
                details['organic_graph']=data[1]
            except GettingDetailsFailed as e:
                print(e)


        if self.domain_keyword:
            for urls in self.key_word_url:
                try:
                    response=self.get_data(req='GET',url=urls.get('url').format(self.cshash))
                    data=response.json()
                    if data.get('data') is not None:
                        data=data.get('data')
                    details[urls.get('name')]=data
                except GettingDetailsFailed as e:
                    print(e)
                    continue

        self.pop_insignificant_keys(details)

        return details

    def check_session(self):
        session_storage = self.load_sess()
        if not isinstance(session_storage, bool):
            return self.main_site()
        else:
            raise SessionNotActive

    @classmethod
    def do_login(cls, db_ob, **kwargs):
        obj = cls(db_ob, **kwargs)
        try:
            try:
                return obj.check_session()
            except SessionNotActive:
                return obj.pre_query()
        except SessionExpired:
            return cls.do_login(db_ob,**kwargs)

def test():
    applicant = AhrefsModel()
    applicant.username = 'arzamaanh@gmail.com'
    applicant.password = 'Oibnews@#784'
    applicant.domain='dtu.ac.in'

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'api-manager-verifier:{}'.format(applicant.username.replace('/', '_')))

    return AhrefsSiteDetails.do_login(applicant,persistor=persistor,details=True,proxy='http://179.49.161.58:999')
    #http://59.124.224.180:3128

if __name__ == '__main__':
    print(test())

