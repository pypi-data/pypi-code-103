import graphene
from . import type_


##__________________________________________________________________||
def resolve_web_config(parent, info, **kwargs):
    return type_.WebConfig.get_query(info).one_or_none()


web_config_field = graphene.Field(type_.WebConfig, resolver=resolve_web_config)

##__________________________________________________________________||
