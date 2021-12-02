#!/usr/bin/env python3
#
# Copyright 2021 Jonathan Lee Komar
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
from typing import Dict, Tuple, List
from opencastapi.domain import events
import requests
from functionaljlk import getMapValue, Result, IniConfigReader
import inspect
import logging
logger = logging.getLogger('OpencastApiCallable')

# all return requests.Response
verbsToFunctions = {  'GET': requests.get, 
                      'POST': requests.post, 
                      'PUT': requests.put, 
                      'DELETE': requests.delete, 
                      'PATCH': requests.patch,
                      'HEAD': requests.head
                  }

authStrategiesToFunctions = { 'digest': requests.auth.HTTPDigestAuth,
                              'basic': requests.auth.HTTPBasicAuth
                            }

class OpencastApiCallable:
  # TODO: support different authentication strategies
  """HTTP-Protocol Action to an Opencast node

     Parameters:
     http_verb: the HTTP verb
     address: the address segment
     path: the URL path segment
     parameters: the URL parameters segment
     headers: the headers to be used in the HTTP header section
     username: the username
     password: the password
  """
  def __init__(self, 
                http_verb: str="", 
                address: str="",
                path: str="", 
                headers: str="", 
                parameters: Dict={}, 
                auth_strategy: str="digest",
                data=b"",
                username: str="", 
                password:str=""):
    self.http_verb = http_verb # used only to create event
    self.http_request_func = \
      getMapValue(http_verb.upper(), verbsToFunctions).getOrException()
    self.http_request_func_call_specific_kwargs = dict((x,y) for x,y in self.generate_arguments_from_members())
    self.address = address
    self.path = path
    self.params = parameters
    self.headers = headers
    self.data = data
    self.auth_strategy_func = getMapValue(auth_strategy, authStrategiesToFunctions).getOrException()
    self.username = username
    self.password = password
    self.url = Result.of(self.address).map(lambda url: url.rstrip('/')).map(lambda url: url + self.path).getOrException()

    self.events = [] # TODO

  def __call__(self) -> str:
    try:
      self.response = self.http_request_func(
                                    self.url, 
                                    auth=self.auth_strategy_func(self.username, self.password), 
                                    headers=self.headers, # every req supports this
                                    verify=True, 
                                    **self.http_request_func_call_specific_kwargs
                                    )
      return self.response
    except Exception as e:
      logger.error("{} encountered error: {}".format(self.__class__.__name__, e))

  def generate_arguments_from_members(self) -> List[Tuple]:
    result = []
    for p in inspect.signature(self.http_request_func).parameters:
      r = getattr(self, p, None)
      if r is not None:
        logger.debug(f"Binding {self}.{r} to {p}")
        result.append((p, r))
    return result
