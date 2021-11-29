#!/usr/bin/env python3
#
# todo:
#   service announcement for web server allowing user to browse PIC_DIR. Could be done using UDP broadcasts: https://stackoverflow.com/questions/6177423/send-broadcast-datagram
#   mqtt service detection for home assistant
#   exif info auslesen: /share/ro/Tools/Image-Downloaders/Pixabay/repo/Pixabay-Image-Scarper-Downloader/scraper_3.py

import os
import configparser
import re
import logging
import logging.handlers
import subprocess
import traceback
import time
import socket
import paho.mqtt.client as mqtt  # from: https://pypi.org/project/paho-mqtt/
import paho.mqtt as pm
from pi3dpf_ns.pi3dpf_base import pf_mqtt as mqh
from pi3dpf_ns.pi3dpf_common import pf_common as mqc

this_host = os.uname()[1]
this_dir = os.path.dirname(__file__)
this_file = os.path.basename(__file__)

config_file = [os.path.join(os.path.dirname(mqh.__file__),
                            'cfg/pf.config')]  # os.path.join(os.path.dirname(this_dir), 'etc','pf.config')
if os.path.isfile('/home/pi/.pf/pf.config'):
    config_file.append('/home/pi/.pf/pf.config')

# -----------------------------------------------------------------------------------------------------------------------
# From: https://stackoverflow.com/a/53274707
config = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                                   converters={'list': lambda x: [i.strip() for i in x.split(
                                       ',')]})  # cannot use interpolation=None, need to escape % (as %%) in values!
config.read(config_file)
config.cfg_fname = config_file[0]

log = logging.getLogger(__name__)
LOG_LEVEL = mqc.get_config_param(config, 'LOG_LEVEL')
numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % LOG_LEVEL)
# logging.basicConfig(level=numeric_level)

LOG_DIR = mqc.get_config_param(config, 'LOG_DIR')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, os.path.splitext(os.path.basename(__file__))[0]) + '.log'
print("for more information, check log file '{}'.".format(LOG_FILE))
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO, filename=LOG_FILE)
for h in log.handlers:
    log.removeHandler(h)
RotatingFileHandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
log.name = os.path.basename(__file__)
RotatingFileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(RotatingFileHandler)
log.HANDLER = RotatingFileHandler

# pi3d_log.info("pi3d version: {}, PIL Image version: {}".format(pi3d.__version__, Image.__version__))
log.info("paho.mqtt version: {}".format(pm.__version__))

SECRETS_PATH = mqc.get_config_param(config, 'SECRETS_PATH')
MQTT_SERVER_NAME = mqc.get_config_param(config, 'MQTT_SERVER_NAME')
MQTT_SERVER_PORT = mqc.get_config_param(config, 'MQTT_SERVER_PORT')
MQTT_CLIENT_USERNAME = mqc.get_config_param(config, 'MQTT_CLIENT_USERNAME')
MQTT_CLIENT_PASSWORD = mqc.get_config_param(config, 'MQTT_CLIENT_PASSWORD')
if MQTT_CLIENT_PASSWORD == 'add-your-secret-here':
    print("ERROR - please add password to secrets file")
    log.error("please add password to secrets file")
    exit(1)
TOPICS_TO_SUBSCRIBE = mqc.get_config_param(config, 'TOPICS_TO_SUBSCRIBE')
MQTT_TOPLEVEL_TOPIC = mqc.get_config_param(config, 'MQTT_TOPLEVEL_TOPIC')
PIC_FRAME_CTL_PROG = mqc.get_config_param(config, 'PIC_FRAME_CTL_PROG')
PIC_FRAME_TRACE_FOPEN = mqc.get_config_param(config, 'PIC_FRAME_TRACE_FOPEN')
CEC_CONTROL_TV = mqc.get_config_param(config, 'CEC_CONTROL_TV')
PIC_FRAME_DEFAULT_PIC_LOCATION = mqc.get_config_param(config, 'PIC_FRAME_DEFAULT_PIC_LOCATION')
n = mqc.get_config_param(config, 'PIC_FRAME_FAVORITE_DIRS')
# make dict with nicknames as key. E.g. nick:/var/tmp will be x[nick] contains /var/tmp
PIC_FRAME_FAVORITE_DIRS = {n[i].split(":")[0]: os.path.abspath(n[i].split(":")[1]) for i in range(0, len(n))}
# PIC_FRAME_FAVORITE_DIRS = dict(map(lambda x: x.split(':'), n))

