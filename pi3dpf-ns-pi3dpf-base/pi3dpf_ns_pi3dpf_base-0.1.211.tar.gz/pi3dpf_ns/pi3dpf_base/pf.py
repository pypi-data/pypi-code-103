import datetime
import distutils
import json
import logging
import os
import pi3d
import re
import regex
import threading
import traceback

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pi3d import opengles
from pi3d.constants import GL_SCISSOR_TEST, GLint, GLsizei

from pi3dpf_ns.pi3dpf_common import pf_common as pfc

_log = logging.getLogger('pf.py')

#
# From: https://pi3d.github.io/html/pi3d.util.html#pi3d.util.Font.Font (Font Module):
#  grid_size:
#    number rows and cols to divide 1024 pixels. For high res fonts this can be
#    changed 4 -> 16chars, 8 -> 64chars, 10 -> 100chars etc.
# Purpose:
#   Determining grid_size depends on the number of codepoints handed over to pi3d.util.Font
#   As I want this to be dynamical (some users will want to name their files in their language,
#   there must be a way for adding additional codepoints in mqttForHyperion.config (parameter ???)
#   This method allows to specify the codepoints to be added in multiple ways, multiple times (in *argv):
#     range:  '65-90' or '0x41-0x5A' or '0o101-0o132' will all add A-Z
#     string: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' or '/-+=_' or '0123456789'
def mk_codepoints(cp_list, log):
  import re, math
  ranges = list()
  r      = {}
  s = set([])
  for i in cp_list:
#   log.info ("Working on '{}'".format(i))
    m = re.search(r'(0x[0-9a-f]+|0o[0-7]+|\d+)\s*-\s*(0x[0-9a-f]+|0o[0-7]+|\d+)', i, flags=re.IGNORECASE)
    if not m:
      log.info("Treating as string: '{}'".format(i))
      for k in i:
        s.add(ord(k))
    else:
      pair = []
      for i in m.group(1), m.group(2):
        if i[0:2].lower() == '0x':
          v = int(i, base=16)
        elif i[0:2].lower() == '0o':
          v = int(i, base=8)
        elif re.match('^\d+$', i):
          v = int(i)
        else:
          log.error("unexpected input: '{}'.".format(i))
          exit(1)
        pair.append(v)
      ranges.append(pair)
  for a,b in ranges:
    for ii in range(int(a), int(b)+1):
      s.add(ii)
# print(s)
  r['codepoints'] = ''.join(list(map(lambda x: chr(x), s)))
  r['grid_size']  = math.ceil(math.sqrt(len(s)))
  log.info("required grid_size: {:d}".format(r['grid_size']))
  r['matrix'] = ''
  for i in range(0, len(s), r['grid_size']):
    r['matrix'] += "{}\n".format(r['codepoints'][i:i + r['grid_size']])
  return r # {'grid_size' : grid_size, 'codepoints' : cp_string}

def parseOwmClockFormatstring(clock_formatstring):
  res = []
  for segment in clock_formatstring.split('\n'):
    res.append({'max_len': 30, 'font_size': 0.99, 'txt': segment})
    ms = re.search('({max_len:(\d+)})', segment)
    if ms:
      res[-1]['max_len'] = ms.group(2)
      res[-1]['txt']     = res[-1]['txt'].replace(ms.group(1), '')
    mf = re.search('({font_size:(\d+\.\d+)})', segment)
    if mf:
      res[-1]['font_size'] = float(mf.group(2))
      res[-1]['txt']       = res[-1]['txt'].replace(mf.group(1), '')
  return res

def getMdate(fname):
  return os.path.getmtime(fname) if os.path.exists(fname) else 0.0


def put_iFiles_to_cache(pic_dir, iFiles, cache_dir="/var/tmp/pf/pic_name_cache"):
  cache_fname = os.path.join(cache_dir, pic_dir.strip('/').replace('/', '.'))
# cache_mdate = os.path.getmtime(cache_fname) if os.path.exists(cache_fname) else 0.0
  try:
    if not os.path.isdir(cache_dir):
      os.mkdir(cache_dir)
    with open(cache_fname, 'w', encoding='utf-8') as f:
      f.write(json.dumps(iFiles, sort_keys=True, indent=4, separators=(',', ': ')))
  except Exception as e:
    print("put_iFiles_to_cache - exception: {}".format(e))

# PIC_EXTENSIONS = ['.png', '.jpg', '.jpeg']
def get_iFiles_from_cache(pic_dir, extensions, cache_dir="/var/tmp/pf/pic_name_cache"):
  cache_fname = os.path.join(cache_dir, pic_dir.strip('/').replace('/', '.'))
# cache_mdate = os.path.getmtime(cache_fname) if os.path.exists(cache_fname) else 0.0
  _log.info("evaluating cache file {} for consistency.".format(cache_fname))
  try:
    with open(cache_fname, 'r', encoding='utf-8') as f:
      res_cached = json.load(f)
  except Exception as e:
    _log.info("get_iFiles_from_cache - open {}: {}".format(cache_fname, e))
    return None
  # compare list of current files with the cached ones
  # sorted([elemt[0] for elemt in res])
  fn_cached = {elemt[0] for elemt in res_cached} # create set() holding file names only
  res_fsys = set()
  for root, _dirnames, files in os.walk(pic_dir):
    for d in _dirnames:
      if os.path.exists(os.path.join(root, d, '.nomedia')):
        _dirnames.remove(d)
    for file in files:
      if os.path.splitext(file)[1].lower() in extensions:
        res_fsys.add(os.path.join(root, file))
  diff = fn_cached - res_fsys
  if len(diff) == 0:
    _log.info("cache file {} valid, using info instead of re-scanning dir {}".format(cache_fname, pic_dir))
    return res_cached
  _log.info("found discrepancies between cached files and available ones. Cache will not be used.")
  _log.info("Number of files cached: {:6d} in cache file {}".format(len(res_cached), cache_fname))
  _log.info("Number of files in dir: {:6d} in directory {}".format(len(res_fsys), pic_dir))
  _log.info("differences: {}".format(diff))
  return None


#        _ ____      _ _____
#       (_)___ \    | |  __ \
#  _ __  _  __) | __| | |__) |_ _ _ __ __ _ _ __ ___  ___
# | '_ \| ||__ < / _` |  ___/ _` | '__/ _` | '_ ` _ \/ __|
# | |_) | |___) | (_| | |  | (_| | | | (_| | | | | | \__ \
# | .__/|_|____/ \__,_|_|   \__,_|_|  \__,_|_| |_| |_|___/
# | |
# |_|
#
# global variables from pf.config to prevent repeated loading
PI3D_TB_CHAR_COUNT = None
PI3D_PT_POINT_SIZE = None
PI3D_TB_SPACING = None
PI3D_TB_SPACE = None
PI3D_TB_COLOR = None
PI3D_TB_JUSTIFY = None
PI3D_SCIS_LEN_PIX = None
PI3D_SCIS_FONT_POINT = None
PI3D_SCIS_FONT_COLOR = None
PI3D_SCIS_BMP_DIR = None
PI3D_FT_FONT = None
PIC_TEXT_POSITION_FILE = None
PIC_LIBREOFFICE_BITMAP_OUT = None
LOG_DIR = None
PF_HOME_DIR = None
OWM_FORMATSTRING_CONCATENATE = None
PI3D_NOW_PLAYING_BM = None
PI3D_NOW_PLAYING_COLOR = None
PI3D_NOW_PLAYING_ALIGN = None
PI3D_NOW_PLAYING_FONT_SIZE_PX = None
PI3D_NOW_PLAYING_COLOR_BG = None
PI3D_NOW_PLAYING_ALBUM_ART_SIZE = None
missing_entries = {}
positions = {}


class pi3dObj:

  def __init__(self, positionfile, bmfile, entry, glbls, font, camera, config, pi3d_log):  # P3d_PointText,
    global PI3D_PT_POINT_SIZE, PI3D_TB_SPACING, PI3D_TB_SPACE, PI3D_TB_COLOR, PI3D_TB_JUSTIFY, PI3D_TB_CHAR_COUNT
    global PIC_LIBREOFFICE_BITMAP_OUT, PF_HOME_DIR, PIC_CLOCK_MAXCHAR, PI3D_SCIS_LEN_PIX, PI3D_SCIS_FONT_POINT
    global PI3D_SCIS_FONT_COLOR, PI3D_SCIS_BMP_DIR, PI3D_FT_FONT, PIC_TEXT_POSITION_FILE, LOG_DIR
    global OWM_FORMATSTRING_CONCATENATE, PI3D_NOW_PLAYING_BM, PI3D_NOW_PLAYING_COLOR, PI3D_NOW_PLAYING_FONT_SIZE_PX
    global PI3D_NOW_PLAYING_ALIGN, PI3D_NOW_PLAYING_COLOR_BG, PI3D_NOW_PLAYING_ALBUM_ART_SIZE, positions

    self.positionfile = positionfile
    self.posFileLastRead = 0.0 # set to 1970-01-01 00:00
