import os
import shutil

from hdfs import InsecureClient
from .file_io import FileIO
from .get_arguments import get_argument
from zipfile import ZipFile


class Hdfs(FileIO):

    storage_type = os.path.basename(__file__).split('.py')[0]
    
    def __init__(self, storage_type=None):
        super().__init__()
        self.web_hdfs_url = get_argument('webHdfsUrl')

    def upload(self, local_path, remote_path, overwrite=True):

        output_zip = remote_path.split("/")[-1] + ".zip"
        self.zip_file(local_path, output_zip)

        # Upload model and zipped model to HDFS
        client = InsecureClient(self.web_hdfs_url)
        client.upload(remote_path, local_path, overwrite=overwrite, temp_dir="/tmp")
        client.upload(remote_path + ".zip", output_zip, overwrite=overwrite, temp_dir="/tmp")

    def download(self, remote_path, local_path, overwrite=True):
        # Dowload model from HDFS to disk
        client = InsecureClient(self.web_hdfs_url)
        client.download(remote_path, local_path, overwrite=overwrite, temp_dir="/tmp")

    @staticmethod
    def zip_file(local_path, output_zip):

        # Zip the file/directory to upload

        if os.path.isdir(local_path):

            shutil.make_archive(local_path, 'zip', local_path)

        else:  # it's a file

            ZipFile(output_zip, mode='w').write(local_path)