nickname_list = "Available nicknames for picture frame directories:\n"
log.info("Available nicknames for picture frame directories:")
max_len_nicknames = max(list(map(lambda l: len(l), PIC_FRAME_FAVORITE_DIRS.keys())))
format_string = "{:>" + str(max_len_nicknames) + "}: {}{}"
for k in sorted(PIC_FRAME_FAVORITE_DIRS.keys()):
    dir_status = ""
    if not os.path.exists(PIC_FRAME_FAVORITE_DIRS[k]):
        dir_status = " (directory not found!)"
    txt = format_string.format(k, PIC_FRAME_FAVORITE_DIRS[k], dir_status)
    log.info(txt)
    nickname_list += txt + '\n'


# -----------------------------------------------------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    while rc != 0:
        # meanings of rc in rc_to_text_on_connect
        log.error("Connection failed with rc = {}. Reason: {}".format(rc, mqh.rc_to_text_on_connect(rc)))
        client.connect(MQTT_SERVER_NAME, MQTT_SERVER_PORT, 60)

    log.info("Successfully connected with MQTT broker {}:{} as user {}".format(MQTT_SERVER_NAME, MQTT_SERVER_PORT,
                                                                               MQTT_CLIENT_USERNAME))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    # Subscribing to all topics allows to send feedback on stuff that does not work...
    client.subscribe(MQTT_TOPLEVEL_TOPIC + '/#')
    log.info('Subscribing to {}/#'.format(MQTT_TOPLEVEL_TOPIC))
    # i = 0
    # for topic in TOPICS_TO_SUBSCRIBE:
    #  log.info('Subscribing to {:>3} topic {}'.format(i, topic))
    #  client.subscribe(TOPICS_TO_SUBSCRIBE[i])
    #  i += 1


