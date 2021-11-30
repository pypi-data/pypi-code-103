from localstack.utils.aws import aws_models
GxJzr=super
GxJzb=None
GxJzC=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  GxJzr(LambdaLayer,self).__init__(arn)
  self.cwd=GxJzb
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.GxJzC.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(RDSDatabase,self).__init__(GxJzC,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(RDSCluster,self).__init__(GxJzC,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(AppSyncAPI,self).__init__(GxJzC,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(AmplifyApp,self).__init__(GxJzC,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(ElastiCacheCluster,self).__init__(GxJzC,env=env)
class TransferServer(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(TransferServer,self).__init__(GxJzC,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(CloudFrontDistribution,self).__init__(GxJzC,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,GxJzC,env=GxJzb):
  GxJzr(CodeCommitRepository,self).__init__(GxJzC,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
