from .BaseServer import AduneoError
from .BaseServer import BaseServer
from cryptography.fernet import Fernet
import copy
import json
import os


class Configuration():

  def read_configuration(conf_filename):

    """
    Lit un fichier de configuration JSON du répertoire conf
    Met le nom du fichier dans /meta/filename
    
    mpham 26/02/2021
    """
    
    conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
    conf_filepath = conf_dir+'/'+conf_filename

    if not BaseServer.check_path_traversal(conf_dir, conf_filepath):
      raise AduneoError('file '+conf_filename+' not in conf directory')

    crypto = ConfCrypto()
    crypto.read(conf_filepath)
    return crypto.app_conf
  

  def write_configuration(conf):

    """
    Enregistre un JSON de configuration
    Le nom du fichier est dans /meta/filename
    
    mpham 27/02/2021
    """
    
    conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
    crypto = ConfCrypto()
    crypto.set_conf(conf)
    crypto.write()
    #crypto = ConfCrypto(conf_filepath)
    #return crypto.decrypt()
  

  def is_on(value):
    
    """
    Indique si une valeur (a prioiri issue d'un fichier de configuration) est vraie :
    on, yes, true, oui
    
    mpham 26/02/2021
    """
    
    return value.lower() in ('on', 'yes', 'true', 'oui')
    

  def is_off(value):
    
    """
    Indique si une valeur (a prioiri issue d'un fichier de configuration) est false :
    off, no, false, non
    
    mpham 26/02/2021
    """
    
    return value.lower() in ('off', 'no', 'false', 'non')
    
    
    
class ConfCrypto:
  
  def __init__(self):
    
    self.app_conf = None
    self.file_conf = None
    self.cipher = None
    self.modification = False
    

  def read(self, conf_filepath):
    
    self.conf_filepath = conf_filepath
    self.cipher = None
    self.modification = False
    
    with open(conf_filepath) as json_file:
      self.file_conf = json.load(json_file)
    
    if not 'meta' in self.file_conf:
      self.file_conf['meta'] = {}
    self.file_conf['meta']['filename'] = os.path.basename(conf_filepath)
    
    self.decrypt()
    
  
  def set_conf(self, conf):
    
    self.app_conf = conf
    
  
  def decrypt(self):
    
    self.app_conf = copy.deepcopy(self.file_conf)
    self.decrypt_json(self.app_conf)
    
    if self.modification:
      self.get_cipher()
      self.write()
    
    
  def decrypt_json(self, data):
    
    if isinstance(data, dict):
      for key in list(data.keys()):
        value = data[key]
        if key.endswith('!'):
          if not isinstance(value, str):
            raise AduneoError('key '+key+' has not a string value')
            
          # on regarde si la valeur est déjà chiffrée
          if value.startswith('{Fernet}'):
            data[key] = self.decrypt_string(value[8:])           
          else:
            self.modification = True
        else:
          self.decrypt_json(value)
    elif isinstance(data, list):
      for item in data:
        self.decrypt_json(item)


  def encrypt_json(self, data):

    if isinstance(data, dict):
      for key in list(data.keys()):
        value = data[key]
        if key.endswith('!'):
          if not isinstance(value, str):
            raise AduneoError('key '+key+' has not a string value')
            
          # on regarde si la valeur est déjà chiffrée
          if not value.startswith('{Fernet}'):
            data[key] = '{Fernet}'+self.encrypt_string(value)
        else:
          self.encrypt_json(value)
    elif isinstance(data, list):
      for item in data:
        self.encrypt_json(item)

    
  def write(self):
  
    self.file_conf = copy.deepcopy(self.app_conf)
    del self.file_conf['meta']['filename']
    self.encrypt_json(self.file_conf)
    
    conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
    conf_filepath = conf_dir + '/' + self.app_conf['meta']['filename']
    
    temp_filepath = conf_filepath+'.tmp'
    with open(temp_filepath, "w") as outfile: 
      json.dump(self.file_conf, outfile, indent=2)
      
    os.replace(temp_filepath, conf_filepath)
    
  
  def get_cipher(self):
    
    if self.cipher is None:
      
      key_filename = None
      if 'meta' in self.file_conf:
        if 'key' in self.file_conf['meta']:
          key_filename = self.file_conf['meta']['key']
          
      if key_filename is None:
        raise AduneoError('encryption: key file name not found in configuration (should be in /meta/key')
  
      conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')
      key_filepath = conf_dir+'/'+key_filename
      
      if not BaseServer.check_path_traversal(conf_dir, key_filepath):
        raise AduneoError('file '+key_filename+' not in conf directory')
      
      if not os.path.isfile(key_filepath):
        raise AduneoError('encryption: key file not found')

      file_in = open(key_filepath, 'r')
      key = file_in.read()
      file_in.close
      key = key[:5]+key[11:]
      
      self.cipher = Fernet(key.encode('ascii'))
      
    return self.cipher
  
  
  def decrypt_string(self, string):
    token = string.encode('ascii')
    decrypted_token = self.get_cipher().decrypt(token)
    return decrypted_token.decode('UTF-8')
    
    
  def encrypt_string(self, string):
    token = self.get_cipher().encrypt(string.encode('UTF-8'))
    return token.decode('ascii')
