import importlib
import json
import pdb
import re
import time
import traceback
import datetime
from datetime import timedelta
from dateutil import tz
import configparser
import logging
import os
import numpy as np
from enum import Enum
from pathlib import Path
import pi3d
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pi3dpf_ns.pi3dpf_owm.owm_org import pythainlp_util_date as pud
from pi3dpf_ns.pi3dpf_common import pf_common as pfc

_log = logging.getLogger(__name__)
WORLD_CLOCK_TZ1, WORLD_CLOCK_TZ2, WORLD_CLOCK_DT_FORMAT = None, None, None
main_config_file = [os.path.join(os.path.dirname(__file__), 'cfg', 'pf.config')]
main_config = configparser.ConfigParser(
    inline_comment_prefixes=';', empty_lines_in_values=False, strict=False,  # strict=False will merge sections
    converters={'list': lambda x: [i.strip() for i in x.split(',')]}, interpolation=None)
if os.path.exists("/home/pi/.pf/pf.config"):
    main_config_file.append("/home/pi/.pf/pf.config")
main_config.read(main_config_file)
main_config.cfg_fname = main_config_file
PF_HOME_DIR = pfc.get_config_param(main_config, 'PF_HOME_DIR')
# use PI3D_SCIS_FONT_COLOR as default when font_color parameter in elements.config is missing
PI3D_SCIS_FONT_COLOR = pfc.get_config_param(main_config, 'PI3D_SCIS_FONT_COLOR')
PI3D_SCIS_FONT_POINT = pfc.get_config_param(main_config, 'PI3D_SCIS_FONT_POINT')
PI3D_FT_FONT = pfc.get_config_param(main_config, 'PI3D_FT_FONT')
PIC_DEFAULT_REFRESH_RATE_SEC = pfc.get_config_param(main_config, 'PIC_DEFAULT_REFRESH_RATE_SEC')
PIC_FRAME_FALLBACK_IMAGE = pfc.get_config_param(main_config, 'PIC_FRAME_FALLBACK_IMAGE')
if not os.path.exists(PIC_FRAME_FALLBACK_IMAGE):
    _log.error("fallback image {} does not exist".format(PIC_FRAME_FALLBACK_IMAGE))
    exit(1)


class ElementsConfig:
    def __init__(self):
        self.elements_config_file = [os.path.join(os.path.join(os.path.dirname(Path(__file__))), 'cfg', 'elements.config')]
        self.elements_config = configparser.ConfigParser(
            inline_comment_prefixes=';', empty_lines_in_values=False, strict=False,  # strict=False will merge sections
            converters={'list': lambda x: [i.strip() for i in x.split(',')]}, interpolation=None)
        self.elements_config_file_mdates, self.ELEMENTS_REFRESH_RATE_SEC, self.elements_revision = 0, None, 0
        self.last_file_age_check = datetime.datetime.fromtimestamp(0)
        self.check_update(force_update=True)

    def check_update(self, force_update=False):
        changed = False if force_update else self.elements_config_change_check()
        if force_update or changed:
            if os.path.exists("/home/pi/.pf/elements.config"):
                self.elements_config_file.append("/home/pi/.pf/elements.config")
            self.elements_config.read(self.elements_config_file)
            self.ELEMENTS_REFRESH_RATE_SEC = pfc.get_config_param(self.elements_config, 'ELEMENTS_REFRESH_RATE_SEC')
            self.elements_revision += 1
            _log.info("check_update - elements_revision={}".format(self.elements_revision))
            self.elements_config_file_mdates = [os.path.getmtime(f) for f in self.elements_config_file]
        return changed

    def elements_config_change_check(self):
        nc = self.last_file_age_check + datetime.timedelta(seconds=self.ELEMENTS_REFRESH_RATE_SEC)
        if datetime.datetime.now() < nc:
            return False
        self.last_file_age_check = datetime.datetime.now()
        rv = False
        for i in range(0, len(self.elements_config_file)):
            if os.path.getmtime(self.elements_config_file[i]) != self.elements_config_file_mdates[i]:
                rv = True
        _log.info("elements_config_change_check - time to check for changes in elements.config. Result: {}".format(rv))
        return rv


