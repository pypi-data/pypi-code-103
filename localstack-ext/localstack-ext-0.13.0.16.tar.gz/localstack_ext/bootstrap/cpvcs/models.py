from datetime import datetime
wfjLt=str
wfjLR=int
wfjLM=super
wfjLH=False
wfjLC=isinstance
wfjLV=hash
wfjLb=bool
wfjLF=True
wfjLk=list
wfjLo=map
wfjLh=None
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
class CPVCSObj:
 def __init__(self,hash_ref:wfjLt):
  self.hash_ref:wfjLt=hash_ref
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:wfjLt,rel_path:wfjLt,file_name:wfjLt,size:wfjLR,service:wfjLt,region:wfjLt):
  wfjLM(StateFileRef,self).__init__(hash_ref)
  self.rel_path:wfjLt=rel_path
  self.file_name:wfjLt=file_name
  self.size:wfjLR=size
  self.service:wfjLt=service
  self.region:wfjLt=region
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path)
 def __eq__(self,other):
  if not other:
   return wfjLH
  if not wfjLC(other,StateFileRef):
   return wfjLH
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return wfjLV((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->wfjLb:
  if not other:
   return wfjLH
  if not wfjLC(other,StateFileRef):
   return wfjLH
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->wfjLb:
  for other in others:
   if self.congruent(other):
    return wfjLF
  return wfjLH
 def metadata(self)->wfjLt:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:wfjLt,state_files:Set[StateFileRef],parent_ptr:wfjLt):
  wfjLM(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:wfjLt=parent_ptr
 def state_files_info(self)->wfjLt:
  return "\n".join(wfjLk(wfjLo(lambda state_file:wfjLt(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:wfjLt,head_ptr:wfjLt,message:wfjLt,timestamp:wfjLt=wfjLt(datetime.now().timestamp()),delta_log_ptr:wfjLt=wfjLh):
  self.tail_ptr:wfjLt=tail_ptr
  self.head_ptr:wfjLt=head_ptr
  self.message:wfjLt=message
  self.timestamp:wfjLt=timestamp
  self.delta_log_ptr:wfjLt=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:wfjLt,to_node:wfjLt)->wfjLt:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:wfjLt,state_files:Set[StateFileRef],parent_ptr:wfjLt,creator:wfjLt,rid:wfjLt,revision_number:wfjLR,assoc_commit:Commit=wfjLh):
  wfjLM(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:wfjLt=creator
  self.rid:wfjLt=rid
  self.revision_number:wfjLR=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(wfjLo(lambda state_file:wfjLt(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:wfjLt,state_files:Set[StateFileRef],parent_ptr:wfjLt,creator:wfjLt,comment:wfjLt,active_revision_ptr:wfjLt,outgoing_revision_ptrs:Set[wfjLt],incoming_revision_ptr:wfjLt,version_number:wfjLR):
  wfjLM(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(wfjLo(lambda stat_file:wfjLt(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
