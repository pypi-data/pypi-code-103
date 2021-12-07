from kntgen.ui.figma import *
from kntgen.ui.flutter_parser import *


class FigmaUIGenerator:
    REGEX_FIGMA_LINK = r'(https:\/\/www.figma.com\/file\/)(?P<file_id>[A-Za-z0-9-]+)(\/\S.*\/?node-id=(?P<node_id>\S.*))?'

    def __init__(self, config: UiConfig):
        self.ui_config = config
        self.figma_config = config.figma
        self.google_config = config.google
        self.assets_config = config.assets
        self.file_id = ''
        self.node_id = ''
        self.figma = None
        self.file_node = None
        self.parent_node = None
        self._input_figma_source()

    def export_strings(self, need_print=True):
        parser = FStringParser(self.parent_node, self.figma, self.ui_config)
        parser.generate(folder=self.assets_config.translations,
                        pivot_locale=self.google_config.translate.main_locale,
                        need_print=need_print)

    def export_colors(self, need_print=True):
        parser = FColorParser(self.parent_node, self.figma, self.ui_config)
        parser.generate(folder=self.assets_config.colors,
                        need_print=need_print)

    def export_images(self, need_print=True):
        parser = FImageParser(self.parent_node, self.figma, self.ui_config)
        parser.generate(folder=self.assets_config.images,
                        svg_maximum_size=self.figma_config.maximum_svg_size_in_px,
                        need_print=need_print)

    def export_fonts(self, need_print=True):
        parser = FFontParser(self.parent_node, self.figma, self.ui_config)
        parser.generate(folder=self.assets_config.fonts,
                        api_key=self.google_config.font.api_key,
                        need_print=need_print)

    def export_widgets(self, need_preview=True):
        parser = FWidgetParser(self.parent_node, self.figma, self.ui_config)
        parser.generate(need_preview=need_preview,
                        gen_string=True,
                        gen_color=True,
                        gen_image=True,
                        gen_font=True)

    def export_enum(self, need_print=True):
        pass

    @staticmethod
    def translate_locale(folder: str = None,
                         pivot_locale: str = None,
                         placeholder: str = None,
                         need_print=True):
        FGenerator.translate_locales(locale_folder_path=folder,
                                     pivot_locale=pivot_locale,
                                     placeholder=placeholder,
                                     need_print=need_print)

    def _input_figma_source(self):
        def _print_finding_node_error(message=None):
            error_printer(message if message is not None
                          else f'Could not fetch Node information with id {self.node_id}!')
            exit(1)

        self.figma = FigmaPy(self.figma_config.access_token)
        self.file_id = self.figma_config.file_id
        self.node_id = self.figma_config.node_id

        if self.node_id is None or self.node_id.isspace():
            _print_finding_node_error(
                message='🙀 Sorry! No file id found!'
            )

        if self.node_id is None or self.node_id.isspace():
            _print_finding_node_error(
                message='🙀 Sorry! No node id found!'
            )

        info_printer(
            f'Fetching Figma File with file [{self.file_id}] node [{self.node_id}] ...')
        self.file_node = self.figma.get_file_nodes(
            file_key=self.file_id,
            ids=[self.node_id]
        )

        # Validate node information
        if self.node_id not in self.file_node.nodes:
            _print_finding_node_error()
        node_info = self.file_node.nodes[self.node_id]
        if node_info is None or 'document' not in node_info:
            _print_finding_node_error()
        self.parent_node = node_info['document']
        if self.parent_node is None or 'children' not in self.parent_node:
            _print_finding_node_error(
                message=f'Node {self.node_id} has no children!'
            )
        info_printer('Fetched Figma File successfully!')
