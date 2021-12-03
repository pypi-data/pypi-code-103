#!/usr/bin/env python3
# /usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
    Also has a minimal use of PointText and TextBlock system with reduced  codepoints
and reduced grid_size to give better resolution for large characters.
    Also shows a simple use of MQTT to control the slideshow parameters remotely
see http://pi3d.github.io/html/FAQ.html and https://www.thedigitalpictureframe.com/control-your-digital-picture-frame-with-home-assistents-wifi-presence-detection-and-mqtt/
and https://www.cloudmqtt.com/plans.html

USING exif info to rotate images

    ESC to quit, 's' to reverse, any other key to move on one.
'''
import os
import time
import random
import math
import pi3d
import sys, re, traceback, time, datetime, random, pi3d, configparser, threading, logging.handlers, pdb

from pi3d.Texture import MAX_SIZE
from PIL import Image, ExifTags, ImageFilter  # these are needed for getting exif data from images
from pi3dpf_ns.pi3dpf_base import PictureFrame2020config as config
from pi3dpf_ns.pi3dpf_base import pf
from pi3dpf_ns.pi3dpf_common import pf_common as pfc
# import pi3dpf.openweathermapToerikflowers_wi as owm
from operator import itemgetter

#####################################################
# these variables are constants
#####################################################
this_dir = os.path.dirname(__file__)
this_file = os.path.basename(__file__)
config_file = [os.path.join(os.path.dirname(pf.__file__), 'cfg', 'pf.config')]
cfg = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                                converters={'list': lambda x: [i.strip() for i in x.split(',')]})
if os.path.isfile('/home/pi/.pf/pf.config'):
    config_file.append('/home/pi/.pf/pf.config')
cfg.cfg_fname = config_file
cfg.read(config_file)
LOG_LEVEL = pfc.get_config_param(cfg, 'LOG_LEVEL')
LOG_DIR = pfc.get_config_param(cfg, 'LOG_DIR')
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, os.path.splitext(os.path.basename(__file__))[0]) + '.log'
print("for more information, check log file '{}'.".format(LOG_FILE))
pi3d_log = pi3d.Log(level=LOG_LEVEL)  # name=None, file=LOG_FILE
for h in pi3d_log.logger.handlers:
    pi3d_log.logger.removeHandler(h)
RotatingFileHandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
pi3d_log.logger.name = os.path.basename(__file__)
RotatingFileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
pi3d_log.logger.addHandler(RotatingFileHandler)
pi3d_log.HANDLER = RotatingFileHandler

pi3d_log.info("pi3d version: {}, PIL Image version: {}".format(pi3d.__version__, Image.__version__))
OWM_RETRIEVE_LOCAL_WEATHER = pfc.get_config_param(cfg, 'OWM_RETRIEVE_LOCAL_WEATHER')
PIC_LIBREOFFICE_TEMPLATE_USE = pfc.get_config_param(cfg, 'PIC_LIBREOFFICE_TEMPLATE_USE')
OWM_FORMATSTRING_USE = pfc.get_config_param(cfg, 'OWM_FORMATSTRING_USE')
if PIC_LIBREOFFICE_TEMPLATE_USE == False and OWM_FORMATSTRING_USE == False:
    OWM_RETRIEVE_LOCAL_WEATHER = False

PI3D_FT_CODEPOINT_RANGES = pfc.get_config_param(cfg, 'PI3D_FT_CODEPOINT_RANGES')
PI3D_FT_FONT = pfc.get_config_param(cfg, 'PI3D_FT_FONT')
PI3D_TB_CHAR_COUNT = pfc.get_config_param(cfg, 'PI3D_TB_CHAR_COUNT')
PIC_EXTENSIONS = pfc.get_config_param(cfg, 'PIC_EXTENSIONS')
OWM_FORMATSTRING = pfc.get_config_param(cfg, 'OWM_FORMATSTRING')
PIC_LIBREOFFICE_BITMAP_OUT = pfc.get_config_param(cfg, 'PIC_LIBREOFFICE_BITMAP_OUT')
PIC_LIBREOFFICE_BITMAP_OUTmdate = pf.getMdate(PIC_LIBREOFFICE_BITMAP_OUT)
PIC_TEXT_POSITION_FILE = pfc.get_config_param(cfg, 'PIC_TEXT_POSITION_FILE')
PIC_CLOCK_ENABLED = pfc.get_config_param(cfg, 'PIC_CLOCK_ENABLED')
PIC_CLOCK_DTFORMAT = pfc.get_config_param(cfg, 'PIC_CLOCK_DTFORMAT')
PI3D_PT_POINT_SIZE = pfc.get_config_param(cfg, 'PI3D_PT_POINT_SIZE')
PIC_IFILES_CACHE_DIR = pfc.get_config_param(cfg, 'PIC_IFILES_CACHE_DIR')
PI3D_ALEXA_ACCOUNT_USERNAME = pfc.get_config_param(cfg, 'PI3D_ALEXA_ACCOUNT_USERNAME')
PI3D_PLEX_ACCOUNT_USERNAME = pfc.get_config_param(cfg, 'PI3D_PLEX_ACCOUNT_USERNAME')
PI3D_NOW_PLAYING_MODE = pfc.get_config_param(cfg, 'PI3D_NOW_PLAYING_MODE')
now_playing_enabled = PI3D_NOW_PLAYING_MODE == 'mqtt_receiver' or PI3D_ALEXA_ACCOUNT_USERNAME != 'not-configured' or \
                      PI3D_PLEX_ACCOUNT_USERNAME != 'not-configured'
# owm_pf = owm.owm4pf(cfg, pi3d_log)

# https://www.raspberrypi.org/forums/viewtopic.php?t=218537 Hint to import unicode fonts
# pf.mk_codepoints() # need ranges from PI3D_FT_CODEPOINT_RANGES
txt_cp = {}
txt_cp = pf.mk_codepoints(PI3D_FT_CODEPOINT_RANGES, pi3d_log)
pf_opts = pf.folderOpts(config.PIC_DIR, cfg, pi3d_log, txt_cp, config.SHOW_NAMES_TM)
CODEPOINTS = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ., _-/'  # limit to 49 ie 7x7 grid_size
USE_MQTT = False
RECENT_N = 4  # shuffle the most recent ones to play before the rest
SHOW_NAMES = True
CHECK_DIR_TM = 60.0  # seconds to wait between checking if directory has changed

# check_changes() as implemented in original PictureFrame2020.py causes to block the weather scroll bar.
# Added thread to fix
pic_dir_changed = False


def check_changes_thread():
    while True:
        time.sleep(config.CHECK_DIR_TM)
        pic_dir_changed = check_changes


dir_change_thread = threading.Thread(target=check_changes_thread, daemon=True)
dir_change_thread.start()

#####################################################
# these variables can be altered using MQTT messaging
#####################################################
time_delay = config.TIME_DELAY
fade_time = config.FADE_TIME
shuffle = config.SHUFFLE
subdirectory = config.SUBDIRECTORY
date_from = None
date_to = None
quit = False
paused = False  # NB must be set to True *only* after the first iteration of the show!
#####################################################
# only alter below here if you're keen to experiment!
#####################################################
if config.KENBURNS:
    kb_up = True
    config.FIT = False
    config.BLUR_EDGES = False
if config.BLUR_ZOOM < 1.0:
    config.BLUR_ZOOM = 1.0
delta_alpha = 1.0 / (config.FPS * fade_time)  # delta alpha
last_file_change = 0.0  # holds last change time in directory structure
next_check_tm = time.time() + config.CHECK_DIR_TM  # check if new file or directory every n seconds


#####################################################
# some functions to tidy subsequent code
#####################################################
## From: https://stackoverflow.com/a/39478157/7154477
def debug_signal_handler():
    global config
    import pdb
    pdb.set_trace()
    if not config.KEYBOARD:
        import signal
        signal.signal(signal.SIGINT, debug_signal_handler)


def tex_load(fname, orientation, size=None):
    start = datetime.datetime.now()
    try:
        im = Image.open(fname)
        (w, h) = im.size
        if w > MAX_SIZE:
            im = im.resize((MAX_SIZE, int(h * MAX_SIZE / w)))
        elif h > MAX_SIZE:
            im = im.resize((int(w * MAX_SIZE / h), MAX_SIZE))
        if orientation == 2:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            im = im.transpose(Image.ROTATE_180)  # rotations are clockwise
        elif orientation == 4:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 6:
            im = im.transpose(Image.ROTATE_270)
        elif orientation == 7:
            im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
        elif orientation == 8:
            im = im.transpose(Image.ROTATE_90)
        if config.BLUR_EDGES and size is not None:
            wh_rat = (size[0] * im.size[1]) / (size[1] * im.size[0])
            if abs(wh_rat - 1.0) > 0.01:  # make a blurred background
                (sc_b, sc_f) = (size[1] / im.size[1], size[0] / im.size[0])
                if wh_rat > 1.0:
                    (sc_b, sc_f) = (sc_f, sc_b)  # swap round
                (w, h) = (round(size[0] / sc_b / config.BLUR_ZOOM), round(size[1] / sc_b / config.BLUR_ZOOM))
                (x, y) = (round(0.5 * (im.size[0] - w)), round(0.5 * (im.size[1] - h)))
                box = (x, y, x + w, y + h)
                blr_sz = (int(x * 512 / size[0]) for x in size)
                im_b = im.resize(size, resample=0, box=box).resize(blr_sz)
                im_b = im_b.filter(ImageFilter.GaussianBlur(config.BLUR_AMOUNT))
                im_b = im_b.resize(size, resample=Image.BICUBIC)
                im_b.putalpha(round(255 * config.EDGE_ALPHA))  # to apply the same EDGE_ALPHA as the no blur method.
                im = im.resize((int(x * sc_f) for x in im.size), resample=Image.BICUBIC)
                im_b.paste(im, box=(round(0.5 * (im_b.size[0] - im.size[0])),
                                    round(0.5 * (im_b.size[1] - im.size[1]))))
                im = im_b  # have to do this as paste applies in place
        tex = pi3d.Texture(im, blend=True, m_repeat=True, automatic_resize=True, free_after_load=True)
    except Exception as e:
        if config.VERBOSE:
            pi3d_log.info('''Couldn't load file {} giving error: {}'''.format(fname, e))
        tex = None
    delta = str(datetime.datetime.now() - start).split(':')
    pi3d_log.debug(
        "tex_load: {:02d}min {:03.1f}sec, fname: '{}' ({:,d} bytes)".format(int(delta[1]), float(delta[2]), fname,
                                                                            os.stat(fname).st_size))
    return tex


