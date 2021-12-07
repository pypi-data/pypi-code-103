from os import walk

from googletrans import Translator
from jinja2 import Environment, PackageLoader

from kntgen.collection_helpers import *
from kntgen.ui.ui_external_source import *


class FGenerator:
    DEFAULT_LOCALE_FILE_EXTENSION = 'json'
    REGEX_DETECT_LOCALE = '^(?P<languageCode>[a-z]{2})(?P<countryCode>-[A-Z]{2})?.json$'
    MAP_PATH_DELIMITER = '.'

    @staticmethod
    def generate_json_locale_file(text_dict: OrderedDict = None,
                                  locale_folder_path=None,
                                  pivot_locale=None,
                                  need_print=True):
        if not text_dict:
            return
        generated_content = []
        # Guarantee non null variables
        nn_locale_folder_path = locale_folder_path \
                                or DEFAULT_PATH_ASSETS_TRANSLATIONS
        nn_pivot_locale = pivot_locale or DEFAULT_LOCALE
        # Create new locale keys
        new_string_dict = OrderedDict()
        for page, text_in_page in text_dict.items():
            prefix, page_without_type = FWidgetExtractor.localized_key_from_name(
                page)
            if not page_without_type:
                continue
            page_without_type = to_camel_case(page_without_type)
            for text_id, text_name_with_content in text_in_page.items():
                text_id_without_type = FWidgetExtractor.name_without_type(
                    text_name_with_content[0])
                if not text_id_without_type:
                    continue
                text_id_without_type = to_camel_case(text_id_without_type)
                if prefix not in new_string_dict:
                    new_string_dict[prefix] = OrderedDict()
                if page_without_type not in new_string_dict[prefix]:
                    new_string_dict[prefix][page_without_type] = OrderedDict()
                new_string_dict[prefix][page_without_type][
                    text_id_without_type] = text_name_with_content[1]
        # Check if locale file has content, then collect all
        file_path = f'{nn_locale_folder_path}/{nn_pivot_locale}.{FGenerator.DEFAULT_LOCALE_FILE_EXTENSION}'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'r', encoding='utf-8') as pivot_locale_file:
            pivot_locale_dict = json.loads(pivot_locale_file.read(),
                                           object_pairs_hook=OrderedDict)
        if pivot_locale_dict:
            # Merge with existed keys
            ordered_dict_merge(result_d=pivot_locale_dict,
                               complement_d=new_string_dict)
            file_path, _ = create_json_file(pivot_locale_dict,
                                            file_path)
            additional_info = ModifiedFileState.HAS_APPENDED
        else:
            file_path, additional_info = create_json_file(new_string_dict,
                                                          file_path)
        generated_content.append(
            make_content_output_file(file_path, additional_info))

        if need_print:
            beauty_printer(
                title='Successfully generated localization file',
                content=generated_content
            )

    @staticmethod
    def generate_color_file(named_colors: dict[str: NamedColor] = None,
                            folder: str = None,
                            need_print=True):
        if not named_colors:
            return
        header_file = """<?xml version="1.0" encoding="utf-8"?>
<resources>
"""
        footer_file = '</resources>'
        body_file = ''
        for hex_named_color, color in named_colors.items():
            if not color:
                continue
            name_snake_case = color.snake_case_latin_name
            body_file = body_file + f'    <color name="{name_snake_case}">{hex_named_color}</color>\n'
        file_path, additional_info = create_file(
            content=f'{header_file}{body_file}{footer_file}',
            file_name='colors',
            file_extension='xml',
            folder=folder or DEFAULT_PATH_ASSETS_COLORS
        )
        if need_print:
            beauty_printer(
                title='Successfully generated colors file',
                content=[make_content_output_file(file_path, additional_info)]
            )

    @staticmethod
    def generate_ui_file(f_gen_list: dict[str: str],
                         need_print=True):
        generated_files = []
        for path, f_w in (f_gen_list or {}).items():
            if not path or not f_w:
                continue
            path_component = path.split('/')
            folder = '/'.join(path_component[:-1])
            file_name = path_component[-1]
            file_path, additional_info = create_file(
                content=f_w,
                file_name=to_snake_case(file_name),
                file_extension='dart',
                folder=f'./lib/ui/{folder}'
            )
            generated_files.append(
                make_content_output_file(file_path, additional_info))
        # Also generate [resources.dart] which exports all generated files
        # by Flutter [build_runner]
        resource_path, modified_info = FGenerator._generate_ui_file(
            template_file_name='resources.dart',
            file_name='resources',
            package_name=get_flutter_project_package()
        )
        generated_files.append(
            make_content_output_file(resource_path, modified_info))
        if need_print and generated_files:
            beauty_printer(
                title='Successfully generated widget file',
                content=generated_files
            )

    @staticmethod
    def translate_locales(locale_folder_path=None,
                          pivot_locale=None,
                          supported_locale: list = None,
                          placeholder=None,
                          need_print=True):
        nn_locale_folder_path = locale_folder_path \
                                or DEFAULT_PATH_ASSETS_TRANSLATIONS
        nn_pivot_locale = pivot_locale or DEFAULT_LOCALE
        nn_supported_locale = supported_locale or []
        with open(
                f'{nn_locale_folder_path}/{nn_pivot_locale}.{FGenerator.DEFAULT_LOCALE_FILE_EXTENSION}',
                'r',
                encoding='utf-8'
        ) as pivot_locale_file:
            pivot_locale_dict = json.loads(pivot_locale_file.read(),
                                           object_pairs_hook=OrderedDict)
        # Translate lacked locale keys from other locales when compare to pivot locale
        # pivot_locale_dict = new_string_dict
        if not nn_supported_locale:
            # In case user doesn't define supported locales, then we browse
            # through locale folder to file all locales as much as possible
            _, _, filenames = next(walk(nn_locale_folder_path),
                                   (None, None, []))
            for filename in filenames:
                match_filename_info = re.search(FGenerator.REGEX_DETECT_LOCALE,
                                                filename)
                if match_filename_info:
                    language_code = match_filename_info.group('languageCode')
                    # Current [googletrans] library just support [languageCode]
                    locale = language_code
                    if locale != pivot_locale and locale not in nn_supported_locale:
                        nn_supported_locale.append(locale)
        if not nn_supported_locale or not pivot_locale:
            error_printer('Could not find any locale to translate!')
            return
        generated_content = []
        if pivot_locale_dict and nn_supported_locale:
            generated_files = run_parallel_tasks(
                FGenerator.generate_translated_locale,
                nn_supported_locale,
                nn_pivot_locale,
                nn_locale_folder_path,
                pivot_locale_dict,
                placeholder)
            generated_content.extend(generated_files)

        if need_print:
            beauty_printer(
                title='Successfully translated localization file',
                content=generated_content
            )

    @staticmethod
    def generate_translated_locale(locale: str,
                                   pivot_locale: str,
                                   folder_path: str,
                                   pivot_locale_dict: dict = None,
                                   placeholder: str = None):
        if not locale:
            error_printer('Locale is not valid!')
            return
        if not pivot_locale:
            error_printer('Source locale is not valid!')
            return
        if not folder_path:
            error_printer('Could not find translations folder!')
            return
        if not pivot_locale_dict:
            error_printer('Source of translation is not defined!')
            return

        # Start translating
        info_printer(f'Translating all text into locale [{locale}] ...',
                     emphasis=False)
        with open(
                f'{folder_path}/{locale}.{FGenerator.DEFAULT_LOCALE_FILE_EXTENSION}',
                'r',
                encoding='utf-8'
        ) as locale_file:
            locale_dict = json.loads(locale_file.read(),
                                     object_pairs_hook=OrderedDict)
        # Compare with pivot locale and find lacked keys, then create a complement dict
        complement_dict = OrderedDict()
        FGenerator._find_complement_of_2_dicts(
            complement_dict=complement_dict,
            pivot_dict=pivot_locale_dict,
            lacked_dict=locale_dict
        )
        # Translate
        locale_map_path = OrderedDict()
        FGenerator._convert_locale_tree_to_map_path(
            locale_dict=complement_dict,
            map_path=locale_map_path
        )
        keys_to_translate = [k for k in locale_map_path.keys()]
        strings_to_translate = [v for v in locale_map_path.values()]
        translator = Translator()
        translations = []
        # [googletrans] library currently has an issue about bulk mode
        for s in strings_to_translate:
            try:
                translation = translator.translate(
                    s,
                    dest=f'{locale}-cn' if locale == 'zh' else locale,
                    src=pivot_locale
                )
                print(f'🌏 {translation.origin} -> {translation.text}')
                translations.append(translation)
            except TypeError:
                translations.append(
                    f'{placeholder or DEFAULT_PLACEHOLDER_TRANSLATE} [{s}]')
        if len(translations) != len(keys_to_translate):
            error_printer('Oops... [googletrans] mismatch error!')
            return
        for i in range(len(translations)):
            t = translations[i]
            locale_map_path[keys_to_translate[i]] = t \
                if isinstance(t, str) else t.text
        complement_dict.clear()
        FGenerator._convert_map_path_to_locale_tree(
            map_path=locale_map_path,
            locale_dict=complement_dict
        )
        # Merge complement dict into full locale dict
        full_locale_dict = OrderedDict()
        FGenerator._merge_complement_to_lacked(
            complement_dict=complement_dict,
            lacked_dict=locale_dict,
            pivot_dict=pivot_locale_dict,
            result_dict=full_locale_dict
        )
        # Print lacked locale files which filled with complement locale keys
        file_path = f'{folder_path}_complement/{locale}.{FGenerator.DEFAULT_LOCALE_FILE_EXTENSION}'
        return make_content_output_file(*create_json_file(full_locale_dict,
                                                          file_path))

    @staticmethod
    def _generate_ui_file(template_file_name: str,
                          file_name: str,
                          folder: str = None,
                          *render_args,
                          **render_kwargs):
        env = Environment(
            loader=PackageLoader('kntgen_templates', 'ui'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template(template_file_name)
        content = template.render(*render_args, **render_kwargs)
        return create_file(
            content=content,
            file_name=file_name,
            file_extension='dart',
            folder=f'./lib/{folder}' if folder else './lib')

    @staticmethod
    def _find_complement_of_2_dicts(complement_dict: OrderedDict,
                                    pivot_dict: OrderedDict,
                                    lacked_dict: OrderedDict):
        if complement_dict is None or pivot_dict is None or lacked_dict is None:
            return
        for k, v in pivot_dict.items():
            if k not in lacked_dict:
                complement_dict[k] = v
            else:
                if not isinstance(v, OrderedDict):
                    continue
                if k not in complement_dict:
                    complement_dict[k] = OrderedDict()
                FGenerator._find_complement_of_2_dicts(
                    complement_dict=complement_dict[k],
                    pivot_dict=v,
                    lacked_dict=lacked_dict[k]
                )
                # Remove sub dict if it's empty
                if not complement_dict[k]:
                    complement_dict.pop(k, None)

    @staticmethod
    def _merge_complement_to_lacked(complement_dict: OrderedDict,
                                    lacked_dict: OrderedDict,
                                    pivot_dict: OrderedDict,
                                    result_dict: OrderedDict,
                                    previous_key=None):
        if complement_dict is None or pivot_dict is None \
                or lacked_dict is None or result_dict is None:
            return
        for k, v in pivot_dict.items():
            if k in lacked_dict:
                result_dict[k] = lacked_dict[k]
                previous_key = k
                if not isinstance(v, OrderedDict):
                    continue
                # Check dry-run if still has locale key need to be complemented in this lacked sub-dict
                if k in complement_dict:
                    FGenerator._merge_complement_to_lacked(
                        complement_dict=complement_dict[k],
                        lacked_dict=lacked_dict[k],
                        pivot_dict=v,
                        result_dict=result_dict[k]
                    )
                    previous_key = None
            else:
                insert_at_pos_ordered_dict(
                    dic=result_dict,
                    current_key_dict=k,
                    item=complement_dict[k],
                    key_to_insert_after=previous_key
                )
                previous_key = k

    @staticmethod
    def _convert_locale_tree_to_map_path(locale_dict: OrderedDict,
                                         map_path: OrderedDict,
                                         last_key: str = None):
        def _append_path(path, new_path):
            return f'{path}{FGenerator.MAP_PATH_DELIMITER}{new_path}' \
                if path else new_path

        def _remove_last_path(path):
            components = (path or '').split(FGenerator.MAP_PATH_DELIMITER)
            if not components:
                return ''
            components.pop()
            return FGenerator.MAP_PATH_DELIMITER.join(components)

        if locale_dict is None or map_path is None:
            return
        for k, v in locale_dict.items():
            if not isinstance(v, str) and not isinstance(v, OrderedDict):
                continue
            last_key = _append_path(last_key, k)
            if isinstance(v, str):
                map_path[last_key] = v
            if isinstance(v, OrderedDict):
                FGenerator._convert_locale_tree_to_map_path(
                    locale_dict=v,
                    map_path=map_path,
                    last_key=last_key
                )
            last_key = _remove_last_path(last_key)

    @staticmethod
    def _convert_map_path_to_locale_tree(map_path: OrderedDict,
                                         locale_dict: OrderedDict):
        if map_path is None or locale_dict is None:
            return
        for path, text in map_path.items():
            temp_dict = locale_dict
            components = (path or '').split(FGenerator.MAP_PATH_DELIMITER)
            if not components:
                continue
            for component in components[:-1]:
                if component not in temp_dict:
                    temp_dict[component] = OrderedDict()
                temp_dict = temp_dict[component]
            temp_dict[components[-1]] = text
