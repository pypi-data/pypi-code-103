from kntgen.file_helpers import *
from kntgen.model.flutter.flutter_raw_widget import *


class FWidget:
    MIN_OFFSET_PX = 4
    ALIGNMENT_OFFSET_RATIO = 0.14
    POSITIONED_STACK_OFFSET_RATIO = 0.16

    def __init__(self,
                 figma_node,
                 parent=None,
                 children: list = None):
        self.figma_node = figma_node
        self.parent = parent
        self.children = children or []
        # Extract info from node
        w_full_name, w_name, _ = FWidgetExtractor.regex_info(figma_node)
        self.w_raw_name = to_snake_case(
            w_full_name.replace(FWidgetExtractor.FW_CLICKABLE, '').replace(
                FWidgetExtractor.FW_DYNAMIC_DATA, '')
        )
        self.w_name = to_snake_case(w_name)
        self.need_data_object = FWidgetExtractor.FW_DYNAMIC_DATA in w_full_name
        self.clickable = FWidgetExtractor.FW_CLICKABLE in w_full_name
        self.rect = FWidgetExtractor.as_rect(self.figma_node)

    @property
    def w_id(self):
        return self.figma_node['id'] if 'id' in self.figma_node else ''

    @property
    def w_class(self):
        return 'SizedBox'

    @property
    def w_size(self):
        width = math.ceil(self.rect.width)
        height = math.ceil(self.rect.height)
        return width, height

    @property
    def w_size_present(self):
        width, height = self.w_size
        width_present = f'{width}.w'
        height_present = f'{height}.w'
        if FRawWidget.SCREEN_DESIGN_WIDTH - 5 < width:
            width_present = '1.sw'
        if FRawWidget.SCREEN_DESIGN_HEIGHT - 5 < height:
            height_present = '1.sh'
        return f'width: {width_present}', f'height: {height_present}'

    @property
    def w_on_tap_action_name(self):
        present_action = self.w_name if self.w_name else self.w_raw_name
        return f'_onTapped{to_pascal_case(present_action)}'

    @property
    def is_flex_size(self):
        """
        Whether this widget has flex size such as Text, List View... or not.
        This property will be used when we consider to wrap Expanded & Flexible in Column/Row's children

        :return:
        """
        return False

    @property
    def margin(self):
        """
        Calculate relative margin created between this widget and it's parent.
        In case widget's parent is Stack, then margin could be considered as a Positioned widget.

        :return: A ordered dictionary contains (left, top, right, bottom)
        """
        if not self.parent:
            return OrderedDict({
                Edge.LEFT: 0,
                Edge.TOP: 0,
                Edge.RIGHT: 0,
                Edge.BOTTOM: 0
            })
        parent_rect = self.parent.rect
        left_differ = max(0, math.ceil(self.rect.left - parent_rect.left))
        top_differ = max(0, math.ceil(self.rect.top - parent_rect.top))
        right_differ = max(0, math.ceil(parent_rect.right - self.rect.right))
        bottom_differ = max(0, math.ceil(parent_rect.bottom - self.rect.bottom))
        return OrderedDict({
            Edge.LEFT: left_differ,
            Edge.TOP: top_differ,
            Edge.RIGHT: right_differ,
            Edge.BOTTOM: bottom_differ
        })

    @property
    def padding(self):
        """
        Calculate distance from this widget to its children.

        :return: A ordered dictionary contains (left, top, right, bottom)
        """
        if not self.children:
            return OrderedDict({
                Edge.LEFT: 0,
                Edge.TOP: 0,
                Edge.RIGHT: 0,
                Edge.BOTTOM: 0
            })
        left_most = top_most = right_most = bottom_most = 0
        for c in self.children:
            rect = c.rect
            left_most = min(left_most, rect.left)
            top_most = min(top_most, rect.top)
            right_most = max(right_most, rect.right)
            bottom_most = max(bottom_most, rect.bottom)
        left_differ = max(0, math.ceil(left_most - self.rect.left))
        top_differ = max(0, math.ceil(top_most - self.rect.top))
        right_differ = max(0, math.ceil(self.rect.right - right_most))
        bottom_differ = max(0, math.ceil(self.rect.bottom - bottom_most))
        return OrderedDict({
            Edge.LEFT: left_differ,
            Edge.TOP: top_differ,
            Edge.RIGHT: right_differ,
            Edge.BOTTOM: bottom_differ
        })

    def generate(self,
                 strings_mapping: dict,
                 colors_mapping: dict,
                 images_mapping: dict):
        properties = ''.join([f'{p},' for p in
                              self.generate_properties(strings_mapping,
                                                       colors_mapping,
                                                       images_mapping) if p])
        properties_present = '' if not properties else f'\n{properties}'
        widget = f'{self.w_class}({properties_present})'
        # Check clickable
        if self.clickable:
            widget = f"""
RippleOverlay(
    onTap: {self.w_on_tap_action_name},
    child: {widget},
)
"""
        return self.generate_wrapper(widget)

    def generate_wrapper(self, generated_content):
        if not isinstance(self.parent, FViewGroup):
            return generated_content
        present_padding = FWidget.extract_edge_insets(
            self.margin,
            specific_edges=self.parent.needed_child_edge_insets
        )
        return f'Padding({present_padding},child:{generated_content},)' \
            if present_padding else generated_content

    def generate_child(self,
                       strings_mapping: dict,
                       colors_mapping: dict,
                       images_mapping: dict):
        if not self.children:
            return None
        total_child = len(self.children)
        prefix_children = 'child:' if total_child == 1 else 'children:['
        child_content = []
        for c in self.children:
            if not c:
                continue
            content = c.generate(
                strings_mapping=strings_mapping,
                colors_mapping=colors_mapping,
                images_mapping=images_mapping
            ) if not isinstance(c, FCustom) else c.instance_generate()
            content = self.generate_child_wrapper(c, content)
            if content:
                child_content.append(content)
        generate_children = ','.join(child_content)
        postfix_children = '' if total_child == 1 else ',]'
        return f'{prefix_children}{generate_children}{postfix_children}'

    def generate_child_wrapper(self, child_widget, generated_child_content):
        return generated_child_content

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        return [
            self.generate_child(strings_mapping=strings_mapping,
                                colors_mapping=colors_mapping,
                                images_mapping=images_mapping)
        ]

    @staticmethod
    def extract_dependencies_import(widget, imports: list):
        if imports is None:
            return
        for child in widget.children:
            if isinstance(child, FCustom):
                imports.append(child)
                continue
            FWidget.extract_dependencies_import(child, imports)

    @staticmethod
    def extract_interactive_functions(widget, functions: list):
        if functions is None:
            return
        if widget.clickable:
            functions.append(f'void {widget.w_on_tap_action_name}() {{}}')
        for child in widget.children:
            if isinstance(child, FCustom):
                continue
            FWidget.extract_interactive_functions(child, functions)

    @staticmethod
    def extract_edge_insets(edge_insets: OrderedDict,
                            specific_edges: list[Edge] = None,
                            inset_type: InsetType = InsetType.PADDING):
        """
        Present EdgeInsets

        :param edge_insets: A ordered dictionary contains insets at (left, top, right, bottom)
        :param specific_edges: Focus on which edge insets
        :param inset_type: Either EdgeInsets for padding or margin. Default is padding
        :return:
        """
        if not edge_insets or not specific_edges or len(edge_insets) < 4:
            return ''
        prefix = (inset_type or InsetType.PADDING).value
        named_constructor = 'only'
        edge_insets_present = ''
        # Fetch all edges that has an inset (> 0)
        edges = {e: edge_insets[e] for e in specific_edges if
                 edge_insets[e] > 0}
        vertical_symmetric = ''
        horizontal_symmetric = ''
        if Edge.TOP in edges and Edge.BOTTOM in edges:
            vertical_symmetric = f'vertical: {edges[Edge.TOP]}.w' \
                if edges[Edge.TOP] == edges[Edge.BOTTOM] else ''
        if Edge.LEFT in edges and Edge.RIGHT in edges:
            horizontal_symmetric = f'horizontal: {edges[Edge.LEFT]}.w' \
                if edges[Edge.LEFT] == edges[Edge.RIGHT] else ''

        # Consider appropriated EdgeInsets
        def _basic_present():
            return ''.join(
                [f'{e.value}:{v}.w,' for e, v in edges.items()])

        total_edges = len(edges)
        if total_edges == 1 or total_edges == 3:
            named_constructor = 'only'
            edge_insets_present = _basic_present()
        if total_edges == 2:
            if vertical_symmetric:
                named_constructor = 'symmetric'
                edge_insets_present = vertical_symmetric
            elif horizontal_symmetric:
                named_constructor = 'symmetric'
                edge_insets_present = horizontal_symmetric
            else:
                named_constructor = 'only'
                edge_insets_present = _basic_present()
        if total_edges == 4:
            if vertical_symmetric and horizontal_symmetric:
                named_constructor = 'symmetric'
                edge_insets_present = f'{vertical_symmetric},{horizontal_symmetric},'
            else:
                named_constructor = 'fromLTRB'
                edge_insets_present = ','.join(
                    [f'{v}.w' for v in edges.values()])
        return f'{prefix}:EdgeInsets.{named_constructor}({edge_insets_present})' \
            if edge_insets_present else ''

    @staticmethod
    def extract_image_path(node_id, images_mapping: dict):
        w_id_without_extension = (node_id or '').replace('+', '')
        if w_id_without_extension not in images_mapping:
            return None
        return images_mapping[w_id_without_extension].path

    @staticmethod
    def extract_colors(figma_node, colors_mapping: dict):
        if not figma_node:
            return None
        if 'fills' in figma_node and figma_node['fills']:
            first_bg = figma_node['fills'][0]
            if 'type' not in first_bg or not first_bg['type']:
                return None
            bg_type = first_bg['type']
            if bg_type == 'SOLID':
                return FWidgetExtractor.present_f_color(first_bg,
                                                        colors_mapping)
            if bg_type.startswith('GRADIENT'):
                # Guaranteed that each element in the below list is not empty
                gradient_hex_c_list = FWidgetExtractor.gradient_color_related(
                    first_bg)
                if not gradient_hex_c_list:
                    return None
                gradient_type = Gradient(bg_type) \
                    if Gradient.has_value(bg_type) \
                    else Gradient.LINEAR
                position_vector = [
                    Gradient.convert_coordinate_figma_to_flutter(coordinate) for
                    coordinate in gradient_hex_c_list[0][3]]
                first_pos_vector = f'{position_vector[0][0]}, {position_vector[0][1]}'
                second_pos_vector = f'{position_vector[1][0]}, {position_vector[1][1]}'
                gradient_width_vector = f'{math.fabs(position_vector[2][0])}'
                # Fetch named colors from mapping dict
                named_c_list = [FWidgetExtractor.present_f_color_from_scratch(
                    hex_color=hex_c[0],
                    alpha=hex_c[1],
                    colors_mapping=colors_mapping,
                    need_prefix=False
                ) for hex_c in gradient_hex_c_list]
                colors_present = ''.join(
                    [f'{named_c},' for named_c in named_c_list if named_c])
                stops = [f'{hex_c[2]:.2f}' for hex_c in gradient_hex_c_list]
                stops_present = ''.join(f'{s},\n' for s in stops)
                if gradient_type == Gradient.RADIAL:
                    position_vector_present = f'center: Alignment({first_pos_vector}),' \
                                              f'radius: {gradient_width_vector},'
                elif gradient_type == Gradient.SWEEP:
                    # TODO: Calculate [startAngle] & [endAngle] by device first_pos/second_pos
                    position_vector_present = f'center: Alignment({first_pos_vector}),' \
                                              'startAngle: 0.0,' \
                                              'endAngle: 360.0,'
                else:
                    position_vector_present = f'begin: Alignment({first_pos_vector}),' \
                                              f'end: Alignment({second_pos_vector}),'
                return f'gradient: {gradient_type.f_class_name()}(' \
                       f'{position_vector_present}' \
                       f'colors:[{colors_present}], ' \
                       f'stops:[{stops_present}],)'
        return None

    @staticmethod
    def extract_border(figma_node, colors_mapping: dict):
        if not figma_node:
            return None
        if 'strokes' not in figma_node:
            return None
        strokes = figma_node['strokes']
        if not strokes:
            return None
        stroke_weight = math.ceil(figma_node['strokeWeight']) \
            if 'strokeWeight' in figma_node else 1
        stroke_weight_present = '' if stroke_weight <= 1 else f'width: {stroke_weight}.w'
        solid_color_present = FWidgetExtractor.present_f_color(strokes[0],
                                                               colors_mapping)
        if not solid_color_present:
            # Determine if stroke color in gradient mode
            gradient_colors = FWidgetExtractor.gradient_color_related(
                strokes[0])
            if gradient_colors:
                # Just get the first color, we are currently not supporting gradient border
                first_stroke_color = FWidgetExtractor.hex_to_named_color(
                    hex_color=gradient_colors[0][0],
                    colors_mapping=colors_mapping
                )
                alpha_present = FWidgetExtractor.present_f_color_alpha(
                    gradient_colors[0][1])
                solid_color_present = f'color: {first_stroke_color}{alpha_present}'
        return f"border: Border.all({''.join([f'{p},' for p in [solid_color_present, stroke_weight_present] if p])})"

    @staticmethod
    def extract_border_radius(figma_node):
        if not figma_node:
            return None
        top_left = top_right = bottom_left = bottom_right = 0
        if 'cornerRadius' in figma_node:
            radius = math.ceil(figma_node['cornerRadius'])
            top_left = radius
            top_right = radius
            bottom_left = radius
            bottom_right = radius
        if 'rectangleCornerRadii' in figma_node:
            radii = figma_node['rectangleCornerRadii']
            if len(radii) == 4:
                top_left = math.ceil(radii[0])
                top_right = math.ceil(radii[1])
                bottom_left = math.ceil(radii[3])
                bottom_right = math.ceil(radii[2])
        if top_left > 0 and top_left == top_right \
                and top_right == bottom_right \
                and bottom_right == bottom_left:
            return f'borderRadius: BorderRadius.circular({top_left}.w)'
        border_radius_present = [
            '' if top_left <= 0 else f'topLeft: Radius.circular({top_left}.w)',
            '' if top_right <= 0 else f'topRight: Radius.circular({top_right}.w)',
            '' if bottom_left <= 0 else f'bottomLeft: Radius.circular({bottom_left}.w)',
            '' if bottom_right <= 0 else f'bottomRight: Radius.circular({bottom_right}.w)']
        border_radius_present_only = [r for r in border_radius_present if r]
        if not border_radius_present_only:
            return ''
        return f"borderRadius: BorderRadius.only({''.join([f'{r},' for r in border_radius_present_only])})"

    @staticmethod
    def extract_shadows(figma_node, colors_mapping: dict):
        if not figma_node:
            return None
        if 'effects' not in figma_node:
            return None
        if not figma_node['effects']:
            return None
        first_effect = figma_node['effects'][0]
        if 'type' not in first_effect or first_effect['type'] != 'DROP_SHADOW':
            return None
        if 'visible' not in first_effect or not first_effect['visible']:
            return None
        offset = first_effect['offset'] if 'offset' in first_effect else {}
        offset_x = math.ceil(offset['x']) if 'x' in offset else 0
        offset_y = math.ceil(offset['y']) if 'y' in offset else 0
        blur_radius = math.ceil(
            first_effect['radius']) if 'radius' in first_effect else 0
        # Present
        shadow_present = [FWidgetExtractor.present_f_color(first_effect,
                                                           colors_mapping),
                          '' if blur_radius <= 0 else f'blurRadius: {blur_radius}.w',
                          f'offset: Offset({offset_x}.w, {offset_y}.w)']
        return f"boxShadow: [BoxShadow({''.join([f'{s},' for s in shadow_present if s])}),]"