def tidy_name(path_name):
    name = os.path.basename(path_name).upper()
    name = ''.join([c for c in name if c in config.CODEPOINTS])
    return name


def tidy_name_new(path_name, mode='fname'):
    if mode == 'fname':
        # in mode 'fname': turn '/var/tmp/TOP.Directory/THIS.IS_AN.Example.jpg' into 'This Is An Example'
        input = os.path.splitext(os.path.basename(path_name))[0]  # file name w/o extension
    else:
        # in mode 'dname': turn '/var/tmp/TOP.directory/THIS.IS_AN.Example.jpg' into 'Top Directory'
        input = os.path.basename(os.path.dirname(path_name))
    name = ' '.join(list(map(lambda s: s.capitalize(), re.sub('[_\.]', ' ', input).split())))
    name = ''.join([c for c in name if c in txt_cp['codepoints']])
    if PI3D_TB_CHAR_COUNT > 0:
        name = name[:PI3D_TB_CHAR_COUNT]
    return name


def check_changes():
    global last_file_change
    update = False
    for root, _, _ in os.walk(config.PIC_DIR):
        mod_tm = os.stat(root).st_mtime
        if mod_tm > last_file_change:
            # modified directory does not necessarily mean a picture has changed, so let's do some more tests.
            for file in os.listdir(root):
                if os.path.isfile(os.path.join(root, file)) and \
                        os.path.splitext(file)[1].lower() in PIC_EXTENSIONS and \
                        os.stat(os.path.join(root, file)).st_mtime > last_file_change:
                    last_file_change = mod_tm
                    update = True
    #       last_file_change = mod_tm
    #       update = True
    return update


