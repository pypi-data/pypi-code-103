from localstack.utils.aws import aws_models
KfESW=super
KfESh=None
KfESL=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  KfESW(LambdaLayer,self).__init__(arn)
  self.cwd=KfESh
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.KfESL.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(RDSDatabase,self).__init__(KfESL,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(RDSCluster,self).__init__(KfESL,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(AppSyncAPI,self).__init__(KfESL,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(AmplifyApp,self).__init__(KfESL,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(ElastiCacheCluster,self).__init__(KfESL,env=env)
class TransferServer(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(TransferServer,self).__init__(KfESL,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(CloudFrontDistribution,self).__init__(KfESL,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,KfESL,env=KfESh):
  KfESW(CodeCommitRepository,self).__init__(KfESL,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
