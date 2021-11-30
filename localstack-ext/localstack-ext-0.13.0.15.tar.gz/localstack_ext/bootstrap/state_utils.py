import logging
CwNEG=bool
CwNEU=hasattr
CwNEL=set
CwNEP=True
CwNEi=False
CwNEH=isinstance
CwNER=dict
CwNET=getattr
CwNEM=None
CwNEk=str
CwNEV=Exception
CwNEF=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[CwNEG,Set]:
 if CwNEU(obj,"__dict__"):
  visited=visited or CwNEL()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return CwNEP,visited
  visited.add(wrapper)
 return CwNEi,visited
def get_object_dict(obj):
 if CwNEH(obj,CwNER):
  return obj
 obj_dict=CwNET(obj,"__dict__",CwNEM)
 return obj_dict
def is_composite_type(obj):
 return CwNEH(obj,(CwNER,OrderedDict))or CwNEU(obj,"__dict__")
def api_states_traverse(api_states_path:CwNEk,side_effect:Callable[...,CwNEM],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except CwNEV as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with CwNEF(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except CwNEV as e:
   LOG.debug("Unable to read pickled persistence file %s: %s"%(state_file,e))
def persist_object(obj,state_file):
 with CwNEF(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
