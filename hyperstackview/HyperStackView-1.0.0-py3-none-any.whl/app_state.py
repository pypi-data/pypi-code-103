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
import yaml
from PySide6.QtCore import *

from .paths import data_dir

"""This file provides class for storage of application state.
"""

with open(data_dir / 'defaults.yaml', 'r') as f:
    parameter_metadata = list(yaml.safe_load(f).items())


def _get_defaults():
    """Returns default state of all application state parameters.
    """

    parameters = {}
    for parameter_name, info in parameter_metadata:
        parameters[parameter_name] = info['value']
    return parameters


class ApplicationState(QObject):
    """Provides all information about current application parameters and input data.

    *Note:* Variable name ``app_state`` is used to refer one shared instance of this class through the application.

    Retrieving and changing values can be done in two ways::

      app_state.param
      app_state.param = new_value

      getattr(app_state, 'param')
      setattr(app_state, 'param', new_value)

    Custom setter function can be created using this call::

      setter_function = app_state.setter_for('param')

    The setter then updates the application state when called::

      setter_function(new_value)

    This class provides Qt signal that is invoked when *any* application parameter changes. Use following code to
    connect custom function to it::

      def handler(changed_parameter_name, new_parameter_value):
          ...

      app_state.changed.connect(handler)

    Signal that is emitted on when only specific parameter changes used as follows::

      def handler(new_parameter_value):
          ...

      app_state.signal_for('param_name').connect(handler)

    Instances of this class also handle animations and enforce some parameter limitations. See closure ``on_changed`` in
    the constructor for details.
    """

    _tracking = True
    changed = Signal(str, object)
    _app_state_parameters = {}

    def __init__(self):
        super().__init__()

        for key in _get_defaults().keys():
            class Tmp(QObject):
                signal = Signal(object)

            t = Tmp()
            setattr(self, f'_sig_{key}', t)

        self._app_state_parameters = _get_defaults()

        # Processing of new values
        def on_changed(changed_parameter, new_value):
            if self._tracking:
                try:
                    self._tracking = False

                    # This part of code contains some constraints that are applied to the values so they stay
                    # meaningful. Please be sure that some of the values are not overwritten more than one time.

                    if changed_parameter == 'rotation':
                        self.rotation = (np.array(new_value) + np.pi) % (2 * np.pi) - np.pi

                    if self.scale < .1:
                        self.scale = .1
                    elif self.scale > 10:
                        self.scale = 10

                    if self.projection_type == 'slice':
                        self.z_samples = 1
                        if changed_parameter == 'projection_type':
                            self.near_plane_screen_z = self.far_plane_screen_z + .01
                        elif changed_parameter == 'far_plane_screen_z':
                            self.near_plane_screen_z = self.far_plane_screen_z + .01
                        elif changed_parameter == 'near_plane_screen_z':
                            self.far_plane_screen_z = self.near_plane_screen_z - .01
                    else:
                        if changed_parameter == 'projection_type':
                            self.z_samples = 500
                            self.near_plane_screen_z = 1.44
                            self.far_plane_screen_z = -.44

                        if changed_parameter == 'z_samples':
                            self.z_samples = int(new_value)

                    if self.near_plane_screen_z <= self.far_plane_screen_z:
                        if changed_parameter == 'near_plane_screen_z':
                            self.near_plane_screen_z = self.far_plane_screen_z + .01
                        else:
                            self.far_plane_screen_z = self.near_plane_screen_z - .01

                    if changed_parameter == 'animation_interval':
                        self._animation_timer.setInterval(new_value)

                    if changed_parameter == 'animation_running':
                        if new_value:
                            self._animation_timer.start()
                        else:
                            self._animation_timer.stop()
                finally:
                    self._tracking = True

            new_value = getattr(self, changed_parameter)
            self.signal_for(changed_parameter).emit(new_value)

        self.changed.connect(on_changed)

        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._animation_timer_timeout)

        self._object_blink_timer = QTimer()
        self._object_blink_timer.setInterval(300)
        self._object_blink_timer.timeout.connect(self._object_blink_timer_timeout)
        self._object_blink_timer.start()

    def _animation_timer_timeout(self):
        self.rotation = np.array(self.animation_step[:3]) + self.rotation

        if self.base_img is not None:
            self.current_frame = (self.current_frame + self.animation_step[3]) % self.base_img.frame_count

    def _object_blink_timer_timeout(self):
        if self.mask_enabled:
            if self.mask_highlight_blink:
                self.mask_highlight_blink_state = not self.mask_highlight_blink_state
            else:
                self.mask_highlight_blink_state = False

    def __getattr__(self, item):
        if item in self._app_state_parameters:
            return self._app_state_parameters[item]
        else:
            return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self._app_state_parameters and not key.startswith('_'):
            old_value = self._app_state_parameters[key]
            self._app_state_parameters[key] = value
            changed = (old_value is not value)
            if self.changed is not None and changed:
                self.changed.emit(key, value)
        else:
            try:
                # CPython 3.8 and newer
                return super().__setattr__(key, value)
            except TypeError:
                return object.__setattr__(self, key, value)

    def setter_for(self, key):
        """Creates a setter function for the specified parameter name.

        More information can be found in the class documentation."""

        def setter(value):
            setattr(self, key, value)

        return setter

    def signal_for(self, key):
        """Creates a Qt Signal for the specified parameter name.

        More information can be found in the class documentation."""

        return getattr(self, f'_sig_{key}').signal

    def connect_and_invoke(self, key, slot):
        """Connects on-change signal of specific key to Qt slot and invokes the slot.
        """

        signal = self.signal_for(key)
        signal.connect(slot)
        slot(getattr(self, key))

    def connect_checkbox(self, key, checkbox):
        """Connects Qt checkbox to specified key in the application state.
        """

        self.connect_and_invoke(key, checkbox.setChecked)
        checkbox.clicked.connect(self.setter_for(key))
