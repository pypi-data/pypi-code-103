from abc import ABC, abstractmethod

# test
class ConnectorBase(ABC):
    def __init__(
        self,
        bucket: str = None,
        boto_sess: str = None,
        database: str = None,
        host: str = None,
        user: str = None,
        password: str = None,
        port: int = None,
        uri: str = None,
        logmech: str = None,
        temp_output_prefix: str = "athena/temp/",
        table_suffix: str = None,
        region: str = "us-east-1",
        **kwargs
    ):

        self._bucket = bucket
        self._boto_sess = boto_sess
        self._region = region
        self._database = database
        self._temp_output_prefix = temp_output_prefix
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self._uri = uri
        self._logmech = logmech
        self._table_suffix = table_suffix

    @abstractmethod
    def set_connection(self):
        pass

    @abstractmethod
    def read_sql(self):
        pass

