# HyperStackView -- application for rendering 3D raster images
# Copyright (C) 2021  Jiří Wolker
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

"""Various Qt sliders with number fields.
"""

__all__ = [
    'LabelledSliderWithNumber',
    'RotationSliderWithNumber',
    'RoundSliderWithNumber',
    'SliderWithNumber',
    'SliderWithNumberAndResetButton',
    'AnimationAngularSpeedSlider',
    'AnimationTimeSpeedSlider',
]


class SliderWithNumber(QWidget):
    """Minimal slider widget with spin box on its side.

    This widget emits its ``changed`` signal when the slider values is changed.
    """

    def __init__(self, min_value=0, max_value=1, slider_step=.01, spin_box_step=.01,
                 app_state=None, app_state_param=None, layout_direction=QBoxLayout.Direction.LeftToRight, suffix=None,
                 decimals=2):
        QWidget.__init__(self)

        self._create_children()
        self._layout(layout_direction)
        self.setLayout(self.layout)

        self._value = 0
        self._slider_step = .01
        self._ignore_events = False

        self.min_value = min_value
        self.max_value = max_value
        self.slider_step = slider_step
        self.spin_box_step = spin_box_step
        self.suffix = suffix
        self.decimals = decimals
        if layout_direction in [QBoxLayout.Direction.TopToBottom, QBoxLayout.Direction.BottomToTop]:
            self.slider_orientation = Qt.Orientation.Vertical
        else:
            self.slider_orientation = Qt.Orientation.Horizontal

        self.slider.valueChanged.connect(self._slider_changed)
        self.spin_box.valueChanged.connect(self._spin_box_changed)

        self._update_slider_range()

        if app_state is not None and app_state_param is not None:
            self.bind_to_app_state(app_state, app_state_param)

    changed = Signal(float)

    def bind_to_app_state(self, app_state, parameter):
        """Connects this slider to numerical application state parameter.
        """

        def changed(new_value):
            self._store_to_app_state(app_state, parameter, new_value)

        def app_state_changed(changed_parameter, _new_value):
            if changed_parameter == parameter:
                self._load_from_app_state(app_state, parameter)

        self.changed.connect(changed)
        app_state.changed.connect(app_state_changed)

        self._load_from_app_state(app_state, parameter)

    def _load_from_app_state(self, app_state, parameter):
        """Updates slider and spin box value from the application state object.
        """

        value = getattr(app_state, parameter)
        self.set_value(value, emit_signal=False)

    def _store_to_app_state(self, app_state, parameter, new_value):
        """Updates specified application property with current slider value.
        """

        setattr(app_state, parameter, new_value)

    def _create_children(self):
        """Creates child widgets. This function can be overriden to add more child widgets.
        """

        self._create_slider()
        self._create_spin_box()

    def _layout(self, direction):
        """Creates Qt layout with children widgets. This function can be overriden to add more widgets to the layout
        or to use custom layout.
        """

        self.layout = QBoxLayout(direction)
        self.layout.addWidget(self.slider)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.spin_box)

    def _create_slider(self):
        self.slider = QSlider()

    def _create_spin_box(self):
        self.spin_box = QDoubleSpinBox()

    def _slider_changed(self):
        if not self._ignore_events:
            self.set_value(self.slider.value() * self.slider_step,
                           update_slider=False)

    def _spin_box_changed(self):
        if not self._ignore_events:
            self.set_value(self.spin_box.value(),
                           update_spin_box=False)

    def get_min_value(self):
        return self.spin_box.minimum()

    def set_min_value(self, value):
        self.spin_box.setMinimum(value)
        self._update_slider_range()

    min_value = property(get_min_value, set_min_value, doc='Minimum acceptable value of the slider and spin box.')

    def get_max_value(self):
        return self.spin_box.maximum()

    def set_max_value(self, value):
        self.spin_box.setMaximum(value)
        self._update_slider_range()

    max_value = property(get_max_value, set_max_value, doc='Maximum acceptable value of teh slider and spin box.')

    def get_spin_box_step(self):
        return self.spin_box.singleStep()

    def set_spin_box_step(self, value):
        self.spin_box.setSingleStep(value)

    spin_box_step = property(get_spin_box_step, set_spin_box_step, doc='Smallest value step representable in the spin '
                                                                       'box.')

    def get_slider_orientation(self):
        return self.slider.orientation()

    def set_slider_orientation(self, value):
        self.slider.setOrientation(value)

    slider_orientation = property(get_slider_orientation, set_slider_orientation, doc="Orientation of the slider.\n\n"
                                  "Either ``Qt.Orientation.Vertical`` or ``Qt.Orientation.Horizontal``.")

    def get_slider_step(self):
        return self._slider_step

    def set_slider_step(self, value):
        self._slider_step = value
        self._update_slider_range()

    slider_step = property(get_slider_step, set_slider_step, doc="Smallest value step representable by the slider.\n\n"
                           "When the screen and/or mouse resolution is not high enough, the real smallest step can be"
                           "higher.")

    def get_suffix(self):
        return self.spin_box.suffix()

    def set_suffix(self, suffix):
        self.spin_box.setSuffix(suffix)

    suffix = property(get_suffix, set_suffix, doc="Number suffix shown in the number field. Use this to show units.")

    def get_decimals(self):
        return self.spin_box.decimals()

    def set_decimals(self, decimals):
        self.spin_box.setDecimals(decimals)

    decimals = property(get_decimals, set_decimals, doc="Number of decimal places in the spin boz.")

    def _update_slider_range(self):
        min_value, max_value = self.min_value, self.max_value
        slider_step = self.slider_step

        multiplier = 1 / slider_step
        self.slider.setRange(int(min_value * multiplier), int(max_value * multiplier))

    def get_value(self):
        return self._value

    def set_value(self, value, update_slider=True, update_spin_box=True, emit_signal=True):
        old_value = self.value
        self._value = value

        if update_slider:
            self._update_slider()
        if update_spin_box:
            self._update_spin_box()

        if emit_signal and self.value != old_value:
            self.changed.emit(self.value)

    value = property(get_value, set_value, doc='Value currently shown by the widget.')

    def _update_slider(self):
        self._ignore_events = True
        self.slider.setValue(int(self.value / self.slider_step))
        self._ignore_events = False

    def _update_spin_box(self):
        self._ignore_events = True
        self.spin_box.setValue(self._value)
        self._ignore_events = False


