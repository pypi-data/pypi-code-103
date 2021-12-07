from collections import OrderedDict

from kntgen.model.figma_models import *
from kntgen.str_helpers import *


class FWidgetType(str, Enum):
    PAGE = 'page'
    BACKGROUND = 'bg'
    CONTAINER = 'container'
    SIZED_BOX = 'sb'
    ICON = 'ic'
    TEXT = 'tv'
    TEXT_FIELD = 'tf'
    IMAGE = 'img'
    BUTTON = 'btn'
    SWITCHER = 'sw'
    CHECK_BOX = 'cb'
    COLUMN = 'column'
    ROW = 'row'
    WRAP = 'wrap'
    WRAP_VERTICAL = 'wrapv'
    STACK = 'stack'
    LIST_VIEW = 'lv'
    LIST_VIEW_HORIZONTAL = 'lvh'
    GRID_VIEW = 'gv'
    GRID_VIEW_HORIZONTAL = 'gvh'
    NEW_WIDGET = 'f'
    # Add built-in knt_ui
    TAB_PAGE = 'tpage'
    APP_BAR = 'ab'
    TOOL_BAR = 'tb'
    BOTTOM_BAR = 'bb'
    GALLERY = 'gallery'
    CALENDAR = 'calendar'
    DIVIDER = 'div'
    WEB = 'web'
    CHART = 'chart'
    IGNORED = 'ignored'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    def is_view_group(self):
        return self.is_flex_view_group() or self.is_consistent_view_group()

    def is_flex_view_group(self):
        """
        Flutter View Types which Flutter View is a view group with dynamic child
        style and size

        :return: Whether this type is a flex view group type or not
        """
        return self in [
            FWidgetType.COLUMN,
            FWidgetType.ROW,
            FWidgetType.WRAP,
            FWidgetType.STACK
        ]

    def is_consistent_view_group(self):
        """
        Flutter View Types which Flutter View is a view group with every child has
        the same structure

        :return: Whether this type is a consistent view group type or not
        """
        return self in [
            FWidgetType.LIST_VIEW,
            FWidgetType.LIST_VIEW_HORIZONTAL,
            FWidgetType.GRID_VIEW,
            FWidgetType.GRID_VIEW_HORIZONTAL
        ]


class Alignment(str, Enum):
    START = 'start'
    CENTER = 'center'
    END = 'end'
    SPACE_BETWEEN = 'spaceBetween'


class Direction(str, Enum):
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'


class Edge(str, Enum):
    LEFT = 'left'
    TOP = 'top'
    RIGHT = 'right'
    BOTTOM = 'bottom'

    @staticmethod
    def values():
        return [Edge.LEFT, Edge.TOP, Edge.RIGHT, Edge.BOTTOM]


class InsetType(str, Enum):
    PADDING = 'padding'
    MARGIN = 'margin'


class Gradient(str, Enum):
    LINEAR = 'GRADIENT_LINEAR'
    RADIAL = 'GRADIENT_RADIAL'
    SWEEP = 'GRADIENT_ANGULAR'

    def f_class_name(self):
        return {
            Gradient.RADIAL: 'RadialGradient',
            Gradient.SWEEP: 'SweepGradient'
        }.get(self, 'LinearGradient')

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @staticmethod
    def convert_coordinate_figma_to_flutter(coordinate: dict):
        if not coordinate or 'x' not in coordinate or 'y' not in coordinate:
            return 0.0, 0.0
        x = coordinate['x']
        y = coordinate['y']
        return round((x - 0.5) * 2, 2), round((y - 0.5) * 2, 2)


