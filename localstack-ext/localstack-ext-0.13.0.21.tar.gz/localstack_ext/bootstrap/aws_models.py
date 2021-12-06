from localstack.utils.aws import aws_models
YavyJ=super
YavyO=None
YavyK=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  YavyJ(LambdaLayer,self).__init__(arn)
  self.cwd=YavyO
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.YavyK.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(RDSDatabase,self).__init__(YavyK,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(RDSCluster,self).__init__(YavyK,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(AppSyncAPI,self).__init__(YavyK,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(AmplifyApp,self).__init__(YavyK,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(ElastiCacheCluster,self).__init__(YavyK,env=env)
class TransferServer(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(TransferServer,self).__init__(YavyK,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(CloudFrontDistribution,self).__init__(YavyK,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,YavyK,env=YavyO):
  YavyJ(CodeCommitRepository,self).__init__(YavyK,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