# -----------------------------------------------------------------------------------------------------------------------
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode('UTF-8')
    log.info('Received message {} with payload {}'.format(msg.topic, msg.payload))
    msg_handling = 'unhandled'

    if msg.topic in MQTT_TOPLEVEL_TOPIC + '/help':
        msg_handling = 'recognized'
        lopu.show_help(TOPICS_TO_SUBSCRIBE)

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/status']:
        msg_handling = 'recognized'
        status = "Hyperion status: {}\nPicture Frame Status: {}".format(
            mqh.hyperion('status'),
            mqh.pictureframe(PIC_FRAME_CTL_PROG, 'status', None, None))
        lopu.info(status)

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/pictureframe/start',
                     MQTT_TOPLEVEL_TOPIC + '/pictureframe/stop',
                     MQTT_TOPLEVEL_TOPIC + '/pictureframe/restart',
                     MQTT_TOPLEVEL_TOPIC + '/pictureframe/dirlist',
                     MQTT_TOPLEVEL_TOPIC + '/pictureframe/x11-start']:
        msg_handling = 'recognized'
        pic_dir = mqh.resolve_picframe_nicks(PIC_FRAME_FAVORITE_DIRS, msg.payload)
        if not os.path.isdir(pic_dir):
            log.warning(
                "cannot access directory '{}' given in mqtt paylod. Using PIC_FRAME_DEFAULT_PIC_LOCATION='{}'".format(
                    pic_dir, PIC_FRAME_DEFAULT_PIC_LOCATION))
            pic_dir = PIC_FRAME_DEFAULT_PIC_LOCATION
        log.info(
            "mqh.pictureframe(prog_path='{}', operation='{}', pic_dir='{}', use_cec='{}')".format(PIC_FRAME_CTL_PROG,
                                                                                                  os.path.basename(
                                                                                                      msg.topic),
                                                                                                  pic_dir,
                                                                                                  CEC_CONTROL_TV))
        if os.path.basename(msg.topic) in ['dirlist']:
            lopu.show_siblings(pic_dir)
        else:
            status = mqh.pictureframe(PIC_FRAME_CTL_PROG, os.path.basename(msg.topic), pic_dir, CEC_CONTROL_TV,
                                      PIC_FRAME_TRACE_FOPEN)
            lopu.info(status)

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/pictureframe/nicknames']:
        msg_handling = 'recognized'
        lopu.show_nicknames(nickname_list)

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/status',
                     MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/start',
                     MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/stop']:
        msg_handling = 'recognized'
        rc = mqh.hyperion(os.path.basename(msg.topic))
        log.info("state for {}: {}".format(msg.topic, rc))
        client.publish(MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/state', "state for {}: {}".format(msg.topic, rc))

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/command']:
        msg_handling = 'recognized'
        if msg.payload == 'ON':
            rc = mqh.hyperion('start')
        elif msg.payload == 'OFF':
            rc = mqh.hyperion('start')
        else:
            lopu.error("unexpected payload '{}' in topic '{}'".format(msg.payload, msg.topic))

    if msg.topic in [MQTT_TOPLEVEL_TOPIC + '/state',
                     MQTT_TOPLEVEL_TOPIC + '/hyperion/andi/state',
                     MQTT_TOPLEVEL_TOPIC + '/hyperion/pictureframe/state',
                     MQTT_TOPLEVEL_TOPIC + '/pictureframe/state']:
        msg_handling = 'ignored'

    if msg_handling == 'recognized':
        log.info("message '{}' was recognized and handled".format(msg.topic))
    elif msg_handling == 'ignored':
        log.info("mqtt message '{}' is configured to be ignored".format(msg.topic))
    else:
        log.warning("unhandled mqtt message: '{}'".format(msg.topic))
        lopu.show_help(TOPICS_TO_SUBSCRIBE)


# -----------------------------------------------------------------------------------------------------------------------
# From: https://stackoverflow.com/a/52428947
def on_log(client, userdata, level, buff):
    log.info(buf)


# -----------------------------------------------------------------------------------------------------------------------
# From: https://gist.github.com/betrcode/0248f0fda894013382d7#file-is_port_open-py
# todo: use identical method from pf_mqtt.py instead
def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        log.error(traceback.format_exc())
        return False


##  __  __       _
## |  \/  |     (_)
## | \  / | __ _ _ _ __
## | |\/| |/ _` | | '_ \
## | |  | | (_| | | | | |
## |_|  |_|\__,_|_|_| |_|
##

# -----------------------------------------------------------------------------------------------------------------------


if CEC_CONTROL_TV:
    # check required program 'cec-client' is installed (From: https://unix.stackexchange.com/a/418623 and https://stackoverflow.com/a/24850026)
    try:
        cmd = "echo scan|cec-client -s -d 1|grep -A 5 'device #0: TV'|grep '^vendor:'"
        getTV = subprocess.check_output(cmd, shell=True)
        tv = getTV.decode('UTF-8').rstrip()
        log.info("TV manufacturer detected by external program 'cec-client': {}".format(tv[15:]))
    except Exception as e:
        log.error("caught exception while executing command {}".format(cmd))
        log.error(traceback.format_exc())
        log.info("Disabling CEC_CONTROL_TV. (did you execute 'sudo apt install cec-utils'?")
        CEC_CONTROL_TV = False

client = mqtt.Client()
client.username_pw_set(username=MQTT_CLIENT_USERNAME, password=MQTT_CLIENT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.enable_logger()
lopu = mqh.helpers(client, MQTT_TOPLEVEL_TOPIC + '/state')

# prevent MQTT connect errors on system startup when network services (such as DNS) are not fully up and running by
# attempting to connect to given IP:port socket and only continue when succeeding.
connect_retry_count = 10
while True:
    if isOpen(MQTT_SERVER_NAME, MQTT_SERVER_PORT):
        break
    else:
        log.info("Could not reach {}:{}. Sleeping 5 seconds before retrying ({} retries left).".format(MQTT_SERVER_NAME,
                                                                                                       MQTT_SERVER_PORT,
                                                                                                       connect_retry_count))
        time.sleep(5)
    connect_retry_count -= 1
    if connect_retry_count <= 0:
        log.error(
            "failed to establish network connection to mqtt server at {}:{}".format(MQTT_SERVER_NAME, MQTT_SERVER_PORT))
        exit(1)

client.connect(MQTT_SERVER_NAME, MQTT_SERVER_PORT, 60)
log.info("successfully connected to mqtt server {}:{}".format(MQTT_SERVER_NAME, MQTT_SERVER_PORT))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
