from kama_sdk.utils import utils

"""
Five types of recordable telem events:
  - operation
  - action
  - injection
  - update
  - system check

action.parent = events.*


"""
class TelemEvent:

  def __init(self, **kwargs):
    self.parent_id = kwargs.get('parent_id')
    self.id = utils.rand_str()
    self._type = kwargs.get()