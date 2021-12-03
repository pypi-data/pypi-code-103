""" A widget for displaying a rotating set of quotations.

Includes an application such that if this module is run directly with a path to a
text file containing one quotation per line, it will rotate through those quotations.
"""
from typing import List, Union
import sys
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random

Builder.load_string("""
<QuotationDisplay>:
    padding: 50
    canvas:
        Color: 
            rgb: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color: 
            rgba: 1, 1, 1, 1
        Line:
            width: 2.0
            rounded_rectangle: 10, 10, self.width-20, self.height-20, 10, 10, 10, 10
    Label:
        text: root.text
        text_size: self.width-20, self.height-20    
        valign: 'middle'
        halign: 'center'
        font_size: '20sp'
""")


class QuotationDisplay(BoxLayout):
    """ Widget that displays a rotating set of quotations.
    """
    text = StringProperty(defaultvalue="huh?")
    _update_sec = 10
    _quotations: List[str] = ["No quotations specified"]

    def __init__(self, quotations = Union[str, List[str]], **kwargs):
        """ Create a new QuotationDisplay widget

        :param quotations: Either a list of quotations or a path to a file containing one quotation per line
        :param kwargs:
        """
        super(QuotationDisplay, self).__init__(**kwargs)
        self.event = Clock.schedule_interval(self.update, self.update_sec)

    def update(self, dt):
        """ Display a randomly chosen quotation
        :param dt:
        """
        self.text = random.choice(self._quotations)

    @property
    def update_sec(self):
        """ Number of seconds between quotation transitions.

        :return:
        """
        return self._update_sec

    @update_sec.setter
    def update_sec(self, value: int):
        """ Set the number of seconds between quotation transitions.  Resets and restarts the schedule for this object.

        :param value:
        """
        self._update_sec = value
        self.event.cancel()
        self.event = Clock.schedule_interval(self.update, self.update_sec)

    @property
    def quotations(self):
        """ A list of strings, each of which represents a quotation.

        :return:
        """
        return self._quotations

    @quotations.setter
    def quotations(self, quotations: Union[str, List[str]]):
        """ Set the quotations used by this object.

        :param quotations: Either a list of strings, each of which represent a quotation or a path to a file
        containing quotations.  Also sets a new quotation on the display.
        """
        if isinstance(quotations, str):
            with open(quotations, 'r', encoding="latin-1") as f:
                self._quotations = [l.strip() for l in f.readlines()]
        else:
            self._quotations = quotations
        self.text = random.choice(self._quotations)


class QuotationDisplayApp(App):
    """ Displays a Quotation display with an exit button on the right.

    If a path is provided on the command line, it loads and displays those quotations.
    If "fullscreen" is added
    """
    def build(self):
        container = Builder.load_string('''
#:import exit sys.exit
BoxLayout:
    q: quotation_widget
    QuotationDisplay:
        id: quotation_widget
        size_hint: .9, 1
        update_sec: 60*30
        quotations: "I have a bad feeling about this.", "Luke, I am your father."
    BoxLayout:
        size_hint: .1, 1
        Button:
            text: 'X'
            on_press: exit()
''')

        if len(sys.argv) > 2 and ('fullscreen' in sys.argv):
            Window.fullscreen=True
        if len(sys.argv) > 1:
            container.q.quotations = sys.argv[1]
        return container


if __name__ == "__main__":
    QuotationDisplayApp().run()
