import os
import re
import logging
import logging.handlers
import subprocess
import traceback
import configparser
import paho.mqtt.client as mqtt
from pi3dpf_ns.pi3dpf_common import pf_common as mqc
import socket


config_file    = [os.path.join(os.path.dirname(__file__), 'cfg/pf.config')] # os.path.join(os.path.dirname(this_dir), 'etc','pf.config')
if os.path.isfile('/home/pi/.pf/pf.config'):
  config_file.append('/home/pi/.pf/pf.config')
config         = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                                           converters={'list': lambda x: [i.strip() for i in x.split(',')]}) # cannot use interpolation=None, need to escape % (as %%) in values!
config.read(config_file)
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
LOG_LEVEL            = mqc.get_config_param(config, 'LOG_LEVEL')
numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % LOG_LEVEL)
logging.basicConfig(level=numeric_level)

#LOG_DIR                        = mqc.get_config_param(config, 'LOG_DIR')
#if not os.path.exists(LOG_DIR):
#  os.mkdir(LOG_DIR)
#LOG_FILE                       = os.path.join(LOG_DIR, os.path.splitext(os.path.basename(__file__))[0])+'.log'
#print ("for more information, check log file '{}'.".format(LOG_FILE))
#for h in log.handlers:
#  log.removeHandler(h)
#RotatingFileHandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
#log.name = os.path.basename(__file__)
#RotatingFileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#import pdb; pdb.set_trace()
#log.addHandler(RotatingFileHandler)
#log.HANDLER = RotatingFileHandler



#-----------------------------------------------------------------------------------------------------------------------
def rc_to_text_on_connect(rc):
  # Connection Return Codes:
  # 0: Connection successful
  # 1: Connection refused - incorrect protocol version
  # 2: Connection refused - invalid client identifier
  # 3: Connection refused - server unavailable
  # 4: Connection refused - bad username or password
  # 5: Connection refused - not authorised
  # 6-255: Currently unused.
  rc_texts = ['Connection successful',                           # rc = 0
              'Connection refused - incorrect protocol version', # rc = 1
              'Connection refused - invalid client identifier',  # rc = 2
              'Connection refused - server unavailable',         # rc = 3
              'Connection refused - bad username or password',   # rc = 4
              'Connection refused - not authorised']             # rc = 5
  rc_text = 'server return code rc={} is currently unused'.format(rc)
  if rc < len(rc_texts):
    rc_text = rc_texts[rc]
  
  return rc_text


#-----------------------------------------------------------------------------------------------------------------------
def hyperion(operation):
  if operation == 'status':
    # get Hyperion service status 
    # systemctl is-active hyperion: returns active or inactive
    log.info("+ systemctl is-active hyperion")
    rc = os.system("systemctl is-active hyperion") # active: rc=0, inactive: rc=768
    status = "active"
    if rc == 768:
      status = "inactive"
    log.info("sudo systemctl {} hyperion # result: {}".format(operation, status))
    return status
  elif operation in ['start', 'stop']:
    log.info("+ sudo systemctl {} hyperion".format(operation))
    rc = os.system("sudo systemctl {} hyperion".format(operation))
    if rc == 0 and operation == 'stop':
      return 'incative'
    elif rc == 0 and operation == 'start':
      return 'active'
    else:
      return 'unknown'
  else:
    log.error("hyperion(): unsupported operation '{}'".format(operation))
    exit(1)
  return rc

