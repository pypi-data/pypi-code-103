from localstack.utils.aws import aws_models
qsjTW=super
qsjTX=None
qsjTp=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  qsjTW(LambdaLayer,self).__init__(arn)
  self.cwd=qsjTX
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.qsjTp.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(RDSDatabase,self).__init__(qsjTp,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(RDSCluster,self).__init__(qsjTp,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(AppSyncAPI,self).__init__(qsjTp,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(AmplifyApp,self).__init__(qsjTp,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(ElastiCacheCluster,self).__init__(qsjTp,env=env)
class TransferServer(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(TransferServer,self).__init__(qsjTp,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(CloudFrontDistribution,self).__init__(qsjTp,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,qsjTp,env=qsjTX):
  qsjTW(CodeCommitRepository,self).__init__(qsjTp,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
