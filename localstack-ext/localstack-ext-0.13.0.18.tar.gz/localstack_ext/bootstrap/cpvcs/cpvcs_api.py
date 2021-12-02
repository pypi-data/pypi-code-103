import inspect
FsTdk=None
FsTdi=set
FsTdW=open
FsTdS=str
FsTdO=bool
FsTdA=False
FsTdq=True
FsTdn=filter
FsTdx=int
FsTdE=Exception
FsTdB=next
FsTdj=sorted
FsTdy=isinstance
FsTdC=dict
FsTdo=getattr
FsTdL=type
import json
import logging
import os
import shutil
import zipfile
from typing import Dict,List,Optional,Set,Tuple
from deepdiff import DeepDiff
from localstack.utils.common import json_safe,mkdir,new_tmp_dir,rm_rf,short_uid
from localstack.utils.testutil import create_zip_file_python
from moto.s3.models import FakeBucket
from moto.sqs.models import Queue
from localstack_ext.bootstrap.cpvcs.constants import(COMMIT_FILE,COMPRESSION_FORMAT,META_ZIP,METAMODELS_FILE,NIL_PTR,STATE_ZIP,VER_SYMLINK,VERSION_SERVICE_INFO_FILE,VERSION_SPACE_ARCHIVE)
from localstack_ext.bootstrap.cpvcs.models import Commit,Revision,StateFileRef,Version
from localstack_ext.bootstrap.cpvcs.obj_storage import default_storage as object_storage
from localstack_ext.bootstrap.cpvcs.utils.common import config_context
from localstack_ext.bootstrap.cpvcs.utils.hash_utils import(compute_file_hash,compute_revision_hash,compute_version_archive_hash,random_hash)
from localstack_ext.bootstrap.cpvcs.utils.remote_utils import(_metadata_create_func,extract_meta_and_state_archives,merge_version_space,register_remote)
from localstack_ext.bootstrap.state_merge import merge_object_state
from localstack_ext.bootstrap.state_utils import(API_STATES_DIR,api_states_traverse,load_persisted_object,persist_object)
LOG=logging.getLogger(__name__)
def init(pod_name="My-Pod"):
 if config_context.pod_exists_locally(pod_name=pod_name):
  LOG.warning(f"Pod with name {pod_name} already exists locally")
  return
 config_context.set_pod_context(pod_name)
 def _create_internal_fs():
  mkdir(config_context.get_pod_root_dir())
  mkdir(config_context.get_ver_refs_path())
  mkdir(config_context.get_rev_refs_path())
  mkdir(config_context.get_ver_obj_store_path())
  mkdir(config_context.get_rev_obj_store_path())
  mkdir(config_context.get_delta_log_path())
 _create_internal_fs()
 r0_hash=random_hash()
 v0_hash=random_hash()
 r0=Revision(hash_ref=r0_hash,parent_ptr=NIL_PTR,creator=config_context.get_context_user(),rid=short_uid(),revision_number=0,state_files={})
 v0=Version(hash_ref=v0_hash,parent_ptr=NIL_PTR,creator=config_context.get_context_user(),comment="Init version",active_revision_ptr=r0_hash,outgoing_revision_ptrs={r0_hash},incoming_revision_ptr=FsTdk,state_files=FsTdi(),version_number=0)
 rev_key,ver_key=object_storage.upsert_objects(r0,v0)
 ver_symlink=config_context.create_version_symlink(VER_SYMLINK.format(ver_no=v0.version_number),ver_key)
 with FsTdW(config_context.get_head_path(),"w")as fp:
  fp.write(ver_symlink)
 with FsTdW(config_context.get_max_ver_path(),"w")as fp:
  fp.write(ver_symlink)
 with FsTdW(config_context.get_known_ver_path(),"w")as fp:
  fp.write(ver_symlink)
 config_context.update_ver_log(author=config_context.get_context_user(),ver_no=v0.version_number,rev_id=r0.rid,rev_no=r0.revision_number)
 LOG.debug(f"Successfully initated CPVCS for pod at {config_context.get_pod_root_dir()}")
