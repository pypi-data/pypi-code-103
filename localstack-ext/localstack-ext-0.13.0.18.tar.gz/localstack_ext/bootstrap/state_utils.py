import logging
pIWcN=bool
pIWck=hasattr
pIWcX=set
pIWcs=True
pIWcQ=False
pIWcU=isinstance
pIWch=dict
pIWcO=getattr
pIWcg=None
pIWcv=str
pIWcD=Exception
pIWco=open
import os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
API_STATES_DIR="api_states"
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited:Set)->Tuple[pIWcN,Set]:
 if pIWck(obj,"__dict__"):
  visited=visited or pIWcX()
  wrapper=ObjectIdHashComparator(obj)
  if wrapper in visited:
   return pIWcs,visited
  visited.add(wrapper)
 return pIWcQ,visited
def get_object_dict(obj):
 if pIWcU(obj,pIWch):
  return obj
 obj_dict=pIWcO(obj,"__dict__",pIWcg)
 return obj_dict
def is_composite_type(obj):
 return pIWcU(obj,(pIWch,OrderedDict))or pIWck(obj,"__dict__")
def api_states_traverse(api_states_path:pIWcv,side_effect:Callable[...,pIWcg],mutables:List[Any]):
 for dir_name,_,file_list in os.walk(api_states_path):
  for file_name in file_list:
   try:
    subdirs=os.path.normpath(dir_name).split(os.sep)
    region=subdirs[-1]
    service_name=subdirs[-2]
    side_effect(dir_name=dir_name,fname=file_name,region=region,service_name=service_name,mutables=mutables)
   except pIWcD as e:
    LOG.warning(f"Failed to apply {side_effect.__name__} for {file_name} in dir {dir_name}: {e}")
    continue
def load_persisted_object(state_file):
 if not os.path.isfile(state_file):
  return
 import dill
 with pIWco(state_file,"rb")as f:
  try:
   content=f.read()
   result=dill.loads(content)
   return result
  except pIWcD as e:
   LOG.debug("Unable to read pickled persistence file %s: %s"%(state_file,e))
def persist_object(obj,state_file):
 with pIWco(state_file,"wb")as f:
  result=f.write(dill.dumps(obj))
  return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
