from datetime import datetime
lrXVu=str
lrXVC=int
lrXVY=super
lrXVs=False
lrXVM=isinstance
lrXVd=hash
lrXVm=bool
lrXVG=True
lrXVE=list
lrXVh=map
lrXVJ=None
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
class CPVCSObj:
 def __init__(self,hash_ref:lrXVu):
  self.hash_ref:lrXVu=hash_ref
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:lrXVu,rel_path:lrXVu,file_name:lrXVu,size:lrXVC,service:lrXVu,region:lrXVu):
  lrXVY(StateFileRef,self).__init__(hash_ref)
  self.rel_path:lrXVu=rel_path
  self.file_name:lrXVu=file_name
  self.size:lrXVC=size
  self.service:lrXVu=service
  self.region:lrXVu=region
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path)
 def __eq__(self,other):
  if not other:
   return lrXVs
  if not lrXVM(other,StateFileRef):
   return lrXVs
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return lrXVd((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->lrXVm:
  if not other:
   return lrXVs
  if not lrXVM(other,StateFileRef):
   return lrXVs
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->lrXVm:
  for other in others:
   if self.congruent(other):
    return lrXVG
  return lrXVs
 def metadata(self)->lrXVu:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:lrXVu,state_files:Set[StateFileRef],parent_ptr:lrXVu):
  lrXVY(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:lrXVu=parent_ptr
 def state_files_info(self)->lrXVu:
  return "\n".join(lrXVE(lrXVh(lambda state_file:lrXVu(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:lrXVu,head_ptr:lrXVu,message:lrXVu,timestamp:lrXVu=lrXVu(datetime.now().timestamp()),delta_log_ptr:lrXVu=lrXVJ):
  self.tail_ptr:lrXVu=tail_ptr
  self.head_ptr:lrXVu=head_ptr
  self.message:lrXVu=message
  self.timestamp:lrXVu=timestamp
  self.delta_log_ptr:lrXVu=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:lrXVu,to_node:lrXVu)->lrXVu:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:lrXVu,state_files:Set[StateFileRef],parent_ptr:lrXVu,creator:lrXVu,rid:lrXVu,revision_number:lrXVC,assoc_commit:Commit=lrXVJ):
  lrXVY(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:lrXVu=creator
  self.rid:lrXVu=rid
  self.revision_number:lrXVC=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(lrXVh(lambda state_file:lrXVu(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:lrXVu,state_files:Set[StateFileRef],parent_ptr:lrXVu,creator:lrXVu,comment:lrXVu,active_revision_ptr:lrXVu,outgoing_revision_ptrs:Set[lrXVu],incoming_revision_ptr:lrXVu,version_number:lrXVC):
  lrXVY(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(lrXVh(lambda stat_file:lrXVu(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