def init_remote(version_space_archive:FsTdS,meta_archives:Dict[FsTdS,FsTdS],state_archives:Dict[FsTdS,FsTdS],remote_info:Dict[FsTdS,FsTdS],pod_name:FsTdS):
 config_context.set_pod_context(pod_name=pod_name)
 mkdir(config_context.get_pod_root_dir())
 with zipfile.ZipFile(version_space_archive)as version_space_zip:
  version_space_zip.extractall(config_context.get_pod_root_dir())
  LOG.debug("Successfully extracted version space zip")
 rm_rf(version_space_archive)
 extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives)
 max_ver=_get_max_version()
 ver_symlink=config_context.create_version_symlink(name=VER_SYMLINK.format(ver_no=max_ver.version_number))
 with FsTdW(config_context.get_head_path(),"w")as fp:
  fp.write(ver_symlink)
 register_remote(remote_info=remote_info)
def merge_from_remote(version_space_archive:FsTdS,meta_archives:Dict[FsTdS,FsTdS],state_archives:Dict[FsTdS,FsTdS]):
 merge_version_space(version_space_archive)
 extract_meta_and_state_archives(meta_archives=meta_archives,state_archives=state_archives)
def is_remotely_managed()->FsTdO:
 return config_context.is_remotly_managed()
def set_pod_context(pod_name:FsTdS):
 config_context.set_pod_context(pod_name)
def rename_pod(new_pod_name:FsTdS)->FsTdO:
 if config_context.pod_exists_locally(new_pod_name):
  LOG.warning(f"{new_pod_name} already exists locally")
  return FsTdA
 config_context.rename_pod(new_pod_name)
 return FsTdq
def list_locally_available_pods(show_remote_or_local:FsTdO=FsTdq)->Set[FsTdS]:
 available_pods=os.listdir(config_context.cpvcs_root_dir)
 if not show_remote_or_local:
  return available_pods
 result=FsTdi()
 for available_pod in available_pods:
  pod_name=(f"remote/{available_pod}" if config_context.is_remotly_managed(available_pod)else f"local/{available_pod}")
  result.add(pod_name)
 return result
def create_state_file_from_fs(path:FsTdS,file_name:FsTdS,service:FsTdS,region:FsTdS)->FsTdS:
 file_path=os.path.join(path,file_name)
 key=compute_file_hash(file_path)
 rel_path=path.split(f"{API_STATES_DIR}/")[1]
 shutil.copy(file_path,os.path.join(config_context.get_obj_store_path(),key))
 state_file=StateFileRef(hash_ref=key,rel_path=rel_path,file_name=file_name,size=os.path.getsize(file_path),service=service,region=region)
 _add_state_file_to_expansion_point(state_file)
 return key
def _create_state_file_from_in_memory_blob(blob)->FsTdS:
 tmp_file_name=random_hash()
 tmp_dest=os.path.join(config_context.get_obj_store_path(),tmp_file_name)
 persist_object(blob,tmp_dest)
 key=compute_file_hash(tmp_dest)
 dest=os.path.join(config_context.get_obj_store_path(),key)
 os.rename(tmp_dest,dest)
 return key
def _get_state_file_path(key:FsTdS)->FsTdS:
 file_path=os.path.join(config_context.get_obj_store_path(),key)
 if os.path.isfile(file_path):
  return file_path
 LOG.warning(f"No state file with found with key: {key}")
def _add_state_file_to_expansion_point(state_file:StateFileRef):
 revision,_=_get_expansion_point_with_head()
 updated_state_files=FsTdi(FsTdn(lambda sf:not sf.congruent(state_file),revision.state_files))
 updated_state_files.add(state_file)
 revision.state_files=updated_state_files
 object_storage.upsert_objects(revision)
def list_state_files(key:FsTdS)->Optional[FsTdS]:
 cpvcs_obj=object_storage.get_revision_or_version_by_key(key)
 if cpvcs_obj:
  return cpvcs_obj.state_files_info()
 LOG.debug(f"No Version or Revision associated to {key}")
def get_version_info(version_no:FsTdx)->Dict[FsTdS,FsTdS]:
 archive_path=get_version_meta_archive(version_no)
 if not archive_path:
  LOG.warning(f"No Info found for version {version_no}")
  return
 return read_file_from_archive(archive_path,VERSION_SERVICE_INFO_FILE)
