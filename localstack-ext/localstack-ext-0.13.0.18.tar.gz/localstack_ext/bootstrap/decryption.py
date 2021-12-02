import inspect
BWiYp=bytes
BWiYu=None
BWiYR=isinstance
BWiYo=list
BWiYt=getattr
BWiYP=open
BWiYT=property
BWiYF=Exception
BWiYw=setattr
BWiYD=True
import os.path
import sys
import traceback
from importlib.abc import MetaPathFinder,SourceLoader
from importlib.util import spec_from_file_location
import pyaes
class DecryptionHandler:
 decryption_key:BWiYp
 def __init__(self,decryption_key:BWiYp):
  self.decryption_key=decryption_key
 def decrypt(self,content)->BWiYp:
  cipher=pyaes.AESModeOfOperationCBC(self.decryption_key,iv="\0"*16)
  decrypter=pyaes.Decrypter(cipher)
  decrypted=decrypter.feed(content)
  decrypted+=decrypter.feed()
  decrypted=decrypted.partition(b"\0")[0]
  return decrypted
class EncryptedFileFinder(MetaPathFinder):
 decryption_handler:DecryptionHandler
 def __init__(self,decryption_handler:DecryptionHandler):
  self.decryption_handler=decryption_handler
 def find_spec(self,fullname,path,target=BWiYu):
  if path and not BWiYR(path,BWiYo):
   path=BWiYo(BWiYt(path,"_path",[]))
  if not path:
   return BWiYu
  name=fullname.split(".")[-1]
  file_path=os.path.join(path[0],name+".py")
  enc=file_path+".enc"
  if not os.path.isfile(enc):
   return BWiYu
  if os.path.isfile(file_path):
   return BWiYu
  return spec_from_file_location(fullname,enc,loader=DecryptingLoader(enc,self.decryption_handler))
class DecryptingLoader(SourceLoader):
 decryption_handler:DecryptionHandler
 def __init__(self,encrypted_file,decryption_handler:DecryptionHandler):
  self.encrypted_file=encrypted_file
  self.decryption_handler=decryption_handler
 def get_filename(self,fullname):
  return self.encrypted_file
 def get_data(self,filename):
  with BWiYP(filename,"rb")as f:
   data=f.read()
  data=self.decryption_handler.decrypt(data)
  return data
def init_source_decryption(decryption_handler:DecryptionHandler):
 sys.meta_path.insert(0,EncryptedFileFinder(decryption_handler))
 patch_traceback_lines()
 patch_inspect_findsource()
def patch_traceback_lines():
 if BWiYt(traceback.FrameSummary,"_ls_patch_applied",BWiYu):
  return
 @BWiYT
 def line(self):
  try:
   return line_orig.fget(self)
  except BWiYF:
   self._line=""
   return self._line
 line_orig=traceback.FrameSummary.line
 BWiYw(traceback.FrameSummary,"line",line)
 traceback.FrameSummary._ls_patch_applied=BWiYD
def patch_inspect_findsource():
 if BWiYt(inspect,"_ls_patch_applied",BWiYu):
  return
 def findsource(*args,**kwargs):
  try:
   return findsource_orig(*args,**kwargs)
  except BWiYF:
   return[],0
 findsource_orig=inspect.findsource
 inspect.findsource=findsource
 inspect._ls_patch_applied=BWiYD
# Created by pyminifier (https://github.com/liftoff/pyminifier)
