import redis
from data_verifier.utils.persist_cookies import PersistCookies
from data_verifier.model.rm_model import RMLoginManager
from data_verifier.identities.rm_internships.jobs.job_list import RMJobs


class RMApplication(RMJobs):
    application_url = "https://rm.dtu.ac.in/api/application/myApplications"
    progress_url = 'https://rm.dtu.ac.in/api/company/progressPost?jobId={}'

    def __init__(self, to_verify, **kwargs):
        super().__init__(to_verify, **kwargs)
        self.applications = []
        self.applied_job_ids = []
        self.notif = self.safe_dict(kwargs, 'notif', False)
        self.alert = self.safe_dict(kwargs, 'alert', False)
        self.get_jobs()

    def jobs_query(self):
        response = self.smart_request('GET', self.application_url, headers=self.headers)
        json = self.safe_json(response)

        return self.extract_jobs(json.get('data'))

    def extract_jobs(self, jobs):
        for i in jobs:
            self.applied_job_ids.append(i.get('post').get('_id'))

        if self.alert:
            for i in self.job_filter_list:
                if i.get('_id') in self.applied_job_ids:
                    self.job_filter_list.pop(self.job_filter_list.index(i))
                else:
                    if not (60 < i.get('seconds') < 3600):
                        self.job_filter_list.pop(self.job_filter_list.index(i))

            return self.job_filter_list

        # if self.notif:
        #     nofifi = dict()
        #     for i in self.notifications:
        #         if i.get('jobPost') in self.applied_job_ids:
        #             response = self.smart_request('GET', self.progress_url.format(i.get('jobPost')),
        #                                           headers=self.headers)
        #             if response.ok:
        #                 nofifi[i.get('jobPost')] = self.safe_json(response).get('data', [])
        #
        #     import time
        #     print(time.time() - self.start)
        #     return nofifi

        for i in self.jobs:
            if i.get('_id') in self.applied_job_ids:
                try:
                    indx = self.applied_job_ids.index(i.get('_id'))
                    i['status'] = jobs[indx].get('status')
                    i.pop('remaining_time')
                    # i['createdAt'] = str(self.get_timzone_convesion(i.pop('createdAt')[:-1])).split('.')[0]
                    # i['updatedAt'] = str(self.get_timzone_convesion(i.pop('updatedAt')[:-1])).split('.')[0]
                except Exception as e:
                    break
                self.applied_job_ids.pop(indx)
                self.applied_job_ids.insert(indx, i)

        for i in self.applied_job_ids:
            if not isinstance(i,dict):
                self.applied_job_ids.pop(self.applied_job_ids.index(i))


        if self.notif:
            nofifi = list()
            for i in self.applied_job_ids:
                if i.get('status','').lower()=="applied":
                    response = self.smart_request('GET', self.progress_url.format(i.get('_id')),
                                                  headers=self.headers)
                    if response.ok:
                        value=self.safe_json(response).get('data', [])
                        for j in range(len(value)):
                            value[j]['created_at'] = str(
                                self.get_timzone_convesion(value[j].pop('createdAt')[:-1]).date())
                            value[j]['updated_at'] = str(
                                self.get_timzone_convesion(value[j].pop('updatedAt')[:-1]).date())
                            value[j]['event_date'] = str(
                                self.get_timzone_convesion(value[j].pop('eventDate')[:-1]).date())

                        data={'name':i.get('name'),'company':i.get('company',{}).get('name'),'ctc':i.get('ctc'),
                              'job_desc':i.get('jobDescription'),'location':i.get('location'),'progress':value}

                        nofifi.append(data)
            return nofifi

        return self.filter_branch_name(self.applied_job_ids)

    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        return cls(db_ob, **kwargs).jobs_query()


def test():
    applicant = RMLoginManager()
    applicant.username = '2K19/ME/051'
    applicant.password = 'April@2000'

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'api-manager-verifier:{}'.format(applicant.username.replace('/', '_')))

    data= RMApplication.extract_data(applicant, persistor=persistor,alert=True)

    return data

if __name__ == '__main__':
    print(test())
    # test()