def read_file_from_archive(archive_path:FsTdS,file_name:FsTdS):
 try:
  with zipfile.ZipFile(archive_path)as archive:
   content=json.loads(archive.read(file_name))
   return json.dumps(content)
 except FsTdE as e:
  LOG.debug(f"Could not find {file_name} in archive {archive_path}: {e}")
def commit(message:FsTdS=FsTdk)->Revision:
 curr_expansion_point,head_version=_get_expansion_point_with_head()
 curr_expansion_point_hash=compute_revision_hash(curr_expansion_point)
 curr_expansion_point_parent_state_files=FsTdi()
 if curr_expansion_point.parent_ptr!=NIL_PTR:
  referenced_by_version=FsTdk
  curr_expansion_point_parent=object_storage.get_revision_by_key(curr_expansion_point.parent_ptr)
  curr_expansion_point_parent_state_files=curr_expansion_point_parent.state_files
  curr_expansion_point_parent.assoc_commit.head_ptr=curr_expansion_point_hash
  object_storage.upsert_objects(curr_expansion_point_parent)
 else:
  referenced_by_version=head_version.hash_ref
 object_storage.update_revision_key(curr_expansion_point.hash_ref,curr_expansion_point_hash,referenced_by_version)
 curr_expansion_point.hash_ref=curr_expansion_point_hash
 new_expansion_point=Revision(hash_ref=random_hash(),state_files={},parent_ptr=curr_expansion_point_hash,creator=curr_expansion_point.creator,rid=short_uid(),revision_number=curr_expansion_point.revision_number+1)
 delta_log_ptr=_create_delta_log(curr_expansion_point_parent_state_files,curr_expansion_point.state_files)
 assoc_commit=Commit(tail_ptr=curr_expansion_point.hash_ref,head_ptr=new_expansion_point.hash_ref,message=message,delta_log_ptr=delta_log_ptr)
 curr_expansion_point.assoc_commit=assoc_commit
 object_storage.upsert_objects(new_expansion_point,curr_expansion_point)
 config_context.update_ver_log(author=new_expansion_point.creator,ver_no=head_version.version_number,rev_id=new_expansion_point.rid,rev_no=new_expansion_point.revision_number)
 return curr_expansion_point
def zip_directories(zip_dest:FsTdS,directories:List[FsTdS])->FsTdS:
 for version_space_dir in directories:
  create_zip_file_python(source_path=version_space_dir,content_root=os.path.basename(version_space_dir),base_dir=version_space_dir,zip_file=zip_dest,mode="a")
 return zip_dest
def create_version_space_archive()->FsTdS:
 zip_dest=os.path.join(config_context.get_pod_root_dir(),VERSION_SPACE_ARCHIVE)
 rm_rf(zip_dest)
 result=zip_directories(zip_dest=zip_dest,directories=config_context.get_version_space_dir_paths())
 with zipfile.ZipFile(result,"a")as archive:
  for version_space_file in config_context.get_version_space_file_paths():
   archive.write(version_space_file,arcname=os.path.basename(version_space_file))
 return result
def get_head()->Version:
 return object_storage.get_version_by_key(config_context._get_head_key())
def _get_max_version()->Version:
 return object_storage.get_version_by_key(config_context.get_max_ver_key())
def get_max_version_no()->FsTdx:
 with FsTdW(config_context.get_max_ver_path())as fp:
  return FsTdx(os.path.basename(fp.readline()))
def _get_expansion_point_with_head()->Tuple[Revision,Version]:
 head_version=get_head()
 active_revision_root=object_storage.get_revision_by_key(head_version.active_revision_ptr)
 expansion_point=object_storage.get_terminal_revision(active_revision_root)
 return expansion_point,head_version
def _filter_special_cases(state_files:Set[StateFileRef])->Tuple[List[StateFileRef],List[StateFileRef],List[StateFileRef]]:
 regular_refs,s3_bucket_refs,sqs_queue_refs=[],[],[]
 for state_file in state_files:
  if state_file.service=="sqs":
   sqs_queue_refs.append(state_file)
  elif state_file.service=="s3":
   s3_bucket_refs.append(state_file)
  else:
   regular_refs.append(state_file)
 return regular_refs,s3_bucket_refs,sqs_queue_refs