def getf_cache_or_fsys(dt_from=None, dt_to=None):
    if dt_from != None or dt_to != None:
        return get_files(dt_from, dt_to)
    else:
        iFiles_cached = pf.get_iFiles_from_cache(config.PIC_DIR, PIC_EXTENSIONS, PIC_IFILES_CACHE_DIR)
        if iFiles_cached == None:
            iFiles, nFi = get_files(dt_from, dt_to)
            pf.put_iFiles_to_cache(config.PIC_DIR, iFiles, PIC_IFILES_CACHE_DIR)
            return iFiles, nFi
        else:
            if shuffle:
                pi3d_log.info("getf_cache_or_fsys - shuffle files")
                iFiles_cached.sort(key=lambda x: x[2])  # will be later files last
                temp_list_first = iFiles_cached[-config.RECENT_N:]
                temp_list_last = iFiles_cached[:-config.RECENT_N]
                random.shuffle(temp_list_first)
                random.shuffle(temp_list_last)
                iFiles_cached = temp_list_first + temp_list_last
            else:
                pi3d_log.info("getf_cache_or_fsys - returning sorted complete list")
                # if not shuffled; sort by name
                # iFiles_cached.sort() # does not work the way I want. (I want sorted by directories, the by file name)
                iFiles_cached.sort(key=lambda x: (os.path.dirname(x[0]), x[0]))
            return iFiles_cached, len(iFiles_cached)


