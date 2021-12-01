from kama_sdk.model.base.model import Model


class VariableCategory(Model):

  def get_graphic(self) -> str:
    return self.get_attr(GRAPHIC_KEY)

  def get_graphic_type(self) -> str:
    return self.get_attr(GRAPHIC_TYPE_KEY, backup='icon')


GRAPHIC_KEY = 'graphic'
GRAPHIC_TYPE_KEY = 'graphic_type'
