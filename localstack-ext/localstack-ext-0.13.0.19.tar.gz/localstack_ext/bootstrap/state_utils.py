import logging
cXTPG=bool
cXTPb=hasattr
cXTPU=set
cXTPV=True
cXTPO=False
cXTPA=isinstance
cXTPL=dict
cXTPB=getattr
cXTPj=None
cXTPi=str
cXTPF=Exception
cXTPx=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[cXTPG,Set]:
 if cXTPb(obj,"__dict__"):
  visited=visited or cXTPU()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return cXTPV,visited
  visited.add(wrapper)
 return cXTPO,visited
def get_object_dict(obj):
 if cXTPA(obj,cXTPL):
  return obj
 obj_dict=cXTPB(obj,"__dict__",cXTPj)
 return obj_dict
def is_composite_type(obj):
 return cXTPA(obj,(cXTPL,OrderedDict))or cXTPb(obj,"__dict__")
def api_states_traverse(api_states_path:cXTPi,side_effect:Callable[...,cXTPj],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except cXTPF as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with cXTPx(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except cXTPF as e:
   LOG.debug("Unable to read pickled persistence file %s: %s"%(state_file,e))
def persist_object(obj,state_file):
 with cXTPx(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