elements_config = ElementsConfig()


class PfElementState(Enum):
    displayOn = 'displayOn'
    displayOff = 'displayOff'
    uninitialized = 'uninitialized'

    def __repr__(self):
        return "{}.{}".format(self.__class__.__name__, self.value)


class PfElementKind(Enum):
    plainText = 'plainText'
    pi3dTexture = 'pi3dTexture'

    def __repr__(self):
        return "{}.{}".format(self.__class__.__name__, self.value)


class PfElement:
    def __init__(self, section_name, elements_config_raw, pi3d_display: pi3d.Display):
        self.tz_primary, self.tz_secondary, self.data_source_callable = None, None, None
        self.base_path, self.pypi_package, self.kind, self.property_file_eval = None, None, None, None
        self.pypi_pkg_prop_file, self.pypi_pkg_properties, self.description = None, None, None
        self.formatting_spec, self.formatting_eval = None, None
        self.data_source_spec, self.data_source_eval = None, None
        self.font_color, self.font_point, self.image_mdate, self.image_pil = None, None, 0, None
        self.pos_x_spec, self.pos_y_spec, self.pos_x_eval, self.pos_y_eval = None, None, None, None
        self.th_time, self.refresh_rate_sec, self.last_check, self.pos_debug = False, None, 0, False
        self.elements_cfg_raw = dict(elements_config_raw)
        self.elements_cfg_raw = dict(elements_config.elements_config[section_name])
        self.id = section_name
        self.pi3d_display = pi3d_display
        self.display = PfElementState.uninitialized
        self.elements_revision = -1
        if self.elements_revision != elements_config.elements_revision:
            self.load_config()

        # now self.image_pil
        # self.image = Image.new("RGB", (4,4), (0, 0, 0))  # there seems to be new pi3d code requiring size % 4 == 0

        # self.libre and self.plane are needed
        self.libre, self.plane = None, None
        # self.libre = pi3d.Texture(file_string=self.image)
        # self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
        # self.plane.position(x=self.x, y=self.y, z=0.1)
        # self.log.info("pi3d.Plane for {} - x={:+.2f}, y={:+.2f}".format(entry, self.x, self.y))
        # self.bmfile = self.image