class RoundSliderWithNumber(SliderWithNumber):
    """Rotational slider (skeumorph of potentiometer knob) with numerical field.
    """

    def __init__(self, wrapping=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wrapping = wrapping

    def _create_slider(self):
        self.slider = QDial()
        self.slider.setWrapping(True)

    def get_wrapping(self):
        return self.slider.wrapping()

    def set_wrapping(self, value):
        self.slider.setWrapping(value)

    wrapping = property(get_wrapping, set_wrapping)


class LabelledSliderWithNumber(SliderWithNumber):
    """Slider with spin box and label on its one side.
    """

    def __init__(self, label, label_alignment=Qt.AlignCenter, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label.setAlignment(label_alignment)

        if type(label) is str:
            self.label.setText(label)
        elif type(label) is QPixmap:
            self.label.setPixmap(label)
        else:
            raise ValueError('unsupported label type')

    def _create_children(self):
        super()._create_children()

        self._create_label()

    def _create_label(self):
        self.label = QLabel()

    def _layout(self, *args, **kwargs):
        super()._layout(*args, **kwargs)

        self.layout.insertWidget(0, self.label)


class SliderWithNumberAndResetButton(SliderWithNumber):
    """Slider with spin box and button that sets default value.
    """

    def __init__(self, reset_button_text='Reset', default_value=0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_value = default_value
        self.reset_button_text = reset_button_text

    def _create_children(self):
        super()._create_children()

        self._create_reset_button()

    def _create_reset_button(self):
        self.reset_button = QPushButton()

        self.reset_button.clicked.connect(self.reset)

    def reset(self):
        self.value = self.default_value

    def _layout(self, *args, **kwargs):
        super()._layout(*args, **kwargs)

        self.layout.addWidget(self.reset_button)

    def get_reset_button_text(self):
        return self.reset_button.text()

    def set_reset_button_text(self, value):
        self.reset_button.setText(value)

    reset_button_text = property(get_reset_button_text, set_reset_button_text)


class RotationSliderWithNumber(LabelledSliderWithNumber, RoundSliderWithNumber, SliderWithNumberAndResetButton):
    """“Knob” widget that is used in configuration to control rotation of view.
    """

    def __init__(self, axis, *args, **kwargs):
        LABELS = ['X', 'Y', 'Z']
        label = LABELS[axis]
        self.axis = axis
        super().__init__(label, suffix='°', *args, **kwargs)

    def _load_from_app_state(self, app_state, parameter):
        value = getattr(app_state, parameter)[self.axis] * 180 / np.pi
        self.set_value(value, emit_signal=False)

    def _store_to_app_state(self, app_state, parameter, new_value):
        value = list(getattr(app_state, parameter))
        value[self.axis] = new_value * np.pi / 180
        setattr(app_state, parameter, value)


class AnimationAngularSpeedSlider(LabelledSliderWithNumber, SliderWithNumberAndResetButton):
    """Slider widget that is used in the configuration interface to control angular speed of animation.
    """

    def __init__(self, axis, *args, **kwargs):
        LABELS = ['X', 'Y', 'Z']
        label = LABELS[axis]
        self.axis = axis
        super().__init__(label, *args, **kwargs)

    def _load_from_app_state(self, app_state, parameter):
        value = getattr(app_state, parameter)[self.axis] * 180 / np.pi
        self.set_value(value, emit_signal=False)

    def _store_to_app_state(self, app_state, parameter, new_value):
        value = list(getattr(app_state, parameter))
        value[self.axis] = new_value * np.pi / 180
        setattr(app_state, parameter, value)


class AnimationTimeSpeedSlider(SliderWithNumberAndResetButton):
    """Slider with spin box that is used to control animation speed on the time axis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _load_from_app_state(self, app_state, parameter):
        value = getattr(app_state, parameter)[3]
        self.set_value(value, emit_signal=False)

    def _store_to_app_state(self, app_state, parameter, new_value):
        value = list(getattr(app_state, parameter))
        value[3] = new_value
        setattr(app_state, parameter, value)