#   self.P3d_PointText= P3d_PointText
    self.font = font
    self.CAMERA = camera
    self.bmfile = bmfile
    self.entry = entry
    self.config = config
    self.log = pi3d_log
    self.globals = glbls
    if PI3D_PT_POINT_SIZE == None:
      # todo: set max_len depeding on entry: clock: PIC_CLOCK_MAXCHAR, pic_fname: PIC_TITLE_MAX_LENGTH, owm_formatstring: ???
      PI3D_TB_CHAR_COUNT = pfc.get_config_param(self.config, 'PI3D_TB_CHAR_COUNT')
      PI3D_PT_POINT_SIZE = pfc.get_config_param(self.config, 'PI3D_PT_POINT_SIZE')
      PI3D_TB_SPACING = pfc.get_config_param(self.config, 'PI3D_TB_SPACING')
      PI3D_TB_SPACING = 'F' if PI3D_TB_SPACING == False else PI3D_TB_SPACING # F gets converted to False by config reader
      PI3D_TB_SPACE = pfc.get_config_param(self.config, 'PI3D_TB_SPACE')
      PI3D_TB_COLOR = tuple(pfc.get_config_param(self.config, 'PI3D_TB_COLOR'))
      PI3D_TB_JUSTIFY = pfc.get_config_param(self.config, 'PI3D_TB_JUSTIFY')
      PI3D_SCIS_LEN_PIX = pfc.get_config_param(self.config, 'PI3D_SCIS_LEN_PIX')
      PI3D_SCIS_FONT_POINT = pfc.get_config_param(self.config, 'PI3D_SCIS_FONT_POINT')
      PI3D_SCIS_FONT_COLOR = pfc.get_config_param(self.config, 'PI3D_SCIS_FONT_COLOR')
      PI3D_SCIS_BMP_DIR = pfc.get_config_param(self.config, 'PI3D_SCIS_BMP_DIR')
      PI3D_FT_FONT = pfc.get_config_param(self.config, 'PI3D_FT_FONT')
      PIC_TEXT_POSITION_FILE = pfc.get_config_param(self.config, 'PIC_TEXT_POSITION_FILE')
      PIC_LIBREOFFICE_BITMAP_OUT = pfc.get_config_param(self.config, 'PIC_LIBREOFFICE_BITMAP_OUT')
      LOG_DIR = pfc.get_config_param(self.config, 'LOG_DIR')
      PF_HOME_DIR = pfc.get_config_param(self.config, 'PF_HOME_DIR')
      OWM_FORMATSTRING_CONCATENATE = pfc.get_config_param(self.config, 'OWM_FORMATSTRING_CONCATENATE')
      PI3D_NOW_PLAYING_BM = pfc.get_config_param(self.config, 'PI3D_NOW_PLAYING_BM')
      PI3D_NOW_PLAYING_COLOR = pfc.get_config_param(self.config, 'PI3D_NOW_PLAYING_COLOR')
      PI3D_NOW_PLAYING_COLOR_BG = pfc.get_config_param(self.config, 'PI3D_NOW_PLAYING_COLOR_BG')
      PI3D_NOW_PLAYING_ALIGN = pfc.get_config_param(self.config, 'PI3D_NOW_PLAYING_ALIGN')
      PI3D_NOW_PLAYING_ALBUM_ART_SIZE = pfc.get_config_param(self.config, 'PI3D_NOW_PLAYING_ALBUM_ART_SIZE')
      if not os.path.exists(PI3D_SCIS_BMP_DIR):
        os.mkdir(PI3D_SCIS_BMP_DIR)


    self.x            = 0
    self.expr_x       = ""
    self.y            = 0
    self.expr_y       = ""
    self.tb_font_size = 0.99 # makes sure point_size is obeyed by default
    self.max_len      = PI3D_TB_CHAR_COUNT
    self.point_size   = PI3D_PT_POINT_SIZE
    self.spacing      = PI3D_TB_SPACING
    self.space        = PI3D_TB_SPACE
    self.color        = PI3D_TB_COLOR
    self.justify      = PI3D_TB_JUSTIFY
    self.posDebug     = False
    # stuff specific to objects manipulated using glScissors
    self.scis_text    = None
    self.len_pix      = PI3D_SCIS_LEN_PIX
    self.font_point   = PI3D_SCIS_FONT_POINT
    self.font_color   = PI3D_SCIS_FONT_COLOR
    self.plane_x      = self.x
    self.start_x      = self.x
    self.plane_y      = self.y
    self.glScis_idx   = 0
    self.glScis_Image = [Image.new("RGB", (4,4), (0,0,0))] # simple 1 pixel image to make self.glScis_Image.height/self.Image.width available
    self.glScis_x     = 0
    self.glScis_y     = 0
    self.glScis_h     = 0
    self.glScis_w     = 0
    self.glScis_wthr  = 'no weather info'
    ### if automatic_resize=False in pi3d.Texture() is removed, display on RPi3 is ok. But not on RPi4 (needed for glScissors)
    # +------------------------+-----+-----------+-------------------------------------+
    # | Model and PCB Revision | RAM | Revision  | Hardware Revision Code from cpuinfo |
    # +------------------------+-----+-----------+-------------------------------------+
    # | Pi 3 Model B           | 1GB | 1.2       | a02082 (Sony, UK)                   |
    # | Pi 3 Model B           | 1GB | 1.2       | a22082 (Embest, China)              |
    # | Pi 3 Model B+          | 1GB | 1.3       | a020d3 (Sony, UK)                   |
    # +------------------------+-----+-----------+-------------------------------------+
    rev = 'unknown'
    self.auto_resize=False
    with open('/proc/cpuinfo', 'r') as ci:
     for line in ci.readlines():
       if 'Revision' in line:
         rev = line[-7:-1]
    if rev in ['a02082', 'a22082', 'a020d3']:
      self.auto_resize=None
    self.log.info("pi3d.Texture(automatic_resize = {}) # rev = {}".format(self.auto_resize, rev))

    # stuff for TextBlock with text_type == 'Texture'
    self.text_type    = 'uninitialized' # text_type can only change during init
    self.text_format  = None
    self.plane        = None
    # positions is mainly used to position the 'pic_title:' object at the 'pic_fname:' location when .pf-opts parameter pos_dname_on_fname=true
    positions[self.entry]      = {}
    positions[self.entry]['x'] = self.x
    positions[self.entry]['y'] = self.y
    self.flatsh= pi3d.Shader("uv_flat")

    if self.entry[:18] == 'libreoffice_to_png':
      self.type = 'Texture'
      self.getPositionFromFile(init=True)  # set init=True to suppress logging
      if os.path.exists(PIC_LIBREOFFICE_BITMAP_OUT):
        self.flatsh= pi3d.Shader("uv_flat")
        self.image = Image.open(PIC_LIBREOFFICE_BITMAP_OUT)
      else:
        self.image = Image.new("RGB", (4,4), (0, 0, 0))  # there seems to be new pi3d code requiring size % 4 == 0

      self.bmfile = self.image
      self.PIC_LIBREOFFICE_BITMAP_OUTmdate = 0.0
      self.libre  = pi3d.Texture(self.image, blend=True, automatic_resize=False) #@@#
      self.plane  = pi3d.Plane(w=self.libre.ix, h=self.libre.iy, z=0.1) #NB x,y both default zero puts it in the middle of the screen #@@#
    elif self.entry[:11] == 'now_playing':
      self.type = 'Texture'
      self.now_playing_mdate = -1
      self.getPositionFromFile(init=True)  # set init=True to suppress logging
      # self.now_playing_png = "{}.png".format(os.path.splitext(PI3D_NOW_PLAYING_HTML)[0])
      # self.now_playing_transp_fname = "{}-transparent.png".format(os.path.splitext(PI3D_NOW_PLAYING_HTML)[0])
      if os.path.exists(PI3D_NOW_PLAYING_BM):
        self.flatsh = pi3d.Shader("uv_flat")
        self.libre = pi3d.Texture(file_string=PI3D_NOW_PLAYING_BM)
        self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
        self.bmfile = Image.open(PI3D_NOW_PLAYING_BM)
      else:
        self.log.warning("no image '{}' found. Disabling now-playing".format(PI3D_NOW_PLAYING_BM))
    elif self.entry[:16] == 'owm_formatstring':
      self.type = 'ScissorsScroll'
      self.getPositionFromFile(init=True) # set init=True to suppress logging
      self.scis_bmp_fname = os.path.join(PI3D_SCIS_BMP_DIR, self.entry.replace('.', '_').replace(':','')+'.png')
    else:
      self.type = 'TextBlock'
      self.getPositionFromFile(init=True)  # set init=True to suppress logging
      if self.text_type == 'Texture':
        self.image = Image.new("RGB", (4,4), (0, 0, 0))  # there seems to be new pi3d code requiring size % 4 == 0
        self.libre = pi3d.Texture(file_string=self.image)
        self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
        self.plane.position(x=self.x, y=self.y, z=0.1)
        self.log.info("pi3d.Plane for {} - x={:+.2f}, y={:+.2f}".format(entry, self.x, self.y))
        self.bmfile = self.image
      else:
        self.P3d_PointText = pi3d.PointText(self.font, self.CAMERA, max_chars=PI3D_TB_CHAR_COUNT+1, point_size=PI3D_PT_POINT_SIZE)
        self.P3d_TextBlock = pi3d.TextBlock(x=self.x, y=self.y, z=0.1, rot=0.0, char_count=self.max_len, text_format="{}".format(" "), size=self.tb_font_size, spacing=self.spacing, space=self.space, colour=self.color)
        self.P3d_PointText.add_text_block(self.P3d_TextBlock)
        self.log.info("pi3d.TextBlock for {} - x={:+.2f}, y={:+.2f}, size={:+.2f}, spacing={}, space={}, colour={}".format(entry, self.x, self.y, self.tb_font_size, self.spacing, self.space, self.color))
    self.posFileLastRead = 0.0  # set to 1970-01-01 00:00 to make sure initialization is run through again on arrival of first weather text


  def getPositionFromFile(self, init=False):  # , bmfile, self.entry, globals
    global missing_entries
    entry_found = False
    if self.bmfile != None:
      if hasattr(self.bmfile, 'size'):
        self.globals.update({'BM_IMG': self.bmfile})
      elif hasattr(self.bmfile, 'filename'):
        BM_IMG = Image.open(self.bmfile)
        self.globals.update({'BM_IMG': BM_IMG})

    # search parameters x=;y=font_size=;max_len=  ;point_size= ;spacing=[CMF] ;space= ;color= ;justify= and process
    with open(self.positionfile, 'r') as f:
      for line in f:
        if not re.match('^'+self.entry+':?', line):
          continue
        self.log.pos_debug("getPositionFromFile - reading properties for entry {}".format(self.entry))
        val_change  = 0
        entry_found = True
        expr_x = "undef"; expr_y = "undef"; expr_fs = "undef"; expr_ml = "undef"; expr_ps = "undef"; expr_spng = "undef"; expr_sp = "undef"; expr_col = "undef"; expr_jus = "undef";

        self.posFileLastRead = os.path.getmtime(self.positionfile)
        # pi3d.TextBlock: text_type =
        m = re.search('^' + self.entry + r':?.*text_type\s*=\s*(PointText|Texture)', line.rstrip())
        if m:
          text_type = m.group(1)
          if init == True and text_type != self.text_type:
            if self.text_type == 'uninitialized':
              self.text_type = text_type
            elif self.text_type != text_type:
              self.log.error("getPositionFromFile - new: text_type='{}' (old: '{}'). Entry: '{}', File: '{}'".format(text_type, self.text_type, self.entry, self.positionfile))
              self.log.info("getPositionFromFile - text_type must not be changed after initialization.")
              exit(1)
            self.log.info("getPositionFromFile - new: text_type='{}' (old: '{}'). Entry: '{}', File: '{}'".format(text_type, self.text_type, self.entry, self.positionfile))
        else:
          self.text_type = 'PointText'

        # pi3d.TextBlock: x =
        m = re.search('^' + self.entry + r':?.*\bx\b\s*=\s*([^;]+)', line.rstrip())
        if m:
          try:
            self.expr_x = m.group(1)
            x = eval(m.group(1), self.globals)
            if init == False and x != self.x:
              val_change += 1
              self.log.info("getPositionFromFile - new: x='{:.2f}' (old: '{:.2f}'). Entry: '{}', File: '{}'".format(x, self.x, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
                self.P3d_TextBlock.set_position(x=x, y=self.y)
              elif self.type == 'TextBlock' and self.text_type == 'Texture':
                self.log.info("getPositionFromFile - self.plane.position(x={}, y={})".format(x, self.y))
                self.plane.position(x, self.y, 4.0)
            self.x = x
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'x={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting x=0")
            x = 0
            self.expr_x = "invalid: {}".format(m.group(1))

        # pi3d.TextBlock: y =
        m = re.search('^' + self.entry + r':?.*\s*\by\b\s*=\s*([^;]+)', line.rstrip())
        if m:
          try:
            self.expr_y = m.group(1)
            y = eval(m.group(1), self.globals)
            if init == False and y != self.y:
              val_change += 1
              self.log.info("getPositionFromFile - new: y='{:.2f}' (old: '{:.2f}'). Entry: '{}', File: '{}'".format(y, self.y, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
#               import pdb; pdb.set_trace()
                self.P3d_TextBlock.set_position(x=self.x, y=y)
              elif self.type == 'TextBlock' and self.text_type == 'Texture':
                self.log.info("getPositionFromFile - self.plane.position(x={}, y={})".format(self.x, y))
                self.plane.position(self.x, y, 4.0)
            self.y = y
            self.expr_y = m.group(1)
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'y={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting y=0")
            expr_y = m.group(1)
            y = 0
            self.expr_y = "invalid: {}".format(m.group(1))

        # pi3d.TextBlock: tb_font_size (0...0.9999)
        m = re.search('^' + self.entry + ':?.*\s*tb_font_size\s*=\s*(\d+\.\d+)', line.rstrip())
        if m:
          try:
            expr_fs = m.group(1)
            tb_font_size = float(m.group(1))
            if init == False and tb_font_size != self.tb_font_size:
              val_change += 1
              self.log.info("getPositionFromFile - new: tb_font_size='{:.2f}' (old: '{:.2f}'). Entry: '{}', File: '{}'".format(tb_font_size, self.tb_font_size, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
                self.P3d_TextBlock.set_text(size=tb_font_size)
            self.tb_font_size = tb_font_size
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'tb_font_size={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting tb_font_size=0.99")
            tb_font_size = 0.99 # todo: get default value PIC_TITLE_MAX_LENGTH!!WRONG from pf.config

        # internal: max_len, not dynamicaly changable
        m = re.search('^' + self.entry + ':?.*\s*max_len\s*=\s*(\d+)', line.rstrip())
        if m:
          try:
            expr_ml = m.group(1)
            max_len = int(m.group(1))
            if init == False and max_len != self.max_len:
              val_change += 1
              self.log.info("getPositionFromFile - new: max_len='{}' (old: '{}'). Entry: '{}', File: '{}'".format(max_len, self.max_len, self.entry, self.positionfile))
            self.max_len = max_len
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'max_len={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting max_len={}".format(PIC_TITLE_MAX_LENGTH))
            max_len = PIC_TITLE_MAX_LENGTH

        #  pi3d.PointText: point_size, not dynamicaly changable
        m = re.search('^' + self.entry + ':?.*\s*point_size\s*=\s*(\d+)', line.rstrip())
        if m:
          try:
            expr_ps    = m.group(1)
            point_size = int(m.group(1))
            if init == False and point_size != self.point_size:
              val_change += 1
              self.log.info("getPositionFromFile - new: point_size='{}' (old: '{}'). Entry: '{}', File: '{}'".format(point_size, self.point_size, self.entry, self.positionfile))
            self.point_size = point_size
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'point_size={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting point_size={}".format(PI3D_PT_POINT_SIZE))
            point_size = PI3D_PT_POINT_SIZE # todo: get default value PI3D_PT_POINT_SIZE from pf.config

        # expr_ps = "undef"; expr_sp = "undef"; expr_col = "undef"; expr_jus = "undef";

        # pi3d.TextBlock: spacing=[CMF]
        m = re.search('^' + self.entry + ':?.*\s*spacing\s*=\s*([CMF])', line.rstrip())
        if m:
          try:
            expr_spng = m.group(1)
            spacing   = m.group(1)
            if init == False and spacing != self.spacing:
              val_change += 1
              self.log.info("getPositionFromFile - new: spacing='{}' (old: '{}'). Entry: '{}', File: '{}'".format(spacing, self.spacing, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
                self.P3d_TextBlock.set_text(spacing=spacing)
            self.spacing = spacing
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'spacing={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting spacing={}".format(PI3D_TB_SPACING))
            spacing = PI3D_TB_SPACING # todo: get default value PI3D_TB_SPACING from pf.config

        # pi3d.TextBlock: space=
        m = re.search('^' + self.entry + ':?.*\s*space\s*=\s*(\d+\.\d+)', line.rstrip())
        if m:
          try:
            expr_sp = m.group(1)
            space   = float(m.group(1))
            if init == False and space != self.space:
              val_change += 1
              self.log.info("getPositionFromFile - new: space='{}' (old: '{}'). Entry: '{}', File: '{}'".format(space, self.space, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
                self.P3d_TextBlock.set_text(space=space)
            self.space = space
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'space={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting space={:4.2f}".format(PI3D_TB_SPACE))
            space = PI3D_TB_SPACE

        # pi3d.TextBlock: color= (0.99, 0.99, 0.99, 0.99) # (R,G,B, Alpha)
        m = re.search('^' + self.entry + ':?.*\s*color\s*=\s*(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+),\s*(\d+\.\d+)', line.rstrip())
        if m:
          try:
            expr_col= "({}, {}, {}, {})".format(m.group(1),m.group(2),m.group(3),m.group(4))
            color   = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
            if init == False and color != self.color:
              val_change += 1
              self.log.info("getPositionFromFile - new: color='{}' (old: '{}'). Entry: '{}', File: '{}'".format(color, self.color, self.entry, self.positionfile))
              if self.type == 'TextBlock' and self.text_type == 'PointText':
                self.P3d_TextBlock.colouring.set_colour(color)
            self.color = color
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'color={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting color={}".format(PI3D_TB_COLOR))
            color = PI3D_TB_COLOR

        # pi3d.TextBlock: justify= # Justification position. 0.0=Left, 0.5=Center, not dynamicaly changable
        m = re.search('^' + self.entry + ':?.*\s*justify\s*=\s*(\d+\.\d+)', line.rstrip())
        if m:
          try:
            expr_jus= m.group(1)
            justify = float(m.group(1))
            if init == False and justify != self.justify:
              val_change += 1
              self.log.info("getPositionFromFile - new: justify='{}' (old: '{}'). Entry: '{}', File: '{}'".format(justify, self.justify, self.entry, self.positionfile))
            self.justify = justify
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'justify={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting justify={:4.2f}".format(PI3D_TB_JUSTIFY))
            justify = PI3D_TB_JUSTIFY # todo: get default value PI3D_TB_SPACE from pf.config


        # glScissorsScroll: len_pix
        m = re.search('^' + self.entry + ':?.*\s*len_pix\s*=\s*([^;]+)', line.rstrip())
        if m:
          try:
            expr_len_pix= m.group(1)
            len_pix = int(m.group(1))
            if init == False and len_pix != self.len_pix:
              val_change += 1
              self.log.info("getPositionFromFile - new: len_pix='{}' (old: '{}'). Entry: '{}', File: '{}'".format(len_pix, self.len_pix, self.entry, self.positionfile))
            self.len_pix = len_pix
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'len_pix={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting len_pix={:d}".format(PI3D_SCIS_LEN_PIX))
            len_pix = PI3D_SCIS_LEN_PIX

        # glScissorsScroll: font_point
        m = re.search('^' + self.entry + ':?.*\s*font_point\s*=\s*(\d+)', line.rstrip())
        if m:
          try:
            expr_font_point= m.group(1)
            font_point = int(m.group(1))
            if init == False and font_point != self.font_point:
              val_change += 1
              self.log.info("getPositionFromFile - new: font_point='{}' (old: '{}'). Entry: '{}', File: '{}'".format(font_point, self.font_point, self.entry, self.positionfile))
            self.font_point = font_point
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'font_point={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting font_point={:d}".format(PI3D_SCIS_FONT_POINT))
            font_point = PI3D_SCIS_FONT_POINT

        # glScissorsScroll: font_color
        m = re.search('^' + self.entry + ':?.*\s*font_color\s*=\s*(black|white)', line.rstrip())
        if m:
          try:
            expr_font_color= m.group(1)
            font_color = m.group(1)
            if init == False and font_color != self.font_color:
              val_change += 1
              self.log.info("getPositionFromFile - new: font_color='{}' (old: '{}'). Entry: '{}', File: '{}'".format(font_color, self.font_point, self.entry, self.positionfile))
            self.font_color = font_color
          except Exception as e:
            self.log.info("getPositionFromFile - unable evaluating expression 'font_color={}' in file '{}', self.entry '{}'.\nReason: {}".format(m.group(1),self.positionfile, self.entry, str(e)))
            self.log.info("getPositionFromFile - Setting font_color{:d}".format(PI3D_SCIS_FONT_COLOR))
            font_point = PI3D_SCIS_FONT_COLOR

        # self.posDebug
        m = re.search('^' + self.entry + ':?.*\s*debug\s*=\s*(yes|true)', line.rstrip())
        self.posDebug = True if m else False


        if self.type == 'ScissorsScroll' and val_change == True:
          self.log.info("a)         entry: {}".format(self.entry))
          self.log.info("a)   Display - w: {:+8.2f}, h: {:+8.2f}".format(self.globals['DISPLAY'].width, self.globals['DISPLAY'].height))
          if hasattr(self, 'Image'):
            self.log.info("a)     Image - w: {:+8.2f}, h: {:+8.2f}".format(self.Image.width,   self.Image.height))
            self.log.info("a)     Image - x: {:+8.2f}, y: {:+8.2f}".format(self.x,   self.y))
          if hasattr(self, 'glScis_x'):
            self.log.info("a) glScissor - x: {:+8.2f}, y: {:+8.2f} # x=0, y=0 is at bottom left corner".format(self.glScis_x,   self.glScis_y))
            self.log.info("a) glScissor - w: {:+8.2f}, h: {:+8.2f}".format(self.glScis_w,   self.glScis_h))
            if self.glScis_x < 0 or self.glScis_x > self.globals['DISPLAY'].height:
              self.log.warning("glScis_x={} is out of visible range".format(self.glScis_x))
            if self.glScis_y < 0 or self.glScis_y > self.globals['DISPLAY'].width:
              self.log.warning("glScis_y={} is out of visible range".format(self.glScis_y))

        self.log.info("getPositionFromFile - {} {} modifications detected in {}".format(self.entry, val_change, self.positionfile))
        positions[self.entry]           = {}
        positions[self.entry]['x']      = self.x
        positions[self.entry]['expr_x'] = self.expr_x
        positions[self.entry]['y']      = self.y
        positions[self.entry]['expr_y'] = self.expr_y
        return val_change > 0 # (self.x, self.y, self.tb_font_size, self.max_len, self.point_size, self.spacing, self.space, self.color, self.justify)

    if not entry_found:
      self.log.warning("getPositionFromFile - {} not found in {}".format(self.entry, self.positionfile))


    self.log.info("getPositionFromFile - {} {} modifications detected in {}".format(self.entry, val_change, self.positionfile))
    return val_change > 0 # (self.x, self.y, self.tb_font_size, self.max_len, self.point_size, self.spacing, self.space, self.color, self.justify)

  def text_to_image(self, text_format):
    COL_BLACK = (  0,   0,   0)
    COL_WHITE = (255, 255, 255)
    text_format = ' ' if text_format == '' else text_format  # numpy array not the way needed when string empty
    col_font = COL_WHITE if self.font_color == 'white' else COL_BLACK
    col_back = COL_BLACK if self.font_color == 'white' else COL_WHITE
    image = Image.new("RGB", (4, 4), col_back)
    draw  = ImageDraw.Draw(image)
    # Make image 3 times the needed size to improve quality
    font_3  = ImageFont.truetype(PI3D_FT_FONT, self.font_point * 3)
    # determine space needed by given text.
    dim_3   = draw.textsize(text_format, font_3)
    image = Image.new('RGB', (dim_3[0], dim_3[1]+30), col_back)
    draw  = ImageDraw.Draw(image)
    font  = ImageFont.truetype(PI3D_FT_FONT, self.font_point)
    draw.text((0,0), text_format, col_font, font=font_3)
    # make background transparent
#   print(self.entry)
#    import pdb;
#    if self.entry[:16] == 'owm_formatstring':
#      pdb.set_trace()
    img_trans = self.black_to_transparency_gradient(image) if self.font_color == 'white' else self.white_to_transparency_gradient(image)
    # resize to requested point_size and save image
    dim   = draw.textsize(text_format, font)
    img_resized = img_trans.resize(dim, Image.ANTIALIAS)
    if img_resized.size[0] > self.globals['DISPLAY'].width and self.entry[:16] != 'owm_formatstring':
      self.log.warning("text_to_image - black bar caution - text '{}' larger than display.".format(text_format))
      self.log.info("Image width before crop: {}px, display width: {}px".format(img_resized.size[0], self.globals['DISPLAY'].width))
      self.log.info("img_resized.crop({}, {}, {}, {})".format(0, 0, self.globals['DISPLAY'].width, img_resized.size[1]))
    if self.posDebug:
      if not os.path.isdir(os.path.join(PF_HOME_DIR, 'dbg')):
        os.mkdir(os.path.join(PF_HOME_DIR, 'dbg'))
      path_img_3 = os.path.join(PF_HOME_DIR, 'dbg', re.sub(':', '', self.entry)) + '_x3.png'
      image.save(path_img_3)
      path_img = os.path.join(PF_HOME_DIR, 'dbg', re.sub(':', '', self.entry)) + '.png'
      img_resized.save(path_img)
      path_text = os.path.join(PF_HOME_DIR, 'dbg', re.sub(':', '', self.entry)) + '.txt'
      with open(path_text, 'w') as tf:
        tf.write(text_format)
      self.log.info("text_to_image - {} wrote image {} and text file {}".format(self.entry, path_img, path_text))
    return img_resized


  def update(self, text_format=None, pos_dname_on_fname=False):
    if os.path.getmtime(self.positionfile) > self.posFileLastRead:
      self.getPositionFromFile()
      self.redoScisorsCalculations = True
#   self.log.info("pi3dObj: entry={} type={} text_type={}".format(self.entry, self.type, self.text_type))

    if self.type == 'TextBlock' and self.text_type in ['PointText', 'Texture']:
      x, y = (self.x, self.y)
      if pos_dname_on_fname and self.entry[:9] == 'pic_title' and 'pic_fname:' in positions.keys():
        # position the 'pic_title:' object at the 'pic_fname:' location when .pf-opts parameter pos_dname_on_fname=true
        if self.text_type == 'PointText':
          x, y = (positions['pic_fname:']['x'], positions['pic_fname:']['y'])
        elif self.text_type == 'Texture':
          # x and y for textures are from the object's centre. So object size must be taken into account to get alignment right
          self.evalTexturePosition(pos_dname_on_fname)
          x, y = (self.x, self.y)
      if self.text_type == 'PointText':
        self.P3d_TextBlock.set_position(x=x, y=y)
      elif self.text_type == 'Texture':
        self.plane.position(x=x, y=y, z=0.2)
        if self.posDebug:
          self.log.info("update - plane.position(x={:+7.1f}, y={:+7.1f}) # entry: {} (pos_dname_on_fname={})".format(x, y, self.entry, 'True' if pos_dname_on_fname else 'False'))

    if self.type == 'ScissorsScroll':  # and text_format != None
      ### start calulations for glScissors
      ### opengles.glScissors:
      ##   From: /usr/local/lib/python3.7/dist-packages/pi3d/sprite/ScissorBall.py
      ##     #NB the screen coordinates for glScissor have origin in BOTTOM left
      ##   From: https://research.ncl.ac.uk/game/mastersdegree/graphicsforgames/scissorsandstencils/
      ##     Like other OpenGL states, testing against a scissor region when rendering is
      ##     enabled with glEnable, using the GL_SCISSOR_TEST symbolic constant. There
      ##     can be only one scissor region active at a time, and the area this scissor
      ##     region covers is set by the glScissor OpenGL function. This takes 4
      ##     parameters - the x and y axis start positions of the scissor region, and the
      ##     x and y axis size of the region. Like glViewport, these parameters are in
      ##     screen space, and so are measured in pixels. It's worth noting that scissor
      ##     testing also influences glClear - it'll only clear what's inside the
      ##     scissor region, if scissor testing is enabled.
      if self.redoScisorsCalculations:
        self.plane_x = self.x
        self.start_x = self.x
        self.plane_y = self.y
      self.glScis_x = self.globals['DISPLAY'].width  // 2 + self.x # was: self.plane_x
      self.glScis_y = self.globals['DISPLAY'].height // 2 + self.y - self.glScis_Image[self.glScis_idx].height // 2 # position refers to plane's center.
      self.glScis_h = self.glScis_Image[self.glScis_idx].height
      self.glScis_w = self.len_pix
      if self.redoScisorsCalculations:
        self.log.info("b)         entry: {}".format(self.entry))
        self.log.info("b)   Display - w: {:+8.2f}, h: {:+8.2f}".format(self.globals['DISPLAY'].width, self.globals['DISPLAY'].height))
        self.log.info("b)     Image - w: {:+8.2f}, h: {:+8.2f}".format(self.glScis_Image[self.glScis_idx].width, self.glScis_Image[self.glScis_idx].height))
        self.log.info("b)     Image - x: {:+8.2f}, y: {:+8.2f}".format(self.x,   self.y))
        self.log.info("b) glScissor - x: {:+8.2f}, y: {:+8.2f} # x=0, y=0 is at bottom left corner".format(self.glScis_x,   self.glScis_y))
        self.log.info("b) glScissor - w: {:+8.2f}, h: {:+8.2f}".format(self.glScis_w,   self.glScis_h))
        self.redoScisorsCalculations = False

    if self.type == 'TextBlock' and text_format != None:
      if self.text_type == 'PointText':
        self.P3d_TextBlock.set_text(text_format=text_format)
      elif self.text_type == 'Texture' and text_format != self.text_format:
        self.text_format = text_format
        self.flatsh= pi3d.Shader("uv_flat")
        self.image = self.text_to_image(text_format)
        self.libre = pi3d.Texture(file_string=self.image, automatic_resize=False)
        # todo: we need to change width and height. And place title on file name location if pos_dname_on_fname=yes
        self.evalTexturePosition(pos_dname_on_fname)
        self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
        if self.posDebug:
           self.log.info("pi3d.Plane(x={}, y={}, w={}, h={}) # {}".format(self.x, self.y, self.libre.ix, self.libre.iy, self.entry))
        self.plane.set_draw_details(self.flatsh, [self.libre])

    elif self.type == 'ScissorsScroll' and text_format != None:
      if text_format == '':
        if self.glScis_wthr == 'no weather info':
          # weather not updated, so we need to retrieve the old information
          path_text = os.path.join(PF_HOME_DIR, 'dbg', re.sub(':', '', self.entry)) + '.txt'
          try:
            with open(path_text, 'r') as tf:
              text_format = tf.read()
            self.glScis_wthr = text_format
          except:
            self.log.info("update - file {} is not available".format(path_text))
        else:
          text_format = self.glScis_wthr

      if text_format != self.scis_text:
        # text changed, generate new image containing the text
        self.log.info("detected (scrolling) text change for {} old: {} new: {}".format(self.entry, self.scis_text, text_format))
        self.scis_text  = text_format
        self.glScis_idx = 0
        img_resized     = self.text_to_image(text_format)
        img_resized.save(self.scis_bmp_fname)
        self.log.info("saved unsplit image {} for entry {}".format(self.scis_bmp_fname, self.entry))
        # save text so it can be reloaded on restart, when weather information is still sufficiently fresh
        path_text = os.path.join(PF_HOME_DIR, 'dbg', re.sub(':', '', self.entry)) + '.txt'
        if not os.path.isdir(os.path.join(PF_HOME_DIR, 'dbg')):
          os.mkdir(os.path.join(PF_HOME_DIR, 'dbg'))
        with open(path_text, 'w') as tf:
          tf.write(text_format)
        caution_limit = 4000
        if img_resized.size[0] > caution_limit: # self.globals['DISPLAY'].width:
          self.log.info("black bar caution - text length {}px exceeds max {}px, splitting on OWM_FORMATSTRING_CONCATENATE='{}'".format(img_resized.size[0], caution_limit, OWM_FORMATSTRING_CONCATENATE))
          self.glScis_Image = []
          for txt_fmt_split in text_format.split(OWM_FORMATSTRING_CONCATENATE):
            self.glScis_Image.append(self.text_to_image(txt_fmt_split))
            if self.glScis_Image[-1].size[0] > caution_limit: # self.globals['DISPLAY'].width:
              self.log.warning("black bar caution - slice {} still exceeds max width ({}px)".format(len(self.glScis_Image)-1, caution_limit))
              self.log.info("black bar caution - slice text: '{}'".format(txt_fmt_split))
        else:
          self.glScis_Image = [Image.open(self.scis_bmp_fname)]
        self.log.info("number of images: {}".format(len(self.glScis_Image)))
        self.glScis_plane = []
        self.glScis_libre = []
        for icnt in range(0,len(self.glScis_Image)):
          # initialize pi3d variables
          self.flatsh     = pi3d.Shader("uv_flat")
          # self.libre    = pi3d.Texture(self.scis_bmp_fname) ### if automatic_resize=False is removed, display on RPi3+RPi4 is ok. 
          # self.plane.set_draw_details(self.flatsh, [self.libre])
          self.glScis_plane.append(pi3d.Plane(x=self.x, y=self.y, w=self.glScis_Image[icnt].size[0], h=self.glScis_Image[icnt].size[1], z=4.0))

          self.glScis_libre.append(pi3d.Texture(self.glScis_Image[icnt], automatic_resize=self.auto_resize)) 
          self.glScis_plane[icnt].set_draw_details(self.flatsh, [self.glScis_libre[icnt]])

      # even if text has not changed, we need to shift the picture (=plane) a little
      # opengles.glScissor(GLint(540), GLint(960),  GLsizei(200), GLsizei(-100))
      # plane.position(x, y, z)
      opengles.glScissor(GLint(self.glScis_x), GLint(self.glScis_y), GLsizei(self.glScis_w), GLsizei(self.glScis_h))
      self.glScis_plane[self.glScis_idx].position(self.plane_x, self.plane_y, 4.0)
      opengles.glEnable(GL_SCISSOR_TEST)
      self.glScis_plane[self.glScis_idx].draw()
      opengles.glDisable(GL_SCISSOR_TEST)
      self.plane_x -= 4
      if self.posDebug:
        print("{} idx={} x={:<+6d} y={:<+6d} plane_x={:<+6d} plane_y={:<+6d} len_pix={:<6d} Image_w={:<6d} Image_h={:<6d} glScis_x={:<+6d} glScis_y={:<+6d}{}".format(
          self.entry, self.glScis_idx, self.x, self.y, self.plane_x, self.plane_y, self.len_pix, self.glScis_Image[self.glScis_idx].width, self.glScis_Image[self.glScis_idx].height, self.glScis_x, self.glScis_y, " "*30), end='\r')

      if self.plane_x < -self.glScis_Image[self.glScis_idx].width // 2:
        self.glScis_idx = self.glScis_idx + 1 if self.glScis_idx < len(self.glScis_Image)-1 else 0
        self.plane_x = self.start_x + self.glScis_Image[self.glScis_idx].width // 2 + self.len_pix

    elif self.entry[:11] == 'now_playing':
      try:
        # mdate_notrans = -1 if not os.path.exists(PI3D_NOW_PLAYING_BM) else os.path.getmtime(PI3D_NOW_PLAYING_BM)
        mdate_trans = 1 if not os.path.exists(PI3D_NOW_PLAYING_BM) else os.path.getmtime(PI3D_NOW_PLAYING_BM)
        # self.log.debug("updating now_playing. x={}, y={}, type: {}, text_type: {}".format(self.x, self.y, self.type, self.text_type))
        if mdate_trans > self.now_playing_mdate:
          self.now_playing_mdate = mdate_trans
          self.bmfile = Image.open(PI3D_NOW_PLAYING_BM)
          self.getPositionFromFile()
          self.log.info("now_playing - '{}' updated. x={}, y={}, w={}, h={}, ".format(
            PI3D_NOW_PLAYING_BM, self.x, self.y, self.bmfile.size[0], self.bmfile.size[1]))
        self.libre = pi3d.Texture(PI3D_NOW_PLAYING_BM, blend=True, automatic_resize=False)
        self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
        self.plane.set_draw_details(self.flatsh, [self.libre])
        self.plane.set_alpha(1.0)
        self.plane.draw()
      except Exception as exp:
        # todo: how to refer to the self.log file name? self.logger.name does not work
        self.log.warning("now playing did not succeed.\n{}".format(traceback.format_exc()))
        pass
        # traceback.print_exc(file=open(self.log.name, "a"))
    elif self.type == 'Texture':
      if os.path.exists(PIC_LIBREOFFICE_BITMAP_OUT) and os.path.getmtime(PIC_LIBREOFFICE_BITMAP_OUT) > self.PIC_LIBREOFFICE_BITMAP_OUTmdate:
        # From: http://pi3d.github.io/html/pi3d.html#pi3d.Texture.Texture
        #    NB images loaded as textures can cause distortion effects unless they are certain sizes (below). 
        #    If the image width is a value not in this list then it will be rescaled with a resulting loss of clarity
        #    Allowed widths 4, 8, 16, 32, 48, 64, 72, 96, 128, 144, 192, 256, 288, 384, 512, 576, 640, 720, 768, 800, 960, 1024, 1080, 1920
        #    automatic_resize
        #      default to None, if this has not been overridden and you are running on a RPi before v4 then the width will be coerced to one of the ‘standard’ WIDTHs. 
        #      Otherwise, where the GPU can cope with any image dimension - or alternatively where you know that the images will comply and don’t need to check, no resizing will take place.
        # maybe this restriction leads to distortions for some images
        #
        img_name = '{}{}'.format(os.path.splitext(PIC_LIBREOFFICE_BITMAP_OUT)[0], '-right-aligned.png') if self.x > 0 else '{}{}'.format(os.path.splitext(PIC_LIBREOFFICE_BITMAP_OUT)[0], '-left-aligned.png')
        if not os.path.exists(img_name):
          img_name = PIC_LIBREOFFICE_BITMAP_OUT
        self.image = Image.open(img_name)
        self.log.info("update - read PIC_LIBREOFFICE_BITMAP_OUT={} for entry {}. w={}, h={}".format(img_name, self.entry, self.image.width, self.image.height))
        self.bmfile = self.image
        self.getPositionFromFile()
        self.log.info("update - renewing libre PIC_LIBREOFFICE_BITMAP_OUT={}".format(img_name))
        self.libre = pi3d.Texture(img_name, blend=True, automatic_resize=False)
        self.PIC_LIBREOFFICE_BITMAP_OUTmdate = os.path.getmtime(img_name)
      self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)  #NB x,y both default zero puts it in the middle of the screen
      if self.posDebug:
        self.log.info("update - pi3d.Plane(x={:+7.1f}, y={:+7.1f}, w={:+7.1f}, h={:+7.1f}) # entry: {} ".format(self.x, self.y, self.libre.ix, self.libre.iy, self.entry))
      self.plane.set_draw_details(self.flatsh, [self.libre])
      self.plane.set_alpha(1.0)
      self.plane.draw()




  def regen(self):
#   import pdb; pdb.set_trace()
#   self.log.info("regen() - entry={}, type={}, text_type={}".format(self.entry, self.type, self.text_type))
    if self.type == 'TextBlock':
      if self.text_type == 'PointText':
        self.P3d_PointText.regen()
      elif self.text_type == 'Texture':
        pass
      else:
        self.log.error("Implementation error")
        exit(1)

  def draw(self):
    if self.type == 'TextBlock':
      if self.text_type == 'PointText':
        self.P3d_PointText.draw()
      elif self.text_type == 'Texture':
        self.plane.draw()
      else:
        self.log.error("Implementation error")
        exit(1)

  def colouring_set_colour(self, alpha):
    if self.type == 'TextBlock':
      if self.text_type == 'PointText':
        self.P3d_TextBlock.colouring.set_colour(alpha=alpha)
      elif self.text_type == 'Texture':
        self.plane.set_alpha(alpha=alpha)
      else:
        self.log.error("Implementation error")
        exit(1)

  def evalTexturePosition(self, pos_dname_on_fname):
    # Texture image has changed, re-evaluate self.x and self.y as chances are high that the size (specified with BM_IMG.width and BM_IMG.height) has changed
    if self.expr_x[:9] == 'invalid: ':
      self.log.warning("evalTexturePosition - invalid x-position '{}' in entry {}".format(self.expr_x, self.entry))
    elif self.expr_y[:9] == 'invalid: ':
      self.log.warning("evalTexturePosition - invalid y-position '{}' in entry {}".format(self.expr_y, self.entry))
    else:
#     self.bmfile = self.image # todo: do some more checks!
      self.globals.update({'BM_IMG': self.image})

      expr_x, expr_y  = (self.expr_x, self.expr_y)
      if pos_dname_on_fname and self.entry == 'pic_title:' and 'pic_fname:' in positions.keys() and self.type == 'TextBlock' and self.text_type == 'Texture':
        expr_x, expr_y  = (positions['pic_fname:']['expr_x'], positions['pic_fname:']['expr_y'])
      try:
         self.x = eval(expr_x, self.globals)
      except Exception as e:
        import pdb; pdb.set_trace()
        self.log.info("evalTexturePosition - unable evaluating expression '{}' for x. Entry: {}, file: {}.\nReason: {}".format(expr_x, entry, positionfile, str(e)))

      try:
         self.y = eval(expr_y, self.globals)
      except Exception as e:
        self.log.info("evalTexturePosition - unable evaluating expression '{}' for y. Entry: {}, file: {}.\nReason: {}".format(expr_y, entry, positionfile, str(e)))
      if self.posDebug:
#       import pdb; pdb.set_trace()
        self.log.info("evalTexturePosition - {} x={:+8.1f}, y={:+8.1f}, BM_IMG: {:+8.1f}x{:+8.1f}, pos_dname_on_fname: {}, text: {}".format(self.entry, self.x, self.y,
          self.image.width, self.image.height, 'True' if pos_dname_on_fname else 'False', self.text_format))

  # From: https://stackoverflow.com/a/54148416
  def white_to_transparency_gradient(self, img):
      x = np.asarray(img.convert('RGBA')).copy()
      x[:, :, 3] = (255 - x[:, :, :3].mean(axis=2)).astype(np.uint8)
      return Image.fromarray(x)

  def black_to_transparency_gradient(self, img):
      x = np.asarray(img.convert('RGBA')).copy() # returns an np.ndarray
      # more info on x[:, :, 3]: https://www.pythoninformer.com/python-libraries/numpy/numpy-and-images/
      # RGB (255, 255, 255) = white, (0, 0, 0) = black
      x[:, :, 3] = (x[:, :, :3].mean(axis=2)).astype(np.uint8)
      return Image.fromarray(x)

##                     _ _ _______        _
##                    | | |__   __|      | |
##  ___  ___ _ __ ___ | | |  | | _____  _| |_
## / __|/ __| '__/ _ \| | |  | |/ _ \ \/ / __|
## \__ \ (__| | | (_) | | |  | |  __/>  <| |_
## |___/\___|_|  \___/|_|_|  |_|\___/_/\_\\__|
# ASCII ART From: http://patorjk.com/software/taag

class scrollText:
#todo: regex # regex: pip3 install regex to scroll Thai text properly, see https://stackoverflow.com/a/30105788
# todo: implement time out in class (with speed as config parameter)
  def __init__(self, text, display_subrange=40, spacer='... ', delay=0.5):
    self.text      = text
    self.spacer    = spacer
    self.delay     = delay
    self.next_run  = datetime.datetime.now() + datetime.timedelta(seconds=-0.1)
    self.subr      = display_subrange
    self._listtxt  = regex.findall(u'\\X', self.text) + list(spacer)
    self._listlen  = len(self._listtxt)
    self._listtxt  = self._listtxt * 2 # (2 * self.subr//lile + 1)
    self.firstChar = -1

  def getText(self):
    if len(self.text) <= self.subr:
      # text shorter than available space, no scrolling
      return self.text
    else:
      # scroll text in given text window
      if datetime.datetime.now() >= self.next_run:
       self.firstChar = self.firstChar + 1 if self.firstChar < self._listlen else 0
       self.next_run  = datetime.datetime.now() + datetime.timedelta(seconds=self.delay)
      return "".join(self._listtxt[self.firstChar:self.subr+self.firstChar])

  def updateText(self, text):
    self.text      = text
    self._listtxt  = regex.findall(u'\\X', self.text) + list(self.spacer) + regex.findall(u'\\X', self.text)
    self._listlen  = len(regex.findall(u'\\X', self.text))
    return self.getText()


##        _  _____      _                         _____                _ _
##       | |/ ____|    (_)                       / ____|              | | |
##   __ _| | (___   ___ _ ___ ___  ___  _ __ ___| (___   ___ _ __ ___ | | |
##  / _` | |\___ \ / __| / __/ __|/ _ \| '__/ __|\___ \ / __| '__/ _ \| | |
## | (_| | |____) | (__| \__ \__ \ (_) | |  \__ \____) | (__| | | (_) | | |
##  \__, |_|_____/ \___|_|___/___/\___/|_|  |___/_____/ \___|_|  \___/|_|_|
##   __/ |
##  |___/
class glScissorsScroll:
  def __init__(self, display, text):
    self.display     = display
    self.text        = text

    # START: hard coded parameters, to be read from positions.txt
    self.plane_x     =  137
    self.start_x     = self.plane_x
    self.plane_y     = -270
    self.plane_w_vis =  822
    self.text_img    = "/var/media/keto/ro/tmp/x-trans.png"
    # END: hard coded parameters, to be read from positions.txt

    self.Image       = Image.open(self.text_img)
    self.shader      = pi3d.Shader("uv_flat")

    self.plane       = pi3d.Plane(w=self.Image.width, h=self.Image.height, z=4.0)
    self.libre       = pi3d.Texture(self.text_img)
    self.plane.set_draw_details(self.shader, [self.libre])

    ### start calulations for glScissors
    ### opengles.glScissors:
    ##   From: /usr/local/lib/python3.7/dist-packages/pi3d/sprite/ScissorBall.py
    ##     #NB the screen coordinates for glScissor have origin in BOTTOM left
    ##   From: https://research.ncl.ac.uk/game/mastersdegree/graphicsforgames/scissorsandstencils/
    ##     Like other OpenGL states, testing against a scissor region when rendering is
    ##     enabled with glEnable, using the GL_SCISSOR_TEST symbolic constant. There
    ##     can be only one scissor region active at a time, and the area this scissor
    ##     region covers is set by the glScissor OpenGL function. This takes 4
    ##     parameters - the x and y axis start positions of the scissor region, and the
    ##     x and y axis size of the region. Like glViewport, these parameters are in
    ##     screen space, and so are measured in pixels. It’s worth noting that scissor
    ##     testing also influences glClear - it’ll only clear what’s inside the
    ##     scissor region, if scissor testing is enabled.
    self.glScis_x = self.display.width  // 2 + self.plane_x
    self.glScis_y = self.display.height // 2 + self.plane_y - self.Image.height // 2 # position refers to plane's center.
    self.glScis_h = self.Image.height
    self.glScis_w = self.plane_w_vis
    print("    Image - w: {:+.2f}, h: {:+.2f}".format(self.Image.width,   self.Image.height))
    print("  Display - w: {:+.2f}, h: {:+.2f}".format(self.display.width, self.display.height))
    print("glScissor - x: {:+.2f}, y: {:+.2f}".format(self.glScis_x,   self.glScis_y))
    print("glScissor - h: {:+.2f}, w: {:+.2f}".format(self.glScis_h,   self.glScis_w))


  def move(self):
    # opengles.glScissor(GLint(540), GLint(960),  GLsizei(200), GLsizei(-100))
    # plane.position(x, y, z)
    opengles.glScissor(GLint(self.glScis_x), GLint(self.glScis_y), GLsizei(self.glScis_w), GLsizei(self.glScis_h))
    self.plane.position(self.plane_x, self.plane_y, 4.0)
    opengles.glEnable(GL_SCISSOR_TEST)
    self.plane.draw()
    opengles.glDisable(GL_SCISSOR_TEST)
    self.plane_x -= 4
    if self.plane_x < -self.Image.width / 2:
      self.plane_x = self.start_x + self.Image.width / 2 + self.plane_w_vis



##   _____      .__       .___           ________          __
## _/ ____\____ |  |    __| _/___________\_____  \ _______/  |_  ______
## \   __\/  _ \|  |   / __ |/ __ \_  __ \/   |   \\____ \   __\/  ___/
##  |  | (  <_> )  |__/ /_/ \  ___/|  | \/    |    \  |_> >  |  \___ \
##  |__|  \____/|____/\____ |\___  >__|  \_______  /   __/|__| /____  >
##                         \/    \/              \/|__|             \/
class folderOpts:

  def __init__(self, pic_dir, config, pi3d_log, txt_cp, show_names):
    self.config                                    = config
    self.log                                       = pi3d_log
    self.pf_opts                                   = {}
    self.pf_opts_warnings                          = {}
    self.pf_opts['defaults'] = {}
    self.pf_opts['defaults']['apply_to_subdirs']   = 1
    self.pf_opts['defaults']['track_last_viewed']  = pfc.get_config_param(self.config, 'PIC_TRACK_LAST_VIEWED')
    self.pf_opts['defaults']['show_clock']         = pfc.get_config_param(self.config, 'PIC_CLOCK_ENABLED')
    self.pf_opts['defaults']['show_fname']         = show_names # config.SHOW_NAMES_TM
    self.pf_opts['defaults']['show_dname']         = show_names
    self.pf_opts['defaults']['pos_dname_on_fname'] = 1 # TODO: make parameter
    self.pf_opts['defaults']['exif_for_fname']     = None
    self.pf_opts['defaults']['last_write']         = 0.0 # set to 1970-01-01 00:00
    self.pic_dir                                   = pic_dir
    self.txt_cp                                    = txt_cp
    self.PI3D_TB_CHAR_COUNT                        = pfc.get_config_param(self.config, 'PI3D_TB_CHAR_COUNT')
    self.PIC_TRACK_LAST_VIEWED_DIR                 = pfc.get_config_param(self.config, 'PIC_TRACK_LAST_VIEWED_DIR')
    if not os.path.exists(self.PIC_TRACK_LAST_VIEWED_DIR):
      os.mkdir(self.PIC_TRACK_LAST_VIEWED_DIR)

  def getLastViewedFile(self, pic_dir):
    try:
      tf = open(os.path.join(self.PIC_TRACK_LAST_VIEWED_DIR, self.pic_dir.strip('/').replace('/', '.')), 'r')
      return tf.readline()
    except FileNotFoundError:
      return ""

  def getOpt(self, option, fname): # , pos_dname_on_fname=False
    opt_dir = fname if os.path.isdir(fname) else os.path.dirname(fname)
    self.updateOptionsFromFile(opt_dir)
    while True:
      opt_file = os.path.join(opt_dir, '.pf-opts')
      if os.path.exists(opt_file) or opt_dir == '/':
        break
      opt_dir = os.path.dirname(opt_dir)
    idx = opt_dir if os.path.exists(opt_file) else 'defaults'
    if self.pf_opts[idx]['show_fname'] and self.pf_opts[idx]['show_dname'] and self.pf_opts[idx]['pos_dname_on_fname']:
      self.log.warning("getOpt - show_fname=true, show_dname=true and pos_dname_on_fname=true. Names will be stacked on top of each other!")
    if option in ['exif_for_fname', 'title_for_dname']: # title_for_dname is used when show_dname=True
      if self.pf_opts[idx]['track_last_viewed']:
        # keep track of the currently displayed picture so we can resume from here should need be
        tf = open(os.path.join(self.PIC_TRACK_LAST_VIEWED_DIR, self.pic_dir.strip('/').replace('/', '.')), 'w')
        tf.writelines(fname)
        tf.close()
      if option == 'title_for_dname':
        return self.tidy_name(fname, mode='dname')
      elif self.pf_opts[idx]['exif_for_fname'] == None:
        return self.tidy_name(fname)
      else:
        return self.getExifCont(fname, self.pf_opts[idx]['exif_for_fname'])
    else:
      return self.pf_opts[idx][option]

  def updateOptionsFromFile(self, dname):
    opt_dir  = dname
    opt_file = None

    while True:
      opt_file = os.path.join(opt_dir, '.pf-opts')
      if os.path.exists(opt_file) or opt_dir == '/':
        break
      opt_dir = os.path.dirname(opt_dir)

    idx = opt_dir if os.path.exists(opt_file) else 'defaults'
    if os.path.exists(opt_file) and opt_dir in self.pf_opts.keys() and self.pf_opts[idx]['last_write'] >= os.path.getmtime(opt_file):
      # .pf-opts exists, already in data structure and up-to-date
      return

    opt_status = " (does not exist)" if not os.path.exists(opt_file) else ""
    if not opt_file in self.pf_opts_warnings.keys():
      # keep track of directories a warning was issued (to prefent clutter)
      self.log.info("updateOptionsFromFile - options file: '{}'{}".format(opt_file, opt_status))
      self.pf_opts_warnings[opt_file] = 'x'
    self.pf_opts[opt_dir] = self.pf_opts['defaults']

    if not os.path.exists(opt_file):
      return
    with open(opt_file) as of:
      for line in of:
        for k in self.pf_opts['defaults'].keys():
          m = re.search('^'+k+'\s*=\s*(.*)', line)
          if m:
            self.log.info("updateOptionsFromFile - updating: {}={}".format(k, m.group(1)))
            try:
              self.pf_opts[opt_dir][k] = distutils.util.strtobool(m.group(1))
            except:
              self.pf_opts[opt_dir][k] = m.group(1)
              pass
    self.pf_opts[opt_dir]['last_write'] = os.path.getmtime(opt_file)

  def getExifCont(self, fname, spec_string):
    m = re.search('\s*attr\s*=\s*(\d+);\s*encoding\s*=\s*(utf-(?:8|16));\s*regexp\s*=\s*(.*)', spec_string, re.DOTALL)
    if m:
      attr     = int(m.group(1))
      encoding = m.group(2)
      regexp   = m.group(3)
    else:
      self.log.warning("specification {} does not match expected pattern".format(spec_string))
      return ""
    im = Image.open(fname)
    exif_data = im._getexif()
    if type(exif_data) == None.__class__:
      # no exif data. Todo: beautify file name
      return self.tidy_name(fname)
    try:
      raw_val = exif_data[attr].decode(encoding) if hasattr(exif_data[attr], 'decode') else exif_data[attr]
      if re != "":
        m = re.search(regexp, raw_val)
        if m:
          return self.tidy_name(" ".join(m.groups()))
      return self.tidy_name(raw_val)
    except Exception as e:
      self.log.warning("something went wrong. {}".format(e))
      return ""

  def tidy_name(self, path_name, mode='fname'):
      if mode == 'fname':
        # in mode 'fname': turn path_name='/var/tmp/TOP.Directory/Subdir/THIS.IS_AN.Example.jpg' into 'This Is An Example'
        input = os.path.splitext(os.path.basename(path_name))[0] # file name w/o extension
      else:
        # in mode 'dname': turn path_name='/var/tmp/TOP.directory/Subdir/THIS.IS_AN.Example.jpg' into 'Top Directory | Subdir'
        if os.path.dirname(path_name) == os.path.dirname(self.pic_dir):
          input = os.path.basename(os.path.dirname(path_name))
        else:
          input = os.path.dirname(re.sub(self.pic_dir, '', path_name)).strip('/')
          input = re.sub('/', ' | ', input)
      name = ' '.join(list(map(lambda s: s.capitalize(), re.sub('[_\.]', ' ', input).split())))
      name = ''.join([c for c in name if c in self.txt_cp['codepoints']])
      name = re.sub(' \| ', '|', name)
      if self.PI3D_TB_CHAR_COUNT > 0:
        name = name[:self.PI3D_TB_CHAR_COUNT]
      return name



class pi3dTexThreaded:

  def __init__(self, fn_list, DISPLAY, pf2020_config, start=0):
    self.lock            = threading.Lock()
    self.free_to_load    = threading.Event()
    self.free_to_load.set()
    self.img_loader      = threading.Thread(target=self.img_loader, daemon=True)
    self.fn_list         = fn_list
    self.pic_num_current = None
    self.pic_num_next    = start
    self.pf2020_config   = pf2020_config
    self.DISPLAY_width   = DISPLAY.width
    self.DISPLAY_height  = DISPLAY.height
    # variables for image on display
    self.img             = None
    self.tex             = None
    # variables for next image
    self.img_next        = None # variable 'im'  in original tex_load function, PIL.Image() object
    self.tex_next        = None # variable 'tex' in original tex_load function, pi3d.Texture object
    self.img_loader.start()

  def img_loader(self):
    while True:
      self.free_to_load.wait()
      self.tex_pre_load()
      self.free_to_load.clear()

  def tex_pre_load(self):
    from pi3d.Texture import MAX_SIZE

    start = datetime.datetime.now()
    self.lock.acquire()
    self.tex_next = None
    idx = self.pic_num_next
    while True:
      try:
        fname = self.fn_list[idx][0]
        orientation = self.fn_list[idx][1]
        self.img_next = Image.open(fname)
#       _log.info("loading image {}".format(fname))
        self.img_next.load()
        (w, h) = self.img_next.size
        if w > MAX_SIZE:
            self.img_next = self.img_next.resize((MAX_SIZE, int(h * MAX_SIZE / w)))
        elif h > MAX_SIZE:
            self.img_next = self.img_next.resize((int(w * MAX_SIZE / h), MAX_SIZE))

        if orientation == 2:
            self.img_next = self.img_next.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            self.img_next = self.img_next.transpose(Image.ROTATE_180) # rotations are clockwise
        elif orientation == 4:
            self.img_next = self.img_next.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            self.img_next = self.img_next.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 6:
            self.img_next = self.img_next.transpose(Image.ROTATE_270)
        elif orientation == 7:
            self.img_next = self.img_next.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
        elif orientation == 8:
            self.img_next = self.img_next.transpose(Image.ROTATE_90)
        if self.pf2020_config.BLUR_EDGES and self.DISPLAY_width is not None:
          wh_rat = (self.DISPLAY_width * self.img_next.size[1]) / (self.DISPLAY_height * self.img_next.size[0])
          if abs(wh_rat - 1.0) > 0.01: # make a blurred background
            (sc_b, sc_f) = (self.DISPLAY_height / self.img_next.size[1], self.DISPLAY_width / self.img_next.size[0])
            if wh_rat > 1.0:
              (sc_b, sc_f) = (sc_f, sc_b) # swap round
            (w, h) =  (round(self.img_next.size[0] / sc_b / self.pf2020_config.BLUR_ZOOM), round(self.img_next.size[1] / sc_b / self.pf2020_config.BLUR_ZOOM))
            (x, y) = (round(0.5 * (self.img_next.size[0] - w)), round(0.5 * (self.img_next.size[1] - h)))
            box = (x, y, x + w, y + h)
            blr_sz = (int(x * 512 / self.img_next.size[0]) for x in self.img_next.size)
            im_b = self.img_next.resize((self.DISPLAY_width, self.DISPLAY_height), resample=0, box=box).resize(blr_sz)
            im_b = im_b.filter(ImageFilter.GaussianBlur(self.pf2020_config.BLUR_AMOUNT))
            im_b = im_b.resize((self.DISPLAY_width, self.DISPLAY_height), resample=Image.BICUBIC)
            im_b.putalpha(round(255 * self.pf2020_config.EDGE_ALPHA))  # to apply the same EDGE_ALPHA as the no blur method.
            self.img_next = self.img_next.resize((int(x * sc_f) for x in self.img_next.size), resample=Image.BICUBIC)
            im_b.paste(self.img_next, box=(round(0.5 * (im_b.size[0] - self.img_next.size[0])),
                                round(0.5 * (im_b.size[1] - self.img_next.size[1]))))
            self.img_next = im_b # have to do this as paste applies in place
        self.tex_next = pi3d.Texture(self.img_next, blend=True, m_repeat=True, automatic_resize=True, free_after_load=True)
      except Exception as e:
        logging.error("tex_pre_load: Couldn't load file '{}', giving error: '{}'".format(fname, e))
#       if self.pf2020_config.VERBOSE:
        _log.info(e)
        self.tex_next = None
      self.img_next_fname = self.fn_list[idx][0]
      idx = idx + 1 if idx < len(self.fn_list) - 1 else 0
      if self.tex_next != None:
        break
    delta = str(datetime.datetime.now()-start).split(':')
    logging.debug("tex_pre_load: {:02d}min {:03.1f}sec, fname: '{}' ({:,d} bytes)".format(int(delta[1]), float(delta[2]), fname, os.stat(fname).st_size))
    self.pic_num_next = idx
    self.lock.release()


  def load_next_texture(self):
    acquire_start = datetime.datetime.now()
    self.lock.acquire()
    max_wait_ms = 200
    if datetime.datetime.now() > acquire_start + datetime.timedelta(milliseconds=max_wait_ms):
      logging.info("premature image load for {} ".format(self.img_next_fname))
#   import pdb; pdb.set_trace()
    self.img = self.img_next
    self.tex = self.tex_next
    self.pic_num_current = self.pic_num_next
    self.free_to_load.set()
    self.lock.release()

