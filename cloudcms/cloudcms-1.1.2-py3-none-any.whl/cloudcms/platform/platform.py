from . import CloudCMSObject
from ..repository import Repository
from ..project import Project
from ..job import Job
from ..error import JobError

import time

class Platform(CloudCMSObject):

    def __init__(self, client, data):
        super(Platform, self).__init__(client, data)

    def uri(self):
        return ''

    def list_repositories(self):
        uri = self.uri() + '/repositories'
        res = self.client.get(uri)
        return Repository.repository_map(self.client, res['rows'])

    def read_repository(self, repository_id):
        res = self.client.get('/repositories/' + repository_id)
        repository = Repository(self.client, res)
        
        return repository

    def create_repository(self, obj={}):
        uri = self.uri() + '/repositories'
        res = self.client.post(uri, obj)

        repository_id = res['_doc']        
        return self.read_repository(repository_id)

    # Projects
    def read_project(self, projectId):
        uri = self.uri() + '/projects/' + projectId
        res = self.client.get(uri, {})
        return Project(self.client, res)

    def start_create_project(self, obj):
        uri = self.uri() + '/projects/start'
        response = self.client.post(uri, {}, obj)

        return response['_doc']


    # Jobs
    def read_job(self, jobId):
        uri = self.uri() + '/jobs/' + jobId
        res = self.client.get(uri, {})
        return Job(self.client, res)
    
    def query_jobs(self, query, pagination):
        uri = self.uri() + '/jobs/query'
        res = self.client.post(uri, pagination, query)
        return Job.job_map(self.client, res['rows'])

    def kill_job(self, jobId):
        uri = self.uri() + '/jobs/' + jobId + '/kill'
        res = self.client.post(uri, {}, {})
        return Job(self.client, res)

    def wait_for_job_completion(self, jobId):
        
        # Use with caution
        while True:
            job = self.read_job(jobId)
            
            if job.data['state'] == 'FINISHED':
                return job
            elif job.data['state'] == 'ERROR':
                raise JobError(jobId)
            else:
                time.sleep(1)
