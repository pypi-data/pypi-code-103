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

from pathlib import Path

import numpy as np
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import HyperStackView.config_ui as config_ui
import HyperStackView.hyperstack as hyperstack
from .paths import data_dir
from .app_state import ApplicationState
from .color_picker import ColorPicker
from .gl_view import HyperStackView, ScreenCapturePendingError
from .object_selector import ObjectSelectorWindow
from .sliders import *


class HyperStackViewApplication(QApplication):
    """Qt application class of the HyperStackView.

    Code for creation of instance and starting the application is in file ``hyperstackview.py``.
    """

    def __init__(self, argv):
        QApplication.__init__(self, argv)

        self.app_state = ApplicationState()
        self.color_picker = ColorPicker(self.app_state)
        self.main_window = MainWindow(self)

    def show_windows(self):
        self.main_window.show()


class DeferredFrameChangeWorker(QObject):
    """Provides Qt signal-slot interface for changing displayed frames on separate thread.
    """

    frame_changed = Signal()
    current_frame_changed = Signal()

    def __init__(self, app_state):
        super().__init__()

        self.app_state = app_state

        self.current_frame_changed.connect(self.change_frame, type=Qt.QueuedConnection)

        def app_state_changed(changed_parameter, new_value):
            if changed_parameter == 'current_frame':
                self.current_frame_changed.emit()

        self.app_state.changed.connect(app_state_changed)

    def change_frame(self):
        if self.app_state.base_img is not None and self.app_state.base_img.t != self.app_state.current_frame:
            self.app_state.base_img.select_frame(self.app_state.current_frame)
        if self.app_state.binary_img is not None and self.app_state.binary_img.t != self.app_state.current_frame:
            self.app_state.binary_img.select_frame(self.app_state.current_frame)
            self.frame_changed.emit()


