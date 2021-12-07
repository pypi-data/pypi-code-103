from os.path import splitext
from urllib.parse import urlparse

from sheetfu import SpreadsheetApp

from kntgen.file_helpers import *
from kntgen.model.figma_models import Color
from kntgen.model.flutter.flutter_raw_widget import FWidgetExtractor
from kntgen.model.ui_config import *
from kntgen.parallel_helpers import run_parallel_tasks
from kntgen.printer import *
from kntgen.str_helpers import *


class FDefined:
    NAMED_COLOR_ENDPOINT = 'https://api.color.pizza/v1/'
    GOOGLE_FONT_ENDPOINT = 'https://www.googleapis.com/webfonts/v1/webfonts'
    ASSETS_FLUTTER_GEN = 'Assets.images.'
    ASSETS_FLUTTER_PATH = '.path'
    COLOR_FLUTTER_GEN = 'ColorName.'
    LOCALE_KEYS = 'LocaleKeys.'
    LOCALE_KEYS_EXTENSION = '.tr()'


class NamedLocaleText:
    @staticmethod
    def localized(custom_widget_name: str, text_name: str):
        prefix, name_without_type = FWidgetExtractor.localized_key_from_name(
            custom_widget_name)
        text_name_without_type = FWidgetExtractor.name_without_type(text_name)
        if not name_without_type or not text_name_without_type:
            return None
        text_name_with_page = f'{to_camel_case(prefix)}_' \
                              f'{to_camel_case(name_without_type)}_' \
                              f'{to_camel_case(text_name_without_type)}'
        return f'{FDefined.LOCALE_KEYS}' \
               f'{text_name_with_page}' \
               f'{FDefined.LOCALE_KEYS_EXTENSION}'


class NamedColor:
    def __init__(self, name_duplicated_times=1, **kwargs):
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.hex = kwargs['hex'] if 'hex' in kwargs else ''
        self.requested_hex = kwargs[
            'requestedHex'] if 'requestedHex' in kwargs else ''
        self.name_duplicated_times = name_duplicated_times or 0
        # Handle name with format
        snake_case_name = to_snake_case(
            ''.join([c for c in self.name if 'a' <= c.lower() <= 'z']))
        postfix = '' if self.name_duplicated_times <= 0 \
            else f'_{(self.name_duplicated_times + 1)}'
        self.snake_case_latin_name = f'{snake_case_name}{postfix}'
        self.camel_case_latin_name = to_camel_case(self.snake_case_latin_name)

    @property
    def flutter_gen_color(self):
        return f'{FDefined.COLOR_FLUTTER_GEN}{self.camel_case_latin_name}'


class NamedImage:
    def __init__(self, image_name: str, image_format: str):
        resource_name = (image_name or '') \
            .replace(FWidgetExtractor.FW_CLICKABLE, '') \
            .replace(FWidgetExtractor.FW_DYNAMIC_DATA, '')
        if resource_name.startswith(FWidgetExtractor.FW_CUSTOM_WIDGET):
            resource_name = resource_name.replace(
                FWidgetExtractor.FW_CUSTOM_WIDGET, '')
        self.image_name = ''.join(
            [c for c in (resource_name or '') if not c.isspace()])
        self.path = f'{FDefined.ASSETS_FLUTTER_GEN}' \
                    f'{to_camel_case(self.image_name)}' \
                    f'{FDefined.ASSETS_FLUTTER_PATH}'
        self.image_format = image_format or 'svg'


class ImageResource:
    def __init__(self, url: str,
                 folder: str,
                 image_name: str,
                 format_image: str):
        self.url = url
        self.folder = folder or DEFAULT_PATH_ASSETS_IMAGES
        self.image_name = image_name
        self.format_image = format_image or 'png'


class FontResource:
    def __init__(self, font_url, folder, file_name):
        self.font_url = font_url
        self.folder = folder or DEFAULT_PATH_ASSETS_FONTS
        self.file_name = file_name


def fetch_named_colors(hex_color_list: list):
    """
    Fetch name of input colors.
    Duplicated name with differ colors will add an extra number postfix .e.g pearl_1

    :param hex_color_list: List colors in RGA hex format
    :return: Dictionary of named color with (k, v) = (hex_color, dict_color_from_api)
    """
    if not hex_color_list:
        return []
    hex_as_id_colors = ','.join(
        [hex_color[1:] for hex_color in hex_color_list])
    response = requests.get(
        f'{FDefined.NAMED_COLOR_ENDPOINT}?values={hex_as_id_colors}'
    )
    named_colors = {}
    if response.status_code == 200:
        res_dict = json.loads(response.text)
        if 'colors' in res_dict:
            named_list = []
            for color in res_dict['colors']:
                if 'hex' not in color \
                        or 'name' not in color \
                        or 'requestedHex' not in color:
                    continue
                c_name = color['name']
                name_duplicated_times = named_list.count(c_name)
                named_color = NamedColor(
                    name_duplicated_times=name_duplicated_times,
                    **color
                )
                named_colors[named_color.requested_hex] = named_color
                named_list.append(c_name)
    return named_colors