class FCustom(FWidget):
    def generate_build(self,
                       strings_mapping: dict,
                       colors_mapping: dict,
                       images_mapping: dict):
        first_view = self.children[0] if self.children else None
        return first_view.generate(
            strings_mapping=strings_mapping,
            colors_mapping=colors_mapping,
            images_mapping=images_mapping
        ) if first_view else 'const SizedBox()'

    def generate(self,
                 strings_mapping: dict,
                 colors_mapping: dict,
                 images_mapping: dict):
        imports = []
        functions = []
        FWidget.extract_dependencies_import(self, imports)
        FWidget.extract_interactive_functions(self, functions)
        imports_present = '\n'.join(
            [f'import {c.project_absolute_file_path()!r};' for c in imports
             if c])
        functions_present = '\n\n'.join(functions)
        return f"""
import 'package:flutter/material.dart';
import 'package:knt_ui/knt_ui.dart';
import '{self.package_name}/resources.dart';
{imports_present}

class {self.w_class} extends StatelessWidget {{
    const {self.w_class}({{Key? key}}) : super(key: key);
    
    {functions_present}
    
    @override
    Widget build(BuildContext context) {{
        return {self.generate_build(strings_mapping=strings_mapping,
                                    colors_mapping=colors_mapping,
                                    images_mapping=images_mapping)};
    }}
}}
"""

    def instance_generate(self):
        return f'const {self.w_class}()'

    def generated_file_name(self):
        return self.w_raw_name

    def generate_container_folder(self):
        if FWidgetExtractor.FW_CUSTOM_ITEM in self.w_raw_name:
            return 'items'
        return 'custom'

    def project_absolute_file_path(self):
        return f'{self.package_name}/ui/{self.generate_relative_file_path()}.dart'

    def generate_relative_file_path(self):
        return f'{self.generate_container_folder()}/{self.generated_file_name()}'

    @property
    def w_class(self):
        return to_pascal_case(self.w_raw_name)

    @property
    def package_name(self):
        project_package = get_flutter_project_package()
        return f'package:{project_package}'


