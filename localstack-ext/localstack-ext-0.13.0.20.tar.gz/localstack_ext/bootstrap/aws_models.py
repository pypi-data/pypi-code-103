from localstack.utils.aws import aws_models
pVoIg=super
pVoIl=None
pVoIP=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  pVoIg(LambdaLayer,self).__init__(arn)
  self.cwd=pVoIl
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.pVoIP.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(RDSDatabase,self).__init__(pVoIP,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(RDSCluster,self).__init__(pVoIP,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(AppSyncAPI,self).__init__(pVoIP,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(AmplifyApp,self).__init__(pVoIP,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(ElastiCacheCluster,self).__init__(pVoIP,env=env)
class TransferServer(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(TransferServer,self).__init__(pVoIP,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(CloudFrontDistribution,self).__init__(pVoIP,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,pVoIP,env=pVoIl):
  pVoIg(CodeCommitRepository,self).__init__(pVoIP,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
