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
                try:
                    factory = Factory()
                    l_h = factory.loki_handler(tags={"application": "log-decorator"}, version="1")
                    l_h.setLevel(logging.DEBUG)
                    l_h.setFormatter(formatter)
                    cust_logger.addHandler(l_h)
                except:
                    pass
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


def retry(_func=None, *, num_retry = 1, sleep_s = 0.1):
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
    def_instance_name = "default"
    key_new = "new"
    key_istance_name = "instance_name"
    def __init__(self, vault_url=None, vault_token=None):
        self.__consul_keys = {"clickhouse": "env/databases/clickhouse",
                         "kafka": "env/databases/kafka",
                         "ms-azure-se": "env/databases/ms-azure-se",
                         "loki": "env/databases/loki"}
        self.__services = {"consul": {}, "kafka_producer": {}, "kafka_consumer": {}, "clickhouse_client": {},
                      "azure_container_client": {}, "azure_blob_client": {}, "loki_handler": {}}
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
        s += "Для создания именнованного экземпляра укажите в kwargs: instance_name='Имя экземпляра'\n"
        s += "\n"
        s += "Пути настроек в consul:\n"
        s += json.dumps(self.__consul_keys)
        return s

    def init_secrets(self) -> dict:
        rs = {}
        for service in list(self.__consul_keys.keys())+["consul"]:
            rs[service] = self._get_secrets(service)
        return rs

    def init_config(self):
        rs = {}
        for service in self.__consul_keys.keys():
            rs[service] = self.get_config_from_consul(service)
        return rs

    def delete_from_kwargs(self, kwargs):
        if self.key_new in kwargs:
            del kwargs[self.key_new]
        if self.key_istance_name in kwargs:
            del kwargs[self.key_istance_name]
        return kwargs

    def get_instance(self, service_builder, service_name, instance_name, args=[], kwargs={}):
        if (not self.key_new in kwargs) and (not instance_name in self.__services[service_name]):
            kwargs = self.delete_from_kwargs(kwargs)
            inst = service_builder(*args, **kwargs)
            self.__services[service_name][instance_name] = inst
        return self.__services[service_name][instance_name]

    def vault_client(self, url: str, token: str) -> hvac.Client:
        vault = hvac.Client(url=url, token=token)
        return vault

    def _get_secrets(self, service: str) -> dict:
        ret = self.vault.secrets.kv.v2.read_secret_version(path=service)["data"]["data"]
        return ret

    def get_config_from_consul(self, service):
        cnsl = self.consul(instance_name="in_uses_for_factory")
        config = cnsl.kv[self.__consul_keys[service]]
        config = json.loads(config)
        return config

    def consul(self, **kwargs):
        service_name = "consul"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        scrts = self.secrets["consul"]
        kwargs["host"] = scrts["url"] if not "url" in kwargs else kwargs["url"]
        kwargs["port"] = scrts["port"] if not "port" in kwargs else kwargs["port"]
        kwargs["token"] = scrts["backend_token"] if not "token" in kwargs else kwargs["token"]
        return self.get_instance(consulate.Consul, service_name, instance_name, [], kwargs)

    def clickhouse_client(self, **kwargs):
        service_name = "clickhouse_client"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        scrts = self.secrets["clickhouse"]
        cnfg = self.config["clickhouse"]
        args = []
        args.append(cnfg["url"] if "url" not in kwargs else kwargs["url"])
        kwargs["port"] = cnfg["port"] if not ("port" in kwargs) else kwargs["port"]
        kwargs["user"] = scrts["user"] if not ("user" in kwargs) else kwargs["user"]
        kwargs["password"] = scrts["password"] if not ("password" in kwargs) else kwargs["password"]
        kwargs["secure"] = True if "secure" not in kwargs else kwargs["secure"]
        kwargs["verify"] = False if "verify" not in kwargs else kwargs["verify"]
        return self.get_instance(ch_d.Client, service_name, instance_name, args, kwargs)

    def kafka_producer(self, **kwargs):
        service_name = "kafka_producer"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        scrts = self.secrets["kafka"]
        cnfg = self.config["kafka"]
        if "ssl_cafile" not in kwargs:
            filename = os.getcwd() + service_name+"_"+instance_name+".pem"
            if not os.path.exists(filename):
                with open(filename, "w") as f:
                    pass
                    f.write(scrts["pem"])
            kwargs["ssl_cafile"] = filename
        kwargs["bootstrap_servers"] = cnfg["url"] if "url" not in kwargs else kwargs["url"]
        kwargs["security_protocol"] = "SSL" if "security_protocol" not in kwargs else kwargs["security_protocol"]
        return self.get_instance(KafkaProducer, service_name, instance_name, [], kwargs)

    def kafka_consumer(self, **kwargs):
        service_name = "kafka_consumer"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        scrts = self.secrets["kafka"]
        cnfg = self.config["kafka"]
        if "ssl_cafile" not in kwargs:
            filename = os.getcwd() + service_name+"_"+instance_name+".pem"
            if not os.path.exists(filename):
                with open(filename, "w") as f:
                    pass
                    f.write(scrts["pem"])
            kwargs["ssl_cafile"] = filename
        kwargs["bootstrap_servers"] = cnfg["url"] if "url" not in kwargs else kwargs["url"]
        kwargs["security_protocol"] = "SSL" if "security_protocol" not in kwargs else kwargs["security_protocol"]
        return self.get_instance(KafkaConsumer, service_name, instance_name, [], kwargs)

    def azure_container_client(self,**kwargs):
        service_name = "azure_container_client"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        if "conn_str" not in kwargs:
            scrts = self.secrets["ms-azure-se"]
            cnfg = self.config["ms-azure-se"]
            account_name = scrts["AccountName"]
            account_key = scrts["AccountKey"]
            kwargs["conn_str"] = self.get_cs4azure(account_name, account_key)
        return self.get_instance(ContainerClient.from_connection_string, service_name, instance_name, [], kwargs)

    def azure_blob_client(self, **kwargs):
        service_name = "azure_blob_client"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        if "conn_str" not in kwargs:
            scrts = self.secrets["ms-azure-se"]
            cnfg = self.config["ms-azure-se"]
            account_name = scrts["AccountName"]
            account_key = scrts["AccountKey"]
            kwargs["conn_str"] = self.get_cs4azure(account_name, account_key)
        return self.get_instance(BlobClient.from_connection_string, service_name, instance_name, [], kwargs)

    def get_cs4azure(self, account_name, account_key):
        cs = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net"
        cs += ";AccountName=" + account_name
        cs += ";AccountKey=" + account_key
        return cs

    def loki_handler(self, **kwargs):
        service_name = "loki_handler"
        instance_name = self.def_instance_name if not self.key_istance_name in kwargs else kwargs[self.key_istance_name]
        scrts = self.secrets["loki"]
        cnfg = self.config["loki"]
        kwargs["url"] = cnfg["url"] if not "url" in kwargs else kwargs["url"]
        kwargs["auth"] = (scrts["user"], scrts["password"]) if not "auth" in kwargs else kwargs["auth"]
        return self.get_instance(logging_loki.LokiHandler, service_name, instance_name, [], kwargs)