def get_files(dt_from=None, dt_to=None):
    startload = datetime.datetime.now()
    # dt_from and dt_to are either None or tuples (2016,12,25)
    if dt_from is not None:
        dt_from = time.mktime(dt_from + (0, 0, 0, 0, 0, 0))
    if dt_to is not None:
        dt_to = time.mktime(dt_to + (0, 0, 0, 0, 0, 0))
    global shuffle, EXIF_DATID, last_file_change
    file_list = []
    f_cnt = {'no_exif': 0, 'exif_orient_missing': 0, 'exif_date_missing': 0, 'f_not_open': 0, 'nomedia': 0,
             'total_files': 0, 'out_of_d_range': 0}
    extensions = PIC_EXTENSIONS
    picture_dir = os.path.join(config.PIC_DIR, subdirectory)
    for root, _dirnames, filenames in os.walk(picture_dir):
        pi3d_log.info("reading pictures from directory '{}'.".format(root))
        if len(_dirnames) > 0:
            for d in _dirnames:
                if os.path.exists(os.path.join(root, d, '.nomedia')):
                    pi3d_log.info("skiping pictures from directory '{}'. (dir contains .nomedia file)".format(
                        os.path.join(root, d)))
                    _dirnames.remove(d)
                    f_cnt['nomedia'] += 1
        mod_tm = os.stat(root).st_mtime  # time of alteration in a directory
        if mod_tm > last_file_change:
            last_file_change = mod_tm
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            f_cnt['total_files'] += 1
            if ext in extensions and not '.AppleDouble' in root and not filename.startswith('.'):
                file_path_name = os.path.join(root, filename)
                include_flag = True
                orientation = 1  # this is default - unrotated
                if EXIF_DATID is not None and EXIF_ORIENTATION is not None:
                    try:
                        im = Image.open(file_path_name)  # lazy operation so shouldn't load (better test though)
                        # print(filename, end="")
                    except Exception as e:
                        pi3d_log.info(
                            "Image.open for '{}' failed with error '{}'. Skipping file.".format(file_path_name, e))
                        f_cnt['f_not_open'] += 1
                        continue
                        raise  # need to see the exception before improving anything here
                    try:
                        exif_data = im._getexif()
                    except Exception as e:
                        orientation = 1
                        dt = os.path.getmtime(file_path_name)
                        f_cnt['no_exif'] += 1
                    try:
                        dt = time.mktime(time.strptime(exif_data[EXIF_DATID][:19],
                                                       '%Y:%m:%d %H:%M:%S'))  # [:19]: at times, there is a \x00 appended so only use first 19 chars, e.g. 2019:06:12 15:07:05
                    except Exception as e:
                        dt = os.path.getmtime(file_path_name)
                        f_cnt['exif_date_missing'] += 1
                        pass
                    try:
                        orientation = int(exif_data[EXIF_ORIENTATION])
                    except Exception as e:
                        orientation = 1
                        f_cnt['exif_orient_missing'] += 1
                        pass

                    if (dt_from is not None and dt < dt_from) or (dt_to is not None and dt > dt_to):
                        include_flag = False
                if include_flag:
                    file_list.append((file_path_name, orientation, os.path.getmtime(
                        file_path_name)))  # iFiles now list of tuples (file_name, orientation)
                else:
                    f_cnt['out_of_d_range'] += 1
    pi3d_log.info("Directories ignored due to .nomedia file: {:d}".format(f_cnt['nomedia']))
    pi3d_log.info(" Files w/ errors while reading exif data: {:d}".format(f_cnt['no_exif']))
    pi3d_log.info("     Files with exif orientation missing: {:d}".format(f_cnt['exif_orient_missing']))
    pi3d_log.info("            Files with exif date missing: {:d}".format(f_cnt['exif_date_missing']))
    pi3d_log.info("          Files that could not be opened: {:d}".format(f_cnt['f_not_open']))
    pi3d_log.info("           Files out of given date range: {:d}".format(f_cnt['out_of_d_range']))
    pi3d_log.info("                   Total number of files: {:d}".format(f_cnt['total_files']))
    delta = str(datetime.datetime.now() - startload).split(':')
    pi3d_log.info("get_files: loading files took {:02d}min {:03.1f}sec".format(int(delta[1]), float(delta[2])))
    if shuffle:
        file_list.sort(key=lambda x: x[2])  # will be later files last
        temp_list_first = file_list[-config.RECENT_N:]
        temp_list_last = file_list[:-config.RECENT_N]
        random.shuffle(temp_list_first)
        random.shuffle(temp_list_last)
        file_list = temp_list_first + temp_list_last
    else:
        # if not shuffled; sort by name
        # file_list.sort() # does not work the way I want. (I want sorted by directories, the by file name)
        file_list.sort(key=lambda x: (os.path.dirname(x[0]), x[0]))
    return file_list, len(file_list)  # tuple of file list, number of pictures


