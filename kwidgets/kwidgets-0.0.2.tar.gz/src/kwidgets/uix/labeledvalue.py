""" Labeled Value

This provides a key/value display with a text label
and a value that can be formatted using a provided
formatting string.
"""

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ListProperty

Builder.load_string("""
<LabeledValue>:
    canvas:
        Color:
            rgba: root.box_color
        Line:
            width: root.line_width
            rectangle: self.x+root.box_padding, self.y+root.box_padding, self.width-(2*root.box_padding), self.height-(2*root.box_padding)
    Label:
        text_size: self.width-root.text_padding*2, self.height-root.text_padding*2
        size_hint_x: root.key_size_hint_x  
        halign: root.key_halign
        valign: root.valign
        text: root.key
    Label:
        text_size: self.width-root.text_padding*2, self.height-root.text_padding*2
        size_hint_x: 1.0-root.key_size_hint_x
        halign: root.value_halign
        valign: root.valign
        text: root._value
""")

class LabeledValue(BoxLayout):
    """ A combination of a key and a value to display.

    Relevant attributes are:

    * key - the key
    * value - the value
    * text_padding - number of pixels of padding around
      the label.
    * box_padding - Number of pixels of padding around the
      border
    * line_width - The width of the border
    * box_color - Color of the box
    * valign - How to vertically align the text
    * key_halign - How to horizontally align the key
    * value_halign - How to horizontally align the value
    * format - a format string for the value

    """
    text_padding = NumericProperty(10)
    box_padding = NumericProperty(5)
    box_color = ListProperty([1,1,1,0])
    line_width = NumericProperty(1)
    valign = StringProperty("center")

    key_halign = StringProperty("left")
    key_size_hint_x = NumericProperty(0.5)
    key = StringProperty("A Key")

    value_halign = StringProperty("right")
    format = StringProperty("%s")
    _value = StringProperty("A Value")
    _original_value = None


    @property
    def value(self):
        """ The value to display.

        :return:
        """
        return self._original_value

    @value.setter
    def value(self, value):
        """ The value to display

        :param value:
        """
        self._original_value=value
        self._value = self.format % value


class LabeledValueApp(App):

    def build(self):
        return Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    LabeledValue:
        key: 'first key'
        value: 'first value'
    LabeledValue:
        key: 'A Number'
        format: '%10.4f'
        value: 1.2345678910
        box_color: 0,1,0,1
        box_width: 2
        value_halign: 'left'
        key_size_hint_x: 0.25
    LabeledValue:
        key: 'Another Number'
        format: '%10.2f'
        value: 46.78912
        box_padding: 20
        text_padding: 30
        box_color: 1,0,0,.8
        ''')

if __name__ == "__main__":
    LabeledValueApp().run()