class FWidgetExtractor:
    REGEX_F_WIDGET = r'((?P<type>[A-Za-z0-9]+)_?)(?P<name>[A-Za-z0-9-_]+)?'
    FW_CLICKABLE = 'click_'
    FW_DYNAMIC_DATA = 'obj_'
    FW_CUSTOM_ITEM = 'item_'
    FW_CUSTOM_WIDGET = f'{FWidgetType.NEW_WIDGET.value}_'
    DEFAULT_COLORS = 'Colors.black'

    @staticmethod
    def figma_to_raw_flutter(current_node: dict):
        if 'name' not in current_node:
            return None
        # Defined view information
        *redundant, w_type = FWidgetExtractor.regex_info(current_node)
        widget = FRawWidget(figma_node=current_node)
        widget.type = w_type
        return widget

    @staticmethod
    def regex_info(current_node: dict):
        return FWidgetExtractor.regex_info_from_name(
            current_node['name'] if 'name' in current_node else '')

    @staticmethod
    def regex_info_from_name(v_name: str):
        w_full_name = v_name or ''
        w_name = ''
        w_type = FWidgetType.IGNORED
        w_full_name_for_matcher = w_full_name \
            .replace(FWidgetExtractor.FW_CLICKABLE, '') \
            .replace(FWidgetExtractor.FW_DYNAMIC_DATA, '')
        # In case this node is defined as a new widget
        if w_full_name_for_matcher.startswith(
                FWidgetExtractor.FW_CUSTOM_WIDGET):
            w_full_name_for_matcher = w_full_name_for_matcher.replace(
                FWidgetExtractor.FW_CUSTOM_WIDGET, '')
            w_type = FWidgetType.NEW_WIDGET
            w_name = w_full_name_for_matcher
            w_full_name = w_full_name_for_matcher
        # Continue to find info from regex
        match_view_info = re.search(
            FWidgetExtractor.REGEX_F_WIDGET,
            w_full_name_for_matcher
        )
        if match_view_info:
            match_type = match_view_info.group('type')
            match_name = match_view_info.group('name')
            converted_type = FWidgetType(match_type) \
                if FWidgetType.has_value(match_type) \
                else FWidgetType.IGNORED
            if converted_type != FWidgetType.IGNORED:
                w_type = converted_type
            if match_name:
                w_name = match_name.replace(FWidgetExtractor.FW_CUSTOM_ITEM, '') \
                    if match_name.startswith(FWidgetExtractor.FW_CUSTOM_ITEM) \
                    else match_name
        return w_full_name, w_name, w_type

    @staticmethod
    def name_without_type(v_name: str):
        _, text_without_type, _ = FWidgetExtractor.regex_info_from_name(v_name)
        return text_without_type

    @staticmethod
    def localized_key_from_name(v_name: str):
        """
        Convert Figma's node name into locale keys

        :param v_name: Name of a Figma node
        :return: A tuple contains (prefix such as page/item/custom, literal locale keys)
        """
        if not v_name:
            return '', ''
        name_without_type = FWidgetExtractor.name_without_type(v_name)
        prefix = ''
        if v_name.startswith(FWidgetExtractor.FW_CUSTOM_WIDGET):
            prefix = 'custom'
            v_name_remove_customized = v_name.replace(
                FWidgetExtractor.FW_CUSTOM_WIDGET, '')
            if v_name_remove_customized.startswith(f'{FWidgetType.PAGE}_'):
                prefix = 'page'
            if v_name_remove_customized.startswith(
                    FWidgetExtractor.FW_CUSTOM_ITEM):
                prefix = 'item'
        return prefix, name_without_type

    @staticmethod
    def text_related(current_node: dict):
        if not current_node:
            return None
        if not FWidgetExtractor.is_node_as_text_view(current_node):
            return None
        if 'type' not in current_node or current_node['type'] != 'TEXT':
            return None
        text_in_node = current_node[
            'characters'] if 'characters' in current_node else ''
        if not FWidgetExtractor.valid_content_in_text_node(text_in_node):
            return None
        # Flutter just supports only 1 text color with possible alpha mode
        hex_text_color = ''
        alpha_text_color = 255
        if 'fills' in current_node:
            if len(current_node['fills']) > 0:
                hex_text_color, alpha_text_color = FWidgetExtractor.get_hex_in_color_node(
                    current_node['fills'][0])
        return FTextRelated(
            character=text_in_node,
            character_style_override=current_node[
                'characterStyleOverrides'] if 'characterStyleOverrides'
                                              in current_node else [],
            hex_text_color=hex_text_color,
            alpha_text_color=alpha_text_color,
            style=TextStyle(**current_node[
                'style']) if 'style' in current_node else None,
            style_override_table=current_node[
                'styleOverrideTable'] if 'styleOverrideTable'
                                         in current_node else []
        )

    @staticmethod
    def color_related(current_node: dict) -> list[str]:
        def extract_color(component_color_node):
            hex_c_list = []
            for component in component_color_node:
                hex_c, _ = FWidgetExtractor.get_hex_in_color_node(component)
                if hex_c:
                    hex_c_list.append(hex_c)
                    continue
                # Dry-run to get gradient colors
                gradient_hex_c_list = FWidgetExtractor.gradient_color_related(
                    component)
                hex_c_list.extend([c[0] for c in gradient_hex_c_list if c])
            return hex_c_list

        hex_colors = []
        if 'fills' in current_node:
            hex_colors.extend(extract_color(current_node['fills']))
        if 'strokes' in current_node:
            hex_colors.extend(extract_color(current_node['strokes']))
        if 'effects' in current_node:
            hex_colors.extend(extract_color(current_node['effects']))
        return hex_colors

    @staticmethod
    def gradient_color_related(current_node: dict) -> list[tuple]:
        """
        Extract colors/alpha/stop positions/vector from gradient object

        :param current_node: Node contains gradient information
        :return: A tuple of (colors, alpha, stop positions, vector)
        """
        hex_c_list_with_position = []
        if 'type' in current_node \
                and current_node['type'].startswith('GRADIENT'):
            if 'gradientStops' in current_node \
                    and current_node['gradientStops']:
                # Get list vector presents gradient
                position_vector = current_node.get('gradientHandlePositions',
                                                   [])
                for gradient_color_node in current_node['gradientStops']:
                    hex_c, alpha_c = FWidgetExtractor.get_hex_in_color_node(
                        gradient_color_node)
                    position = gradient_color_node[
                        'position'] if 'position' in gradient_color_node else 0
                    if hex_c:
                        hex_c_list_with_position.append(
                            (hex_c, alpha_c, position, position_vector))
        return hex_c_list_with_position

    @staticmethod
    def get_hex_in_color_node(component):
        if 'color' in component and Color.valid_color_properties(
                component['color']):
            dict_c = component['color']
            alpha_c = math.floor(dict_c.get('a', 1) * 255)
            tuple_c = (
                math.floor(dict_c['r'] * 255),
                math.floor(dict_c['g'] * 255),
                math.floor(dict_c['b'] * 255)
            )
            hex_c = Color.rbg_to_hex(*tuple_c)
            if 'opacity' in component:
                alpha_c = math.floor(component.get('opacity', 1) * 255)
            return hex_c, alpha_c
        return '', 255

    @staticmethod
    def present_f_color(component,
                        colors_mapping: dict,
                        property_name: str = None):
        hex_color, alpha = FWidgetExtractor.get_hex_in_color_node(component)
        return FWidgetExtractor.present_f_color_from_scratch(
            hex_color=hex_color,
            alpha=alpha,
            colors_mapping=colors_mapping,
            property_name=property_name
        )

    @staticmethod
    def present_f_color_from_scratch(hex_color,
                                     alpha,
                                     colors_mapping: dict,
                                     property_name: str = None,
                                     need_prefix=True):
        named_color = FWidgetExtractor.hex_to_named_color(hex_color,
                                                          colors_mapping)
        property_present = property_name or 'color'
        prefix = f'{property_present}:' if need_prefix else ''
        return f'{prefix}{named_color}' \
               f'{FWidgetExtractor.present_f_color_alpha(alpha)}' \
            if named_color else ''

    @staticmethod
    def present_f_color_alpha(alpha):
        return f'.withAlpha({alpha})' if alpha is not None and alpha < 255 else ''

    @staticmethod
    def hex_to_named_color(hex_color: str, colors_mapping: dict):
        if not hex_color:
            return hex_color
        if hex_color in colors_mapping:
            hex_color = colors_mapping[hex_color] \
                        or FWidgetExtractor.DEFAULT_COLORS
        return hex_color

    @staticmethod
    def valid_content_in_text_node(content: str):
        if len(content) < 2:
            # Too short
            return False
        if is_number(content):
            # Number is meaningless when extract to mobile app strings
            return False
        if is_time_format(content):
            # Time format is meaningless
            return False
        return True

    @staticmethod
    def as_rect(figma_node):
        if 'absoluteBoundingBox' in figma_node:
            return RectLTRB(**figma_node['absoluteBoundingBox'])
        return RectLTRB(0, 0, 0, 0)

    @staticmethod
    def is_node_as_custom_widget(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return v_name.startswith(FWidgetExtractor.FW_CUSTOM_WIDGET)

    @staticmethod
    def is_node_as_page(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return v_name.startswith(
            f'{FWidgetExtractor.FW_CUSTOM_WIDGET}{FWidgetType.PAGE.value}') \
               or v_name.startswith(FWidgetType.PAGE.value)

    @staticmethod
    def is_node_as_tab_page(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return v_name.startswith(
            f'{FWidgetExtractor.FW_CUSTOM_WIDGET}{FWidgetType.TAB_PAGE.value}') \
               or v_name.startswith(FWidgetType.TAB_PAGE.value)

    @staticmethod
    def is_background(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return v_name.startswith(
            f'{FWidgetExtractor.FW_CUSTOM_WIDGET}{FWidgetType.BACKGROUND.value}') \
               or v_name.startswith(FWidgetType.BACKGROUND.value)

    @staticmethod
    def is_node_as_image(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return f'{FWidgetType.IMAGE.value}_' in v_name \
               or f'{FWidgetType.ICON.value}_' in v_name

    @staticmethod
    def is_node_as_text_view(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return f'{FWidgetType.TEXT.value}_' in v_name \
               or f'{FWidgetType.TEXT_FIELD.value}_' in v_name \
               or v_name == FWidgetType.TEXT.value \
               or v_name == FWidgetType.TEXT_FIELD.value

    @staticmethod
    def is_node_need_dynamic_data(figma_node):
        v_name = figma_node['name'] if 'name' in figma_node else ''
        return FWidgetExtractor.FW_DYNAMIC_DATA in v_name

    @staticmethod
    def find_all_custom_widget_node(current_node, page_nodes):
        if FWidgetExtractor.is_node_as_custom_widget(current_node):
            page_nodes.append(current_node)
        if 'children' in current_node:
            for c_view in current_node['children']:
                FWidgetExtractor.find_all_custom_widget_node(c_view, page_nodes)

    @staticmethod
    def get_resource(current_node: dict,
                     text_dict: OrderedDict[
                                str: [OrderedDict[str:tuple[str, str]]]] = None,
                     text_in_page_dict: OrderedDict[str:tuple[str, str]] = None,
                     hex_color_list: list[str] = None,
                     image_node_dict: dict[str: dict] = None,
                     font_node_list: list[TextStyle] = None):
        """
        :param current_node: Figma node dictionary which we use to look up Flutter resource
        :param text_dict: Keeps all Flutter page strings
        :param text_in_page_dict: Keeps value of list text inside each Flutter page. Will be reset when jump to next page
        :param hex_color_list: Keeps HEX format color of [current_node]
        :param image_node_dict: Keeps images that presented as a [current_node]
        :param font_node_list: Keeps all font styles of [current_node]
        :return:
        """
        if not current_node:
            return

        node_id = current_node['id'] if 'id' in current_node else ''
        node_name = current_node['name'] if 'name' in current_node else ''
        # Find nodes that presented as a Flutter page
        if text_dict is not None:
            if FWidgetExtractor.is_node_as_custom_widget(current_node):
                text_in_page_dict = OrderedDict()
                text_dict[node_name] = text_in_page_dict

        # Find strings and also fonts
        text_related = FWidgetExtractor.text_related(current_node)
        if text_related:
            if text_in_page_dict is not None and not \
                    FWidgetExtractor.is_node_need_dynamic_data(current_node):
                text_in_page_dict[node_id] = node_name, text_related.character
            if font_node_list is not None:
                font_node_list.append(text_related.style)
            if hex_color_list is not None \
                    and text_related.hex_text_color is not None \
                    and text_related.hex_text_color not in hex_color_list:
                hex_color_list.append(text_related.hex_text_color)

        # Find hex colors
        if hex_color_list is not None:
            related_c_hex_list = FWidgetExtractor.color_related(current_node)
            hex_color_list.extend(
                [c for c in related_c_hex_list if
                 c and c not in hex_color_list])

        # Find all nodes contain image
        if image_node_dict is not None:
            if FWidgetExtractor.is_node_as_image(current_node):
                image_node_dict[node_id] = current_node
            # Also lookup background with image
            if FWidgetExtractor.is_background(current_node):
                if len(node_name) > len(FWidgetType.BACKGROUND.value):
                    image_node_dict[node_id] = current_node

        # Recursive child views
        if 'children' in current_node:
            for child_node in current_node['children']:
                FWidgetExtractor.get_resource(
                    current_node=child_node,
                    text_dict=text_dict,
                    text_in_page_dict=text_in_page_dict,
                    hex_color_list=hex_color_list,
                    image_node_dict=image_node_dict,
                    font_node_list=font_node_list
                )


class FTextRelated:
    def __init__(self,
                 character: str,
                 character_style_override: list = None,
                 hex_text_color: str = None,
                 alpha_text_color: int = None,
                 style: TextStyle = None,
                 style_override_table: list = None):
        self.character = character or ''
        self.character_style_override = character_style_override or []
        self.hex_text_color = hex_text_color
        self.alpha_text_color = alpha_text_color or 255
        self.style = style
        self.style_override_table = style_override_table or []

    def present_f_color(self, colors_mapping: dict, property_name: str = None):
        return FWidgetExtractor.present_f_color_from_scratch(
            hex_color=self.hex_text_color,
            alpha=self.alpha_text_color,
            colors_mapping=colors_mapping,
            property_name=property_name
        )


class FRawWidget:
    SCREEN_DESIGN_WIDTH = 375.0
    SCREEN_DESIGN_HEIGHT = 812.0

    def __init__(self,
                 figma_node,
                 v_type: FWidgetType = None,
                 children: list = None):
        self.figma_node = figma_node
        self.type = v_type or FWidgetType.IGNORED
        self.children = children or []
        self.rect = FWidgetExtractor.as_rect(self.figma_node)

    def __eq__(self, other):
        return isinstance(other, __class__) \
               and other.id_view == self.id_view

    def __hash__(self):
        return id(self.id_view)

    @property
    def id_view(self):
        return self.figma_node['id'] if 'id' in self.figma_node else ''

    @property
    def raw_name(self):
        return self.figma_node['name'] if 'name' in self.figma_node else ''

    @property
    def full_name(self):
        if self.is_custom_widget:
            return self.raw_name.replace(FWidgetExtractor.FW_CUSTOM_WIDGET, '')
        return self.raw_name

    @property
    def is_custom_widget(self):
        return self.raw_name.startswith(FWidgetExtractor.FW_CUSTOM_WIDGET)

    @property
    def present(self):
        v_type = f'[{self.type.name}]'
        v_id = f'[{self.id_view}]'
        return f'{v_type}{v_id} {self.full_name}'

    def optimize_view_type(self):
        if self.type == FWidgetType.STACK:
            # Firstly, remove mask node if this stack has, also collect size/radius from mask
            mask_node = None
            for child in self.children:
                if child.figma_node.get('isMask', False) is True:
                    mask_node = child
                    break
            if mask_node:
                self.rect = FWidgetExtractor.as_rect(mask_node.figma_node)
                self.children.remove(mask_node)
            # Check if this STACK has first child showing as its BACKGROUND
            if not self.children:
                return
            first_child = self.children[0]
            if first_child.type != FWidgetType.BACKGROUND \
                    or not first_child.rect.is_background_of(self.rect):
                return
            remain_children = self.children[1:]
            if len(remain_children) < 2:
                self.children = remain_children
            else:
                # Create new stack to contains remaining children
                # and make current stack contains that ones as an only child
                new_stack = FRawWidget(
                    figma_node=self.figma_node,
                    v_type=FWidgetType.STACK,
                    children=remain_children
                )
                self.children = [new_stack]
            # Then we convert this stack to container immediately
            self.figma_node = first_child.figma_node
            self.type = FWidgetType.CONTAINER
            self.rect = FWidgetExtractor.as_rect(self.figma_node)