EXIF_DATID = None  # this needs to be set before get_files() above can extract exif date info
EXIF_ORIENTATION = None
for k in ExifTags.TAGS:
    if ExifTags.TAGS[k] == 'DateTimeOriginal':
        EXIF_DATID = k
    if ExifTags.TAGS[k] == 'Orientation':
        EXIF_ORIENTATION = k

##############################################
# MQTT functionality - see https://www.thedigitalpictureframe.com/
##############################################
iFiles = []
nFi = 0
next_pic_num = 0
if config.USE_MQTT:
    try:
        import paho.mqtt.client as mqtt


        def on_connect(client, userdata, flags, rc):
            if config.VERBOSE:
                pi3d_log.info("Connected to MQTT broker")


        def on_message(client, userdata, message):
            # TODO not ideal to have global but probably only reasonable way to do it
            global next_pic_num, iFiles, nFi, date_from, date_to, time_delay
            global delta_alpha, fade_time, shuffle, quit, paused, nexttm, subdirectory
            msg = message.payload.decode("utf-8")
            reselect = False
            if message.topic == "frame/date_from":  # NB entered as mqtt string "2016:12:25"
                try:
                    msg = msg.replace(".", ":").replace("/", ":").replace("-", ":")
                    df = msg.split(":")
                    date_from = tuple(int(i) for i in df)
                    if len(date_from) != 3:
                        raise Exception("invalid date format")
                except:
                    date_from = None
                reselect = True
            elif message.topic == "frame/date_to":
                try:
                    msg = msg.replace(".", ":").replace("/", ":").replace("-", ":")
                    df = msg.split(":")
                    date_to = tuple(int(i) for i in df)
                    if len(date_to) != 3:
                        raise Exception("invalid date format")
                except:
                    date_from = None
                reselect = True
            elif message.topic == "frame/time_delay":
                time_delay = float(msg)
            elif message.topic == "frame/fade_time":
                fade_time = float(msg)
                delta_alpha = 1.0 / (config.FPS * fade_time)
            elif message.topic == "frame/shuffle":
                shuffle = True if msg == "True" else False
                reselect = True
            elif message.topic == "frame/quit":
                quit = True
            elif message.topic == "frame/paused":
                paused = not paused  # toggle from previous value
            elif message.topic == "frame/back":
                next_pic_num -= 2
                if next_pic_num < -1:
                    next_pic_num = -1
                nexttm = time.time() - 86400.0
            elif message.topic == "frame/subdirectory":
                subdirectory = msg
                reselect = True
            elif message.topic == "frame/delete":
                f_to_delete = iFiles[pic_num][0]
                f_name_to_delete = os.path.split(f_to_delete)[1]
                move_to_dir = os.path.expanduser("~/DeletedPictures")
                if not os.path.exists(move_to_dir):
                    os.makedirs(move_to_dir)
                os.rename(f_to_delete, os.path.join(move_to_dir, f_name_to_delete))
                iFiles.pop(pic_num)
                nFi -= 1
                nexttm = time.time() - 86400.0
            if reselect:
                #       iFiles, nFi = get_files(date_from, date_to)
                iFiles, nFi = getf_cache_or_fsys(date_from, date_to)
                next_pic_num = 0


        # set up MQTT listening
        client = mqtt.Client()
        client.username_pw_set(config.MQTT_LOGIN, config.MQTT_PASSWORD)  # replace with your own id
        client.connect(config.MQTT_SERVER, config.MQTT_PORT, 60)  # replace with your own server
        client.loop_start()
        client.subscribe("frame/date_from", qos=0)
        client.subscribe("frame/date_to", qos=0)
        client.subscribe("frame/time_delay", qos=0)
        client.subscribe("frame/fade_time", qos=0)
        client.subscribe("frame/shuffle", qos=0)
        client.subscribe("frame/quit", qos=0)
        client.subscribe("frame/paused", qos=0)
        client.subscribe("frame/back", qos=0)
        client.subscribe("frame/subdirectory", qos=0)
        client.subscribe("frame/delete", qos=0)
        client.on_connect = on_connect
        client.on_message = on_message
    except Exception as e:
        if config.VERBOSE:
            print("MQTT not set up because of: {}".format(e))
