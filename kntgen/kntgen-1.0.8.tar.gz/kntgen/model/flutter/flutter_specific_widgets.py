from kntgen.model.flutter.flutter_base_widgets import *


class FConverter:
    @staticmethod
    def convert(raw_widget: FRawWidget):
        """
        :return: Flutter Specific Widget
        """
        f_widget = None
        if raw_widget.type == FWidgetType.NEW_WIDGET:
            f_widget = FCustom(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.PAGE:
            f_widget = FPage(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.TAB_PAGE:
            f_widget = FTabPage(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.CONTAINER \
                or raw_widget.type == FWidgetType.BACKGROUND:
            f_widget = FContainer(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.COLUMN:
            f_widget = FColumn(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.ROW:
            f_widget = FRow(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.WRAP:
            f_widget = FWrap(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.WRAP_VERTICAL:
            f_widget = FWrap(raw_widget.figma_node, is_horizontal=False)
        if raw_widget.type == FWidgetType.STACK:
            f_widget = FStack(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.LIST_VIEW:
            f_widget = FList(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.LIST_VIEW_HORIZONTAL:
            f_widget = FList(raw_widget.figma_node, is_horizontal=True)
        if raw_widget.type == FWidgetType.GRID_VIEW:
            f_widget = FGrid(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.GRID_VIEW_HORIZONTAL:
            f_widget = FGrid(raw_widget.figma_node, is_horizontal=True)
        if raw_widget.type == FWidgetType.APP_BAR:
            f_widget = FAppbar(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.TOOL_BAR:
            f_widget = FToolbar(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.BOTTOM_BAR:
            f_widget = FBottomBar(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.TEXT:
            f_widget = FText(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.TEXT_FIELD:
            f_widget = FTextField(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.IMAGE \
                or raw_widget.type == FWidgetType.ICON:
            f_widget = FImage(raw_widget.figma_node)
        if raw_widget.type == FWidgetType.DIVIDER:
            f_widget = FDivider(raw_widget.figma_node)
        if not f_widget:
            f_widget = FWidget(raw_widget.figma_node)
        # Recursive to convert this raw widget's children
        for child_raw_w in raw_widget.children:
            f_child_widget = FConverter.convert(child_raw_w)
            if f_child_widget:
                f_child_widget.parent = f_widget
                # Row/Column will has relative size of it's wrapper
                if child_raw_w.type == FWidgetType.ROW:
                    f_child_widget.rect.left = f_widget.rect.left
                    f_child_widget.rect.right = f_widget.rect.right
                if child_raw_w.type == FWidgetType.COLUMN:
                    f_child_widget.rect.top = f_widget.rect.top
                    f_child_widget.rect.bottom = f_widget.rect.bottom
                f_widget.children.append(f_child_widget)
        return f_widget

    @staticmethod
    def generate_widgets(current_widget,
                         gen_content_dict: dict,
                         strings_mapping: dict,
                         colors_mapping: dict,
                         images_mapping: dict):
        if current_widget is None or gen_content_dict is None:
            return
        if not isinstance(current_widget, FCustom):
            return
        content = current_widget.generate(
            strings_mapping=strings_mapping,
            colors_mapping=colors_mapping,
            images_mapping=images_mapping
        )
        gen_content_dict[
            f'{current_widget.generate_relative_file_path()}'] = content


class FPage(FCustom):
    def generate_build(self,
                       strings_mapping: dict,
                       colors_mapping: dict,
                       images_mapping: dict):
        # FIXME: check condition
        bottom_bar_present = f"""
        bottomNavigationBar: BottomNav(
                starterTabIndex: _currentIndexTab,
                onChoseTab: _onChoseTab,
              ), """ \
            if self.has_bottom_navigation_bar() else ''
        tab_present = f"""CustomBB()""" if self.has_bottom_navigation_bar() else \
            super().generate_build(
                strings_mapping=strings_mapping,
                colors_mapping=colors_mapping,
                images_mapping=images_mapping
            )
        return f"""
BlackStatusBarPage(
    page: Scaffold({bottom_bar_present}
        body: {tab_present},
    ),
)"""

    def generate(self,
                 strings_mapping: dict,
                 colors_mapping: dict,
                 images_mapping: dict):
        custom_generate = super().generate(strings_mapping=strings_mapping,
                                           colors_mapping=colors_mapping,
                                           images_mapping=images_mapping)
        return f"""
import '../custom/custom_status_bar_page.dart';
{custom_generate}
"""

    def has_bottom_navigation_bar(self):
        for child in self.children or []:
            if FWidgetType.BOTTOM_BAR.value in child.w_name:
                return True
        return False

    def generated_file_name(self):
        return f'{self.w_name}_page'

    def generate_container_folder(self):
        return 'pages'

    @property
    def w_class(self):
        return to_pascal_case(self.w_name)


class FTabPage(FCustom):
    def generated_file_name(self):
        page_name = self._interpolate_page_name
        tab_name = self.w_name.replace(f'_{page_name}', '') \
            if f'_{page_name}' in self.w_name else self.w_name
        return f'tab_{tab_name}'

    def generate_container_folder(self):
        return f'pages/{self._interpolate_page_name}/tabs'

    @property
    def w_class(self):
        return f'Tab{to_pascal_case(self.w_name)}'

    @property
    def _interpolate_page_name(self):
        return to_snake_case(self.w_raw_name).split('_')[-1]


class FAppbar(FWidget):
    @property
    def w_class(self):
        return 'KntDefaultAppBar'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        return [
            'titlePage: \'{empty_title}\''
        ]


class FToolbar(FWidget):
    @property
    def w_class(self):
        return 'KntDefaultToolBar'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        return [
            'titlePage: \'{empty_title}\''
        ]


class FBottomBar(FWidget):
    @property
    def w_class(self):
        return 'KntBottomNavScaffold'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        return [
            'onTabChanged: ValueNotifier<int>(0)',
            'appBar: KntAppBar(titlePage: \'{empty_title}\')',
            'icons: []',
            'tabs: []'
        ]


class FContainer(FWidget):
    @property
    def w_class(self):
        return 'Container'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        width, height = self.w_size_present
        # Ignore size if parent widget has type FCustom
        if isinstance(self.parent, FCustom):
            width = ''
            height = ''
        # Calculate insets if needed
        margin = ''
        if isinstance(self.parent, FViewGroup):
            # Merge Flutter Padding#padding with this Container#margin
            margin = FWidget.extract_edge_insets(
                self.margin,
                specific_edges=self.parent.needed_child_edge_insets,
                inset_type=InsetType.MARGIN
            )
        padding = ''
        if self.children:
            padding = FWidget.extract_edge_insets(
                self.padding,
                specific_edges=[Edge.LEFT, Edge.TOP, Edge.RIGHT, Edge.BOTTOM]
            )
        return [
            width,
            height,
            margin,
            padding,
            self._decoration(
                colors_mapping=colors_mapping,
                images_mapping=images_mapping
            ),
            self.generate_child(
                strings_mapping=strings_mapping,
                colors_mapping=colors_mapping,
                images_mapping=images_mapping
            )
        ]

    def generate_wrapper(self, generated_content):
        return generated_content

    def _decoration(self, colors_mapping: dict, images_mapping: dict):
        deco_plist = [
            self._deco_background_color(colors_mapping),
            self._deco_radius(),
            self._deco_stroke(colors_mapping),
            self._deco_shadow(colors_mapping),
            self._deco_image(images_mapping)
        ]
        deco_plist_present = ''.join(f'{d},\n' for d in deco_plist if d)
        return f'decoration: BoxDecoration({deco_plist_present})' \
            if deco_plist_present else ''

    def _deco_image(self, images_mapping: dict):
        image_path = FWidget.extract_image_path(self.w_id, images_mapping)
        return f'image: DecorationImage(image: AssetImage({image_path}), ' \
               f'fit: BoxFit.cover,)' if image_path else None

    def _deco_background_color(self, colors_mapping: dict):
        return FWidget.extract_colors(self.figma_node, colors_mapping)

    def _deco_stroke(self, colors_mapping: dict):
        return FWidget.extract_border(self.figma_node, colors_mapping)

    def _deco_radius(self):
        return FWidget.extract_border_radius(self.figma_node)

    def _deco_shadow(self, colors_mapping: dict):
        return FWidget.extract_shadows(self.figma_node, colors_mapping)


class FText(FWidget):
    SPECIAL_CHARS = '\'$'
    EMPTY_TEXT = '{empty_text}'

    def __init__(self, figma_node, children: list = None):
        super().__init__(figma_node, children)
        self.text_related = FWidgetExtractor.text_related(figma_node)

    @property
    def w_class(self):
        # TODO: Rich text if self.text_related has not None character_style_override
        return 'Text'

    @property
    def is_flex_size(self):
        return True

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        if not self.text_related:
            return [FText.EMPTY_TEXT]
        style = self.text_related.style
        character = ''.join(
            [c for c in self.text_related.character if
             c not in FText.SPECIAL_CHARS])
        character = f'{character!r}'
        if self.w_id in strings_mapping:
            localized_text = strings_mapping[self.w_id]
            if localized_text:
                character = localized_text
        color_present = self.text_related.present_f_color(colors_mapping)
        if color_present:
            color_present = f'{color_present},'
        italic_present = '\nfontStyle: FontStyle.italic,' if style.italic else ''
        return [
            character,
            f"""style: TextStyle( {color_present}
    fontFamily: FontFamily.{to_camel_case(style.font_family)},
    fontSize: {style.font_size}.sp,
    fontWeight: FontWeight.w{style.font_weight}, {italic_present}
    height: {style.line_height_px}.sp / {style.font_size}.sp,
)"""
        ]


class FTextField(FText):
    @property
    def w_class(self):
        return 'KntSimpleEditText'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        if not self.text_related:
            return []
        style = self.text_related.style
        character = ''.join(
            [c for c in self.text_related.character if
             c not in FText.SPECIAL_CHARS])
        character = f'{character!r}'
        if self.w_id in strings_mapping:
            localized_text = strings_mapping[self.w_id]
            if localized_text:
                character = localized_text
        color_present = self.text_related.present_f_color(colors_mapping,
                                                          property_name='hintTextColor')
        return [
            f'hintText: {character}',
            color_present,
            f'fontSize: {style.font_size}.sp'
        ]


class FImage(FWidget):
    @property
    def w_class(self):
        return 'KntImage.assets'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        width, height = self.w_size_present
        return [
            self._image_url(images_mapping),
            width,
            height,
            self._border_radius()
        ]

    def _image_url(self, images_mapping: dict):
        image_path = FWidget.extract_image_path(self.w_id, images_mapping)
        return f'uri: {image_path}' if image_path else None

    def _border_radius(self):
        return FWidget.extract_border_radius(self.figma_node)


class FDivider(FWidget):
    @property
    def w_class(self):
        return 'const KntDivider'


class FColumn(FViewGroup):
    @property
    def w_class(self):
        return 'Column'

    @property
    def main_alignment(self):
        return self.y_alignment

    @property
    def cross_alignment(self):
        return self.x_alignment

    @property
    def direction(self):
        return Direction.VERTICAL

    def generate_direction(self) -> str:
        return None


class FRow(FViewGroup):
    @property
    def w_class(self):
        return 'Row'

    @property
    def main_alignment(self):
        return self.x_alignment

    @property
    def cross_alignment(self):
        return self.y_alignment

    @property
    def direction(self):
        return Direction.HORIZONTAL

    def generate_direction(self) -> str:
        return None


class FWrap(FViewGroup):
    def __init__(self, figma_node, children: list = None, is_horizontal=True):
        super().__init__(figma_node, children)
        self.is_horizontal = is_horizontal

    @property
    def w_class(self):
        return 'Wrap'

    def generate_direction(self) -> str:
        return 'direction: Axis.vertical' if self.direction == Direction.VERTICAL else None

    def generate_alignments(self) -> list[str]:
        return []


class FStack(FWidget):
    @property
    def w_class(self):
        return 'Stack'

    def generate_child_wrapper(self, child_widget, generated_child_content):
        if not generated_child_content:
            return generated_child_content
        positioned = FStack.calculate_child_position(child_widget)
        return f'Positioned({positioned},child:{generated_child_content},)' \
            if positioned else generated_child_content

    @staticmethod
    def calculate_child_position(child_widget):
        if not child_widget or not child_widget.margin \
                or len(child_widget.margin) < 4:
            return ''
        # Fetch margin from this child
        margin = [v for v in child_widget.margin.values()]
        # Present margin
        horizontal_position = f'left: {margin[0]}.w' if margin[0] < margin[
            2] else f'right: {margin[2]}.w'
        if child_widget.rect.width > child_widget.parent.rect.width \
                * (1 - FWidget.POSITIONED_STACK_OFFSET_RATIO):
            horizontal_position = f'left: {margin[0]}.w, right: {margin[2]}.w'
        vertical_position = f'top: {margin[1]}.w' if margin[1] < margin[3] \
            else f'bottom: {margin[3]}.w'
        return ','.join([
            horizontal_position,
            vertical_position
        ])


class FList(FViewGroupFixedStyle):
    @property
    def w_class(self):
        return 'ListView.builder'


class FGrid(FViewGroupFixedStyle):
    @property
    def w_class(self):
        return 'GridView.builder'

    def generate_alignments(self) -> list[str]:
        ratio = ''
        child_size = self.presented_child_size
        if child_size:
            ratio = f'childAspectRatio: {child_size[0]} / {child_size[1]},'
        return [
            'gridDelegate: SliverGridDelegateWithFixedCrossAxisCount('
            'crossAxisCount: 2,'
            'mainAxisSpacing: 8.w,'
            'crossAxisSpacing: 8.w,'
            f'{ratio}'
            ')'
        ]
