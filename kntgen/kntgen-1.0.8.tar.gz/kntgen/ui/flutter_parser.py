from kntgen.bash_helpers import *
from kntgen.model.flutter.flutter_raw_widget import *
from kntgen.model.flutter.flutter_specific_widgets import FConverter
from kntgen.ui.flutter_generator import *
from kntgen.ui.ui_external_source import *


class FParser:
    def __init__(self, parent_node, figma_py, ui_config: UiConfig):
        self.parent_node = parent_node
        self.figma_py = figma_py
        self.ui_config = ui_config
        self.figma_config = ui_config.figma
        self.google_config = ui_config.google
        self.assets_config = ui_config.assets
        self.file_id = self.figma_config.file_id


# -------------------------------------------------------------------------
# FLUTTER STRING
# -------------------------------------------------------------------------
class FStringParser(FParser):
    def generate(self,
                 folder: str = None,
                 pivot_locale: str = None,
                 need_print=True):
        # Fetch strings
        text_dict = OrderedDict()
        FWidgetExtractor.get_resource(self.parent_node,
                                      text_dict=text_dict,
                                      text_in_page_dict=OrderedDict())
        # Generate
        FStringParser.generate_flutter_source(strings=text_dict,
                                              locale_folder_path=folder,
                                              pivot_locale=pivot_locale,
                                              need_print=need_print)

    @staticmethod
    def generate_flutter_source(strings: OrderedDict = None,
                                locale_folder_path=None,
                                pivot_locale=None,
                                need_print=True):
        """
        Generate localization files. Get existed content from pivot file then translate into the other files. Just support JSON format

        :param strings: Dict contains locale keys
        :param locale_folder_path: Path to folder which contains locale files
        :param pivot_locale: File for defined which language is default
        :param need_print: Whether need printout generated files
        :return:
        """
        if strings is None:
            error_printer('Could not found any strings!')
            return
        warning_printer('Generating strings...')
        if need_print:
            for page, ordered_d in strings.items():
                if not ordered_d:
                    error_printer(f'Screen {page!r} has no text!',
                                  emphasis=False)
                    continue
                beauty_printer(
                    title=f'Text in screen {page!r}',
                    content=[f'[{text_id}] {text[1]}' for text_id, text in
                             ordered_d.items()],
                    max_char_inline=60
                )
        FGenerator.generate_json_locale_file(strings,
                                             locale_folder_path=locale_folder_path,
                                             pivot_locale=pivot_locale,
                                             need_print=need_print)


# -------------------------------------------------------------------------
# FLUTTER COLOR
# -------------------------------------------------------------------------
class FColorParser(FParser):
    def generate(self, folder=None, need_print=True):
        # Fetch colors
        hex_color_list = []
        FWidgetExtractor.get_resource(self.parent_node,
                                      hex_color_list=hex_color_list)
        # Fetch named colors
        named_colors = fetch_named_colors(hex_color_list or [])
        # Generate
        FColorParser.generate_flutter_source(named_colors=named_colors,
                                             folder=folder,
                                             need_print=need_print)

    @staticmethod
    def generate_flutter_source(named_colors: dict[str: NamedColor] = None,
                                folder: str = None,
                                need_print=True):
        if not named_colors:
            error_printer('Could not found any colors!')
            return
        warning_printer('Generating colors...')
        if need_print:
            beauty_print_named_colors(named_colors)
        FGenerator.generate_color_file(named_colors=named_colors,
                                       folder=folder,
                                       need_print=need_print)