##############################################

DISPLAY = pi3d.Display.create(x=0, y=0, frames_per_second=config.FPS,
                              display_config=pi3d.DISPLAY_CONFIG_HIDE_CURSOR, background=config.BACKGROUND)
CAMERA = pi3d.Camera(is_3d=False)

shader = pi3d.Shader(config.SHADER)
slide = pi3d.Sprite(camera=CAMERA, w=DISPLAY.width, h=DISPLAY.height, z=5.0)
slide.set_shader(shader)
slide.unif[47] = config.EDGE_ALPHA
slide.unif[54] = config.BLEND_TYPE

if config.KEYBOARD:
    kbd = pi3d.Keyboard()

# images in iFiles list
nexttm = 0.0
# iFiles, nFi = get_files(date_from, date_to)
iFiles, nFi = getf_cache_or_fsys(date_from, date_to)
if pf_opts.getOpt('track_last_viewed', config.PIC_DIR):
    # get last files when restarting
    last_file = pf_opts.getLastViewedFile(config.PIC_DIR).strip('\n')
    if os.path.exists(last_file):
        next_pic_num = [element[0] for element in iFiles].index(pf_opts.getLastViewedFile(config.PIC_DIR).strip('\n'))
        pi3d_log.info("resuming picture display on image #{}, name {}".format(next_pic_num, iFiles[next_pic_num][0]))
    else:
        next_pic_num = 0
else:
    next_pic_num = 0
sfg = None  # slide for background
sbg = None  # slide for foreground

# PointText and TextBlock. If SHOW_NAMES_TM <= 0 then this is just used for no images message
grid_size = math.ceil(len(config.CODEPOINTS) ** 0.5)
font = pi3d.Font(PI3D_FT_FONT, codepoints=txt_cp['codepoints'], grid_size=txt_cp['grid_size'], shadow_radius=4.0,
                 shadow=(0, 0, 0, 128))

# pic_fname
pfnm_txtb = pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'pic_fname:', {'DISPLAY': globals()['DISPLAY']}, font, CAMERA, cfg,
                       pi3d_log)
# pic_title
titl_txtb = pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'pic_title:', {'DISPLAY': globals()['DISPLAY']}, font, CAMERA, cfg,
                       pi3d_log)

PIC_CLOCK_MAXCHAR = 40
clock_txtb = pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'clock:', {'DISPLAY': globals()['DISPLAY']}, font, CAMERA, cfg,
                        pi3d_log)

# if OWM_RETRIEVE_LOCAL_WEATHER:
#  owm_info = owm_pf.updateWeatherInfo()

# if now_playing_enabled:
#  nplay_txtb = pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'now_playing:', {'DISPLAY': globals()['DISPLAY']}, font, CAMERA, cfg, pi3d_log)

