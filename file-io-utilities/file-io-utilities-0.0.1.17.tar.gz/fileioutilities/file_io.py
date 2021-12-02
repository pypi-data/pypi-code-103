from abc import ABC, abstractmethod
from .get_arguments import get_argument


class FileIO(ABC):

    def __new__(cls, *args, **kw):
        
        
        if 'storage_type' in kw:
            storage_type = kw['storage_type'].lower()
        elif len(args) > 0:
            storage_type = args[0]
        elif get_argument("webHdfsUrl") is not None:
            storage_type = "hdfs"
        else:
            storage_type = "filesystem"

        # Create a map of all subclasses based on storage type property (present on each subclass)
        subclass_map = {subclass.storage_type: subclass for subclass in cls.__subclasses__()}

        # Select the proper subclass based on
        subclass = subclass_map[storage_type]
        instance = super(FileIO, subclass).__new__(subclass)
        return instance
    
    def __init__(self, storage_type = None):
        super().__init__()

    @abstractmethod
    def upload(self, local_path, remote_path):
        pass

    @abstractmethod
    def download(self, remote_path, local_path):
        pass

