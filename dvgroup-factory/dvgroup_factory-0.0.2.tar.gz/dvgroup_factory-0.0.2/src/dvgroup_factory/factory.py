import os
import time

from singleton_decorator import singleton
import hvac
import consulate
import json
import clickhouse_driver as ch_d
from kafka import KafkaProducer, KafkaConsumer
from azure.storage.blob import BlobClient, ContainerClient
import logging_loki
import logging
import functools
import datetime


def log(_func=None, *, logger = None):
    def decorator_dvglog(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if logger is None:
                cust_logger = logging.Logger(__name__)
                sh = logging.StreamHandler()
                sh.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                sh.setFormatter(formatter)
                cust_logger.addHandler(sh)
            else:
                cust_logger = logger
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cust_logger.debug(f"function {func.__name__} called with args {signature}")
            try:
                tst = datetime.datetime.utcnow()
                result = func(*args, **kwargs)
                cust_logger.debug(f"Work time of function {func.__name__} = {datetime.datetime.utcnow() - tst}")
                return result
            except Exception as e:
                cust_logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise e
        return wrapper
    if _func is None:
        return decorator_dvglog
    else:
        return decorator_dvglog(_func)


def retry(_func=None, *, num_retry = 10, sleep_s = 0.5):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cnt = num_retry
            while True:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    cnt -= 1
                    if cnt <=0:
                        raise e
                    if sleep_s > 0:
                        time.sleep(sleep_s)
        return wrapper
    if _func is None:
        return decorator_retry
    else:
        return decorator_retry(_func)

logger = logging.getLogger(__name__)

@singleton
class Factory:

    def __init__(self, vault_url=None, vault_token=None):
        self.__consul_keys = {"clickhouse": "env/databases/clickhouse",
                         "kafka": "env/databases/kafka",
                         "ms-azure-se": "env/databases/ms-azure-se",
                         "loki": "env/databases/loki"}
        self.__services = {"consul": [], "kafka_producer": [], "kafka_consumer": [], "clickhouse_client": [],
                      "azure_container_client": [], "azure_blob_client": [], "loki_handler": []}
        if vault_url is None:
            self.vault_url = os.getenv("VAULT_URL")
        else:
            self.vault_url = vault_url
        if vault_token is None:
            self.vault_token = os.getenv("VAULT_TOKEN")
        else:
            self.vault_token = vault_token
        self.vault = self.vault_client(url=self.vault_url, token=self.vault_token)
        self.secrets = self.init_secrets()
        self.config = self.init_config()


    def info(self) -> str:
        s = "Класс Factory\n"
        s += 'Создание экземпляра:\n ins = Factory(vault_url=url, vault_token=token)\n'
        s += "Методы: \n" + "1 ins.vault_client(url: str, token: str)\n"
        for i, k in enumerate(self.__services.keys()):
            s += str(i+2)+" "+"ins."+k +"(**kwargs)\n"
        s += "Для создания нового экземпляра укажите в kwargs: new=True\n"
        s += "\n"
        s += "Пути настроек в consul:\n"
        s += json.dumps(self.__consul_keys)
        return s

    @retry
    def init_secrets(self) -> dict:
        rs = {}
        for service in list(self.__consul_keys.keys())+["consul"]:
            rs[service] = self._get_secrets(service)
        return rs

    @retry
    def init_config(self):
        rs = {}
        for service in self.__consul_keys.keys():
            rs[service] = self.get_config_from_consul(service)
        return rs

    def comon_factory__4_del(self, service_name, factory, *args, **kwargs):
        if len(self.__services[service_name])==0 or (("new" in kwargs) and (kwargs["new"])):
            if len(args) == 0:
                k_p = factory(**kwargs)
            else:
                k_p = factory(*args, **kwargs)
            self.__services[service_name].append(k_p)
        return self.__services[service_name][-1]

    def comon_factory(self, service_name, **kwargs):
        if len(self.__services[service_name]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            return None
        return self.__services[service_name][-1]

    @retry
    def vault_client(self, url: str, token: str) -> hvac.Client:
        vault = hvac.Client(url=url, token=token)
        return vault

    @retry
    def _get_secrets(self, service: str) -> dict:
        ret = self.vault.secrets.kv.v2.read_secret_version(path=service)["data"]["data"]
        return ret

    @retry
    def consul(self, **kwargs):
        if len(self.__services["consul"]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            if "new" in kwargs.keys():
                del kwargs["new"]
            c_s = self.secrets["consul"]
            self.__services["consul"].append(consulate.Consul(host=c_s["url"], port=c_s["port"], token=c_s["backend_token"], **kwargs))
        return self.__services["consul"][-1]


    def get_config_from_consul(self, service):
        cnsl = self.consul()
        config = cnsl.kv[self.__consul_keys[service]]
        config = json.loads(config)
        return config

    def clickhouse_client(self, **kwargs):
        if len(self.__services["clickhouse_client"]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            scrts = self.secrets["clickhouse"]
            cnfg = self.config["clickhouse"]
            if "new" in kwargs.keys():
                del kwargs["new"]
            ch = ch_d.Client(cnfg["url"], port=cnfg["port"], user=scrts["user"],
                             password=scrts["password"], secure=True, verify=False, **kwargs) #, ca_certs=scrts["pem"]
            self.__services["clickhouse_client"].append(ch)
        return self.__services["clickhouse_client"][-1]

    def kafka_producer(self, **kwargs):
        if len(self.__services["kafka_producer"]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            if "new" in kwargs.keys():
                del kwargs["new"]
            scrts = self.secrets["kafka"]
            cnfg = self.config["kafka"]
            #with open("tmp_cafile.tmp", "w") as f:
            #    f.write(scrts["pem"])
            k_p = KafkaProducer(bootstrap_servers=cnfg["url"], security_protocol="SSL", **kwargs)
            #try:
            #    os.remove("tmp_cafile.tmp")
            #except:
            #    pass
            self.__services["kafka_producer"].append(k_p)
        return self.__services["kafka_producer"][-1]

    def kafka_consumer(self, **kwargs):
        if len(self.__services["kafka_consumer"]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            if "new" in kwargs.keys():
                del kwargs["new"]
            scrts = self.secrets["kafka"]
            cnfg = self.config["kafka"]
            #with open("tmp_cafile.tmp", "w") as f:
            #    f.write(scrts["pem"])
            k_p = KafkaConsumer(bootstrap_servers=cnfg["url"], security_protocol="SSL", **kwargs)
            #try:
            #    os.remove("tmp_cafile.tmp")
            #except:
            #    pass
            self.__services["kafka_consumer"].append(k_p)
        return self.__services["kafka_consumer"][-1]

    def azure_container_client_old(self, **kwargs):
        if len(self.__services["azure_container_client"]) == 0 or (("new" in kwargs) and (kwargs["new"])):
            if "new" in kwargs.keys():
                del kwargs["new"]
            scrts = self.secrets["ms-azure-se"]
            cnfg = self.config["ms-azure-se"]
            k_p = ContainerClient(account_url=cnfg["account_url"], AccountName=scrts["AccountName"], AccountKey=scrts["AccountKey"], **kwargs)
            self.__services["azure_container_client"].append(k_p)
        return self.__services["azure_container_client"][-1]

    def azure_container_client(self,**kwargs):
        srvc = self.comon_factory("azure_container_client", **kwargs)
        if srvc is not None:
            return srvc
        if "new" in kwargs.keys():
            del kwargs["new"]
        cs = self.get_cs4azure()
        srvc = ContainerClient.from_connection_string(conn_str=cs, **kwargs)
        self.__services["azure_container_client"].append(srvc)
        return self.__services["azure_container_client"][-1]

    def azure_blob_client(self, **kwargs):
        srvc = self.comon_factory("azure_blob_client", **kwargs)
        if srvc is not None:
            return srvc
        if "new" in kwargs.keys():
            del kwargs["new"]
        cs = self.get_cs4azure()
        srvc = BlobClient.from_connection_string(conn_str=cs, **kwargs)
        self.__services["azure_blob_client"].append(srvc)
        return self.__services["azure_blob_client"][-1]

    def get_cs4azure(self):
        cs = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net"
        cs += ";AccountName=" + self.secrets["ms-azure-se"]["AccountName"]
        cs += ";AccountKey=" + self.secrets["ms-azure-se"]["AccountKey"]
        return cs

    def loki_handler(self, **kwargs):
        srvc = self.comon_factory("loki_handler", **kwargs)
        if srvc is not None:
            return srvc
        if "new" in kwargs.keys():
            del kwargs["new"]
        srvc = logging_loki.LokiHandler(url=self.config["loki"]["url"], auth=(self.secrets["loki"]["user"], self.secrets["loki"]["password"]),**kwargs)
        self.__services["loki_handler"].append(srvc)
        return self.__services["loki_handler"][-1]