# From: https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=87061&p=1659566#post_content1659595 #@@#
# flatsh = pi3d.Shader("uv_flat")
if PIC_LIBREOFFICE_TEMPLATE_USE:
    # libre  = pi3d.Texture(PIC_LIBREOFFICE_BITMAP_OUT, blend=True) #@@#
    # plane  = pi3d.Plane(w=libre.ix, h=libre.iy, z=0.1) #NB x,y both default zero puts it in the middle of the screen #@@#
    lo_templ = pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'libreoffice_to_png:', {'DISPLAY': globals()['DISPLAY']}, font,
                          CAMERA, cfg, pi3d_log)
    lo_templ.update()

wthr_scis = []
# if OWM_FORMATSTRING_USE:
#  wthr_position = []
#  for i in range(0, len(owm_info)):
#    wthr_scis.append(pf.pi3dObj(PIC_TEXT_POSITION_FILE, None, 'owm_formatstring.{}:'.format(i), {'DISPLAY': globals()['DISPLAY']}, None, None, cfg, pi3d_log))

tex_n = pf.pi3dTexThreaded(iFiles, DISPLAY, config, next_pic_num)
if nFi <= 0:
    # no images found
    if not config.USE_MQTT:
        # no images, no MQTT in use to change directory. Fail
        print("No images in directory '{}'.".format(config.PIC_DIR))
        exit(1)
    else:
        # TODO: send mqtt message
        if os.path.exists(config.NO_FILES_IMG):
            NO_FILES_IMG = config.NO_FILES_IMG
        else:
            print('generate image to state there is no file in current dir.')
            exit(1)