# From: pi3dpf_ns.pi3dpf_base.pf.py
#    if self.text_type == 'Texture':
#        self.image = Image.new("RGB", (4,4), (0, 0, 0))  # there seems to be new pi3d code requiring size % 4 == 0
#        self.libre = pi3d.Texture(file_string=self.image)
#        self.plane = pi3d.Plane(x=self.x, y=self.y, w=self.libre.ix, h=self.libre.iy, z=0.1)
#        self.plane.position(x=self.x, y=self.y, z=0.1)
#        self.log.info("pi3d.Plane for {} - x={:+.2f}, y={:+.2f}".format(entry, self.x, self.y))
#        self.bmfile = self.image

    def load_config(self):
        self.pypi_pkg_prop_file = self.elements_cfg_raw['pypi_pkg_prop_file'] if 'pypi_pkg_prop_file' in self.elements_cfg_raw.keys() else None
        self.pypi_pkg_properties = None  # loaded in first resolve_symbols() call
        if 'pypi_package' in self.elements_cfg_raw.keys():
            try:
                self.pypi_package = self.elements_cfg_raw['pypi_package']
                i = importlib.import_module(self.pypi_package)
                self.base_path = i.__path__[0]
                self.property_file_eval = os.path.join(i.__path__[0], self.pypi_pkg_prop_file)
            except ModuleNotFoundError:
                prefix = "PfElement.load_config - elements.config"
                _log.error("{} - [{}] pypi_package='{}' pypi_package not found. Traceback:\n{}".format(
                    prefix, self.id, self.elements_cfg_raw['pypi_package'], traceback.format_exc()))
                _log.info("load_config - disabling [{}]".format(self.id))
                self.display = PfElementState.displayOff
                return
        if self.pypi_package is not None and self.pypi_pkg_prop_file is not None:
            self.get_module_config()
        self.description = self.elements_cfg_raw['description'] if 'description' in self.elements_cfg_raw.keys() else None
        self.formatting_spec = self.elements_cfg_raw['formatting_spec'] if 'formatting_spec' in self.elements_cfg_raw.keys() else None
        self.formatting_eval = self.resolve_symbols('formatting_spec', self.id)  # self.property_file_eval, self.elements_cfg_raw,
        if 'kind' in self.elements_cfg_raw.keys():
            if self.elements_cfg_raw['kind'] == 'plain-text':
                self.kind = PfElementKind.plainText
            elif self.elements_cfg_raw['kind'] == 'pi3d-texture':
                self.kind = PfElementKind.pi3dTexture
            else:
                self.kind = PfElementKind.uninitialized
        else:
            self.kind = PfElementKind.uninitialized
        self.data_source_spec = self.elements_cfg_raw['data_source_spec'] if 'data_source_spec' in self.elements_cfg_raw.keys() else None
        self.data_source_eval = self.resolve_symbols('data_source_spec', self.id)  # self.property_file_eval,self.elements_cfg_raw,
        self.font_color = self.elements_cfg_raw['font_color'] if 'font_color' in self.elements_cfg_raw.keys() else PI3D_SCIS_FONT_COLOR
        self.font_point = PI3D_SCIS_FONT_POINT
        self.pos_x_spec = self.elements_cfg_raw['pos_x_spec'] if 'pos_x_spec' in self.elements_cfg_raw.keys() else None
        self.pos_y_spec = self.elements_cfg_raw['pos_y_spec'] if 'pos_y_spec' in self.elements_cfg_raw.keys() else None
        rrs = 'refresh_rate_sec'
        self.refresh_rate_sec = int(self.elements_cfg_raw[rrs]) if rrs in self.elements_cfg_raw.keys() else PIC_DEFAULT_REFRESH_RATE_SEC
        self.display = PfElementState.uninitialized
        if 'display' in self.elements_cfg_raw.keys():
            if self.elements_cfg_raw['display'] == 'on':
                self.display = PfElementState.displayOn
            elif self.elements_cfg_raw['display'] == 'off':
                self.display = PfElementState.displayOff
        if self.display == PfElementState.uninitialized:
            _log.warning("load_config - [{}] display=uninitialized".format(self.id))
        self.pos_debug = True if 'pos_debug' in self.elements_cfg_raw.keys() and self.elements_cfg_raw['pos_debug'] in ['true', 'True'] else False
        if self.kind == PfElementKind.pi3dTexture and self.data_source_eval is not None:
            self.calculate_image_properties()
        if self.kind == PfElementKind.plainText:
            self.text_to_image(self.data_source_eval)
        self.elements_revision = elements_config.elements_revision
        self.libre = pi3d.Texture(file_string=self.image_pil)
        self.plane = pi3d.Plane(x=self.pos_x_eval, y=self.pos_y_eval, w=self.libre.ix, h=self.libre.iy, z=0.1)
        self.plane.position(x=self.pos_x_eval, y=self.pos_y_eval, z=0.1)

    def __repr__(self):
        d = {}
        k = ["id", "description", "kind", "pypi_package", "pypi_pkg_prop_file", "property_file_eval", "data_source_spec",
             "data_source_eval", "data_source_callable", "formatting_spec", "formatting_eval", "image_mdate",
             "image_pil", "font_color", "pos_x_spec", "pos_x_eval", "pos_y_spec", "pos_y_eval", "pos_debug",
             "refresh_rate_sec", "last_check", "display", "elements_revision"]
        try:
            for i in k:
                if i in ['kind', 'display'] and hasattr(self, i):
                    x = getattr(self, i)
                    d[i] = x.name if hasattr(x, 'name') else None
                elif i in ['image_mdate', 'last_check'] and hasattr(self, i):
                    ts = int(getattr(self, i))
                    d[i] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                elif i in ['image_pil']:
                    d[i] = "{}".format(getattr(self, i)) if hasattr(self, i) else None
                elif hasattr(self, i) and callable(getattr(self, i)):
                    d[i] = "callable (more details: see data_source_spec)"
                else:
                    d[i] = getattr(self, i) if hasattr(self, i) else None
        except TypeError:
            _log.error("__repr__ - failed presenting '{}'".format(i))
        return "{}".format(json.dumps(d, indent=4, ensure_ascii=False))  # .encode('utf8')

    def get_module_config(self):
        if not os.path.exists(self.property_file_eval):
            _log.error("get_module_config - property file {} does not exist".format(self.property_file_eval))
            return None
        self.pypi_pkg_properties = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                                                             converters={'list': lambda x: [i.strip() for i in x.split(',')]})
        self.pypi_pkg_properties.read(self.property_file_eval)

    def calculate_image_properties(self):
        global PIC_FRAME_FALLBACK_IMAGE
        data_source_eval = self.data_source_eval
        if not os.path.exists(data_source_eval):
            dse, dss = data_source_eval, self.data_source_spec
            _log.error("file {} from [{}] data_source_spec='{}' does not exist".format(dse, self.id, dss))
            _log.info("using {} instead".format(PIC_FRAME_FALLBACK_IMAGE))
            data_source_eval = PIC_FRAME_FALLBACK_IMAGE
        self.image_mdate = os.path.getmtime(data_source_eval)
        self.image_pil = Image.open(data_source_eval)
        if self.pos_x_spec:
            self.pos_x_eval = eval(self.pos_x_spec, {}, {'DISPLAY': self.pi3d_display, 'IMAGE': self.image_pil})
        if self.pos_y_spec:
            self.pos_y_eval = eval(self.pos_y_spec, {}, {'DISPLAY': self.pi3d_display, 'IMAGE': self.image_pil})

    def resolve_symbols(self, parameter_name: str, element_id: str):  # property_file,raw: dict,
        property_eval = None
        # is raw.keys() equal self.elements_cfg_raw.keys()
        if parameter_name not in self.elements_cfg_raw.keys():
            _log.warning("resolve_symbols - parameter {} does not exist".format(parameter_name))
            return None
        spec_string = self.elements_cfg_raw[parameter_name]
        m = re.match(r'\s*(as-is|property:|exec:|global_var:|callable:)\s*(.*)', spec_string)
        if m:
            if m.group(1) in ['property:', 'exec:']:
                try:
                    # self.pypi_pkg_properties = configparser.ConfigParser(inline_comment_prefixes=';', empty_lines_in_values=False,
                    #                                                      converters={
                    #                                             'list': lambda x: [i.strip() for i in x.split(',')]})
                    # self.pypi_pkg_properties.read(property_file)
                    # 1) injecting some parameters from current element for later expansion
                    substitutions = re.findall('%\(([^\)]+)\)', self.elements_cfg_raw[parameter_name])
                    for parameter in substitutions:
                        if hasattr(self, parameter):
                            self.pypi_pkg_properties[self.pypi_pkg_properties.default_section][parameter] = getattr(self, parameter).replace('%',
                                                                                                                   '%%')
                    # 2) Defining a new parameter «GAGA» and 2) reading the value allows interpolation to occur
                    self.pypi_pkg_properties[self.pypi_pkg_properties.default_section]['GAGA'] = m.group(2)
                    property_eval = self.pypi_pkg_properties[self.pypi_pkg_properties.default_section]['GAGA']
                    if m.group(1) in ['exec:']:
                        loc = {}
                        exec(compile("global rval;" + property_eval, "code", "exec"), {}, loc)
                        property_eval = loc['rv']
                except BaseException:
                    _log.error("resolve_symbols - [{}] - {}={} failed. Traceback:\n{}".format(
                        element_id, parameter_name, self.elements_cfg_raw[parameter_name], traceback.format_exc()))
                    return None
            elif m.group(1) == 'as-is':
                property_eval = m.group(2)
            elif m.group(1) == 'global_var:':
                try:
                    loc = {}
                    exec(compile(m.group(2), "aa", "exec"), {'m': m}, loc)
                    property_eval = loc['gv']
                except AttributeError as e:
                    _log.error("resolve_symbols - [{}] - {}={} failed. Traceback:\n{}".format(
                        element_id, parameter_name, self.elements_cfg_raw[parameter_name], traceback.format_exc()))
            elif m.group(1) == 'callable:':
                self.data_source_callable = getattr(self, m.group(2)) if hasattr(self, m.group(2)) else None
                if hasattr(self, m.group(2)):
                    property_eval = self.data_source_callable()
            else:
                _log.error("resolve_symbols - unexpected prefix '{}' in [{}]{}={}.".format(
                    m.group(1), element_id, parameter_name, spec_string))
                pdb.set_trace()
                exit(1)
            return property_eval
        return property_eval

    def text_to_image(self, text_format):
        COL_BLACK = (0, 0, 0)
        COL_WHITE = (255, 255, 255)
        text_format = ' ' if text_format == '' else text_format  # numpy array not the way needed when string empty
        col_font = COL_WHITE if self.font_color == 'white' else COL_BLACK
        col_back = COL_BLACK if self.font_color == 'white' else COL_WHITE
        image = Image.new("RGB", (4, 4), col_back)
        draw = ImageDraw.Draw(image)
        # Make image 3 times the needed size to improve quality
        font_3 = ImageFont.truetype(PI3D_FT_FONT, self.font_point * 3)
        # determine space needed by given text.
        dim_3 = draw.textsize(text_format, font_3)
        image = Image.new('RGB', (dim_3[0], dim_3[1] + 30), col_back)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(PI3D_FT_FONT, self.font_point)
        draw.text((0, 0), text_format, col_font, font=font_3)
        # make background transparent
        #   print(self.entry)
        #    import pdb;
        #    if self.entry[:16] == 'owm_formatstring':
        #      pdb.set_trace()
        img_trans = self.black_to_transparency_gradient(
            image) if self.font_color == 'white' else self.white_to_transparency_gradient(image)
        # resize to requested point_size and save image
        dim = draw.textsize(text_format, font)
        img_resized = img_trans.resize(dim, Image.ANTIALIAS)
        if img_resized.size[0] > self.pi3d_display.width:  # and self.entry[:16] != 'owm_formatstring':
            w = self.pi3d_display.width
            _log.warning("text_to_image - black bar caution - text '{}' larger than display.".format(text_format))
            _log.info("Image width before crop: {}px, display width: {}px".format(img_resized.size[0], w))
            _log.info("img_resized.crop({}, {}, {}, {})".format(0, 0, w, img_resized.size[1]))
        if self.pos_debug:
            dbg_dir = os.path.join(PF_HOME_DIR, 'dbg')
            if not os.path.isdir(dbg_dir): os.mkdir(dbg_dir)
            path_img_3 = os.path.join(PF_HOME_DIR, 'dbg', self.id + '_x3.png')
            image.save(path_img_3)
            path_img = os.path.join(PF_HOME_DIR, 'dbg', self.id + '.png')
            img_resized.save(path_img)
            path_text = os.path.join(PF_HOME_DIR, 'dbg', self.id + '.txt')
            with open(path_text, 'w') as tf:
                tf.write(text_format)
            _log.info("text_to_image - {} wrote image {} and text file {}".format(self.id, path_img, path_text))
        self.image_pil = img_resized
        try:
            if self.pos_x_spec:
                self.pos_x_eval = eval(self.pos_x_spec, {}, {'DISPLAY': self.pi3d_display, 'IMAGE': self.image_pil})
            if self.pos_y_spec:
                self.pos_y_eval = eval(self.pos_y_spec, {}, {'DISPLAY': self.pi3d_display, 'IMAGE': self.image_pil})
        except AttributeError:
            _log.error("text_to_image - [{}] failed to calculate position. Traceback: {}".format(
                self.id, traceback.format_exc()))
        self.image_mdate = datetime.datetime.now().timestamp()
        # TODO: relocate image if position or size has changed (better on different place)
        # return img_resized

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

    def must_refresh(self):
        rev_this, rev, refresh = self.elements_revision, elements_config.elements_revision, False
        if self.elements_revision != elements_config.elements_revision:
            _log.info("must_refresh - [{}] elements.config rev.={}, req.: {} refreshing".format(self.id, rev_this, rev))
            self.load_config()
            refresh = True
        # From this point forward, it can always be assumed that the config data is up-to-date.
        # So we only need to re-evaluate image properties and their x-/y-position
        _log.info("must_refresh - [{}] kind='{}' revision={} (req: {})".format(self.id, self.kind, rev_this, rev))
        _log.info("must_refresh - [{}] data_source_spec='{}'".format(self.id, self.data_source_spec))
        if not refresh and self.display == PfElementState.displayOff:
            _log.info("must_refresh - [{}] ignoring, PfElementState=displayOff".format(self.id))
            return False

        m = re.match(r'^(exec:|callable:|global_var:)', self.data_source_spec)
        if self.kind == PfElementKind.pi3dTexture and not m:
            # determine next check (nc: next check)
            nc = datetime.datetime.fromtimestamp(self.image_mdate) + datetime.timedelta(seconds=self.refresh_rate_sec)
            if datetime.datetime.now() < nc:  # not the time to do some checks yet, bailing out
                # pdb.set_trace()
                _log.info("must_refresh - [{}] next refresh interval at {} not reached".format(
                    self.id, nc.strftime("%H:%M:%S")))
                return False

        before_reevaluation = self.data_source_eval
        old_vals = (self.image_mdate, self.pos_x_eval, self.pos_y_eval, self.image_pil.width, self.image_pil.height)
        if m:
            _log.info("must_refresh - [{}] must {} data_source_spec".format(self.id,  m.group(1)[:-1]))
            self.data_source_eval = self.resolve_symbols("data_source_spec", self.id)
        else:
            _log.info("must_refresh - [{}] normal data-source stuff".format(self.id))
            # pdb.set_trace()
            # Data_source_spec prefixes: 'property:', ??
            _log.info("must_refresh - [{}] check the use case! ".format(self.id))

        if self.kind == PfElementKind.pi3dTexture and self.data_source_eval is not None:
            if os.path.exists(self.data_source_eval) and os.path.getmtime(self.data_source_eval) != self.image_mdate:
                self.calculate_image_properties()
                # return True
        elif self.kind == PfElementKind.plainText:
            # pdb.set_trace()
            if self.data_source_eval != before_reevaluation:
                self.text_to_image(self.data_source_eval)

        new_vals = (self.image_mdate, self.pos_x_eval, self.pos_y_eval, self.image_pil.width, self.image_pil.height)
        if old_vals != new_vals:
            pdb.set_trace()
            self.libre = pi3d.Texture(file_string=self.image_pil)
            self.plane = pi3d.Plane(x=self.pos_x_eval, y=self.pos_y_eval, w=self.libre.ix, h=self.libre.iy, z=0.1)
            self.plane.position(x=self.pos_x_eval, y=self.pos_y_eval, z=0.1)
            _log.info("must_refresh - [{}] must re-position and re-render".format(self.id))
        _log.info("must_refresh - [{}] data_source_eval='{}'".format(self.id, self.data_source_eval))
        return False

    def get_world_time(self):
        global WORLD_CLOCK_TZ1, WORLD_CLOCK_TZ2, WORLD_CLOCK_DT_FORMAT
        if WORLD_CLOCK_TZ1 is None:
            WORLD_CLOCK_TZ1 = pfc.get_config_param(self.pypi_pkg_properties, 'WORLD_CLOCK_TZ1')
            WORLD_CLOCK_TZ2 = pfc.get_config_param(self.pypi_pkg_properties, 'WORLD_CLOCK_TZ2')
            WORLD_CLOCK_DT_FORMAT = pfc.get_config_param(self.pypi_pkg_properties, 'WORLD_CLOCK_DT_FORMAT')
            self.tz_primary = tz.gettz(WORLD_CLOCK_TZ1)
            self.tz_secondary = tz.gettz(WORLD_CLOCK_TZ2)
        self.th_time = True if 'Asia/Bangkok' in [WORLD_CLOCK_TZ1, WORLD_CLOCK_TZ2] else False
        elements, replacement_string = [], WORLD_CLOCK_DT_FORMAT
        for element in re.findall(r'(\[(TZ[12]):([^\]]+)\])', WORLD_CLOCK_DT_FORMAT):
            # print("working on element {}".format(element))
            element_tz = self.tz_primary if element[1] == 'TZ1' else self.tz_secondary
            if self.th_time:
                elements.append(pud.thai_strftime(datetime.datetime.now(element_tz), element[2]))
            else:
                elements.append(datetime.datetime.now(element_tz).strftime(element[2]))
            replacement_string = replacement_string.replace(element[0], elements[-1], 1)
            # print("replacement_string = '{}'".format(replacement_string))
        return replacement_string