#-----------------------------------------------------------------------------------------------------------------------
def pictureframe(prog_path, operation, pic_dir, use_cec=False, trace_fopen=False):
  # valid operations: pic-stop, pic-start, pic-restart, x11-start
  if operation in ['status', 'stop', 'start', 'restart', 'x11-start']:
    operation      = 'pic-' + operation if operation != 'x11-start' else operation
    more_switches  = ""
    more_switches += " -t" if trace_fopen             else more_switches # switch on tracing for files opened by p13d
    more_switches += " -v" if operation == 'pic-stop' else more_switches # be verbose on picture frame shutdown
    dir_switch     = " -r -d '{}'".format(pic_dir) if operation == 'pic-start' else ""
    
    cmd = "{} -a {}{}{}".format(prog_path, operation, dir_switch, more_switches)
    log.debug(cmd)
    lf = "/home/pi/.pf/logs/{}_command_start_output.tmp".format(os.path.splitext(os.path.basename(prog_path))[0])
    os.system("{} > {} 2>&1".format(cmd, lf))
    with open(lf, 'r') as f:
      result = f.read()
    if os.path.exists(lf):
      os.remove(lf)

    if use_cec == True and operation == 'pic-start':
      cec_control_tv('on')
    if use_cec == True and operation == 'pic-stop':
      cec_control_tv('standby')
    return result
  else:
    log.error("pictureframe(): operation '{}' not in list of valid operations 'stop', 'start', 'restart', 'start'.".format(operation))
    exit(1)

#-----------------------------------------------------------------------------------------------------------------------
def cec_control_tv(operation):
  # valid operations: 'on', 'standby'
  if operation in ['on', 'standby']:
    # echo 'on 0.0.0.0' | cec-client -s -d 1
    log.info("+ echo {} 0.0.0.0|cec-client -s -d 1".format(operation))
    rc = os.system("echo {} 0.0.0.0|cec-client -s -d 1".format(operation))
  else:
    log.error("unexpected cec-client operation '{}'".format(operation))

#-----------------------------------------------------------------------------------------------------------------------
def resolve_picframe_nicks(nicknames, dir_spec):
  # function to identify nicknames for long directory paths defined in the config file.
  # Example:
  #   in config: PIC_FRAME_FAVORITE_DIRS = pix:/var/media/keto/ro/Pictures/Unsorted/Pixabay
  #   dirspec: pix/Landscpaes or pix:Landscapes or /pix/Landscapes
  #   return:  /var/media/keto/ro/Pictures/Unsorted/Pixabay/Landscpaes
  for k,v in nicknames.items():
    if re.match("/?"+k, dir_spec):
      n = re.sub('/?'+k+'[/:]', v+'/', dir_spec)
      log.info("replacing nickname '{}' in '{}' with '{}'".format(k, dir_spec, n))
      return n
  return dir_spec

def isOpen(ip, port):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((ip, int(port)))
    s.shutdown(2)
    return True
  except Exception as e:
    log.error(traceback.format_exc())
    return False


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
class helpers:

  def __init__(self, mqtt_obj, mqtt_topic):
    self.client = mqtt_obj
    self.topic = mqtt_topic
    # https://stackoverflow.com/a/3856502/7154477 methods from referred classes are not automatically visible
    M = mqtt.Client()
    publish = M.publish

  def info(self, msg):
    log.info(msg)
    self.client.publish(self.topic, 'INFO: {}'.format(msg))

  def warning(self, msg):
    log.warning(msg)
    self.client.publish(self.topic, 'WARNING: {}'.format(msg))

  def error(self, msg):
    log.error(msg)
    self.client.publish(self.topic, 'ERROR: {}'.format(msg))

  def show_siblings(self, dir_spec):
    log.info('mqtt topic: {}'.format(self.topic))
    msgs = ""
    for dir in os.listdir(dir_spec):
      path = os.path.join(dir_spec, dir)
      if os.path.isdir(path):
        if msgs == "":
          log.info('available directories in {}:'.format(dir_spec))
          msgs =       'available directories in {}:'.format(dir_spec)
        # From: https://stackoverflow.com/a/47930319
        file_count = sum(len(files) for _, _, files in os.walk(path))
        log.info("{:>5} files - {}".format(file_count, dir))
        msgs += '\n'
        msgs +=      "{:>5} files - {}".format(file_count, dir)

    if msgs != "":
      self.client.publish(self.topic, msgs)

  def show_nicknames(self, nicknames):
    self.client.publish(self.topic, nicknames)

  def show_help(self, topics):
    msg = ""
    for e in topics:
      if msg == "":
        msg = 'Available MQTT topics:\n'
      msg += '{}\n'.format(e)
    self.client.publish(self.topic, msg)
