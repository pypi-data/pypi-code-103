from kama_sdk.model.base.model import Model


class ResourceCategory(Model):

  def get_resource_kinds(self) -> str:
    return self.get_local_attr(KINDS_KEY) or []


KINDS_KEY = 'resources'
GRAPHIC_TYPE_KEY = 'graphic_type'
