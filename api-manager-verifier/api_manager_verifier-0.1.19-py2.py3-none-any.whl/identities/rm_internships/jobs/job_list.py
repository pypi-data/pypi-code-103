import redis
import datetime
from data_verifier.utils.persist_cookies import PersistCookies
from data_verifier.identities.rm_internships.login.rm_login import RMLogin
from data_verifier.model.rm_model import RMLoginManager


class RMJobs(RMLogin):
    job_url = 'https://rm.dtu.ac.in/api/company/jobPost?page={}'
    notif_url = 'https://rm.dtu.ac.in/api/student/notifications?page={}'

    ALERT_TIME_LIMIT = 60

    INSIGNIFICANT_KEYS = ['email', 'createdAt', 'handledBy', 'updatedAt', '__v']

    def __init__(self, to_verify, **kwargs):
        super(RMJobs, self).__init__(to_verify, **kwargs)
        self.jobs = []
        self.job_filter_list = []
        # self.notifications=[]
        self.all_open_jobs = self.safe_dict(kwargs, 'all_open_jobs', False)
        self.open_jobs = self.safe_dict(kwargs, 'open_jobs', False)
        self.all_jobs = self.safe_dict(kwargs, 'all_jobs', False)
        self.get_profile()

    def filter_by_open(self):
        for i in self.jobs:

            open_date = self.get_timzone_convesion(datetime.datetime.fromisoformat(i.get('applicationOpen')[:-1]))
            close_date, now = self.get_timzone_convesion(
                datetime.datetime.fromisoformat(i.get('applicationClosed')[:-1]), True)

            index = self.jobs.index(i)
            i.pop('__v')
            if (close_date - now).total_seconds() > 60:
                diff = (close_date - now)
                i['applicationOpen'] = str(open_date.date())
                i['applicationClosed'] = str(close_date.date())
                i['remaining_time'] = diff
                i['created_at'] = str(self.get_timzone_convesion(i.pop('createdAt')[:-1]).date())
                i['updated_at'] = str(self.get_timzone_convesion(i.pop('updatedAt')[:-1]).date())
                i['seconds'] = diff.total_seconds()
                i['status'] = True
                self.job_filter_list.append(i)
            else:
                i['applicationOpen'] = str(open_date.date())
                i['applicationClosed'] = str(close_date.date())
                i['created_at'] = str(self.get_timzone_convesion(i.pop('createdAt')[:-1]).date())
                i['updated_at'] = str(self.get_timzone_convesion(i.pop('updatedAt')[:-1]).date())
                i['status'] = False

            self.jobs[index] = i

    def filter_job(self, index):

        if len(self.job_filter_list ) == 0 or index>5:
            return

        course = self.profile.get('course')
        branch = self.profile.get('branch')
        i=0
        while(i<len(self.job_filter_list)):
            course_name = self.courses[course].lower()
            if index == 0:
                if not self.job_filter_list[i].get(course_name):
                    self.job_filter_list.pop(i)
                    continue

            elif index == 1:
                if self.safe_list(self.branches, course, None) is not None:
                    if not branch in self.job_filter_list[i].get(course_name.lower() + 'Branches'):
                        self.job_filter_list.pop(i)
                        continue

            elif index == 2:
                aggr_cgpa = self.profile.get('aggregateCgpa')
                cutoff = self.job_filter_list[i].get(course_name.lower() + 'Cutoff')
                cutoff = cutoff if 0 <= cutoff <= 10 else 0
                if aggr_cgpa < cutoff:
                    self.job_filter_list.pop(i)
                    continue

            elif index == 3:
                twelth = self.profile.get('twelfthClass').get('percentage') * 9.5 if self.profile.get(
                    'twelfthClass').get(
                    'percentage') <= 10 else self.profile.get('twelfthClass').get('percentage')
                tenth = self.profile.get('tenthClass').get('percentage') * 9.5 if self.profile.get('tenthClass').get(
                    'percentage') <= 10 else self.profile.get('tenthClass').get('percentage')

                if tenth < self.job_filter_list[i].get('tenthPercentageCutoff') if self.job_filter_list[i].get('tenthPercentageCutoff') is not None else 0:
                    self.job_filter_list.pop(i)
                    continue
                elif twelth < self.job_filter_list[i].get('twelfthPercentageCutoff') if self.job_filter_list[i].get('twelfthPercentageCutoff') is not None else 0:
                    self.job_filter_list.pop(i)
                    continue

            elif index == 4:
                if self.job_filter_list[i].get('genderOpen') != "Both":
                    if self.job_filter_list[i].get('genderOpen', '').lower() != self.profile.get('gender', '').lower():
                        self.job_filter_list.pop(i)
                        continue

            elif index == 5:
                if self.job_filter_list[i].get('pwdOnly') and not self.profile.get('pwd'):
                    self.job_filter_list.pop(i)
                    continue

            i+=1

        self.filter_job(index + 1)

    def pre_query(self):
        # useless piece of code as taking much longer time to run

        # for i in range(100):
        #     response=self.smart_request('GET',self.notif_url.format(i+1),headers=self.headers)
        #     json = self.safe_json(response)
        #     if len(json.get('data'))==0:
        #         break
        #
        #     self.notifications.extend(json.get('data'))

        return self.query_info()

    def query_info(self):

        # for i in range(100):
        response = self.smart_request('GET', self.job_url.format(1), headers=self.headers)
        json = self.safe_json(response)
            # print("running loop: ",i+1)
            # print(json)
            # if len(json.get('data')) == 0:
            #     break

        self.jobs.extend(json.get('data'))

        return self.extract_info()

    def filter_branch_name(self, job_lst):
        jobs = []
        for i in job_lst:
            for j, v in enumerate(self.courses):
                if i.get(v.lower()):
                    branches = []
                    try:
                        for k in i.get(v.lower() + 'Branches'):
                            val = self.safe_list(self.safe_list(self.branches, j, []), k)
                            if val != "":
                                branches.append(val)
                    except:
                        continue
                    i[v.lower() + 'Branches'] = branches
            jobs.append(i)

        return jobs

    def filter_output(self, index=0):
        if index == 0:
            for i in self.jobs:
                indx = self.jobs.index(i)
                i['remaining_time'] = str(i.get('remaining_time', 0))
                self.jobs[indx] = i
        else:
            for i in self.job_filter_list:
                indx = self.job_filter_list.index(i)
                i['remaining_time'] = str(i.get('remaining_time'))
                self.job_filter_list[indx] = i

    def extract_info(self, **kwargs):
        self.filter_by_open()

        course = self.profile.get('course')
        branch = self.profile.get('branch')

        # this will return details of all the open jobs irrespective user branch, marks etc
        if self.all_open_jobs:
            self.filter_output(1)
            job = self.filter_branch_name(self.job_filter_list)
            return {'course': self.courses[course],
                    'branch': self.safe_list(self.safe_list(self.branches, course, []), branch), 'job_list': job}

        # this will filter job with respect to details
        self.filter_job(0)

        # this will return final open jobs that fits critera set by job poster
        if self.open_jobs:
            self.filter_output(1)
            job = self.filter_branch_name(self.job_filter_list)
            return {'course': self.courses[course],
                    'branch': self.safe_list(self.safe_list(self.branches, course, []), branch), 'job_list': job}

        # list of all the jobs irrespective of filters and open and closed both
        if self.all_jobs:
            self.filter_output(0)
            job = self.filter_branch_name(self.jobs)
            return {'course': self.courses[course],
                    'branch': self.safe_list(self.safe_list(self.branches, course, []), branch), 'job_list': job}

        self.filter_output(0)
        return self.jobs

    def get_jobs(self):
        return self.pre_query()

    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        return cls(db_ob, **kwargs).pre_query()


def test():
    applicant = RMLoginManager()
    applicant.username = '2K19/ME/051'
    applicant.password = 'April@2000'

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'api-manager-verifier:{}'.format(applicant.username.replace('/', '_')))

    data= RMJobs.extract_data(applicant, persistor=persistor, open_jobs=True)

    return data


if __name__ == '__main__':
    print(test())
