__version__ = "0.2.1"
__author__ = 'Modelbit'

from ._MbDatasets import _MbDatasets
class __Modelbit:

  _API_HOST = 'https://app.modelbit.com/'
  _LOGIN_HOST = _API_HOST
  _API_URL = None
  _state = {
    "notebookEnv": {
      "userEmail": "",
      "signedToken": "",
      "uuid": "",
      "authenticated": False,
      "workspaceName": ""
    }
  }
    
  def __init__(self):
    import os
    if os.getenv('MB_JUPYTER_API_HOST'):
      self._API_HOST = os.getenv('MB_JUPYTER_API_HOST')
    if os.getenv('MB_JUPYTER_LOGIN_HOST'):
      self._LOGIN_HOST = os.getenv('MB_JUPYTER_LOGIN_HOST')
    self._API_URL = f'{self._API_HOST}api/'

  def _isAuthenticated(self, testRemote=True):
    if testRemote and not self._isAuthenticated(False):
      data = self._getJson("jupyter/v1/login")
      if 'error' in data:
        self._printMk(f'**Error:** {data["error"]}')
        return False
      self._state["notebookEnv"] = data["notebookEnv"]
      return self._isAuthenticated(False)
    return self._state["notebookEnv"]["authenticated"]

  def _getJson(self, path):
    from urllib import request, parse
    import json
    try:
      data = {
        "requestToken": self._state["notebookEnv"]["signedToken"],
        "version": __version__
      }
      with request.urlopen(f'{self._API_URL}{path}', parse.urlencode(data).encode()) as url:
          return json.loads(url.read().decode())
    except BaseException as err:
      return {"error": f'Unable to reach Modelbit. ({err})'}

  def _getJsonOrPrintError(self, path):
    if not self._isAuthenticated():
      self._login()
      return False

    data = self._getJson(path)
    if 'error' in data:
      self._printMk(f'**Error:** {data["error"]}')
      return False
    return data

  def _printMk(self, str):
    from IPython.display import display, Markdown
    display(Markdown(str))

  def _printAuthenticatedMsg(self):
    connectedTag = '<span style="color:green; font-weight: bold;">connected</span>'
    email = self._state["notebookEnv"]["userEmail"]
    workspace = self._state["notebookEnv"]["workspaceName"]
    
    self._printMk(f'You\'re {connectedTag} to Modelbit as {email} in the \'{workspace}\' workspace.')

  def _login(self):
    if self._isAuthenticated():
      self._printAuthenticatedMsg()
      return

    displayUrl = f'modelbit.com/t/{self._state["notebookEnv"]["uuid"]}'
    linkUrl = f'{self._LOGIN_HOST}/t/{self._state["notebookEnv"]["uuid"]}'
    aTag = f'<a style="text-decoration:none;" href="{linkUrl}" target="_blank">{displayUrl}</a>'
    helpTag = '<a style="text-decoration:none;" href="/" target="_blank">Learn more.</a>'
    self._printMk('**Connect to Modelbit**<br/>' +
      f'Open {aTag} to authenticate this kernel, then re-run this cell. {helpTag}')

  # Public APIs
  def datasets(self): return _MbDatasets(self)
  def get_dataset(self, dataset_name): return _MbDatasets(self).get(dataset_name)


def login():
  _modelbit = __Modelbit()
  _modelbit._login()
  return _modelbit
