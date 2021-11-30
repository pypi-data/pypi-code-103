from localstack.utils.aws import aws_models
aITgV=super
aITgm=None
aITgA=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  aITgV(LambdaLayer,self).__init__(arn)
  self.cwd=aITgm
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.aITgA.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(RDSDatabase,self).__init__(aITgA,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(RDSCluster,self).__init__(aITgA,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(AppSyncAPI,self).__init__(aITgA,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(AmplifyApp,self).__init__(aITgA,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(ElastiCacheCluster,self).__init__(aITgA,env=env)
class TransferServer(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(TransferServer,self).__init__(aITgA,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(CloudFrontDistribution,self).__init__(aITgA,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,aITgA,env=aITgm):
  aITgV(CodeCommitRepository,self).__init__(aITgA,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
