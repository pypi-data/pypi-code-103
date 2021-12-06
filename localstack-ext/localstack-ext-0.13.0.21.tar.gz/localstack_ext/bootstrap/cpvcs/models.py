from datetime import datetime
qrEBk=str
qrEBP=int
qrEBg=super
qrEBt=False
qrEBa=isinstance
qrEBn=hash
qrEBh=bool
qrEBj=True
qrEBN=list
qrEBS=map
qrEBQ=None
from typing import Set
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_TXT_LAYOUT,REV_TXT_LAYOUT,STATE_TXT_LAYOUT,STATE_TXT_METADATA,VER_TXT_LAYOUT)
class CPVCSObj:
 def __init__(self,hash_ref:qrEBk):
  self.hash_ref:qrEBk=hash_ref
class StateFileRef(CPVCSObj):
 txt_layout=STATE_TXT_LAYOUT
 metadata_layout=STATE_TXT_METADATA
 def __init__(self,hash_ref:qrEBk,rel_path:qrEBk,file_name:qrEBk,size:qrEBP,service:qrEBk,region:qrEBk):
  qrEBg(StateFileRef,self).__init__(hash_ref)
  self.rel_path:qrEBk=rel_path
  self.file_name:qrEBk=file_name
  self.size:qrEBP=size
  self.service:qrEBk=service
  self.region:qrEBk=region
 def __str__(self):
  return self.txt_layout.format(size=self.size,service=self.service,region=self.region,hash_ref=self.hash_ref,file_name=self.file_name,rel_path=self.rel_path)
 def __eq__(self,other):
  if not other:
   return qrEBt
  if not qrEBa(other,StateFileRef):
   return qrEBt
  return(self.hash_ref==other.hash_ref and self.region==other.region and self.service==self.service and self.file_name==other.file_name and self.size==other.size)
 def __hash__(self):
  return qrEBn((self.hash_ref,self.region,self.service,self.file_name,self.size))
 def congruent(self,other)->qrEBh:
  if not other:
   return qrEBt
  if not qrEBa(other,StateFileRef):
   return qrEBt
  return(self.region==other.region and self.service==other.service and self.file_name==other.file_name and self.rel_path==other.rel_path)
 def any_congruence(self,others)->qrEBh:
  for other in others:
   if self.congruent(other):
    return qrEBj
  return qrEBt
 def metadata(self)->qrEBk:
  return self.metadata_layout.format(size=self.size,service=self.service,region=self.region)
class CPVCSNode(CPVCSObj):
 def __init__(self,hash_ref:qrEBk,state_files:Set[StateFileRef],parent_ptr:qrEBk):
  qrEBg(CPVCSNode,self).__init__(hash_ref)
  self.state_files:Set[StateFileRef]=state_files
  self.parent_ptr:qrEBk=parent_ptr
 def state_files_info(self)->qrEBk:
  return "\n".join(qrEBN(qrEBS(lambda state_file:qrEBk(state_file),self.state_files)))
class Commit:
 txt_layout=COMMIT_TXT_LAYOUT
 def __init__(self,tail_ptr:qrEBk,head_ptr:qrEBk,message:qrEBk,timestamp:qrEBk=qrEBk(datetime.now().timestamp()),delta_log_ptr:qrEBk=qrEBQ):
  self.tail_ptr:qrEBk=tail_ptr
  self.head_ptr:qrEBk=head_ptr
  self.message:qrEBk=message
  self.timestamp:qrEBk=timestamp
  self.delta_log_ptr:qrEBk=delta_log_ptr
 def __str__(self):
  return self.txt_layout.format(tail_ptr=self.tail_ptr,head_ptr=self.head_ptr,message=self.message,timestamp=self.timestamp,log_hash=self.delta_log_ptr)
 def info_str(self,from_node:qrEBk,to_node:qrEBk)->qrEBk:
  return f"from: {from_node}, to: {to_node}, message: {self.message}, time: {datetime.fromtimestamp(float(self.timestamp))}"
class Revision(CPVCSNode):
 txt_layout=REV_TXT_LAYOUT
 def __init__(self,hash_ref:qrEBk,state_files:Set[StateFileRef],parent_ptr:qrEBk,creator:qrEBk,rid:qrEBk,revision_number:qrEBP,assoc_commit:Commit=qrEBQ):
  qrEBg(Revision,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator:qrEBk=creator
  self.rid:qrEBk=rid
  self.revision_number:qrEBP=revision_number
  self.assoc_commit=assoc_commit
 def __str__(self):
  return self.txt_layout.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,rid=self.rid,rev_no=self.revision_number,state_files=";".join(qrEBS(lambda state_file:qrEBk(state_file),self.state_files))if self.state_files else "",assoc_commit=self.assoc_commit)
class Version(CPVCSNode):
 txt_layout=VER_TXT_LAYOUT
 def __init__(self,hash_ref:qrEBk,state_files:Set[StateFileRef],parent_ptr:qrEBk,creator:qrEBk,comment:qrEBk,active_revision_ptr:qrEBk,outgoing_revision_ptrs:Set[qrEBk],incoming_revision_ptr:qrEBk,version_number:qrEBP):
  qrEBg(Version,self).__init__(hash_ref,state_files,parent_ptr)
  self.creator=creator
  self.comment=comment
  self.active_revision_ptr=active_revision_ptr
  self.outgoing_revision_ptrs=outgoing_revision_ptrs
  self.incoming_revision_ptr=incoming_revision_ptr
  self.version_number=version_number
 def __str__(self):
  return VER_TXT_LAYOUT.format(hash_ref=self.hash_ref,parent=self.parent_ptr,creator=self.creator,comment=self.comment,version_number=self.version_number,active_revision=self.active_revision_ptr,outgoing_revisions=";".join(self.outgoing_revision_ptrs),incoming_revision=self.incoming_revision_ptr,state_files=";".join(qrEBS(lambda stat_file:qrEBk(stat_file),self.state_files))if self.state_files else "")
 def info_str(self):
  return f"{self.version_number}, {self.creator}, {self.comment}"
# Created by pyminifier (https://github.com/liftoff/pyminifier)
