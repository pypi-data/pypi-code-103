import re
import os
import ast
import json
import pytz
import redis
import logging
import pandas as pd
from datetime import datetime
from http.client import responses
from collections.abc import Sequence
from data_verifier.base import BaseResposne
from collections.abc import MutableMapping

from data_verifier.model.rm_model import RMLoginManager
from data_verifier.identities.rm_internships.utils import get_auth_header
from data_verifier.identities.rm_internships.templates import login_template
from data_verifier.identities.rm_internships.exceptions import RMLoginError
from data_verifier.utils.persist_cookies import PersistCookies
from data_verifier.exceptions.exception import BackendError, SessionRetrieveException


class RMLogin(BaseResposne):
    login_url = "https://rm.dtu.ac.in/api/auth/login"
    profile_url = 'https://rm.dtu.ac.in/api/student/profile'
    aws_base_url='https://d20gxk19q2gyuc.cloudfront.net/'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,vi;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Host': 'rm.dtu.ac.in',
        'Origin': 'https://rm.dtu.ac.in',
        'Referer': 'https://rm.dtu.ac.in/login',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    DEFAULT_PERSISTOR_EXPIRY = 60 * 60 * 24 * 30
    INSIGNIFICANT_KEYS = ['debarrDate','createdAt','__v' ,'success','extraCurriculars']

    current_tz="GMT"
    conversion_tz="Asia/Kolkata"

    courses=["BTech", "MTech", "MSc", "MBA", "BBA", "BA", "BDes"]
    branches=[["Automotive Engineering", "Bio-Technology Engineering", "Chemical Engineering", "Civil Engineering", "Computer Engineering", "Electronics and Communications Engineering", "Electrical Engineering", "Environmental Engineering", "Engineering Physics", "Information Technology", "Mathematics and Computing", "Mechanical Engineering", "Polymer Science and Chemical Technology", "Production and Industrial Engineering", "Software Engineering"],
              ["Polymer Technology (PTE)", "Nano Science & Technology (NST)", "Bioinformatics (BIO)", "Geotechnical Engineering (GTE)", "Hydraulics & Water Resources Engineering (HRE)", "Structural Engineering (STE)", "Geoinformatics Engineering (GINF)", "Computer Science & Engineering (CSE)", "Software Engineering (SWE)", "Information System (ISY)", "Microwave and Optical Communication Engineering (MOC)", "Signal Processing & Digital Design (SPD)", "VLSI Design and Embedded System (VLS)", "Control & Instrumentation (C&I)", "Power System (PSY)", "Power Electronics and Systems (PES)", "Environmental Engineering (ENE)", "Production Engineering (PRD)", "Thermal Engineering (THE)", "Industrial Biotechnology (IBT)"],
              ["Mathematics", "Physics", "Chemistry", "Biotechnology"],
              ["Data Analytics", "Knowledge and Technology Management", "Supply Chain Management", "Information and Technology Management", "Human Resources", "Finance", "Marketing", "General", "Executive"]]

    def __init__(self, to_verify, **kwargs):
        super().__init__(to_verify)
        self.to_verify = to_verify
        self.persistor = self.safe_dict(kwargs, 'persistor')
        self.kwargs=kwargs

    def safe_dict(self, data: dict, key, default=None):
        try:
            return data.get(key)
        except KeyError:
            return default

    def get_timzone_convesion(self,time:datetime,req_now=False):
        curr_tz=pytz.timezone(self.current_tz)
        conv_tz=pytz.timezone(self.conversion_tz)
        try:
            if isinstance(time,str):
                time=datetime.fromisoformat(time)

            time=curr_tz.localize(time)
            time=time.astimezone(conv_tz)
            if req_now:
                now = datetime.now(tz=conv_tz)
                return time,now
            return time
        except Exception as e:
            import traceback
            traceback.print_exc()
            return time

    def safe_json(self, response):

        if not response.ok:
            data = response.json()
            raise RMLoginError(self.err_msg(response.status_code,data.get('message') if not data.get('success',False) and data.get('message') is not None else responses[response.status_code]))
        # elif response.json().get('success',False) and response.ok:
        #     data = response.json()
        #     raise RMLoginError(self.err_msg(400,data.get('message') if data.get('message') is not None else responses[response.status_code]))

        try:

            data=response.text
            return json.loads(data)
        except json.JSONDecodeError:
            raise BackendError

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

    def safe_list(self,list,index,default=''):
        try:
            return list[index]
        except IndexError:
            return default

    def err_msg(self,status_code,message):
        return {'status_code':status_code,'message':message}

    def save_session(self, additional_data):
        self.persistor.save_session(self.session, additional_data=additional_data,
                                    timeout=self.DEFAULT_PERSISTOR_EXPIRY)

    def load_sess(self):
        try:
            return self.persistor.load_session(self.session)
        except SessionRetrieveException:
            return False

    def login_query(self):
        payload = login_template(self.to_verify.username,self.to_verify.password)
        respose = self.smart_request('POST', self.login_url, headers=self.headers,json=payload)

        json=self.safe_json(respose)

        self.save_session(additional_data=json.get('data'))

        self.headers['Authorization'] = get_auth_header(json.get('data').get('token'))
        return self.profile_query()

    def profile_query(self):

        response = self.smart_request('GET',self.profile_url,headers=self.headers)

        json = self.safe_json(response)

        return self.extract_profile(data=json)

    def extract_profile(self, **kwargs):

        profile = kwargs.get('data')
        profile['data']['lockResumes'] =kwargs.get('data',{}).get('lockResumes')
        profile_data=profile.pop('data')
        kwargs.clear()
        profile.clear()

        resume=profile_data.get('resume')
        for i in range(3):
            pdf=resume.get('resume'+str(i+1))
            if pdf.strip()!='':
                resume['resume'+str(i+1)]=self.aws_base_url+pdf

        profile_data['resume']=resume

        self.profile = profile_data.copy()

        self.pop_insignificant_keys(profile_data)

        profile_data['branch']=self.safe_list(self.safe_list(self.branches,self.profile['course'],[]),self.profile['branch'])
        profile_data['course']=self.safe_list(self.courses,self.profile['course'])

        profile_data["dob"]=str(self.get_timzone_convesion(self.profile['dob'][:-1]).date())
        profile_data['updatedAt']=str(self.get_timzone_convesion(self.profile['updatedAt'][:-1]).date())

        return profile_data

    def check_previous_session(self):
        session_storage = self.load_sess()
        if not isinstance(session_storage, bool):
            try:
                self.headers['Authorization'] = get_auth_header(session_storage['additional_data']['token'])
            except Exception:
                return False,''

            response = self.profile_query()
            return True,response

        return False, {}

    def get_profile(self):
        status, response = self.check_previous_session()

        if not status:
            return self.login_query()
        else:
            return response

    @classmethod
    def do_login(cls, db_ob, **kwargs):

        obj = cls(db_ob, **kwargs)
        status, response = obj.check_previous_session()

        if not status:
            return obj.login_query()
        else:
            return response


def test():
    applicant = RMLoginManager()
    applicant.username = '2K19/ME/052'
    applicant.password = 'Arzam@123'

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'api-manager-verifier:{}'.format(applicant.username.replace('/', '_')))

    return RMLogin.do_login(applicant, persistor=persistor)


if __name__ == '__main__':
    print(test())