def push_overwrite(version:FsTdx,comment:FsTdS)->FsTdO:
 expansion_point,_=_get_expansion_point_with_head()
 if version>get_max_version_no():
  LOG.debug("Attempted to overwrite a non existing version.. Aborting")
  return FsTdA
 version_node=get_version_by_number(version)
 _create_state_directory(version_number=version,state_file_refs=expansion_point.state_files)
 metamodels_file=f"metamodel_commit_{expansion_point.revision_number}.json"
 _create_metadata_archive(version_node=version_node,overwrite=FsTdq,metamodels_file=metamodels_file)
 version_node.comment=comment
 object_storage.upsert_objects(version_node)
 return FsTdq
def push(comment:FsTdS=FsTdk,three_way:FsTdO=FsTdA)->Version:
 expansion_point,head_version=_get_expansion_point_with_head()
 max_version=_get_max_version()
 new_active_revision=Revision(hash_ref=random_hash(),state_files=FsTdi(),parent_ptr=NIL_PTR,creator=expansion_point.creator,rid=short_uid(),revision_number=0)
 new_max_version_no=max_version.version_number+1
 if head_version.version_number!=max_version.version_number:
  _merge_expansion_point_with_max(three_way=three_way)
 else:
  _create_state_directory(new_max_version_no,state_file_refs=expansion_point.state_files)
 new_version=Version(hash_ref=compute_version_archive_hash(new_max_version_no,get_version_state_archive(new_max_version_no)),state_files=FsTdi(),parent_ptr=max_version.hash_ref,creator=expansion_point.creator,comment=comment,active_revision_ptr=new_active_revision.hash_ref,outgoing_revision_ptrs={new_active_revision.hash_ref},incoming_revision_ptr=expansion_point.hash_ref,version_number=new_max_version_no)
 if expansion_point.parent_ptr!=NIL_PTR:
  expansion_point_parent=object_storage.get_revision_by_key(expansion_point.parent_ptr)
  state_from=expansion_point_parent.state_files
 else:
  state_from=FsTdi()
 delta_log_ptr=_create_delta_log(state_from,new_version.state_files)
 expansion_point_commit=Commit(tail_ptr=expansion_point.hash_ref,head_ptr=new_version.hash_ref,message="Finalizing commit",delta_log_ptr=delta_log_ptr)
 expansion_point.state_files=new_version.state_files
 expansion_point.assoc_commit=expansion_point_commit
 head_version.active_revision_ptr=NIL_PTR
 object_storage.upsert_objects(head_version,expansion_point,new_active_revision,new_version)
 _update_head(new_version.version_number,new_version.hash_ref)
 _update_max_ver(new_version.version_number,new_version.hash_ref)
 _add_known_ver(new_version.version_number,new_version.hash_ref)
 _create_metadata_archive(new_version)
 config_context.update_ver_log(author=expansion_point.creator,ver_no=new_version.version_number,rev_id=new_active_revision.rid,rev_no=new_active_revision.revision_number)
 return new_version
def get_version_meta_archive(version_no:FsTdx)->FsTdS:
 version_meta_path=config_context.get_version_meta_archive_path(version_no)
 if os.path.isfile(version_meta_path):
  return version_meta_path
def get_version_state_archive(version_no:FsTdx)->FsTdS:
 version_state_path=config_context.get_version_state_archive_path(version_no)
 if os.path.isfile(version_state_path):
  return version_state_path
def get_version_metamodel(version_no:FsTdx)->FsTdS:
 meta_archive=get_version_meta_archive(version_no)
 if meta_archive:
  return read_file_from_archive(meta_archive,METAMODELS_FILE)
