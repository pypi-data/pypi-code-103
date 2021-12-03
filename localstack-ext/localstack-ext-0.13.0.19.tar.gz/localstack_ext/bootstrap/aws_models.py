from localstack.utils.aws import aws_models
RSXHY=super
RSXHb=None
RSXHn=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  RSXHY(LambdaLayer,self).__init__(arn)
  self.cwd=RSXHb
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.RSXHn.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(RDSDatabase,self).__init__(RSXHn,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(RDSCluster,self).__init__(RSXHn,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(AppSyncAPI,self).__init__(RSXHn,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(AmplifyApp,self).__init__(RSXHn,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(ElastiCacheCluster,self).__init__(RSXHn,env=env)
class TransferServer(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(TransferServer,self).__init__(RSXHn,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(CloudFrontDistribution,self).__init__(RSXHn,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,RSXHn,env=RSXHb):
  RSXHY(CodeCommitRepository,self).__init__(RSXHn,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
