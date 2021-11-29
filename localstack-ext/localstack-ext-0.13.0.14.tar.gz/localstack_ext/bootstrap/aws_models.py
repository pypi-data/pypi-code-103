from localstack.utils.aws import aws_models
GyTHs=super
GyTHl=None
GyTHL=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  GyTHs(LambdaLayer,self).__init__(arn)
  self.cwd=GyTHl
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.GyTHL.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(RDSDatabase,self).__init__(GyTHL,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(RDSCluster,self).__init__(GyTHL,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(AppSyncAPI,self).__init__(GyTHL,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(AmplifyApp,self).__init__(GyTHL,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(ElastiCacheCluster,self).__init__(GyTHL,env=env)
class TransferServer(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(TransferServer,self).__init__(GyTHL,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(CloudFrontDistribution,self).__init__(GyTHL,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,GyTHL,env=GyTHl):
  GyTHs(CodeCommitRepository,self).__init__(GyTHL,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