def _create_metadata_archive(version_node:Version,delete_reference:FsTdO=FsTdA,overwrite:FsTdO=FsTdA,metamodels_file:FsTdS=FsTdk):
 revision_node=object_storage.get_revision_or_version_by_key(version_node.active_revision_ptr if overwrite else version_node.incoming_revision_ptr)
 metadata_dir=os.path.join(config_context.get_pod_root_dir(),META_ZIP.format(version_no=version_node.version_number))
 mkdir(metadata_dir)
 if metamodels_file:
  archive_path=f"{metadata_dir}.{COMPRESSION_FORMAT}"
  if os.path.isfile(archive_path):
   with zipfile.ZipFile(archive_path)as archive:
    archive.extractall(metadata_dir)
 while revision_node:
  assoc_commit=revision_node.assoc_commit
  if not assoc_commit:
   break
  delta_ptr=assoc_commit.delta_log_ptr
  if delta_ptr:
   src=object_storage.get_delta_file_by_key(delta_ptr)
   if not src:
    continue
   dst_name=COMMIT_FILE.format(commit_no=revision_node.revision_number+1)
   dst=os.path.join(config_context.get_pod_root_dir(),metadata_dir,dst_name)
   shutil.copy(src,dst)
   if delete_reference:
    os.remove(src)
  next_revision=assoc_commit.head_ptr if overwrite else revision_node.parent_ptr
  revision_node=object_storage.get_revision_by_key(next_revision)
 metamodels={}
 service_info={}
 tmp_states_dir=new_tmp_dir()
 with zipfile.ZipFile(get_version_state_archive(version_node.version_number))as archive:
  archive.extractall(tmp_states_dir)
 tmp_states_dir_api_states=os.path.join(tmp_states_dir,API_STATES_DIR)
 api_states_traverse(api_states_path=tmp_states_dir_api_states,side_effect=_metadata_create_func,mutables=[metamodels,service_info])
 if not metamodels_file:
  metamodels_file=METAMODELS_FILE
 metamodels_dest=os.path.join(metadata_dir,metamodels_file)
 version_service_info=os.path.join(metadata_dir,VERSION_SERVICE_INFO_FILE)
 with FsTdW(metamodels_dest,"w")as fp:
  metamodels=json_safe(metamodels)
  json.dump(metamodels,fp,indent=4)
 with FsTdW(version_service_info,"w")as fp:
  json.dump(service_info,fp,indent=4)
 shutil.make_archive(metadata_dir,COMPRESSION_FORMAT,root_dir=metadata_dir)
 rm_rf(metadata_dir)
 rm_rf(tmp_states_dir)
def _create_state_directory(version_number:FsTdx,state_file_refs:Set[StateFileRef],delete_files=FsTdA,archive=FsTdq):
 version_state_dir=os.path.join(config_context.get_pod_root_dir(),STATE_ZIP.format(version_no=version_number))
 for state_file in state_file_refs:
  try:
   dst_path=os.path.join(version_state_dir,API_STATES_DIR,state_file.rel_path)
   mkdir(dst_path)
   src=object_storage.get_state_file_location_by_key(state_file.hash_ref)
   dst=os.path.join(dst_path,state_file.file_name)
   shutil.copy(src,dst)
   if delete_files:
    os.remove(src)
  except FsTdE as e:
   LOG.warning(f"Failed to locate state file with rel path: {state_file.rel_path}: {e}")
 mkdir(os.path.join(version_state_dir,"kinesis"))
 mkdir(os.path.join(version_state_dir,"dynamodb"))
 if archive:
  shutil.make_archive(version_state_dir,COMPRESSION_FORMAT,root_dir=version_state_dir)
  rm_rf(version_state_dir)
  return f"{version_state_dir}.{COMPRESSION_FORMAT}"
 return version_state_dir
def set_active_version(version_no:FsTdx,commit_before=FsTdA)->FsTdO:
 known_versions=load_version_references()
 for known_version_no,known_version_key in known_versions:
  if known_version_no==version_no:
   if commit_before:
    commit()
   _set_active_version(known_version_key)
   return FsTdq
 LOG.info(f"Version with number {version_no} not found")
 return FsTdA
def _set_active_version(key:FsTdS):
 current_head=get_head()
 if current_head.hash_ref!=key and object_storage.version_exists(key):
  requested_version=object_storage.get_version_by_key(key)
  _update_head(requested_version.version_number,key)
  if requested_version.active_revision_ptr==NIL_PTR:
   new_path_root=Revision(hash_ref=random_hash(),state_files=FsTdi(),parent_ptr=NIL_PTR,creator=config_context.get_context_user(),rid=short_uid(),revision_number=0)
   requested_version.active_revision_ptr=new_path_root.hash_ref
   requested_version.outgoing_revision_ptrs.add(new_path_root.hash_ref)
   object_storage.upsert_objects(new_path_root,requested_version)
