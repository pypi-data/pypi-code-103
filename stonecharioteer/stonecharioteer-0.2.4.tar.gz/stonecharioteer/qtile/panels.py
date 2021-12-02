"""Holds all the bars"""
from libqtile.widget import (
    Battery,
    CPU,
    CapsNumLockIndicator,
    Clock,
    CurrentLayout,
    GroupBox,
    HDDGraph,
    Memory,
    Net,
    Prompt,
    QuickExit,
    Spacer,
    Systray,
    TextBox,
    Volume,
    WindowName,
)

from libqtile.bar import Bar, STRETCH

# TODO: Modularize and create a constructor function
current_layout = CurrentLayout()
group_box = GroupBox()
prompt_widget = Prompt()
window_name = WindowName()
clock_widget = Clock(format="%Y-%m-%d %a %I:%M %p")
system_tray = Systray()
quick_exit = QuickExit()
capslock_numlock_indicator = CapsNumLockIndicator()
cpu_indicator = CPU()
memory_indicator = Memory()
hdd_indicator = HDDGraph()
volume_control = Volume(cardid="1")

# TODO: Only add this if this is a laptop, control through config.
battery_indicator = Battery()
network_indicator = Net()
spacer = Spacer(length=STRETCH)

default_size = 24
default_top_bar = Bar(
    [
        current_layout,
        prompt_widget,
        spacer,
        TextBox(text="CPU:"),
        cpu_indicator,
        TextBox(text="Memory:"),
        memory_indicator,
        TextBox(text="HDD:"),
        hdd_indicator,
        system_tray,
        TextBox(text="Net:"),
        network_indicator,
        TextBox(text="Vol:"),
        volume_control,
        capslock_numlock_indicator,
    ],
    default_size,
)
default_bottom_bar = Bar(
    [
        group_box,
        window_name,
        clock_widget,
        TextBox(text="Battery ["),
        battery_indicator,
        TextBox(text="]"),
        quick_exit,
    ],
    default_size,
)