num_run_through = 0
while DISPLAY.loop_running():
    tm = time.time()
    if (tm > nexttm and not paused) or (tm - nexttm) >= 86400.0:  # this must run first iteration of loop
        if nFi > 0:
            nexttm = tm + time_delay
            sbg = sfg
            sfg = None
            while sfg is None:  # keep going through until a usable picture is found TODO break out how?
                pic_num = next_pic_num
                tex_n.load_next_texture()
                sfg = tex_n.tex
                #       sfg = next_tex
                #       sfg = tex_load(iFiles[pic_num][0], iFiles[pic_num][1], (DISPLAY.width, DISPLAY.height))
                next_pic_num += 1
                if next_pic_num >= nFi:
                    num_run_through += 1
                    if shuffle and num_run_through >= config.RESHUFFLE_NUM:
                        num_run_through = 0
                        random.shuffle(iFiles)
                    next_pic_num = 0

            # set the file name as the description
            #     if config.SHOW_NAMES_TM > 0.0:
            if pf_opts.getOpt('show_fname', config.PIC_DIR):
                pfnm_txtb.update(text_format="{}".format(pf_opts.getOpt('exif_for_fname', iFiles[pic_num][0])))
            else:
                pfnm_txtb.update(text_format="{}".format(" "))
            pfnm_txtb.regen()
            if pf_opts.getOpt('show_dname', config.PIC_DIR):
                # xxx , pf_opts.getOpt('pos_dname_on_fname', config.PIC_DIR)
                titl_txtb.update(text_format="{}".format(pf_opts.getOpt('title_for_dname', iFiles[pic_num][0])),
                                 pos_dname_on_fname=pf_opts.getOpt('pos_dname_on_fname', config.PIC_DIR))
            else:  # could have a NO IMAGES selected and being drawn
                titl_txtb.update(text_format="{}".format(" "))
            titl_txtb.regen()

            #      if OWM_RETRIEVE_LOCAL_WEATHER:
            #        owm_info = owm_pf.updateWeatherInfo()

            #      if now_playing_enabled:
            #        nplay_txtb.update()
            #        nplay_txtb.regen()

            if pf_opts.getOpt('show_clock', config.PIC_DIR):
                clock_txtb.update(datetime.datetime.now().strftime(PIC_CLOCK_DTFORMAT))
                clock_txtb.regen()

            if PIC_LIBREOFFICE_TEMPLATE_USE:
                lo_templ.update()

        #      if OWM_FORMATSTRING_USE:
        #        owm_info = owm_pf.updateWeatherInfo()
        #        for i in range(0, len(owm_info)):
        #          wthr_scis[i].update(owm_info[i])

        else:
            sfg = tex_load(config.NO_FILES_IMG, 1, (DISPLAY.width, DISPLAY.height))
            sbg = sfg

        a = 0.0  # alpha - proportion front image to back
        name_tm = tm + config.SHOW_NAMES_TM
        if sbg is None:  # first time through
            sbg = sfg
        slide.set_textures([sfg, sbg])
        slide.unif[45:47] = slide.unif[42:44]  # transfer front width and height factors to back
        slide.unif[51:53] = slide.unif[48:50]  # transfer front width and height offsets
        wh_rat = (DISPLAY.width * sfg.iy) / (DISPLAY.height * sfg.ix)
        if (wh_rat > 1.0 and config.FIT) or (wh_rat <= 1.0 and not config.FIT):
            sz1, sz2, os1, os2 = 42, 43, 48, 49
        else:
            sz1, sz2, os1, os2 = 43, 42, 49, 48
            wh_rat = 1.0 / wh_rat
        slide.unif[sz1] = wh_rat
        slide.unif[sz2] = 1.0
        slide.unif[os1] = (wh_rat - 1.0) * 0.5
        slide.unif[os2] = 0.0
        if config.KENBURNS:
            xstep, ystep = (slide.unif[i] * 2.0 / time_delay for i in (48, 49))
            slide.unif[48] = 0.0
            slide.unif[49] = 0.0
            kb_up = not kb_up

    if config.KENBURNS:
        t_factor = nexttm - tm
        if kb_up:
            t_factor = time_delay - t_factor
        slide.unif[48] = xstep * t_factor
        slide.unif[49] = ystep * t_factor

    if a < 1.0:  # transition is happening
        a += delta_alpha
        if a > 1.0:
            a = 1.0
        slide.unif[44] = a * a * (3.0 - 2.0 * a)
    else:  # no transition effect safe to resuffle etc
        if tm > next_check_tm:
            ##    if check_changes():
            ##      iFiles, nFi = get_files(date_from, date_to)
            if pic_dir_changed:
                iFiles, nFi = getf_cache_or_fsys(date_from, date_to)
                num_run_through = 0
                next_pic_num = 0
            next_check_tm = tm + config.CHECK_DIR_TM  # once per hour

    slide.draw()
    lo_templ.plane.draw()
    # nplay_txtb.plane.draw()
    # plane.draw()

    if nFi <= 0:
        pfnm_txtb.update(text_format="{}".format("NO IMAGES SELECTED"))
        # pfnm_txtb.P3d_TextBlock.colouring.set_colour(alpha=1.0)
        pfnm_txtb.colouring_set_colour(alpha=1.0)
        # textblock.set_text("NO IMAGES SELECTED")
        # textblock.colouring.set_colour(alpha=1.0)
        next_tm = tm + 1.0
        # text.regen()
    elif tm < name_tm:
        # this sets alpha for the TextBlock from 0 to 1 then back to 0
        dt = (config.SHOW_NAMES_TM - name_tm + tm) / config.SHOW_NAMES_TM
        alpha = max(0.0, min(1.0, 3.0 - abs(3.0 - 6.0 * dt)))
        # textblock.colouring.set_colour(alpha=alpha)
        # text.regen()
        pfnm_txtb.colouring_set_colour(alpha=alpha)
        # pfnm_txtb.P3d_TextBlock.colouring.set_colour(alpha=alpha)
        pfnm_txtb.regen()
        # titl_txtb.P3d_TextBlock.colouring.set_colour(alpha=alpha)
        titl_txtb.colouring_set_colour(alpha=alpha)
        titl_txtb.regen()
    #      nplay_txtb.colouring_set_colour(alpha=1.0)
    #      nplay_txtb.regen()

    clock_txtb.draw()
    pfnm_txtb.draw()
    titl_txtb.draw()
    #  nplay_txtb.draw()
    #  nplay_txtb.colouring_set_colour(alpha=1.0)
    #  if OWM_FORMATSTRING_USE:
    #    for i in range(0, len(owm_info)):
    #      wthr_scis[i].update(owm_info[i])

    # requires --keyboard true, -k true
    if config.KEYBOARD:
        k = kbd.read()
        if k != -1:
            nexttm = time.time() - 86400.0
        if k == 27 or quit:  # ESC
            break
        if k == ord(' '):
            paused = not paused
        if k == ord('s'):  # go back a picture
            next_pic_num -= 2
            if next_pic_num < -1:
                next_pic_num = -1
        if k == ord('d'):  # invoke debugger
            debug_signal_handler()

try:
    client.loop_stop()
except Exception as e:
    if config.VERBOSE:
        print("this was going to fail if previous try failed!")
if config.KEYBOARD:
    kbd.close()
DISPLAY.destroy()