def get_version_by_number(version_no:FsTdx)->Version:
 versions=load_version_references()
 version_ref=FsTdB((version[1]for version in versions if version[0]==version_no),FsTdk)
 if not version_ref:
  LOG.warning(f"Could not find version number {version_no}")
  return
 return object_storage.get_version_by_key(version_ref)
def load_version_references()->List[Tuple[FsTdx,FsTdS]]:
 result={}
 with FsTdW(config_context.get_known_ver_path(),"r")as vp:
  symlinks=vp.readlines()
  for symlink in symlinks:
   symlink=config_context.get_pod_absolute_path(symlink.rstrip())
   with FsTdW(symlink,"r")as sp:
    result[FsTdx(os.path.basename(symlink))]=sp.readline()
 return FsTdj(result.items(),key=lambda x:x[0],reverse=FsTdq)
def list_versions()->List[FsTdS]:
 version_references=load_version_references()
 result=[object_storage.get_version_by_key(version_key).info_str()for _,version_key in version_references]
 return result
def list_version_commits(version_no:FsTdx)->List[FsTdS]:
 if version_no==-1:
  version=_get_max_version()
 else:
  version=get_version_by_number(version_no)
 if not version:
  return[]
 result=[]
 revision=object_storage.get_revision_by_key(version.incoming_revision_ptr)
 while revision:
  assoc_commit=revision.assoc_commit
  revision_no=revision.revision_number
  if revision_no!=0:
   from_node=f"Revision-{revision_no - 1}"
  elif version_no!=0:
   from_node=f"Version-{version_no}"
  else:
   from_node="Empty state"
  to_node=f"Revision-{revision_no}"
  result.append(assoc_commit.info_str(from_node=from_node,to_node=to_node))
  revision=object_storage.get_revision_by_key(revision.parent_ptr)
 return result
def get_commit_diff(version_no:FsTdx,commit_no:FsTdx)->FsTdS:
 archive_path=get_version_meta_archive(version_no)
 if not archive_path:
  LOG.warning(f"No metadata found for version {version_no}")
  return
 file_name=f"{COMMIT_FILE.format(commit_no=commit_no)}"
 return read_file_from_archive(archive_path=archive_path,file_name=file_name)
def _update_head(new_head_ver_no,new_head_key)->FsTdS:
 with FsTdW(config_context.get_head_path(),"w")as fp:
  ver_symlink=config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_head_ver_no),new_head_key)
  fp.write(ver_symlink)
  return ver_symlink
def _update_max_ver(new_max_ver_no,new_max_ver_key)->FsTdS:
 with FsTdW(config_context.get_max_ver_path(),"w")as fp:
  max_ver_symlink=config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_max_ver_no),new_max_ver_key)
  fp.write(max_ver_symlink)
  return max_ver_symlink
def _add_known_ver(new_ver_no,new_ver_key)->FsTdS:
 with FsTdW(config_context.get_known_ver_path(),"a")as fp:
  new_ver_symlink=config_context.create_version_symlink(VER_SYMLINK.format(ver_no=new_ver_no),new_ver_key)
  fp.write(f"\n{new_ver_symlink}")
  return new_ver_symlink
def _is_special_case(obj)->FsTdO:
 return FsTdy(obj,(Queue,FakeBucket))
def _merge_three_way_dir_func(**kwargs):
 dir_name=kwargs.get("dir_name")
 fname=kwargs.get("fname")
 region=kwargs.get("region")
 service_name=kwargs.get("service_name")
 mutables=kwargs.get("mutables")
 other=mutables[0]
 ancestor=mutables[1]
 src_state_file_path=os.path.join(dir_name,fname)
 ancestor_state_dir=os.path.join(ancestor,service_name,region)
 ancestor_state_file_path=os.path.join(ancestor_state_dir,fname)
 dst_state_dir=os.path.join(other,service_name,region)
 dst_state_file_path=os.path.join(dst_state_dir,fname)
 src_state=load_persisted_object(src_state_file_path)
 ancestor_state=load_persisted_object(ancestor_state_file_path)
 special_case=_is_special_case(src_state)
 if os.path.isfile(dst_state_file_path):
  if not special_case:
   dst_state=load_persisted_object(dst_state_file_path)
   merge_object_state(dst_state,src_state,ancestor_state)
   persist_object(dst_state,dst_state_file_path)
 else:
  mkdir(dst_state_dir)
  persist_object(src_state,dst_state_file_path)