class FViewGroup(FWidget):
    def generate_child(self,
                       strings_mapping: dict,
                       colors_mapping: dict,
                       images_mapping: dict):
        if not self.children:
            return None
        child_content = []
        total_child = len(self.children)
        for i in range(total_child):
            child = self.children[i]
            if not child:
                continue
            content = child.generate(
                strings_mapping=strings_mapping,
                colors_mapping=colors_mapping,
                images_mapping=images_mapping
            ) if not isinstance(child, FCustom) else child.instance_generate()
            content = self.generate_child_wrapper(child, content)
            if content:
                child_content.append(content)
            if self.main_alignment != Alignment.SPACE_BETWEEN and i < total_child - 1:
                if self.direction == Direction.VERTICAL:
                    distance_to_next_child = math.ceil(
                        self.children[i + 1].rect.top - child.rect.bottom
                    )
                    if distance_to_next_child > 0:
                        child_content.append(
                            f'SizedBox(height: {distance_to_next_child}.w)')
                if self.direction == Direction.HORIZONTAL:
                    distance_to_next_child = math.ceil(
                        self.children[i + 1].rect.left - child.rect.right
                    )
                    if distance_to_next_child > 0:
                        child_content.append(
                            f'SizedBox(width: {distance_to_next_child}.w)')
        generate_children = ','.join(child_content)
        return f'children: [{generate_children},]'

    def generate_child_wrapper(self, child_widget, generated_child_content):
        if not generated_child_content:
            return generated_child_content
        # If child widget is a view group fixed style, then we need provide size wrapper for it
        # By default, we use its presented child's size as parent size
        if not isinstance(child_widget, FViewGroupFixedStyle):
            return generated_child_content
        # If parent view group has only 1 child view group fixed style then we just wrap it with Expanded
        if self.total_view_group_fixed_style_child == 1:
            return f'Expanded(child:{generated_child_content},)'
        # Otherwise wrap by Flexible with flex proportion
        present_size = child_widget.presented_child_size
        if not present_size:
            return generated_child_content
        if self.direction == Direction.HORIZONTAL:
            # Provide height when parent view group is a row
            flex_proportion = f'{present_size[0]} / {self.w_size[0]}'
        else:
            # Provide width when parent view group is a column
            flex_proportion = f'{present_size[1]} / {self.w_size[1]}'
        return f'Flexible(flex: {flex_proportion},' \
               f'child:{generated_child_content},)'

    def generate_properties(self,
                            strings_mapping: dict,
                            colors_mapping: dict,
                            images_mapping: dict):
        properties = [self.generate_direction()]
        properties.extend(self.generate_alignments())
        properties.append(self.generate_child(
            strings_mapping=strings_mapping,
            colors_mapping=colors_mapping,
            images_mapping=images_mapping
        ))
        return properties

    def generate_alignments(self) -> list[str]:
        present_main_size = 'mainAxisSize: MainAxisSize.min' \
            if self.total_view_group_fixed_style_child > 0 else ''
        present_main_alignment = f'mainAxisAlignment: MainAxisAlignment' \
                                 f'.{self.main_alignment.value}'
        present_cross_alignment = f'crossAxisAlignment: CrossAxisAlignment' \
                                  f'.{self.cross_alignment.value}'
        if self.main_alignment == Alignment.START:
            present_main_alignment = ''
        if self.cross_alignment == Alignment.CENTER:
            present_cross_alignment = ''
        return [
            present_main_size,
            present_main_alignment,
            present_cross_alignment,
        ]

    def generate_direction(self) -> str:
        return f"direction: Axis.{'horizontal' if self.direction == Direction.HORIZONTAL else 'vertical'}"

    @property
    def direction(self):
        return Direction.VERTICAL

    @property
    def x_alignment(self):
        w_center_x = self.rect.center_x
        alignment_offset = self.rect.width * FWidget.ALIGNMENT_OFFSET_RATIO
        # View group aligns as a column
        if self.direction == Direction.VERTICAL:
            for c_rect in self.children_rect:
                center_x = c_rect.center_x
                if center_x < w_center_x - alignment_offset:
                    return Alignment.START
                if center_x > w_center_x + alignment_offset:
                    return Alignment.END
            # Last check: left edge and right edge of each child
            left_edges_count = 1
            right_edges_count = 1
            first_c_left = self.children_rect[0].left
            first_c_right = self.children_rect[0].right
            total_child = len(self.children_rect)
            for i in range(1, total_child):
                c_rect = self.children_rect[i]
                if first_c_left - FWidget.MIN_OFFSET_PX < c_rect.left \
                        < first_c_left + FWidget.MIN_OFFSET_PX:
                    left_edges_count += 1
                if first_c_right - FWidget.MIN_OFFSET_PX < c_rect.right \
                        < first_c_right + FWidget.MIN_OFFSET_PX:
                    right_edges_count += 1
            if left_edges_count == total_child:
                return Alignment.START
            if right_edges_count == total_child:
                return Alignment.END
            return Alignment.CENTER
        # Otherwise view group aligns as a row
        left_children_edge = self.children[0].rect.left
        right_children_edge = self.children[-1].rect.right
        if left_children_edge > self.rect.left + alignment_offset \
                and right_children_edge < self.rect.right - alignment_offset:
            return Alignment.CENTER
        if left_children_edge > self.rect.left + alignment_offset:
            return Alignment.END
        if right_children_edge < self.rect.right - alignment_offset:
            return Alignment.START
        if len(self.children) == 2:
            left_margin = self.children[1].rect.left - self.children[
                0].rect.right
            if left_margin >= alignment_offset:
                return Alignment.SPACE_BETWEEN
        return Alignment.START

    @property
    def y_alignment(self):
        w_center_y = self.rect.center_y
        alignment_offset = self.rect.height * FWidget.ALIGNMENT_OFFSET_RATIO
        # View group aligns as a row
        if self.direction == Direction.HORIZONTAL:
            for c_rect in self.children_rect:
                center_y = c_rect.center_y
                if center_y < w_center_y - alignment_offset:
                    return Alignment.START
                if center_y > w_center_y + alignment_offset:
                    return Alignment.END
            # Last check: top edge and bottom edge of each child
            top_edges_count = 1
            bottom_edges_count = 1
            first_c_top = self.children_rect[0].top
            first_c_bottom = self.children_rect[0].bottom
            total_child = len(self.children_rect)
            for i in range(1, len(self.children_rect)):
                c_rect = self.children_rect[i]
                if first_c_top - FWidget.MIN_OFFSET_PX < c_rect.top \
                        < first_c_top + FWidget.MIN_OFFSET_PX:
                    top_edges_count += 1
                if first_c_bottom - FWidget.MIN_OFFSET_PX < c_rect.bottom \
                        < first_c_bottom + FWidget.MIN_OFFSET_PX:
                    bottom_edges_count += 1
            if top_edges_count == total_child:
                return Alignment.START
            if bottom_edges_count == total_child:
                return Alignment.END
            return Alignment.CENTER
        # Otherwise view group aligns as a column
        top_children_edge = self.children[0].rect.top
        bottom_children_edge = self.children[-1].rect.bottom
        if top_children_edge > self.rect.top + alignment_offset \
                and bottom_children_edge < self.rect.bottom - alignment_offset:
            return Alignment.CENTER
        if top_children_edge > self.rect.top + alignment_offset:
            return Alignment.END
        if bottom_children_edge < self.rect.bottom - alignment_offset:
            return Alignment.START
        if len(self.children) == 2:
            top_margin = self.children[1].rect.top - self.children[
                0].rect.bottom
            if top_margin >= alignment_offset:
                return Alignment.SPACE_BETWEEN
        return Alignment.START

    @property
    def children_rect(self):
        return [c.rect for c in self.children if c]

    @property
    def main_alignment(self):
        return Alignment.START

    @property
    def cross_alignment(self):
        return Alignment.CENTER

    @property
    def needed_child_edge_insets(self):
        specific_edges = []
        if self.direction == Direction.VERTICAL:
            if self.cross_alignment == Alignment.START:
                specific_edges.append(Edge.LEFT)
            if self.cross_alignment == Alignment.END:
                specific_edges.append(Edge.RIGHT)
        if self.direction == Direction.HORIZONTAL:
            if self.cross_alignment == Alignment.START:
                specific_edges.append(Edge.TOP)
            if self.cross_alignment == Alignment.END:
                specific_edges.append(Edge.BOTTOM)
        return specific_edges

    @property
    def total_view_group_fixed_style_child(self):
        total = 0
        for child in self.children:
            if isinstance(child, FViewGroupFixedStyle):
                total += 1
        return total


