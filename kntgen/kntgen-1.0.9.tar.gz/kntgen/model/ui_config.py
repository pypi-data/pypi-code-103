import yaml

from kntgen.str_helpers import auto_str

DEFAULT_PATH_ASSETS_IMAGES = './assets/images'
DEFAULT_PATH_ASSETS_COLORS = './assets/colors'
DEFAULT_PATH_ASSETS_FONTS = './assets/fonts'
DEFAULT_PATH_ASSETS_TRANSLATIONS = './assets/translations'
DEFAULT_PLACEHOLDER_TRANSLATE = 'need_to_translate'
DEFAULT_LOCALE = 'en'
SVG_MAXIMUM_SIZE = 96
DEFAULT_SCREEN_WIDTH = 375
DEFAULT_SCREEN_HEIGHT = 812


@auto_str
class FigmaInfo:
    def __init__(self, **kwargs):
        self.access_token = kwargs.get('access_token', '')
        self.file_id = kwargs.get('file_id', '')
        self.node_id = kwargs.get('node_id', '')
        self.maximum_svg_size_in_px = kwargs.get('maximum_svg_size_in_px', 128)
        self.screen_width = kwargs.get('screen_width', DEFAULT_SCREEN_WIDTH)
        self.screen_height = kwargs.get('screen_height', DEFAULT_SCREEN_HEIGHT)


@auto_str
class GoogleFontInfo:
    def __init__(self, **kwargs):
        self.api_key = kwargs.get('api_key', '')
        self.basic_font = kwargs.get('basic_font', False)


@auto_str
class GoogleTranslateInfo:
    def __init__(self, **kwargs):
        self.main_locale = kwargs.get('main_locale', DEFAULT_LOCALE)
        self.placeholder = kwargs.get('placeholder',
                                      DEFAULT_PLACEHOLDER_TRANSLATE)


@auto_str
class GoogleInfo:
    def __init__(self, **kwargs):
        self.font = GoogleFontInfo(
            **kwargs['font']) if 'font' in kwargs else GoogleFontInfo()
        self.translate = GoogleTranslateInfo(**kwargs[
            'translate']) if 'translate' in kwargs else GoogleTranslateInfo()


@auto_str
class AssetsInfo:
    def __init__(self, **kwargs):
        self.images = kwargs.get('images', DEFAULT_PATH_ASSETS_IMAGES)
        self.colors = kwargs.get('colors', DEFAULT_PATH_ASSETS_COLORS)
        self.fonts = kwargs.get('fonts', DEFAULT_PATH_ASSETS_FONTS)
        self.translations = kwargs.get('translations',
                                       DEFAULT_PATH_ASSETS_TRANSLATIONS)


@auto_str
class UiConfig:
    def __init__(self, **kwargs):
        self.figma = FigmaInfo(
            **kwargs['figma']) if 'figma' in kwargs else FigmaInfo()
        self.google = GoogleInfo(
            **kwargs['google']) if 'google' in kwargs else GoogleInfo()
        self.assets = AssetsInfo(
            **kwargs['assets']) if 'assets' in kwargs else AssetsInfo()

    @classmethod
    def from_yaml(cls, yaml_stream):
        yaml_model = yaml.safe_load(yaml_stream)
        return cls(**yaml_model)
