from .abstract_test import AbstractTest
import time

class TestProject(AbstractTest):
    def test_projects(self):
        platform = type(self).platform

        title = 'Test Project ' + str(time.time())
        projectObj = {
            'title': title
        }

        jobId = platform.start_create_project(projectObj)
        platform.wait_for_job_completion(jobId)

        job = platform.read_job(jobId)
        projectId = job.data['created-project-id']

        project = platform.read_project(projectId)
        self.assertEqual(title, project.data['title'])

