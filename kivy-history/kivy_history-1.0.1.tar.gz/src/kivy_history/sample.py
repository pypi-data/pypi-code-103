#!/usr/bin/env python
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from kivy_history import History


class Navigation(BoxLayout):
    pass


KV = """
#: import Clock kivy.clock.Clock

<Link@ButtonBehavior+Label>:

<Navigation>
    orientation: 'vertical'
    size_hint_y: .2
    BoxLayout:
        Button:
            text: '<'
            on_press: app.root.history.back()
        Button:
            text: '>'
            on_press: app.root.history.forward()
        Button:
            text: 'Reload'
            on_press: app.root.history.go()
        Button:
            text: 'Push'
            on_press: app.root.history.push_state(name='s4')
        Button:
            text: 'Replace'
            on_press: app.root.history.replace_state(name='s1')

ScreenManager:
    id: sm
    Screen:
        name: 's1'
        BoxLayout:
            orientation: 'vertical'

            Navigation:

            BoxLayout:
                orientation: 'vertical'
                Label:
                    markup: True
                    text: '[b]Page 1[/b]'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 2[/color]'
                    on_press: app.root.current = 's2'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 3[/color]'
                    on_press: app.root.current = 's3'
    Screen:
        name: 's2'
        BoxLayout:
            orientation: 'vertical'
            
            Navigation:

            BoxLayout:
                orientation: 'vertical'
                Label:
                    markup: True
                    text: '[b]Page 2[/b]'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 1[/color]'
                    on_press: app.root.current = 's1'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 3[/color]'
                    on_press: app.root.current = 's3'
    Screen:
        name: 's3'
        BoxLayout:
            orientation: 'vertical'
            
            Navigation:

            BoxLayout:
                orientation: 'vertical'
                Label:
                    markup: True
                    text: '[b]Page 3[/b]'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 1[/color]'
                    on_press: app.root.current = 's1'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 2[/color]'
                    on_press: app.root.current = 's2'
    Screen:
        name: 's4'
        BoxLayout:
            orientation: 'vertical'
            
            Navigation:

            BoxLayout:
                orientation: 'vertical'
                Label:
                    markup: True
                    text: '[b]Pushed page 4[/b]'
                Link:
                    markup: True
                    text: '[color=0000ff]Link page 1[/color]'
                    on_press: app.root.current = 's1'
"""


class DemoApp(App):
    def build(self):
        manager = Builder.load_string(KV)
        manager.history = History()
        manager.bind(current=manager.history.on_state)
        return manager


def main():
    os.environ["HISTORY_LOG"] = "1"
    DemoApp().run()


if __name__ == '__main__':
    main()
