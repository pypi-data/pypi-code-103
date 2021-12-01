from copy import deepcopy
from typing import Optional, Union

from kama_sdk.core.core.types import ErrorCapture


class ActionError(Exception):
  err_capture: ErrorCapture
  is_original: bool

  def __init__(self, err_capture: ErrorCapture, is_original=None):
    err: ErrorCapture = deepcopy(err_capture)
    self.err_capture = {
      **err,
      'fatal': err.get('fatal', False),
      'is_original': True if is_original is None else is_original
    }
    super().__init__(err.get('reason'))


class FatalActionError(ActionError):

  def __init__(self, err_capture: ErrorCapture, is_original=None):
    new_capt = {**err_capture, 'fatal': True}
    super().__init__(new_capt, is_original)


ActionErrOrException = Optional[Union[Exception, ActionError]]