# -------------------------------------------------------------------------
# FLUTTER IMAGE
# -------------------------------------------------------------------------
class FImageParser(FParser):
    def generate(self,
                 folder=None,
                 svg_maximum_size=None,
                 need_print=True):
        # Fetch images information
        image_node_dict = {}
        FWidgetExtractor.get_resource(self.parent_node,
                                      image_node_dict=image_node_dict)
        # Generate
        FImageParser.generate_flutter_source(
            figma_py=self.figma_py,
            file_id=self.file_id,
            folder=folder,
            image_node_dict=image_node_dict,
            svg_maximum_size=svg_maximum_size,
            need_print=need_print
        )

    @staticmethod
    def generate_flutter_source(figma_py,
                                file_id,
                                folder: str,
                                image_node_dict: dict = None,
                                svg_maximum_size=None,
                                need_print=True):
        if image_node_dict is None:
            error_printer('Could not found any images!')
            return
        warning_printer('Generating images...')
        # Split images into SVG (small size/icon) and PNG (2x scale with larger image)
        svg_images, scaled_2x_png_images = FImageParser.detect_image_extension(
            image_node_dict=image_node_dict,
            svg_maximum_size=svg_maximum_size
        )
        # Download images
        downloaded_image_paths = []
        downloaded_image_paths.extend(download_images(
            figma=figma_py,
            file_id=file_id,
            folder=folder,
            images=svg_images,
            format_image='svg'
        ))
        downloaded_image_paths.extend(download_images(
            figma=figma_py,
            file_id=file_id,
            folder=folder,
            images=scaled_2x_png_images
        ))
        if not downloaded_image_paths:
            print('Could not found any images!')
        if need_print:
            beauty_printer(title='Successfully downloaded images file',
                           content=downloaded_image_paths)

    @staticmethod
    def detect_image_extension(image_node_dict: dict = None,
                               svg_maximum_size=None):
        """
        :param image_node_dict: Keeps all detected images/icons from a Figma node
        :param svg_maximum_size: Maximum size as we could consider this image as a svg
        :return: A tuple contains (0: all svg images, 1: all png 2x scaled images)
        """
        svg_images = {}
        scaled_2x_png_images = {}
        if image_node_dict is None:
            return svg_images, scaled_2x_png_images

        nn_svg_maximum_size = svg_maximum_size or SVG_MAXIMUM_SIZE
        for image_id, node in image_node_dict.items():
            rect_node = FWidgetExtractor.as_rect(node)
            if rect_node.width < nn_svg_maximum_size \
                    and rect_node.height < nn_svg_maximum_size:
                svg_images[image_id] = node
            else:
                scaled_2x_png_images[image_id] = node
        return svg_images, scaled_2x_png_images


# -------------------------------------------------------------------------
# FLUTTER FONT
# -------------------------------------------------------------------------
class FFontParser(FParser):
    def generate(self,
                 api_key,
                 folder: str = None,
                 basic_font=False,
                 need_print=True):
        # Fetch fonts
        font_node_list = []
        FWidgetExtractor.get_resource(self.parent_node,
                                      font_node_list=font_node_list)
        # Generate
        FFontParser.generate_flutter_source(font_node_list=font_node_list,
                                            folder=folder,
                                            api_key=api_key,
                                            basic_font=basic_font,
                                            need_print=need_print)

    @staticmethod
    def generate_flutter_source(font_node_list: list = None,
                                folder: str = None,
                                api_key: str = None,
                                basic_font=False,
                                need_print=True):
        if font_node_list is None:
            error_printer('Could not found any font styles!')
            return
        warning_printer('Generating fonts...')
        google_font_dict = TextStyle.extract_google_font_family(
            font_node_list,
            basic_font
        )
        downloaded_font_paths = download_fonts(
            google_font_dict=google_font_dict,
            api_key=api_key,
            folder=folder)
        if not downloaded_font_paths:
            print('Could not found any font styles!')
        if need_print:
            beauty_printer(title='Successfully downloaded fonts file',
                           content=downloaded_font_paths)


