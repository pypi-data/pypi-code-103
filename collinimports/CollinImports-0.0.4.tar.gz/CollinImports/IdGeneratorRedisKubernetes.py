import redis
import os
import itertools

class IdGeneratorRedis():
    def __init__(self):
        self.NamespaceWrapperMap = {}
        self.MasterService = redis.Redis(
            host=os.environ.get('REDIS_MASTER_SERVICE_HOST'),
            port=os.environ.get('REDIS_MASTER_SERVICE_PORT'),
            password=os.environ.get('REDIS_PASSWORD'))
        self.ReplicaService = redis.Redis(
            host=os.environ.get('REDIS_REPLICAS_SERVICE_HOST'),
            port=os.environ.get('REDIS_REPLICAS_SERVICE_PORT'),
            password=os.environ.get('REDIS_PASSWORD'))

    class NamespaceWrapper():
        def __init__(self,namespace):
            self.Namespace = namespace
            self.MasterService = redis.Redis(
                host=os.environ.get('REDIS_MASTER_SERVICE_HOST'),
                port=os.environ.get('REDIS_MASTER_SERVICE_PORT'),
                password=os.environ.get('REDIS_PASSWORD'))
            self.ReplicaService = redis.Redis(
                host=os.environ.get('REDIS_REPLICAS_SERVICE_HOST'),
                port=os.environ.get('REDIS_REPLICAS_SERVICE_PORT'),
                password=os.environ.get('REDIS_PASSWORD'))
            self.CurrentId = 0

        def __getitem__(self,query):
            query = self.Namespace+':'+query
            try: 
                return self.ReplicaService.get(query).decode('utf8')
            except: 
                self.MasterService.set(query,self.CurrentId)
                self.CurrentId += 1
                return str(self.CurrentId-1)

    def __getitem__(self,query):
        try: 
            return self.NamespaceWrapperMap[query]
        except: 
            self.NamespaceWrapperMap[query] = self.NamespaceWrapper(query)
            return self.NamespaceWrapperMap[query]

    def DeleteNamespace(self,namespace):
        def batcher(iterable, n):
            iterable = iter(iterable)
            try:
                while True:
                    yield itertools.chain((next(iterable),), itertools.islice(iterable, n-1))
            except StopIteration:
                return
        for keybatch in batcher(self.ReplicaService.scan_iter(namespace+':*'), 500):
            self.MasterService.delete( * keybatch)
