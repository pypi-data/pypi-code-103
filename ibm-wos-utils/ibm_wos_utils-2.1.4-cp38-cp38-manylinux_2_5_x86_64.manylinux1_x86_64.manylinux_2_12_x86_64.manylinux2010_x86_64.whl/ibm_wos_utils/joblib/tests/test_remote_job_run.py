# coding: utf-8

# (C) Copyright IBM Corp. 2019.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from ibm_wos_utils.joblib.clients.hadoop_job_client import HadoopJobClient
from pathlib import Path

class TestRemoteJobRun(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    def test_remote_job(self):
        hdfs_url = 'http://beetle1.fyre.ibm.com:50070'
        livy_url = 'http://audi1.fyre.ibm.com:8998'
        hdfs_file_url = 'hdfs://beetle1.fyre.ibm.com:9000'
        token = '<TOKEN>'
        service_instance_id='00000000-0000-0000-0000-000000000000'
        
        rc = HadoopJobClient(hdfs_file_url, hdfs_url, livy_url, token)
        
        '''
        Following values needs to be replaced in job payload template
            arguments - List of parameters
            job_file_path - Full HDFS path to the job file
            dependency_zip - Full HDFS path to the job dependency zip file
        '''
        params = []
        job_params = {
             'arguments':params,
             'job_file_path':'testing_data/kishore/first_spark_job.py',
             'dependency_zip':['testing_data/kishore/bias.zip', 'testing_data/kishore/bias.zip' ],
            }
        
        my_files = ['/Users/kishorepatel/_Work/2020/BatchScoring/hdfs_job_testing/first_spark_job.py','/Users/kishorepatel/_Work/2020/BatchScoring/hdfs_job_testing/bias.zip']
        rc.upload_job_artifacts(my_files, 'testing_data/kishore')
        
        job_id, job_state = rc.run_job(job_params, background = False)
        
        print('Job State from run_job: ', job_state)
        print('Job id : ', job_id)
        print('Job Status from get_job_status() ', rc.get_job_status(job_id))
        
        src_file_path = 'testing_data/kishore/first_spark_job.py'
        tgt_file_path = './first_spark_job.py'
        #Reads the src_file_path and write the output to tgt_file_path
        rc.get_job_output('my_JOB_ID',src_file_path, tgt_file_path ) 

if __name__ == '__main__':
    unittest.main()