def download_images(figma,
                    file_id,
                    folder: str,
                    images: dict,
                    format_image='png',
                    scale_image=2):
    downloaded_file_paths = []
    download_info_images = figma.get_file_images(
        file_key=file_id,
        ids=images.keys(),
        format=format_image,
        scale=scale_image
    )
    if not download_info_images or not download_info_images.images:
        return downloaded_file_paths
    # Prepare resources
    image_sources: list[ImageResource] = []
    for image_id, url in download_info_images.images.items():
        node = {}
        if image_id in images.keys():
            node = images[image_id]
        if not node:
            continue
        node_name = node['name'] if 'name' in node else ''
        image_name = to_snake_case(node_name)
        image_sources.append(
            ImageResource(
                url=url,
                folder=folder,
                image_name=image_name,
                format_image=format_image))
    # Start downloading
    downloaded_file_paths.extend(
        run_parallel_tasks(download_single_image, image_sources))
    return downloaded_file_paths


def download_single_image(resource: ImageResource):
    file_ext = get_extension(resource.url)
    if not file_ext:
        file_ext = f'.{resource.format_image}'
    # Download and save image into file
    file_path = f'{resource.folder}/{resource.image_name}{file_ext}'
    downloaded_file_path = download_to_file(resource.url, file_path)
    return make_content_output_file(
        file_path=downloaded_file_path,
        additional_info=ModifiedFileState.HAS_CREATED_NEW
    )


def download_fonts(google_font_dict: dict, api_key: str, folder: str):
    downloaded_file_paths = []
    google_fonts_url = f'{FDefined.GOOGLE_FONT_ENDPOINT}?key={api_key}'
    gf_response = requests.get(google_fonts_url)
    if gf_response.status_code >= 300:
        error_printer('Could not download fonts!')
        return downloaded_file_paths
    gf_fonts_dict = json.loads(gf_response.text)
    gf_fonts = gf_fonts_dict['items'] if 'items' in gf_fonts_dict else []
    checked_font_family = 0
    # Prepare resources
    font_sources: list[FontResource] = []
    for font in gf_fonts:
        if 'family' not in font and 'files' not in font:
            continue
        family_font = font['family']
        font_files = font['files']

        # Get styles of this needed font
        if family_font in google_font_dict:
            for style in google_font_dict[family_font]:
                if style[0] in font_files:
                    font_url = font_files[style[0]]
                    file_name = style[1]
                    font_sources.append(
                        FontResource(
                            font_url=font_url,
                            folder=folder,
                            file_name=file_name))
            # Update progress
            checked_font_family += 1
            if checked_font_family == len(google_font_dict):
                break
    # Start downloading
    downloaded_file_paths.extend(
        run_parallel_tasks(download_single_font, font_sources))
    return downloaded_file_paths


def download_single_font(resource: FontResource):
    file_ext = get_extension(resource.font_url)
    if not file_ext:
        file_ext = '.ttf'
    # Download and save image into file
    file_path = f'{resource.folder}/{resource.file_name}{file_ext}'
    downloaded_file_path = download_to_file(resource.font_url, file_path)
    return make_content_output_file(
        file_path=downloaded_file_path,
        additional_info=ModifiedFileState.HAS_CREATED_NEW
    )


def beauty_print_named_colors(named_colors: dict[str:NamedColor]):
    content_colors = []
    for hex_c, color in (named_colors or {}).items():
        color_tuple = Color.hex_to_rgb(hex_c)
        colored_content = colored_printer(
            *color_tuple,
            text=f'    {color.name:44}{hex_c:>8}    '
        )
        content_colors.append(colored_content)
    if len(content_colors) > 0:
        beauty_printer(
            title=f'{len(content_colors)} colors in design file',
            content=content_colors,
            max_char_inline=60
        )


def create_google_spreadsheet(design_text_dict, package_name):
    sa = SpreadsheetApp(
        './../kntgen_templates/ui/secret/figma_text_generator_gs.json')
    # email_editor = input('Enter your email as an editor of Google Spreadsheet: ')
    email_editor = 'kiennt.ftx@gmail.com'
    spreadsheet = sa.create(
        name='Appixi',
        editor=email_editor
    )
    spreadsheet.create_sheets([package_name])
    project_sheet = spreadsheet.get_sheet_by_name(package_name)
    # Create columns
    title_columns_range = project_sheet.get_range_from_a1('A1:C1')
    title_columns_range.set_values([
        ['localized_key', 'screen', 'en']
    ])
    # Fill rows
    total_design_text = 0
    for k, v in design_text_dict.items():
        total_design_text += len(v)
    data_range = project_sheet.get_range_from_a1(
        f'A2:C{total_design_text + 1}')
    data = []
    for page, texts_in_page in design_text_dict.items():
        for content_text in texts_in_page:
            data.append(['key', page, content_text])
    data_range.set_values(data)


def get_extension(url):
    """Return the filename extension from url, or ''."""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext
