from datetime import datetime
VDWFf=str
VDWFT=int
VDWFU=super
VDWFA=False
VDWFM=isinstance
VDWFm=hash
VDWFB=bool
VDWFa=True
VDWFO=list
VDWFG=map
VDWFv=None
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
class CPVCSObj:
 def __init__(self,hash_ref:VDWFf):
  self.hash_ref:VDWFf=hash_ref
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:VDWFf,rel_path:VDWFf,file_name:VDWFf,size:VDWFT,service:VDWFf,region:VDWFf):
  VDWFU(StateFileRef,self).__init__(hash_ref)
  self.rel_path:VDWFf=rel_path
  self.file_name:VDWFf=file_name
  self.size:VDWFT=size
  self.service:VDWFf=service
  self.region:VDWFf=region
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path)
 def __eq__(self,other):
  if not other:
   return VDWFA
  if not VDWFM(other,StateFileRef):
   return VDWFA
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return VDWFm((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->VDWFB:
  if not other:
   return VDWFA
  if not VDWFM(other,StateFileRef):
   return VDWFA
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->VDWFB:
  for other in others:
   if self.congruent(other):
    return VDWFa
  return VDWFA
 def metadata(self)->VDWFf:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:VDWFf,state_files:Set[StateFileRef],parent_ptr:VDWFf):
  VDWFU(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:VDWFf=parent_ptr
 def state_files_info(self)->VDWFf:
  return "\n".join(VDWFO(VDWFG(lambda state_file:VDWFf(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:VDWFf,head_ptr:VDWFf,message:VDWFf,timestamp:VDWFf=VDWFf(datetime.now().timestamp()),delta_log_ptr:VDWFf=VDWFv):
  self.tail_ptr:VDWFf=tail_ptr
  self.head_ptr:VDWFf=head_ptr
  self.message:VDWFf=message
  self.timestamp:VDWFf=timestamp
  self.delta_log_ptr:VDWFf=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:VDWFf,to_node:VDWFf)->VDWFf:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:VDWFf,state_files:Set[StateFileRef],parent_ptr:VDWFf,creator:VDWFf,rid:VDWFf,revision_number:VDWFT,assoc_commit:Commit=VDWFv):
  VDWFU(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:VDWFf=creator
  self.rid:VDWFf=rid
  self.revision_number:VDWFT=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(VDWFG(lambda state_file:VDWFf(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:VDWFf,state_files:Set[StateFileRef],parent_ptr:VDWFf,creator:VDWFf,comment:VDWFf,active_revision_ptr:VDWFf,outgoing_revision_ptrs:Set[VDWFf],incoming_revision_ptr:VDWFf,version_number:VDWFT):
  VDWFU(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(VDWFG(lambda stat_file:VDWFf(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