class FViewGroupFixedStyle(FViewGroup):
    def __init__(self, figma_node, children: list = None, is_horizontal=False):
        super().__init__(figma_node, children)
        self.is_horizontal = is_horizontal

    def generate_properties(self, strings_mapping: dict, colors_mapping: dict,
                            images_mapping: dict):
        properties = super().generate_properties(strings_mapping,
                                                 colors_mapping,
                                                 images_mapping)
        properties.insert(0, self.generate_scroll_physic())
        return properties

    def generate_child(self,
                       strings_mapping: dict,
                       colors_mapping: dict,
                       images_mapping: dict):
        first_child = 'const SizedBox()'
        if self.children:
            child = self.children[0]
            if child:
                first_child = child.generate(
                    strings_mapping=strings_mapping,
                    colors_mapping=colors_mapping,
                    images_mapping=images_mapping
                ) if not isinstance(child,
                                    FCustom) else child.instance_generate()
                first_child = self.generate_child_wrapper(child, first_child)
        item_builder = f'itemBuilder: (context, index) => {first_child}'
        item_count = 'itemCount: 1'
        return ','.join([item_builder, item_count])

    def generate_direction(self) -> str:
        return 'scrollDirection: Axis.horizontal' \
            if self.direction == Direction.HORIZONTAL else None

    def generate_scroll_physic(self):
        return 'physics: const BouncingScrollPhysics()'

    def generate_alignments(self) -> list[str]:
        return []

    @property
    def direction(self):
        return Direction.HORIZONTAL if self.is_horizontal \
            else Direction.VERTICAL

    @property
    def presented_child(self):
        return self.children[0] if self.children else None

    @property
    def presented_child_size(self):
        return self.presented_child.w_size if self.presented_child else None
