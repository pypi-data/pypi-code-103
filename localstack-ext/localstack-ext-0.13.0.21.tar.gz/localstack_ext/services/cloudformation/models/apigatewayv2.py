import json
QlLve=staticmethod
QlLvq=None
QlLvd=classmethod
QlLvK=super
QlLvB=type
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class ApiGatewayV2VpcLink(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::VpcLink"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  links=client.get_vpc_links()["Items"]
  link_name=self.resolve_refs_recursively(stack_name,self.props["Name"],resources)
  result=[e for e in links if e["Name"]==link_name]
  return(result or[QlLvq])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("VpcLinkId")
 @QlLve
 def get_deploy_templates():
  return{"create":{"function":"create_vpc_link"},"delete":{"function":"delete_vpc_link","parameters":["VpcLinkId"]}}
class ApiGatewayV2DomainName(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::DomainName"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_domain_names()["Items"]
  domain_name=self.resolve_refs_recursively(stack_name,self.props["DomainName"],resources)
  result=([a for a in apis if a["DomainName"]==domain_name]or[QlLvq])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("DomainName")
 @QlLve
 def get_deploy_templates():
  return{"create":{"function":"create_domain_name"},"delete":{"function":"delete_domain_name","parameters":["DomainName"]}}
class ApiGatewayV2Authorizer(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Authorizer"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  auth_name=self.resolve_refs_recursively(stack_name,props["Name"],resources)
  apis=client.get_authorizers(ApiId=api_id)["Items"]
  result=([a for a in apis if a["Name"]==auth_name]or[QlLvq])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("AuthorizerId")
 @QlLve
 def get_deploy_templates():
  return{"create":{"function":"create_authorizer"}}
class ApiGatewayV2Api(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Api"
 def fetch_state(self,stack_name,resources):
  props=self.props
  api_name=(props["Body"].get("info",{}).get("title")if props.get("Body")else props["Name"])
  return self.fetch_details(api_name)
 @QlLvd
 def fetch_details(cls,api_name):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_apis()["Items"]
  result=([a for a in apis if a["Name"]==api_name]or[QlLvq])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("ApiId")
 @QlLve
 def get_deploy_templates():
  def create_resource(resource_id,resources,resource_type,func,stack_name,*args):
   resource=resources[resource_id]
   resource_props=resource["Properties"]
   client=aws_stack.connect_to_service("apigatewayv2")
   body=resource_props.get("Body")
   if body:
    base_path=resource_props.get("Basepath")
    body.setdefault("info",{}).setdefault("title","api-%s"%short_uid())
    body=json.dumps(body)
    kwargs={"Basepath":base_path}if base_path else{}
    return client.import_api(Body=body,**kwargs)
   params=select_attributes(resource_props,["ApiKeySelectionExpression","CorsConfiguration","CredentialsArn","Description","DisableSchemaValidation","Name","ProtocolType","RouteKey","RouteSelectionExpression","Tags","Target","Version"])
   return client.create_api(**params)
  return{"create":{"function":create_resource}}
class ApiGatewayV2IntegrationResponse(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::IntegrationResponse"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  int_id=self.resolve_refs_recursively(stack_name,props["IntegrationId"],resources)
  resp_key=self.resolve_refs_recursively(stack_name,props["IntegrationResponseKey"],resources)
  responses=client.get_integration_responses(ApiId=api_id,IntegrationId=int_id).get("Items",[])
  result=[r for r in responses if r["IntegrationResponseKey"]==resp_key]
  return(result or[QlLvq])[0]
 def get_physical_resource_id(self,attribute=QlLvq,**kwargs):
  return self.props.get("IntegrationResponseId")
 def get_cfn_attribute(self,attribute_name):
  if attribute_name in REF_ID_ATTRS:
   return self.get_physical_resource_id(attribute_name)
  return QlLvK(ApiGatewayV2IntegrationResponse,self).get_cfn_attribute(attribute_name)
 @QlLve
 def get_deploy_templates():
  return{"create":{"function":"create_integration_response"}}
class ApiGatewayV2Integration(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Integration"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("IntegrationId")
 @QlLvd
 def fetch_details(cls,api_id,QlLvB,method,uri=QlLvq):
  client=aws_stack.connect_to_service("apigatewayv2")
  resp=client.get_integrations(ApiId=api_id)
  if "Items" not in resp:
   return QlLvq
  integrations=[r for r in resp["Items"]if QlLvB==r.get("IntegrationType")and uri in[QlLvq,r.get("IntegrationUri")]and method in[QlLvq,r.get("IntegrationMethod")]]
  return(integrations or[QlLvq])[0]
class ApiGatewayV2Deployment(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Deployment"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("DeploymentId")
 @QlLvd
 def fetch_details(cls,api_id,stage_name,description):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_deployments(ApiId=api_id)["Items"]
  apis=[a for a in apis if a.get("StageName")==stage_name or a.get("Description")==description]
  return(apis or[QlLvq])[0]
class ApiGatewayV2Stage(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Stage"
 @QlLvd
 def fetch_details(cls,api_id,stage_name):
  client=aws_stack.connect_to_service("apigatewayv2")
  return client.get_stage(ApiId=api_id,StageName=stage_name)or QlLvq
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("StageName")
class ApiGatewayV2RouteResponse(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::RouteResponse"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  route_id=self.resolve_refs_recursively(stack_name,props["RouteId"],resources)
  response_key=self.resolve_refs_recursively(stack_name,props["RouteResponseKey"],resources)
  responses=client.get_route_responses(ApiId=api_id,RouteId=route_id).get("Items",[])
  result=[r for r in responses if r["RouteResponseKey"]==response_key]
  return(result or[QlLvq])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RouteResponseId")
 @QlLve
 def get_deploy_templates():
  return{"create":{"function":"create_route_response"},"delete":{"function":"delete_route_response","parameters":["ApiId","RouteId","RouteResponseId"]}}
class ApiGatewayV2Route(GenericBaseModel):
 @QlLve
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Route"
 @QlLvd
 def fetch_details(cls,api_id,route_key):
  client=aws_stack.connect_to_service("apigatewayv2")
  routes=client.get_routes(ApiId=api_id).get("Items",[])
  result=[r for r in routes if r["RouteKey"]==route_key]
  return(result or[QlLvq])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RouteId")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