# -------------------------------------------------------------------------
# FLUTTER WIDGET
# -------------------------------------------------------------------------
class FWidgetParser(FParser):
    def __init__(self, parent_node, figma_py, ui_config: UiConfig):
        super().__init__(parent_node, figma_py, ui_config)
        # Strings data structure: { 'text_id' : 'LocaleKeys.camelCase' }
        self.strings_mapping: dict[str: str] = {}
        # Colors data structure: { 'hex_color': 'ColorName.camelCaseNamedColor' }
        self.colors_mapping: dict[str: str] = {}
        # Images data structure: { 'image_node_id':
        # { 'path' : 'Assets.images.svg/img.camelCase', 'format': 'svg' } }
        self.images_mapping: dict[str: NamedImage] = {}

    def generate(self,
                 need_preview=True,
                 gen_string=True,
                 gen_color=True,
                 gen_image=True,
                 gen_font=True):
        """
        Generate all resource from this [figma_node] which we need to create widgets
        in Flutter, such as images/strings/colors/fonts

        :param need_preview: Whether need to printout to console or not
        :param gen_image: Whether need to generate images or not
        :param gen_string: Whether need to generate strings or not
        :param gen_color: Whether need to generate colors or not
        :param gen_font: Whether need to generate fonts or not
        :return:
        """
        # Reset data
        self.strings_mapping.clear()
        self.colors_mapping.clear()
        self.images_mapping.clear()
        FRawWidget.SCREEN_DESIGN_WIDTH = self.figma_config.screen_width
        FRawWidget.SCREEN_DESIGN_HEIGHT = self.figma_config.screen_height
        # Detect screen node
        custom_widget_nodes = []
        FWidgetExtractor.find_all_custom_widget_node(self.parent_node,
                                                     custom_widget_nodes)
        # Fetching resources from root node
        gen_content_dict = {}
        text_dict = OrderedDict()
        hex_color_list = []
        image_node_dict = {}
        font_node_list = []
        FWidgetExtractor.get_resource(self.parent_node,
                                      text_dict=text_dict,
                                      text_in_page_dict=OrderedDict(),
                                      hex_color_list=hex_color_list,
                                      image_node_dict=image_node_dict,
                                      font_node_list=font_node_list)
        named_color_dict = fetch_named_colors(hex_color_list or [])
        # Convert resource to Flutter based mapping
        # Convert strings
        for custom_widget_name, text_in_widget in text_dict.items():
            for text_id, text_name_with_content in text_in_widget.items():
                localized_text = NamedLocaleText.localized(
                    custom_widget_name=custom_widget_name,
                    text_name=text_name_with_content[0]
                )
                if not localized_text:
                    continue
                self.strings_mapping[text_id] = localized_text
        # Convert colors
        self.colors_mapping = {
            hex_c: named_c.flutter_gen_color
            for
            hex_c, named_c in named_color_dict.items()}
        # Convert images
        svg_images, scaled_2x_png_images = FImageParser.detect_image_extension(
            image_node_dict=image_node_dict,
            svg_maximum_size=self.figma_config.maximum_svg_size_in_px
        )
        self.images_mapping = {
            image_id: NamedImage(
                image_name=image_node['name'],
                image_format='svg'
            )
            for
            image_id, image_node in
            svg_images.items() if 'name' in image_node}
        self.images_mapping.update({
            image_id: NamedImage(
                image_name=image_node['name'],
                image_format='png'
            )
            for
            image_id, image_node in
            scaled_2x_png_images.items() if 'name' in image_node})

        # Generate strings
        if gen_string:
            FStringParser.generate_flutter_source(
                strings=text_dict,
                locale_folder_path=self.assets_config.translations,
                pivot_locale=self.google_config.translate.main_locale,
                need_print=need_preview)
        # Generate colors
        if gen_color:
            FColorParser.generate_flutter_source(
                named_color_dict,
                folder=self.assets_config.colors,
                need_print=need_preview)
        # Generate images
        if gen_image:
            FImageParser.generate_flutter_source(
                self.figma_py,
                self.file_id,
                folder=self.assets_config.images,
                image_node_dict=image_node_dict,
                svg_maximum_size=self.figma_config.maximum_svg_size_in_px,
                need_print=need_preview)
        # Generate fonts
        if gen_font:
            FFontParser.generate_flutter_source(
                font_node_list=font_node_list,
                folder=self.assets_config.fonts,
                api_key=self.google_config.font.api_key,
                basic_font=self.google_config.font.basic_font,
                need_print=need_preview)
        # Generate needed resource paths before generating widgets
        if gen_string:
            bash_execute(FLUTTER_GEN_LOCALE)
        if gen_color or gen_image or gen_font:
            bash_execute(FLUTTER_GEN)

        # Fetching Flutter Raw Widgets
        for widget_node in custom_widget_nodes:
            root_view = self._make_tree_view(widget_node)
            if not root_view or not root_view.children:
                continue
            self._optimize_tree_views(root_view)
            if root_view.type == FWidgetType.PAGE:
                # Update screen design size
                FRawWidget.SCREEN_DESIGN_WIDTH = root_view.rect.width
                FRawWidget.SCREEN_DESIGN_HEIGHT = root_view.rect.height
            # Convert resources into a mapping dict for Flutter generator
            f_root_widget = FConverter.convert(root_view)
            FConverter.generate_widgets(
                current_widget=f_root_widget,
                gen_content_dict=gen_content_dict,
                strings_mapping=self.strings_mapping,
                colors_mapping=self.colors_mapping,
                images_mapping=self.images_mapping
            )
            # TODO: In case we just have tpage without page, then generate new page
            if need_preview:
                need_print_custom_widget = root_view.type != FWidgetType.PAGE \
                                           and root_view.type != FWidgetType.TAB_PAGE
                FWidgetParser.preview_tree_view(
                    root_view,
                    need_print_custom_widget=need_print_custom_widget
                )

        # Generate widgets and files
        warning_printer('Generating widgets...')
        FGenerator.generate_ui_file(gen_content_dict)

        # Format Dart code
        bash_execute(command=FLUTTER_FORMAT)

    def _make_tree_view(self, current_node: dict):
        f_widget = FWidgetExtractor.figma_to_raw_flutter(current_node)
        if not f_widget:
            return None
        # Filter useless node
        child_nodes = current_node['children'] \
            if 'children' in current_node \
            else []
        if len(child_nodes) == 0 \
                and f_widget.type == FWidgetType.IGNORED:
            # Ignore this single view has ignored type
            return None

        # Filter customized node
        if f_widget.is_custom_widget:
            current_id = current_node['id'] if 'id' in current_node else ''
            customized_node = current_node.copy()
            customized_node['id'] = f'{current_id}+'
            customized_node['name'] = ''
            first_child_view = self._make_tree_view(customized_node)
            if first_child_view:
                f_widget.children.append(first_child_view)
            return f_widget

        # Filter node that presented as a single view
        if not f_widget.type.is_view_group() \
                and f_widget.type != FWidgetType.IGNORED:
            # Will return defined Flutter single view type
            return f_widget

        # Create children
        child_views = []
        for child_node in child_nodes:
            child_view = self._make_tree_view(child_node)
            if child_view:
                child_views.append(child_view)
        if len(child_views) == 0:
            # Ignore the view which doesn't contain any FlutterView as child
            return None
        FWidgetParser.detect_view_group(f_widget, child_views)
        return f_widget

    def _optimize_tree_views(self, current_view: FRawWidget):
        """
        Merge all child views from parent view into grandpa view if
        grandpa view has the same type as parent view. Only consider flex
        view group type.

        Note: WRAP type will absorb all the other flex types

        :param current_view:
        :return:
        """
        if not current_view:
            return

        for index, child in enumerate(current_view.children):
            self._optimize_tree_views(child)
            if not child.type.is_flex_view_group():
                continue
            if current_view.type != FWidgetType.WRAP \
                    and child.type != current_view.type:
                continue
            # Merge all child views of this `child` into its `parent`
            # (i.e. current_view in this case)
            current_view.children.pop(index)
            for sub_index, sub_child in enumerate(child.children):
                current_view.children.insert(index + sub_index, sub_child)
        current_view.optimize_view_type()
        # Final sorting by left/top to get correct order of row/column
        # Because in some cases finding vertices algorithm has exceptions
        if current_view.type == FWidgetType.ROW:
            current_view.children.sort(key=lambda c: c.rect.left)
        if current_view.type == FWidgetType.COLUMN:
            current_view.children.sort(key=lambda c: c.rect.top)

    @staticmethod
    def detect_view_group(flutter_view: FRawWidget,
                          child_views: list[FRawWidget]):
        """
        Defined by consistent view group type such as ListView/GridView

        or

        Calculate position of child views to detect type of this view as a flex view group
        such as Stack/Column/Row/Wrap

        :param flutter_view: Parent view
        :param child_views: Child views which are considered to append in the [flutter_view] by order. Sorted by ascending z-axis from Figma
        :return: Parent view after detected type and grouped ordered child views
        """
        if not flutter_view:
            return None

        if not child_views or len(child_views) == 0:
            return flutter_view

        # ----Detect background of flutter_view----
        # Usually is the first child which has lowest z-value
        # Ignore the background view
        background_view = None
        clutter_views = []
        # Filter background view and the other clutter views
        for child_v in child_views:
            # Always store the latest background
            if child_v.type == FWidgetType.BACKGROUND:
                background_view = child_v
            else:
                clutter_views.append(child_v)
        if background_view:
            flutter_view.type = FWidgetType.STACK
            flutter_view.children.clear()
            flutter_view.children.append(background_view)
            group_other_views = FWidgetParser.make_group_view(flutter_view,
                                                              clutter_views)
            if group_other_views:
                FWidgetParser.detect_view_group(group_other_views,
                                                clutter_views)
                flutter_view.children.append(group_other_views)
            return flutter_view

        # Filter useless view
        if not clutter_views or len(clutter_views) == 0:
            return flutter_view

        # ----Detect Stack View----
        # clutter_views is sorted by ascending z-axis because child_views is sorted by same way
        # Check overlapping from higher z to lower z
        for higher_z_index in range(len(clutter_views) - 1, 0, -1):
            higher_view = clutter_views[higher_z_index]
            for lower_z_index in range(higher_z_index - 1, -1, -1):
                lower_view = clutter_views[lower_z_index]
                if higher_view.rect.is_contained_by(lower_view.rect) or \
                        higher_view.rect.is_intersected_with(
                            lower_view.rect):
                    flutter_view.type = FWidgetType.STACK
                    flutter_view.children.clear()
                    lower_clutter_views = clutter_views[:higher_z_index]
                    group_other_views = FWidgetParser.make_group_view(
                        flutter_view,
                        lower_clutter_views
                    )
                    if group_other_views:
                        FWidgetParser.detect_view_group(group_other_views,
                                                        lower_clutter_views)
                        flutter_view.children.append(group_other_views)
                    flutter_view.children.append(higher_view)
                    return flutter_view

        # ----Detect consistent view group----
        if flutter_view.type.is_consistent_view_group():
            flutter_view.children = [clutter_views[0]]
            return flutter_view

        # ----Default is CONTAINER if child_views contains only 1 child----
        if len(clutter_views) == 1:
            if flutter_view.type == FWidgetType.IGNORED:
                flutter_view.type = FWidgetType.CONTAINER
                flutter_view.children = clutter_views
            return flutter_view

        # ----Detect Column/Row/Wrap View----
        # Step 1: Find 4 vertices of this view
        #       -Y
        #        ↑
        # -X ← O(x, y) → X
        #        ↓
        #        Y
        top_left_most, bottom_left_most, top_right_most, bottom_right_most = None, None, None, None
        cur_tl, cur_bl, cur_tr, cur_br = None, None, None, None
        for child_v in clutter_views:
            v_rect = child_v.rect
            # Find the top left most: min(x+y)
            tl = v_rect.left + v_rect.top
            if not cur_tl or tl < cur_tl:
                top_left_most = child_v
                cur_tl = tl

            # Find the bottom left most: min(x-y)
            bl = v_rect.left - v_rect.bottom
            if not cur_bl or bl < cur_bl:
                bottom_left_most = child_v
                cur_bl = bl

            # Find the top right most: max(x-y)
            tr = v_rect.right - v_rect.top
            if not cur_tr or tr > cur_tr:
                top_right_most = child_v
                cur_tr = tr

            # Find the bottom right most: max(x+y)
            br = v_rect.right + v_rect.bottom
            if not cur_br or br > cur_br:
                bottom_right_most = child_v
                cur_br = br

        fill_left_side = top_left_most == bottom_left_most
        fill_top_side = top_left_most == top_right_most
        fill_right_side = top_right_most == bottom_right_most
        fill_bottom_side = bottom_left_most == bottom_right_most

        # Step 2: Find side-positional view which occupy 2 vertices
        def _find_ordered_views():
            # WRAP type just need to take the first child
            if flutter_view.type is FWidgetType.WRAP:
                return [top_left_most]

            # If each view occupies just 1 vertex then flutter_view is a COLUMN by default
            if not fill_left_side and not fill_top_side \
                    and not fill_right_side and not fill_bottom_side:
                # Find highest top vertex
                flutter_view.type = FWidgetType.COLUMN
                return [
                    top_left_most
                    if top_left_most.rect.top > top_right_most.rect.top
                    else top_right_most
                ]

            # If 1 view occupies 4 vertices e.g. 1 view has width height too large
            # than the other views, then compare relative position with the other views
            if fill_left_side and fill_top_side \
                    and fill_right_side and fill_bottom_side:
                for clutter_v in [v for v in clutter_views if
                                  v != top_left_most]:
                    if clutter_v.rect.right >= top_left_most.rect.right:
                        flutter_view.type = FWidgetType.ROW
                        return [top_left_most]
                    if clutter_v.rect.bottom >= top_left_most.rect.bottom:
                        flutter_view.type = FWidgetType.COLUMN
                        return [top_left_most]

            # Check whether 1 view occupies 3 vertices then we need to compare relative
            # position with the other view which occupies remaining vertex
            if fill_left_side and fill_top_side:
                # Compare relative position with bottom right most to detect row or column
                flutter_view.type = FWidgetType.ROW \
                    if bottom_right_most.rect.left >= top_left_most.rect.right \
                    else FWidgetType.COLUMN
                return [top_left_most]

            if fill_left_side and fill_bottom_side:
                flutter_view.type = FWidgetType.ROW \
                    if top_right_most.rect.left >= top_left_most.rect.right \
                    else FWidgetType.COLUMN
                return [top_left_most]

            if fill_right_side and fill_top_side:
                flutter_view.type = FWidgetType.ROW \
                    if bottom_left_most.rect.right <= top_right_most.rect.left \
                    else FWidgetType.COLUMN
                return [top_left_most]

            if fill_right_side and fill_bottom_side:
                flutter_view.type = FWidgetType.ROW \
                    if top_left_most.rect.right <= top_right_most.rect.left \
                    else FWidgetType.COLUMN
                return [top_left_most]

            # Otherwise in normal case, when 1 view occupies 2 vertices then
            # we could define the view group's type
            ordered_views = []
            if fill_left_side:
                flutter_view.type = FWidgetType.ROW
                ordered_views.append(top_left_most)
            if fill_top_side:
                flutter_view.type = FWidgetType.COLUMN
                ordered_views.append(top_left_most)
            if fill_right_side:
                flutter_view.type = FWidgetType.ROW
                ordered_views.append(bottom_right_most)
            if fill_bottom_side:
                flutter_view.type = FWidgetType.COLUMN
                ordered_views.append(bottom_right_most)
            return ordered_views

        # Find and disabled redundant sides
        ordered_child_views = _find_ordered_views()
        if len(ordered_child_views) == 1:
            if ordered_child_views[0] == top_left_most:
                if flutter_view.type == FWidgetType.ROW:
                    fill_right_side = False
                if flutter_view.type == FWidgetType.COLUMN:
                    fill_bottom_side = False
            if ordered_child_views[0] == bottom_right_most:
                if flutter_view.type == FWidgetType.ROW:
                    fill_left_side = False
                if flutter_view.type == FWidgetType.COLUMN:
                    fill_top_side = False

        # Step 3: Group the other views into a new frame then recur to (step 1)
        un_ordered_child_views = [child for child in clutter_views if
                                  child not in ordered_child_views]

        # Final check to filter some case that finding vertices algorithm
        # could not handle e.g view has width to long so it will occupy
        # left side but actually it just occupy top left vertex in design file
        removed_ordered_child_views = []
        for un_ordered_child in un_ordered_child_views:
            if flutter_view.type == FWidgetType.ROW:
                if fill_left_side \
                        and un_ordered_child.rect.left < top_left_most.rect.right:
                    if top_left_most in ordered_child_views:
                        ordered_child_views.remove(top_left_most)
                    removed_ordered_child_views.append(top_left_most)
                if fill_right_side \
                        and un_ordered_child.rect.right > bottom_right_most.rect.left:
                    if bottom_right_most in ordered_child_views:
                        ordered_child_views.remove(bottom_right_most)
                    removed_ordered_child_views.append(bottom_right_most)
            if flutter_view.type == FWidgetType.COLUMN:
                if fill_top_side \
                        and un_ordered_child.rect.top < top_left_most.rect.bottom:
                    if top_left_most in ordered_child_views:
                        ordered_child_views.remove(top_left_most)
                    removed_ordered_child_views.append(top_left_most)
                if fill_bottom_side \
                        and un_ordered_child.rect.bottom > bottom_right_most.rect.top:
                    if bottom_right_most in ordered_child_views:
                        ordered_child_views.remove(bottom_right_most)
                    removed_ordered_child_views.append(bottom_right_most)
        un_ordered_child_views.extend(removed_ordered_child_views)

        # Filter useless view group
        if len(ordered_child_views) == 0:
            return flutter_view

        # Make a clutter view group from unordered views
        group_other_views = FWidgetParser.make_group_view(flutter_view,
                                                          un_ordered_child_views)

        # Step 4: Detect ordered children of view group of this view
        if group_other_views:
            FWidgetParser.detect_view_group(group_other_views,
                                            un_ordered_child_views)
            if flutter_view.type == FWidgetType.WRAP:
                ordered_child_views.append(group_other_views)
            elif flutter_view.type == FWidgetType.COLUMN:
                ordered_child_views.insert(
                    1 if len(ordered_child_views) > 0 and ordered_child_views[
                        0] == top_left_most else 0,
                    group_other_views
                )
            elif flutter_view.type == FWidgetType.ROW:
                ordered_child_views.insert(
                    1 if len(ordered_child_views) > 0 and ordered_child_views[
                        0] == top_left_most else 0,
                    group_other_views
                )
        flutter_view.children = ordered_child_views
        return flutter_view

    @staticmethod
    def make_group_view(parent_view: FRawWidget,
                        other_child_views: [FRawWidget]):
        total_other_child = len(other_child_views)
        if total_other_child == 0:
            return None
        first_child = other_child_views[0]
        if total_other_child == 1:
            return first_child
        left_most = first_child.rect.left
        top_most = first_child.rect.top
        right_most = first_child.rect.right
        bottom_most = first_child.rect.bottom
        for index_other_child in range(total_other_child):
            other_child = other_child_views[index_other_child]
            if left_most > other_child.rect.left:
                left_most = other_child.rect.left
            if top_most > other_child.rect.top:
                top_most = other_child.rect.top
            if right_most < other_child.rect.right:
                right_most = other_child.rect.right
            if bottom_most < other_child.rect.bottom:
                bottom_most = other_child.rect.bottom
        v_type = FWidgetType.WRAP \
            if parent_view.type is FWidgetType.WRAP \
            else FWidgetType.IGNORED
        return FRawWidget(
            figma_node={
                'id': f'{parent_view.id_view}+',
                'name': '',
                'absoluteBoundingBox': {
                    'x': left_most,
                    'y': top_most,
                    'width': right_most - left_most,
                    'height': bottom_most - top_most
                },
                'children': [child_dict.figma_node for child_dict in
                             other_child_views]
            },
            v_type=v_type,
            children=other_child_views
        )

    @staticmethod
    def preview_tree_view(root_view: FRawWidget,
                          need_print_custom_widget=True):

        def print_view(current_view: FRawWidget,
                       content_printer: [str],
                       level=0,
                       level_still_has_child: list[int] = None,
                       is_last_child=False,
                       defined_prefix=None):
            level_template = '│' + 5 * space_char
            space_template = 6 * space_char
            box_char = '└' if is_last_child else '├'
            prefix = '' if not defined_prefix \
                else f'{defined_prefix}{box_char}───'

            # Find next level prefix
            def _this_level_still_has_child(cur_level):
                for lv in level_still_has_child:
                    if cur_level == lv:
                        return True
                return False

            prefix_list = []
            for i in range(level):
                prefix_list.append(level_template
                                   if _this_level_still_has_child(i)
                                   else space_template)
            next_prefix = space_template + ''.join(prefix_list)
            hide_custom_type = current_view.type == FWidgetType.NEW_WIDGET \
                               and not need_print_custom_widget
            # Append child line
            child_line = f'{fixed_space_line}{prefix}{current_view.present}'
            content_printer.append(child_line)
            # Append space line
            child_views = current_view.children
            total_children = len(child_views)
            space_line_template = (defined_prefix or '') \
                if is_last_child and total_children == 0 else next_prefix
            space_line_last_char = '' if total_children == 0 \
                                         or hide_custom_type else '│'
            space_line = f'{fixed_space_line}{space_line_template}{space_line_last_char}'
            content_printer.append(space_line)
            # Append children view line
            if hide_custom_type:
                return
            for index, child in enumerate(child_views):
                is_last_child = index == total_children - 1
                if is_last_child and _this_level_still_has_child(level):
                    level_still_has_child.remove(level)
                elif not is_last_child \
                        and not _this_level_still_has_child(level):
                    level_still_has_child.append(level)
                print_view(
                    child,
                    content_printer,
                    level + 1,
                    level_still_has_child=level_still_has_child,
                    is_last_child=is_last_child,
                    defined_prefix=next_prefix
                )

        if not root_view:
            return
        # Show preview of generated view in console
        current_level = 0
        space_char = ' '
        fixed_space_line = 8 * space_char
        content = ['\n']
        print_view(root_view,
                   content,
                   current_level,
                   level_still_has_child=[])
        content.append('\n')
        beauty_printer(
            title=f'Preview for {root_view.full_name!r} widget',
            content=content,
            need_line_separate=False,
            max_char_inline=100
        )
