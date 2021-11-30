# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod

 
class Client(ABC):
    
    """
    Abstract class for all Spark job related actions
    """
    
    @abstractmethod
    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True):
        '''
        - Upload data_file_list
        - Push entry job if it is not already pushed
        - compose job payload
        - run the job (Jobs will be available in wos_utils package
        '''
        pass
    
    @abstractmethod
    def get_job_status(self, job_id):
        pass
    
    @abstractmethod
    def get_file(self,file_path):
        pass

    @abstractmethod
    def get_exception(self, output_file_path):
        pass
    
    @abstractmethod
    def get_job_logs(self, job_id):
        pass
    
    @abstractmethod
    def delete_job_artifacts(self, job_id):
        pass
    
    @abstractmethod
    def kill_job(self, job_id):
        pass
    
    def __upload_job_artifacts(self, files_list, target_folder, overwrite = True):
        pass
    
    
    
   
    