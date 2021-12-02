import os
from hdfs import InsecureClient
from .file_io import FileIO
from .get_arguments import get_argument



class Hdfs(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]
    
    def __init__(self, storage_type=None):
        super().__init__()
        self.web_hdfs_url = get_argument('webHdfsUrl')

    def upload(self, local_path, remote_path, overwrite=True):
        # Upload model to HDFS
        client = InsecureClient(self.web_hdfs_url)
        client.upload(remote_path, local_path, overwrite=overwrite, temp_dir="/tmp")

    def download(self, remote_path, local_path, overwrite=True):
        # Dowload model from HDFS to disk
        client = InsecureClient(self.web_hdfs_url)
        client.download(remote_path, local_path, overwrite=overwrite, temp_dir="/tmp")