def _merge_two_state_dir_func(**kwargs):
 dir_name=kwargs.get("dir_name")
 fname=kwargs.get("fname")
 region=kwargs.get("region")
 service_name=kwargs.get("service_name")
 mutables=kwargs.get("mutables")
 other=mutables[0]
 src_state_file_path=os.path.join(dir_name,fname)
 dst_state_dir=os.path.join(other,service_name,region)
 dst_state_file_path=os.path.join(dst_state_dir,fname)
 src_state=load_persisted_object(src_state_file_path)
 special_case=_is_special_case(src_state)
 if os.path.isfile(dst_state_file_path):
  if not special_case:
   dst_state=load_persisted_object(dst_state_file_path)
   merge_object_state(dst_state,src_state)
   persist_object(dst_state,dst_state_file_path)
 else:
  mkdir(dst_state_dir)
  persist_object(src_state,dst_state_file_path)
def _merge_expansion_point_with_max(three_way=FsTdA):
 expansion_point,head=_get_expansion_point_with_head()
 curr_max_version_no=get_max_version_no()
 new_version_no=curr_max_version_no+1
 curr_max_version_state_archive=get_version_state_archive(curr_max_version_no)
 common_ancestor_state_archive=FsTdk
 tmp_common_ancestor_state_dir=FsTdk
 if head.version_number>1 and three_way:
  common_ancestor_state_archive=get_version_state_archive(head.version_number-1)
  tmp_common_ancestor_state_dir=new_tmp_dir()
  with zipfile.ZipFile(common_ancestor_state_archive)as archive:
   archive.extractall(tmp_common_ancestor_state_dir)
 tmp_max_version_state_dir=new_tmp_dir()
 with zipfile.ZipFile(curr_max_version_state_archive)as archive:
  archive.extractall(tmp_max_version_state_dir)
 new_max_version_states_dir=_create_state_directory(version_number=new_version_no,state_file_refs=expansion_point.state_files,archive=FsTdA)
 new_max_version_states_dir_api_states=os.path.join(new_max_version_states_dir,API_STATES_DIR)
 tmp_max_version_state_dir_api_states=os.path.join(tmp_max_version_state_dir,API_STATES_DIR)
 if not common_ancestor_state_archive:
  api_states_traverse(api_states_path=tmp_max_version_state_dir_api_states,side_effect=_merge_two_state_dir_func,mutables=[new_max_version_states_dir_api_states])
 else:
  LOG.debug(f"Starting three way merge between version {head.version_number} and {curr_max_version_no} with common ancestor {head.version_number - 1}")
  common_ancestor_version_state_dir_api_states=os.path.join(tmp_common_ancestor_state_dir,API_STATES_DIR)
  api_states_traverse(api_states_path=tmp_max_version_state_dir_api_states,side_effect=_merge_three_way_dir_func,mutables=[new_max_version_states_dir_api_states,common_ancestor_version_state_dir_api_states])
 shutil.make_archive(new_max_version_states_dir,COMPRESSION_FORMAT,root_dir=new_max_version_states_dir)
 rm_rf(new_max_version_states_dir)
 rm_rf(tmp_max_version_state_dir)
 rm_rf(tmp_common_ancestor_state_dir)
def _infer_backend_init(clazz,sf):
 if FsTdy(clazz,FsTdC):
  backend={}
 else:
  constructor=FsTdo(clazz,"__init__",FsTdk)
  sig_args=inspect.getfullargspec(constructor)
  if "region" in sig_args.args:
   backend=clazz(region=sf.region)
  elif "region_name" in sig_args.args:
   backend=clazz(region_name=sf.region)
  else:
   backend=clazz()
 return backend
