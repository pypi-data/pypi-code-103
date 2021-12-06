from localstack.services.cloudformation.deployment_utils import lambda_keys_to_lower
gECdJ=staticmethod
gECde=None
gECdU=super
gECdY=str
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack_ext.services.cloudformation.service_models import(lambda_add_tags,lambda_convert_types)
class ECSCluster(GenericBaseModel):
 @gECdJ
 def cloudformation_type():
  return "AWS::ECS::Cluster"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute=="Arn":
   return self.props.get("clusterArn")
  return self.props.get("ClusterName")
 def fetch_state(self,stack_name,resources):
  props=self.props
  cluster=self.resolve_refs_recursively(stack_name,props.get("ClusterName"),resources)
  ecs_client=aws_stack.connect_to_service("ecs")
  result=ecs_client.describe_clusters(clusters=[cluster])["clusters"]
  return(result or[gECde])[0]
 @gECdJ
 def get_deploy_templates():
  return{"create":{"function":"create_cluster","parameters":lambda_keys_to_lower()}}
class ECSService(GenericBaseModel):
 @gECdJ
 def cloudformation_type():
  return "AWS::ECS::Service"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("serviceArn")
 def fetch_state(self,stack_name,resources):
  props=self.props
  cluster=self.resolve_refs_recursively(stack_name,props.get("Cluster"),resources)
  service_name=self.resolve_refs_recursively(stack_name,props.get("ServiceName"),resources)
  ecs_client=aws_stack.connect_to_service("ecs")
  result=ecs_client.describe_services(cluster=cluster,services=[service_name])["services"]
  return(result or[gECde])[0]
 def get_cfn_attribute(self,attribute_name):
  if attribute_name=="Name":
   return self.props.get("ServiceName")
  return gECdU(ECSService,self).get_cfn_attribute(attribute_name)
 @gECdJ
 def get_deploy_templates():
  return{"create":{"function":"create_service","parameters":lambda_add_tags(lambda_keys_to_lower())}}
class ECSTaskDefinition(GenericBaseModel):
 @gECdJ
 def cloudformation_type():
  return "AWS::ECS::TaskDefinition"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("taskDefinitionArn")
 def fetch_state(self,stack_name,resources):
  task_def=self.props.get("Family")
  task_def=self.resolve_refs_recursively(stack_name,task_def,resources)
  ecs_client=aws_stack.connect_to_service("ecs")
  task_defs=ecs_client.list_task_definitions(familyPrefix=task_def)["taskDefinitionArns"]
  return task_defs and{"taskDefinitionArn":task_defs[0]}or gECde
 @gECdJ
 def get_deploy_templates():
  return{"create":{"function":"register_task_definition","parameters":lambda_convert_types(lambda_keys_to_lower(),{".memory":gECdY,".cpu":gECdY})}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
