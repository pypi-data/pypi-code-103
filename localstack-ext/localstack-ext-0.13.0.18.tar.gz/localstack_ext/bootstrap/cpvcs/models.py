from datetime import datetime
vyQwb=str
vyQwu=int
vyQwG=super
vyQwq=False
vyQwY=isinstance
vyQwg=hash
vyQwe=bool
vyQwX=True
vyQwx=list
vyQwB=map
vyQwM=None
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
class CPVCSObj:
 def __init__(self,hash_ref:vyQwb):
  self.hash_ref:vyQwb=hash_ref
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:vyQwb,rel_path:vyQwb,file_name:vyQwb,size:vyQwu,service:vyQwb,region:vyQwb):
  vyQwG(StateFileRef,self).__init__(hash_ref)
  self.rel_path:vyQwb=rel_path
  self.file_name:vyQwb=file_name
  self.size:vyQwu=size
  self.service:vyQwb=service
  self.region:vyQwb=region
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path)
 def __eq__(self,other):
  if not other:
   return vyQwq
  if not vyQwY(other,StateFileRef):
   return vyQwq
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return vyQwg((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->vyQwe:
  if not other:
   return vyQwq
  if not vyQwY(other,StateFileRef):
   return vyQwq
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->vyQwe:
  for other in others:
   if self.congruent(other):
    return vyQwX
  return vyQwq
 def metadata(self)->vyQwb:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:vyQwb,state_files:Set[StateFileRef],parent_ptr:vyQwb):
  vyQwG(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:vyQwb=parent_ptr
 def state_files_info(self)->vyQwb:
  return "\n".join(vyQwx(vyQwB(lambda state_file:vyQwb(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:vyQwb,head_ptr:vyQwb,message:vyQwb,timestamp:vyQwb=vyQwb(datetime.now().timestamp()),delta_log_ptr:vyQwb=vyQwM):
  self.tail_ptr:vyQwb=tail_ptr
  self.head_ptr:vyQwb=head_ptr
  self.message:vyQwb=message
  self.timestamp:vyQwb=timestamp
  self.delta_log_ptr:vyQwb=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:vyQwb,to_node:vyQwb)->vyQwb:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:vyQwb,state_files:Set[StateFileRef],parent_ptr:vyQwb,creator:vyQwb,rid:vyQwb,revision_number:vyQwu,assoc_commit:Commit=vyQwM):
  vyQwG(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:vyQwb=creator
  self.rid:vyQwb=rid
  self.revision_number:vyQwu=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(vyQwB(lambda state_file:vyQwb(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:vyQwb,state_files:Set[StateFileRef],parent_ptr:vyQwb,creator:vyQwb,comment:vyQwb,active_revision_ptr:vyQwb,outgoing_revision_ptrs:Set[vyQwb],incoming_revision_ptr:vyQwb,version_number:vyQwu):
  vyQwG(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(vyQwB(lambda stat_file:vyQwb(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