def _create_delta_log(state_from:Set[StateFileRef],state_to:Set[StateFileRef])->FsTdS:
 state_files_from=_filter_special_cases(state_from)
 state_files_from_regular=state_files_from[0]
 state_files_from_s3=state_files_from[1]
 state_files_from_sqs=state_files_from[2]
 state_files_to=_filter_special_cases(state_to)
 state_files_to_regular=state_files_to[0]
 state_files_to_s3=state_files_to[1]
 state_files_to_sqs=state_files_to[2]
 def _create_sf_lookup(state_files:Set[StateFileRef])->Dict[FsTdS,StateFileRef]:
  return{os.path.join(sf.rel_path,sf.file_name):sf for sf in state_files}
 result={}
 state_files_to_lookup=_create_sf_lookup(state_files_to_regular)
 for state_file_from in state_files_from_regular:
  result_region=result.setdefault(state_file_from.region,{})
  result_service=result_region.setdefault(state_file_from.service,{})
  result_file=result_service.setdefault(state_file_from.file_name,{})
  if state_file_from.any_congruence(state_files_to_regular):
   key=os.path.join(state_file_from.rel_path,state_file_from.file_name)
   state_file_to=state_files_to_lookup.pop(key)
   diff_json=_create_diff_json(state_file_from,state_file_to)
  else:
   diff_json=_create_diff_json(state_file_from,FsTdk)
  result_file["diff"]=diff_json
 for state_files_to in state_files_to_lookup.values():
  result_region=result.setdefault(state_files_to.region,{})
  result_service=result_region.setdefault(state_files_to.service,{})
  result_file=result_service.setdefault(state_files_to.file_name,{})
  diff_json=_create_diff_json(FsTdk,state_files_to)
  result_file["diff"]=diff_json
 def _handle_special_case_containers(service,sf_from,sf_to):
  region_containers_from={}
  region_containers_to={}
  for container_file_from in sf_from:
   region=container_file_from.region
   region_container=region_containers_from.setdefault(region,{})
   container=load_persisted_object(object_storage.get_state_file_location_by_key(container_file_from.hash_ref))
   if container:
    region_container[container.name]=container
  for container_file_to in sf_to:
   region=container_file_to.region
   region_container=region_containers_to.setdefault(region,{})
   container=load_persisted_object(object_storage.get_state_file_location_by_key(container_file_to.hash_ref))
   if container:
    region_container[container.name]=container
  for region,region_queues_from in region_containers_from.items():
   region_queues_to=region_containers_to.pop(region,{})
   region_diff=DeepDiff(region_queues_from,region_queues_to)
   container_result_region=result.setdefault(region,{})
   container_result_service=container_result_region.setdefault(service,{})
   container_result_service["diff"]=region_diff.to_json()
  for region,region_queues_to in region_containers_to.items():
   region_diff=DeepDiff({},region_queues_to)
   container_result_region=result.setdefault(region,{})
   container_result_service=container_result_region.setdefault(service,{})
   container_result_service["diff"]=region_diff.to_json()
 _handle_special_case_containers("sqs",state_files_from_sqs,state_files_to_sqs)
 _handle_special_case_containers("s3",state_files_from_s3,state_files_to_s3)
 tmp_dest=os.path.join(config_context.get_delta_log_path(),random_hash())
 with FsTdW(tmp_dest,"w")as fp:
  json.dump(result,fp,indent=4)
 key=compute_file_hash(tmp_dest)
 dest=os.path.join(config_context.get_delta_log_path(),key)
 os.rename(tmp_dest,dest)
 return key
def _create_diff_json(sf1:StateFileRef,sf2:StateFileRef):
 if sf1 and sf2:
  if sf1.hash_ref==sf2.hash_ref:
   return "No Changes"
  else:
   backend1=load_persisted_object(config_context.get_obj_file_path(sf1.hash_ref))
   backend2=load_persisted_object(config_context.get_obj_file_path(sf2.hash_ref))
   diff=DeepDiff(backend1,backend2)
   return diff.to_json()
 if not sf1:
  backend2=load_persisted_object(config_context.get_obj_file_path(sf2.hash_ref))
  clazz=FsTdL(backend2)
  backend1=_infer_backend_init(clazz,sf2)
 else:
  backend1=load_persisted_object(config_context.get_obj_file_path(sf1.hash_ref))
  clazz=FsTdL(backend1)
  backend2=_infer_backend_init(clazz,sf1)
 diff=DeepDiff(backend1,backend2)
 return diff.to_json()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