class MainWindow(QMainWindow):
    """Main window of the application.
    """

    new_image_loaded = Signal()

    def __init__(self, app):
        QMainWindow.__init__(self)

        self.app = app

        self.resize(1024, 512)

        self.app_state = app.app_state
        self.app_state.changed.connect(self._app_state_changed)

        self.opengl_widget = HyperStackView(self.app_state)

        self.central_widget = QWidget()
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.layout.setColumnMinimumWidth(0, 512)
        self.layout.setContentsMargins(8, 0, 0, 8)

        self.t_slider = SliderWithNumber(
            min_value=0,
            max_value=0,
            slider_step=1,
            spin_box_step=1,
            decimals=0,
            app_state=self.app_state,
            app_state_param='current_frame',
        )

        self.deferred_frame_change_worker = DeferredFrameChangeWorker(self.app_state)
        self.deferred_frame_change_worker_thread = QThread()
        self.deferred_frame_change_worker.moveToThread(self.deferred_frame_change_worker_thread)
        self.deferred_frame_change_worker_thread.start()

        self.new_image_loaded.connect(self.deferred_frame_change_worker.change_frame)
        self.deferred_frame_change_worker.frame_changed.connect(self.update_view)

        self.layout.addWidget(self.opengl_widget, 0, 0)
        self.layout.addWidget(self.t_slider, 1, 0)
        self.layout.setRowStretch(0, 1)

        self.setCentralWidget(self.central_widget)

        self.object_selector_window = ObjectSelectorWindow(app, self.app_state)

        #
        # Configuration widgets
        #
        self.setTabPosition(Qt.DockWidgetArea.RightDockWidgetArea, QTabWidget.North)

        self.config_dock_widgets = []
        for cls in [config_ui.TabView, config_ui.TabPosition, config_ui.TabInput, config_ui.TabAnimation,
                    config_ui.TabProcessing]:
            dock_widget = ConfigDockWidget(self, cls)
            self.config_dock_widgets.append(dock_widget)

        self.open_all_config_dock_widgets()
        self.tabify_all_config_dock_widgets()

        #
        # Menus
        #

        menu_bar = self.menuBar()

        def bind_check_action_to_property(action, property):
            action.setCheckable(True)
            action.setChecked(getattr(self.app_state, property))
            action.toggled.connect(self.app_state.setter_for(property))
            self.app_state.signal_for(property).connect(lambda status: action.setChecked(status))

        def rotate_to_handler(xrot, yrot, zrot):
            def slot():
                self.app_state.rotation = (np.array([xrot, yrot, zrot]) * (np.pi / 180)).tolist()

            return slot

        def rotate_relative_handler(xrot, yrot, zrot):
            STEP = 15 * np.pi / 180

            def slot():
                self.app_state.rotation = (
                        self.app_state.rotation + np.array([xrot, yrot, zrot]) * STEP
                ).tolist()

            return slot

        def zoom_handler(change):
            def slot():
                self.app_state.scale += change

            return slot

        def bind_frame_change_action(action, get_next_frame):
            def state_changed(name, new_value):
                update()

            def update():
                action.setEnabled(
                    (self.app_state.base_img or self.app_state.binary_img) is not None
                    and
                    0 <= get_next_frame() < (self.app_state.base_img or self.app_state.binary_img).frame_count
                )

            def slot():
                self.app_state.current_frame = get_next_frame()

            self.app_state.changed.connect(state_changed)
            action.triggered.connect(slot)
            update()

        # Menu [File] #####################################
        menu_file = menu_bar.addMenu('&File')

        # • Open TIFF…
        open_tiff_action = menu_file.addAction('&Open TIFF…', self.open_tiff_dialog, QKeySequence.Open)
        open_tiff_action.setIcon(QIcon.fromTheme('document-open'))

        # • Unload all images
        unload_images_action = menu_file.addAction('&Unload all images', self.unload_images, QKeySequence.Close)
        unload_images_action.setIcon(QIcon.fromTheme('document-close'))

        # • Screenshot
        screenshot_action = menu_file.addAction('&Screenshot', self.screen_capture_dialog)

        menu_file.addSeparator()

        # • Object selector
        object_selector_action = menu_file.addAction('O&bject selector', self.show_object_selector)
        object_selector_action.setShortcut(QKeySequence(Qt.CTRL | Qt.SHIFT | Qt.Key_O))

        menu_file.addSeparator()

        # • Quit
        menu_file.addAction('&Quit', QApplication.quit, QKeySequence.Quit)

        # Menu [View] #####################################
        menu_view = menu_bar.addMenu('&View')

        # -- Overlays --
        menu_view.addSection('Overlays')

        # √ Enable grid
        enable_grid_action = menu_view.addAction('Enable &grid')
        enable_grid_action.setIcon(QPixmap(str(str(data_dir / 'ic_grid.png'))))
        enable_grid_action.setShortcut(QKeySequence(Qt.SHIFT | Qt.Key_G))
        bind_check_action_to_property(enable_grid_action, 'show_grid')

        # √ Enable cube backdrop
        enable_bg_cube_action = menu_view.addAction('Enable cube &backdrop')
        enable_bg_cube_action.setIcon(QPixmap(str(data_dir / 'ic_bg_cube.png')))
        enable_bg_cube_action.setShortcut(QKeySequence(Qt.SHIFT | Qt.Key_B))
        bind_check_action_to_property(enable_bg_cube_action, 'show_bg_cube')

        # √ Enable preview of rotation
        enable_rotation_osd_action = menu_view.addAction('Enable preview of r&otation')
        enable_rotation_osd_action.setShortcut(QKeySequence(Qt.SHIFT | Qt.Key_O))
        bind_check_action_to_property(enable_rotation_osd_action, 'show_rotation_osd')

        # • Rotation preview settings →
        rotation_osd_submenu = menu_view.addMenu('Rotation preview &settings')
        enable_rotation_osd_action.toggled.connect(rotation_osd_submenu.setEnabled)

        #    √ Show projection plane bounds
        show_projection_plane = rotation_osd_submenu.addAction('Show &projection plane bounds')
        bind_check_action_to_property(show_projection_plane, 'show_rotation_osd_bounds')

        #    √ Clip the preview by near and far planes
        enable_rotation_osd_clipping = rotation_osd_submenu.addAction('&Clip the preview by near and far planes')
        bind_check_action_to_property(enable_rotation_osd_clipping, 'clip_rotation_osd')

        # -- Navigate --
        menu_view.addSection('Navigate')

        # • Home
        rotate_home_action = menu_view.addAction('&Home')
        rotate_home_action.setIcon(QPixmap(str(data_dir / 'ic_rot_home.png')))
        rotate_home_action.triggered.connect(rotate_to_handler(-135, 0, -15))
        rotate_home_action.setShortcut(QKeySequence(Qt.Key_5))
        self.opengl_widget.set_default_rotation_triggered.connect(rotate_home_action.trigger)

        # • Initial position
        rotate_zero_action = menu_view.addAction('&Initial position')
        rotate_zero_action.setIcon(QPixmap(str(data_dir / 'ic_rot_zero.png')))
        rotate_zero_action.triggered.connect(rotate_to_handler(0, 0, 0))
        rotate_zero_action.setShortcut(QKeySequence(Qt.Key_0))

        # • Show front side
        rotate_front_action = menu_view.addAction('Show &front side')
        rotate_front_action.setIcon(QPixmap(str(data_dir / 'ic_rot_front.png')))
        rotate_front_action.triggered.connect(rotate_to_handler(-90, 0, 0))

        # • Show right side
        rotate_side_action = menu_view.addAction('Show &right side')
        rotate_side_action.setIcon(QPixmap(str(data_dir / 'ic_rot_side.png')))
        rotate_side_action.triggered.connect(rotate_to_handler(-90, 0, -90))

        # • Rotate X+
        rotate_x_pos_action = menu_view.addAction('Rotate &X+')
        rotate_x_pos_action.triggered.connect(rotate_relative_handler(1, 0, 0))
        rotate_x_pos_action.setShortcut(QKeySequence(Qt.Key_8))

        # • Rotate X-
        rotate_x_neg_action = menu_view.addAction('Rotate &X-')
        rotate_x_neg_action.triggered.connect(rotate_relative_handler(-1, 0, 0))
        rotate_x_neg_action.setShortcut(QKeySequence(Qt.Key_2))

        # • Rotate Y+
        rotate_y_pos_action = menu_view.addAction('Rotate &Y+')
        rotate_y_pos_action.triggered.connect(rotate_relative_handler(0, 1, 0))
        rotate_y_pos_action.setShortcut(QKeySequence(Qt.Key_7))

        # • Rotate Y-
        rotate_y_neg_action = menu_view.addAction('Rotate &Y-')
        rotate_y_neg_action.triggered.connect(rotate_relative_handler(0, -1, 0))
        rotate_y_neg_action.setShortcut(QKeySequence(Qt.Key_3))

        # • Rotate Z+
        rotate_z_pos_action = menu_view.addAction('Rotate &Z+')
        rotate_z_pos_action.triggered.connect(rotate_relative_handler(0, 0, 1))
        rotate_z_pos_action.setShortcut(QKeySequence(Qt.Key_6))

        # • Rotate Z-
        rotate_z_neg_action = menu_view.addAction('Rotate &Z-')
        rotate_z_neg_action.triggered.connect(rotate_relative_handler(0, 0, -1))
        rotate_z_neg_action.setShortcut(QKeySequence(Qt.Key_4))

        menu_view.addSeparator()

        # • Zoom in
        zoom_in_action = menu_view.addAction('Zoom &in')
        zoom_in_action.triggered.connect(zoom_handler(.1))
        zoom_in_action.setShortcuts([QKeySequence.ZoomIn, QKeySequence(Qt.Key_Plus)])
        zoom_in_action.setIcon(QIcon.fromTheme('zoom-in'))

        # • Zoom out
        zoom_out_action = menu_view.addAction('Zoom &out')
        zoom_out_action.triggered.connect(zoom_handler(-.1))
        zoom_out_action.setIcon(QIcon.fromTheme('zoom-out'))
        zoom_out_action.setShortcuts([QKeySequence.ZoomOut, QKeySequence(Qt.Key_Minus)])

        menu_view.addSeparator()

        # • Intermediate buffer resolution →
        intermediate_resolution_menu = menu_view.addMenu('Intermediate &buffer resolution')

        def set_intermediate_resolution_size_handler(size):
            def slot():
                self.app_state.intermediate_resolution = size

            return slot

        #    √ <size>×<size>
        for size in [128, 256, 512, 1024, 2048]:
            set_size_action = intermediate_resolution_menu.addAction(f'{size}×{size}')
            set_size_action.setCheckable(True)
            set_size_action.triggered.connect(set_intermediate_resolution_size_handler(size))
            self.app_state.signal_for('intermediate_resolution').connect(
                (lambda action, size: lambda value: action.setChecked(value == size))(set_size_action, size))

        # Menu [Multi-frame] ##############################
        menu_frames = menu_bar.addMenu('&Multi-frame')

        def update_menu_frames_enabled():
            menu_frames.setEnabled(
                (self.app_state.base_img or self.app_state.binary_img) is not None
                and (self.app_state.base_img or self.app_state.binary_img).frame_count > 1
            )

        self.app_state.changed.connect(lambda _, _2: update_menu_frames_enabled())
        update_menu_frames_enabled()

        # • First frame
        first_frame_action = menu_frames.addAction('&First frame')
        bind_frame_change_action(first_frame_action, lambda: 0)
        first_frame_action.setIcon(QIcon.fromTheme('go-first'))
        first_frame_action.setShortcuts([
            QKeySequence(Qt.Key_Home),
            QKeySequence(Qt.CTRL | Qt.Key_1)
        ])

        # • Previous frame
        prev_frame_action = menu_frames.addAction('&Previous frame')
        bind_frame_change_action(prev_frame_action, lambda: self.app_state.current_frame - 1)
        prev_frame_action.setIcon(QIcon.fromTheme('go-previous'))
        prev_frame_action.setShortcuts([
            QKeySequence(Qt.Key_PageUp),
            QKeySequence(Qt.Key_1)
        ])
        self.opengl_widget.back_pressed.connect(prev_frame_action.trigger)

        # • Next frame
        next_frame_action = menu_frames.addAction('&Next frame')
        bind_frame_change_action(next_frame_action, lambda: self.app_state.current_frame + 1)
        next_frame_action.setIcon(QIcon.fromTheme('go-next'))
        next_frame_action.setShortcuts([
            QKeySequence(Qt.Key_PageDown),
            QKeySequence(Qt.Key_9)
        ])
        self.opengl_widget.forward_pressed.connect(next_frame_action.trigger)

        # • Last frame
        last_frame_action = menu_frames.addAction('&Last frame')
        bind_frame_change_action(last_frame_action,
                                 lambda: (self.app_state.base_img or self.app_state.binary_img).frame_count - 1)
        last_frame_action.setIcon(QIcon.fromTheme('go-last'))
        last_frame_action.setShortcuts([
            QKeySequence(Qt.Key_End),
            QKeySequence(Qt.CTRL | Qt.Key_9)
        ])

        menu_frames.addSeparator()

        # • Go to frame
        goto_frame_action = menu_frames.addAction('&Go to frame…')
        goto_frame_action.triggered.connect(self.select_frame_dialog)
        goto_frame_action.setIcon(QIcon.fromTheme('go-jump'))
        goto_frame_action.setEnabled(self.app_state.base_img is not None)
        self.app_state.changed.connect(lambda _, _2: goto_frame_action.setEnabled(
            (self.app_state.base_img or self.app_state.binary_img) is not None
        ))
        goto_frame_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_G))

        # Menu [Animation] ################################
        menu_animation = menu_bar.addMenu('&Animation')

        # √ Animate
        animate_action = menu_animation.addAction('&Animate')
        animate_action.setCheckable(True)
        animate_action.setIcon(QIcon.fromTheme('media-playback-start'))
        bind_check_action_to_property(animate_action, 'animation_running')
        animate_action.setShortcut(QKeySequence(Qt.Key_P))

        # • Stop
        stop_animation_action = menu_animation.addAction('&Stop')
        stop_animation_action.triggered.connect(lambda: setattr(self.app_state, 'animation_running', False))
        self.app_state.signal_for('animation_running').connect(lambda state: stop_animation_action.setEnabled(state))
        stop_animation_action.setIcon(QIcon.fromTheme('media-playback-stop'))

        menu_animation.addSection('Presets')

        # • Rotate around X axis
        # • Rotate around Y axis
        # • Rotate around Z axis
        for axis_name, axis in [('X', [.01, 0, 0, 0]), ('Y', [0, .01, 0, 0]), ('Z', [0, 0, .01, 0])]:
            def rotate_around_handler(axis):
                def slot():
                    self.app_state.animation_step = axis
                    self.app_state.animation_running = True

                return slot

            rotate_around_axis = menu_animation.addAction(f'Rotate around &{axis_name} axis')
            rotate_around_axis.triggered.connect(rotate_around_handler(axis))

        # • Play frame sequence
        def play_sequence_handler(t_step):
            def slot():
                self.app_state.animation_step = [0, 0, 0, t_step]
                self.app_state.animation_running = True

            return slot

        def update_play_sequence_enabled():
            play_sequence_action.setEnabled(bool(self.app_state.base_img and self.app_state.base_img.frame_count > 1))
            play_sequence_rev_action.setEnabled(
                bool(self.app_state.base_img and self.app_state.base_img.frame_count > 1))

        play_sequence_action = menu_animation.addAction('&Play frame sequence')
        play_sequence_action.triggered.connect(play_sequence_handler(1))

        # • Play sequence in reverse
        play_sequence_rev_action = menu_animation.addAction('Play sequence in &reverse')
        play_sequence_rev_action.triggered.connect(play_sequence_handler(-1))

        update_play_sequence_enabled()
        self.app_state.changed.connect(update_play_sequence_enabled)

        # Menu [Window] ###################################
        def setup_menu_window():
            menu_window.clear()

            # • Dockable windows and toolbars
            dockables_menu = self.createPopupMenu()
            dockables_menu.setTitle('&Dockable windows and toolbars')
            menu_window.addMenu(dockables_menu)

            # • Restore dockable windows
            restore_dockables_action = menu_window.addAction('&Restore dockable windows')
            restore_dockables_action.triggered.connect(self.restore_dockables)

            menu_window.addSeparator()

            close_action = menu_window.addAction('&Close')
            close_action.triggered.connect(self.close)

        menu_window = self.createPopupMenu()
        menu_window.setTitle('&Window')
        menu_bar.addMenu(menu_window)
        menu_window.aboutToShow.connect(setup_menu_window)

        #
        # Toolbars
        #

        file_actions_toolbar = self.addToolBar('&File')
        file_actions_toolbar.addAction(open_tiff_action)

        view_toolbar = self.addToolBar('&View')
        view_toolbar.addAction(enable_grid_action)
        view_toolbar.addAction(enable_bg_cube_action)
        view_toolbar.addSeparator()
        view_toolbar.addAction(rotate_home_action)
        view_toolbar.addAction(rotate_zero_action)
        view_toolbar.addAction(rotate_front_action)
        view_toolbar.addAction(rotate_side_action)
        view_toolbar.addSeparator()
        view_toolbar.addAction(zoom_out_action)
        view_toolbar.addAction(zoom_in_action)

        frames_toolbar = self.addToolBar('&Multi-frame image operations')
        frames_toolbar.addAction(first_frame_action)
        frames_toolbar.addAction(prev_frame_action)
        frames_toolbar.addAction(next_frame_action)
        frames_toolbar.addAction(last_frame_action)

        self.refresh_ui()
        self._app_state_changed()

    def closeEvent(self, event):
        self.object_selector_window.close()
        self.app.color_picker.close()

        event.accept()

    def open_all_config_dock_widgets(self):
        """Adds all known dock widgets (toolbox windows) to the main window and shows them.
        """

        for widget in self.config_dock_widgets:
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, widget)
            widget.show()

    def tabify_all_config_dock_widgets(self):
        """Places all dock widgets (toolbox windows) in single area with tab bar.
        """

        for widget_1, widget_2 in zip(self.config_dock_widgets, self.config_dock_widgets[1:]):
            self.tabifyDockWidget(widget_1, widget_2)

    def restore_dockables(self):
        """Restores layout and state of all dockable windows.
        """

        for widget in self.config_dock_widgets:
            widget.hide()

        self.open_all_config_dock_widgets()
        self.tabify_all_config_dock_widgets()

    def _app_state_changed(self):
        """Qt slot that is invoked on application state change. Connected in the constructor.
        """

        self.update_view()
        self.update_window_caption()

    def update_window_caption(self):
        """Updates caption of the main window.
        """

        title = ''

        if self.app_state.base_file_path is not None or self.app_state.binary_file_path is not None:
            # We have open file with known name.

            if self.app_state.animation_running:
                title += '▶ '

            if self.app_state.base_file_path is not None:
                title += self.app_state.base_file_path.name
                if self.app_state.binary_file_path is not None:
                    title += ', '
            if self.app_state.binary_file_path is not None:
                title += self.app_state.binary_file_path.name

            if (self.app_state.base_img is not None and self.app_state.base_img.frame_count > 1) \
                    or (self.app_state.binary_img is not None and self.app_state.binary_img.frame_count > 1):
                title += f' (t={int(self.app_state.current_frame)})'

            title += ' '

            if self.app_state.projection_type == '3d':
                title += '3D '
            if self.app_state.projection_type == 'slice':
                title += 'Slice '

            has_bracketed_str = False
            if self.app_state.base_file_path is not None:
                if self.app_state.max_enabled:
                    title += '[MAX]'
                    has_bracketed_str = True
                if self.app_state.avg_enabled:
                    title += '[AVG]'
                    has_bracketed_str = True
            if self.app_state.binary_enabled and self.app_state.binary_file_path is not None:
                title += '[BIN]'
                has_bracketed_str = True

            if has_bracketed_str:
                title += ' '

            title += '– '

        title += 'HyperStackView'

        self.setWindowTitle(title)

    def refresh_ui(self):
        """Updates window controls to reflect current application state.
        """

        if self.app_state.base_img is not None:
            self.t_slider.max_value = self.app_state.base_img.frame_count - 1
            self.t_slider.setEnabled(True)
        elif self.app_state.binary_img is not None:
            self.t_slider.max_value = self.app_state.binary_img.frame_count - 1
            self.t_slider.setEnabled(True)
        else:
            self.t_slider.setEnabled(False)

    def show_object_selector(self):
        self.object_selector_window.show()
        self.object_selector_window.raise_()

    def unload_images(self):
        self.app_state.base_img = None
        self.app_state.base_file_path = None
        self.app_state.binary_img = None
        self.app_state.binary_file_path = None

    def open_tiff_dialog(self):
        """Shows input file chooser.
        """

        dialog = QDialog()
        dialog_layout = QGridLayout()
        dialog.setLayout(dialog_layout)
        dialog_layout.setContentsMargins(0, 0, 0, 0)

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters([
            'TIFF files (*.tif *.tiff)',
            'All files (*)',
        ])
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setSizeGripEnabled(False)
        dialog_layout.addWidget(file_dialog, 0, 0)

        options_layout = QVBoxLayout()
        dialog_layout.addLayout(options_layout, 0, 2)

        destination_selection = QGroupBox()
        destination_selection.setTitle('Destination')
        destination_selection_layout = QVBoxLayout()
        destination_selection.setLayout(destination_selection_layout)
        radio_base_tiff = QRadioButton('Load as “B&ase” image')
        radio_base_tiff.setChecked(True)
        destination_selection_layout.addWidget(radio_base_tiff)
        radio_binary_tiff = QRadioButton('Load as “B&inary” image')
        destination_selection_layout.addWidget(radio_binary_tiff)
        options_layout.addWidget(destination_selection)

        options_layout.addStretch()

        # Add empty widget to the last column to pad the form
        dialog_layout.addWidget(QWidget(), 0, 4)

        def user_responded():
            path = file_dialog.selectedFiles()[0]
            print(f'Loading file {path}')

            try:
                img = hyperstack.TiffFileVirtualStack(path)
            except hyperstack.TiffFileVirtualStack.UnsupportedFileError as error:
                QMessageBox.warning(self, 'Unsupported file', str(error))
                return

            if radio_base_tiff.isChecked():
                self.app_state.base_img = img
                self.app_state.base_file_path = Path(path)
            elif radio_binary_tiff.isChecked():
                self.app_state.binary_img = img
                self.app_state.binary_file_path = Path(path)

            self.new_image_loaded.emit()

            self.update_view()
            self.refresh_ui()

        file_dialog.finished.connect(dialog.done)
        dialog.accepted.connect(user_responded)
        dialog.exec_()

    def select_frame_dialog(self):
        """Shows frame chooser.
        """

        frame, result = QInputDialog.getInt(self, 'Go to frame…', 'Select frame to view:',
                                            value=self.app_state.current_frame,
                                            minValue=0,
                                            maxValue=self.app_state.base_img.frame_count - 1
                                            )
        if result:
            self.app_state.current_frame = frame

    def screen_capture_dialog(self):
        file_name, filter_name = QFileDialog.getSaveFileName(self, 'Save screenshot')

        def error_callback(error):
            QMessageBox.warning('Error',
                                'The following error has occurred while processing screen capture:\n\n' + error.message)

        if file_name is not None:
            try:
                self.opengl_widget.screen_capture_to_file(file_name, error_callback=error_callback)
                self.update_view()
            except ScreenCapturePendingError:
                QMessageBox.warning(self, "Screenshot failed", "Another screen capture is pending.")

    def update_view(self):
        """Requests update of window output area.
        """
        self.opengl_widget.update()


class ConfigDockWidget(QDockWidget):
    def __init__(self, window, config_widget_class):
        super().__init__()

        self.config_widget = config_widget_class(window)
        self.setWidget(self.config_widget)
        self.setWindowTitle(self.config_widget.title)
