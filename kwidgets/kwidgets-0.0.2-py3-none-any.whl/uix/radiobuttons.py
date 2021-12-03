""" Radio Buttons

This provides a set of radio buttons for Kivy with an easy way to
specify the options, a default value, and a callback for when the
options change.
"""
from typing import List, Callable, Any
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty


class RadioButtons(BoxLayout):
    """ The RadioButtons Class.  The key options for this object are:

    * options: a list of strings, one for each button
    * selected_value: a string property with the currently selected value
    * selected_color: an rgba list with the color for the selected button

    """
    _options = ListProperty([])
    _buttons = ListProperty([])
    _oldcolor = ListProperty([])
    _selected_color = ListProperty([1, 0, 0, 1])
    selected_value = StringProperty("")

    def _update_button_colors(self, source, value):
        """ Update the button colors to match the selection.

        :param source: unused
        :param value: The text for the button that is selected.
        """
        for b in self._buttons:
            b.background_normal = '' if b.text==value else self._oldcolor[0]
            b.background_color = self._selected_color if b.text==value else self._oldcolor[1]

    def button_pressed(self, x):
        """ Set the selected value according to the button pressed.

        :param x: The text from the button pressed
        """
        self.selected_value = x.text

    @property
    def selected_color(self):
        """ The color of the selected button.

        :return:
        """
        return self._selected_color

    @selected_color.setter
    def selected_color(self, color = List[float]):
        """ The rgba value for the button when it is pressed

        :param color:
        """
        self._selected_color = color
        self._update_button_colors(None, self.selected_value)

    @property
    def options(self):
        """ A list of strings, one for each radio button

        :return:
        """
        return self._options

    @options.setter
    def options(self, options: List[str]):
        """ A list of strings, one for each radio button.

        Note that this can only be called once per object.  Otherwise
        an exception will be thrown.  This method creates the buttons,
        populates the widget, and binds relevant methods.
        :rtype: object
        """
        if len(self._options) > 0:
            raise RuntimeError("Options can only be set once")
        else:
            self._options = options
            for option in options:
                b = Button(text=option)
                self._oldcolor = [b.background_normal, b.background_color]
                b.bind(on_press=self.button_pressed)
                self.add_widget(b)
                self._buttons.append(b)
            self.bind(selected_value=self._update_button_colors)
            # We have to do this in case the selected value was set before the options
            self._update_button_colors(None, self.selected_value)


def printit(source,value):
    print("source=%s, value=%s" % (str(source), value))


class RadioButtonsApp(App):

    def build(self):
        container = Builder.load_string('''
RadioButtons:
    orientation: 'vertical'
    selected_value: 'B'
    options: 'A', 'B', 'C'
    selected_color: .1, .5, .1, 1
''')
        container.bind(selected_value=printit)
        return container


if __name__ == "__main__":
    RadioButtonsApp().run()