class PfElements:
    def __init__(self, pi3d_display: pi3d.Display):
        global PIC_FRAME_FALLBACK_IMAGE
        self.pi3d_display = pi3d_display
        self.element_list = []
        # xx = ElementsConfig()
        # self.config_file = [os.path.join(os.path.join(os.path.dirname(Path(__file__))), 'cfg', 'elements.config')]
        self.config_file = [os.path.join(os.path.join(os.path.dirname(Path(__file__))), 'cfg', 'elements.config')]
        self.cfg = configparser.ConfigParser(
            inline_comment_prefixes=';', empty_lines_in_values=False, strict=False,  # strict=False will merge sections
            converters={'list': lambda x: [i.strip() for i in x.split(',')]}, interpolation=None)
        if os.path.exists("/home/pi/.pf/elements.config"):
            self.config_file.append("/home/pi/.pf/elements.config")
        self.cfg.read(self.config_file)
        for section in self.cfg.sections():
            self.element_list.append(PfElement(section, self.cfg.items(section), self.pi3d_display))
            _log.info(self.element_list[-1])
        self.get_active_element_ids()
        while True:
            for element in self.element_list:
                elements_cfg_changed = elements_config.check_update()
                must_refresh = element.must_refresh()
                _log.info("[{}] must_refresh={}, elements_cfg_changed={}".format(
                    element.id, must_refresh, elements_cfg_changed))
                if elements_cfg_changed or must_refresh:
                    element.load_config()
            _log.info("spleeping 60s")
            time.sleep(60)
        # print(self.element_list[3])
        pdb.set_trace()
        # self.element_list[1].get_world_time('')
        _log.info("almost done")

    def get_active_element_ids(self):
        el = self.element_list
        return {el[i].id: i for i in range(0, len(el)) if el[i].display == PfElementState.displayOn}

    def recheck_all(self):
        for element in self.element_list:
            element.must_refresh()
