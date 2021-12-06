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

import traceback

import numpy as np
from OpenGL.GL import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtOpenGLWidgets import *

import HyperStackView.transform as transform
from .paths import data_dir
from .shader_util import ExternalFileShader
import HyperStackView.gl_bitmaps as gl_bitmaps

"""All OpenGL-related things.
"""

# Set to true if you want to recompile shaders when their files are changed.
SHADER_AUTO_RELOAD = True

# Maximum resolution of the intermediate buffer. 1024 is sensible value that requires relatively short computation time
# and has low video memory requirements (approx. 4 MiB) while providing good results.
#
# Increased to 2048 to have better results on high-DPI screens or with large window.
MAX_INTERMEDIATE_FBO_RESOLUTION = 2048

#  E───F
# A───B│
# │H──│G
# C───D
cube_vertices = [
    # Front face
    -1.0, -1.0, +1.0, 0.0, 0.0, 1.0, 1 / 3, 0 / 2,  # A
    -1.0, +1.0, +1.0, 0.0, 0.0, 1.0, 1 / 3, 1 / 2,  # C
    +1.0, +1.0, +1.0, 0.0, 0.0, 1.0, 2 / 3, 1 / 2,  # D

    +1.0, +1.0, +1.0, 0.0, 0.0, 1.0, 2 / 3, 1 / 2,  # D
    +1.0, -1.0, +1.0, 0.0, 0.0, 1.0, 2 / 3, 0 / 2,  # B
    -1.0, -1.0, +1.0, 0.0, 0.0, 1.0, 1 / 3, 0 / 2,  # A

    # Back face
    -1.0, -1.0, -1.0, 0.0, 0.0, -1.0, 2 / 3, 2 / 2,  # E
    +1.0, +1.0, -1.0, 0.0, 0.0, -1.0, 3 / 3, 1 / 2,  # G
    -1.0, +1.0, -1.0, 0.0, 0.0, -1.0, 2 / 3, 1 / 2,  # H

    -1.0, -1.0, -1.0, 0.0, 0.0, -1.0, 2 / 3, 2 / 2,  # E
    +1.0, -1.0, -1.0, 0.0, 0.0, -1.0, 3 / 3, 2 / 2,  # F
    +1.0, +1.0, -1.0, 0.0, 0.0, -1.0, 3 / 3, 1 / 2,  # G

    # Right face
    +1.0, -1.0, +1.0, 1.0, 0.0, 0.0, 2 / 3, 1 / 2,  # B
    +1.0, +1.0, +1.0, 1.0, 0.0, 0.0, 2 / 3, 0 / 2,  # D
    +1.0, +1.0, -1.0, 1.0, 0.0, 0.0, 3 / 3, 0 / 2,  # G

    +1.0, +1.0, -1.0, 1.0, 0.0, 0.0, 3 / 3, 0 / 2,  # G
    +1.0, -1.0, -1.0, 1.0, 0.0, 0.0, 3 / 3, 1 / 2,  # F
    +1.0, -1.0, +1.0, 1.0, 0.0, 0.0, 2 / 3, 1 / 2,  # B

    # Left face
    -1.0, -1.0, +1.0, -1.0, 0.0, 0.0, 1 / 3, 1 / 2,  # A
    -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 0 / 3, 1 / 2,  # E
    -1.0, +1.0, -1.0, -1.0, 0.0, 0.0, 0 / 3, 0 / 2,  # H

    -1.0, +1.0, +1.0, -1.0, 0.0, 0.0, 1 / 3, 0 / 2,  # C
    -1.0, -1.0, +1.0, -1.0, 0.0, 0.0, 1 / 3, 1 / 2,  # A
    -1.0, +1.0, -1.0, -1.0, 0.0, 0.0, 0 / 3, 0 / 2,  # H

    # Top face
    -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0 / 3, 1 / 2,  # E
    -1.0, -1.0, +1.0, 0.0, -1.0, 0.0, 0 / 3, 2 / 2,  # A
    +1.0, -1.0, +1.0, 0.0, -1.0, 0.0, 1 / 3, 2 / 2,  # B

    +1.0, -1.0, +1.0, 0.0, -1.0, 0.0, 1 / 3, 2 / 2,  # B
    +1.0, -1.0, -1.0, 0.0, -1.0, 0.0, 1 / 3, 1 / 2,  # F
    -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0 / 3, 1 / 2,  # E

    # Bottom face
    +1.0, +1.0, +1.0, 0.0, 1.0, 0.0, 2 / 3, 1 / 2,  # D
    -1.0, +1.0, +1.0, 0.0, 1.0, 0.0, 1 / 3, 1 / 2,  # C
    +1.0, +1.0, -1.0, 0.0, 1.0, 0.0, 2 / 3, 2 / 2,  # G

    -1.0, +1.0, +1.0, 0.0, 1.0, 0.0, 1 / 3, 1 / 2,  # C
    -1.0, +1.0, -1.0, 0.0, 1.0, 0.0, 1 / 3, 2 / 2,  # H
    +1.0, +1.0, -1.0, 0.0, 1.0, 0.0, 2 / 3, 2 / 2,  # G
]


def _clear(depth=False, color=False):
    """Invokes ``Clear`` OpenGL call to call the depth and/or color buffer.

    Selection fo buffers to clear is done using function parameters. Note that *the default is to clear nothing*.
    """
    glClear(
        (GL_DEPTH_BUFFER_BIT if depth else 0)
        |
        (GL_COLOR_BUFFER_BIT if color else 0)
    )


def _depth_test(state):
    """Sets ``DEPTH_TEST`` OpenGL parameter.
    """

    if state:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)


def _blending(state):
    """Sets ``BLEND`` OpenGL parameter.
    """

    if state:
        glEnable(GL_BLEND)
    else:
        glDisable(GL_BLEND)


class GlOperations:
    """Provides whole rendering pipeline of the HyperStackView.
    """

    def __init__(self, app_state):
        self.app_state = app_state

        self.aspect_ratio = 1.0

        self.flatten_shader = None
        self.final_shader = None
        self.cube_shader = None
        self.bg_cube_shader = None
        self.grid_shader = None
        self.projection_plane_indicator_shader = None

        self.texture = None
        self.texture_binary = None
        self.grid_texture = None
        self.cube_texture = None

        self.last_base_img = None
        self.last_base_t = None
        self.last_binary_img = None
        self.base_img_buf = None

        self.screen_to_texture_matrix = None
        self.rotation_matrix = None
        self.model_matrix = None
        self.osd_matrix = None

        self.window_fbo = None  # not always 0
        self.intermediate_fbo = None
        self.intermediate_max_tex = None
        self.intermediate_sum_tex = None
        self.intermediate_nbz_tex = None

        self.window_width = 0
        self.window_height = 0

        self._screen_capture_image = None
        self._screen_capture_callback = None

    def request_screen_capture(self, callback):
        if self.screen_capture_pending():
            raise ScreenCapturePendingError()

        self._screen_capture_callback = callback

    def disable_screen_capture(self):
        self._screen_capture_callback = None

    def screen_capture_pending(self):
        return self._screen_capture_callback is not None

    def initialize(self):
        """This method should be called exactly once on thread with active OpenGL context before all drawing calls."""

        #
        # Load all shaders
        #

        self.flatten_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "flatten_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "flatten_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        self.final_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "final_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "final_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        self.cube_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "cube_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "cube_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        self.bg_cube_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "bg_cube_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "bg_cube_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        self.grid_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "grid_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "grid_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        self.projection_plane_indicator_shader = ExternalFileShader({
            GL_VERTEX_SHADER: data_dir / "projection_plane_indicator_v.glsl",
            GL_FRAGMENT_SHADER: data_dir / "projection_plane_indicator_f.glsl",
        }, auto_reload=SHADER_AUTO_RELOAD)

        #
        # Provide initial configuration of the OpenGL context.
        #

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_TEXTURE_3D)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive blending
        glClearColor(0.0, 0.0, 0.0, 1.0)  # black

        #
        # Allocate texture objects for input data
        #

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.texture)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterfv(GL_TEXTURE_3D, GL_TEXTURE_BORDER_COLOR, [0.0, 0.0, 0.0, 1.0])
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)

        self.texture_binary = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.texture_binary)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterfv(GL_TEXTURE_3D, GL_TEXTURE_BORDER_COLOR, [0.0, 0.0, 0.0, 1.0])
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER)

        #
        # Allocate texture objects for visual elements and load them from files.
        #

        self.grid_texture = glGenTextures(1)
        flat_grid = gl_bitmaps.grid.reshape([-1])
        glBindTexture(GL_TEXTURE_2D, self.grid_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [0.0, 0.0, 0.0, 1.0])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, gl_bitmaps.grid.shape[1], gl_bitmaps.grid.shape[0], 0, GL_RGBA,
                     GL_FLOAT, flat_grid)

        self.cube_texture = glGenTextures(1)
        flat_cube = gl_bitmaps.cube.reshape([-1])
        glBindTexture(GL_TEXTURE_2D, self.cube_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [0.0, 0.0, 0.0, 1.0])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, gl_bitmaps.cube.shape[1], gl_bitmaps.cube.shape[0], 0, GL_RGBA,
                     GL_FLOAT, flat_cube)

        #
        # Initialize intermediate framebuffer.
        #

        self.intermediate_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.intermediate_fbo)
        self.intermediate_max_tex, self.intermediate_sum_tex, self.intermediate_nbz_tex = glGenTextures(3)
        for tex in [self.intermediate_max_tex, self.intermediate_sum_tex, self.intermediate_nbz_tex]:
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, MAX_INTERMEDIATE_FBO_RESOLUTION, MAX_INTERMEDIATE_FBO_RESOLUTION, 0,
                         GL_RED, GL_FLOAT, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.intermediate_max_tex, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, self.intermediate_sum_tex, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT2, GL_TEXTURE_2D, self.intermediate_nbz_tex, 0)
        assert glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE
        glDrawBuffers([GL_COLOR_ATTACHMENT0 + n for n in range(0, 4)])
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def paint(self):
        """Renders whole scene.
        """

        self._compute_matrices()

        _blending(True)

        # Get current framebuffer
        #
        # When Qt is rendering with OpenGL, rendering to default framebuffer could do funny things (like rendering to
        # wrong place).
        self.window_fbo = glGetInteger(GL_FRAMEBUFFER_BINDING)

        # Get real viewport size
        self.window_width, self.window_height = glGetIntegerv(GL_VIEWPORT)[2:]

        # Compute values for further steps
        self._paint_intermediate_fbo()

        # Make the screen empty
        _clear(depth=True, color=True)

        # Draw OSD behind the image
        _depth_test(False)
        if self.app_state.z_samples != 1:
            if self.app_state.show_bg_cube:
                self._draw_background_cube()
            if self.app_state.show_grid:
                self._draw_grid()

        # Take intermediate image and render it
        _depth_test(False)
        self._draw_final_image()

        # Draw overlays
        _depth_test(True)
        _clear(depth=True)  # We are starting new layer
        if self.app_state.show_rotation_osd:
            _blending(False)
            self._draw_osd_cube()
            _blending(True)
            if self.app_state.show_rotation_osd_bounds:
                self._draw_projection_plane_indicator()

        # Perform screen capture if requested to do so
        if self.screen_capture_pending():
            self._screen_capture_image = glReadPixels(0, 0, self.window_width, self.window_height, GL_RGB,
                                                      GL_UNSIGNED_BYTE)
            self._screen_capture_callback(self, self._screen_capture_image)

    def _paint_intermediate_fbo(self):
        """Renders intermediate stage of data rendering.
        """

        try:
            assert glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE
            glViewport(0, 0, self.app_state.intermediate_resolution, self.app_state.intermediate_resolution)
            glBindFramebuffer(GL_FRAMEBUFFER, self.intermediate_fbo)

            _clear(color=True)

            _blending(False)
            self._perform_flattening()
            _blending(True)
        finally:
            glBindFramebuffer(GL_FRAMEBUFFER, self.window_fbo)
            glViewport(0, 0, self.window_width, self.window_height)

    def _draw_osd_cube(self):
        """Draws rotation preview cube.
        """

        self.cube_shader.use()

        matrix = self.osd_matrix
        if self.app_state.z_samples == 1 or not self.app_state.clip_rotation_osd:
            matrix = matrix.scale([1, 1, .0001])

        glBindTexture(GL_TEXTURE_2D, self.cube_texture)

        glVertexAttribPointer(self.cube_shader.attrib.aPos, 3, GL_FLOAT, GL_FALSE, 32, cube_vertices)
        glVertexAttribPointer(self.cube_shader.attrib.aNormal, 3, GL_FLOAT, GL_FALSE, 32, cube_vertices[3:])
        glVertexAttribPointer(self.cube_shader.attrib.aTexCoord, 2, GL_FLOAT, GL_FALSE, 32, cube_vertices[6:])
        glEnableVertexAttribArray(self.cube_shader.attrib.aPos)
        glEnableVertexAttribArray(self.cube_shader.attrib.aNormal)
        glEnableVertexAttribArray(self.cube_shader.attrib.aTexCoord)
        glUniformMatrix4fv(self.cube_shader.uniform.uM, 1, GL_FALSE, matrix)
        glUniformMatrix4fv(self.cube_shader.uniform.uMRotate, 1, GL_FALSE, self.rotation_matrix)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDisableVertexAttribArray(self.cube_shader.attrib.aPos)
        glDisableVertexAttribArray(self.cube_shader.attrib.aNormal)
        glDisableVertexAttribArray(self.cube_shader.attrib.aTexCoord)

    def _draw_background_cube(self):
        """Draws cube backdrop.
        """

        self.bg_cube_shader.use()

        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)

        glVertexAttribPointer(self.bg_cube_shader.attrib.aPos, 3, GL_FLOAT, GL_FALSE, 32, cube_vertices)
        glVertexAttribPointer(self.bg_cube_shader.attrib.aNormal, 3, GL_FLOAT, GL_FALSE, 32, cube_vertices[3:])
        glEnableVertexAttribArray(self.bg_cube_shader.attrib.aPos)
        glEnableVertexAttribArray(self.bg_cube_shader.attrib.aNormal)
        glUniformMatrix4fv(self.bg_cube_shader.uniform.uM, 1, GL_FALSE, self.model_matrix)
        glUniformMatrix4fv(self.bg_cube_shader.uniform.uMRotate, 1, GL_FALSE, self.rotation_matrix)
        glUniform1f(self.bg_cube_shader.uniform.uBrightness, self.app_state.bg_cube_alpha)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDisableVertexAttribArray(self.bg_cube_shader.attrib.aPos)
        glDisableVertexAttribArray(self.bg_cube_shader.attrib.aNormal)

        glCullFace(GL_BACK)
        glDisable(GL_CULL_FACE)

    def _draw_projection_plane_indicator(self):
        """Draws projection plane visualisation onto rotation preview cube (``see _draw_osd_cube``).
        """

        self.projection_plane_indicator_shader.use()

        vertices = [
            0.0, 0.0,
            0.0, 1.0,
            1.0, 0.0,

            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,
        ]

        glVertexAttribPointer(self.projection_plane_indicator_shader.attrib.aPos, 2, GL_FLOAT, GL_FALSE, 8, vertices)
        glEnableVertexAttribArray(self.projection_plane_indicator_shader.attrib.aPos)
        glUniformMatrix4fv(self.projection_plane_indicator_shader.uniform.uM, 1, GL_FALSE,
                           self.osd_projection_plane_indicator_matrix)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glDisableVertexAttribArray(self.projection_plane_indicator_shader.attrib.aPos)

    def _draw_grid(self):
        """Draws background grid.
        """

        self.grid_shader.use()

        vertices = [
            0.0, 0.0,
            0.0, 1.0,
            1.0, 0.0,
            1.0, 1.0,
        ]

        glBindTexture(GL_TEXTURE_2D, self.grid_texture)

        glVertexAttribPointer(self.grid_shader.attrib.aPos, 2, GL_FLOAT, GL_FALSE, 8, vertices)
        glEnableVertexAttribArray(self.grid_shader.attrib.aPos)
        glUniformMatrix4fv(self.grid_shader.uniform.uM, 1, GL_FALSE, self.model_matrix)
        glUniform1f(self.grid_shader.uniform.uBrightness, self.app_state.grid_alpha)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glDisableVertexAttribArray(self.grid_shader.attrib.aPos)

    def _perform_flattening(self):
        """Performs the first stage of rendering.
        """

        self.flatten_shader.use()

        glClear(GL_DEPTH_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_3D, self.texture)
        if self.app_state.base_img is not None and self.app_state.base_img.current_frame is not None:
            if self.last_base_img is not self.app_state.base_img or self.last_base_t is not self.app_state.base_img.t:
                glTexImage3D(GL_TEXTURE_3D, 0, GL_R16_SNORM, self.app_state.base_img.current_frame.shape[2],
                             self.app_state.base_img.current_frame.shape[1],
                             self.app_state.base_img.current_frame.shape[0],
                             0, GL_RED, GL_UNSIGNED_SHORT, self.app_state.base_img.current_frame.astype('uint16'))

                self.last_base_img = self.app_state.base_img
                self.last_base_t = self.app_state.base_img.t
        else:
            glTexImage3D(GL_TEXTURE_3D, 0, GL_R16_SNORM, 16, 256, 256, 0, GL_RED, GL_UNSIGNED_SHORT,
                         np.zeros(16 * 256 * 256))
            self.last_base_img = None

        glBindTexture(GL_TEXTURE_3D, self.texture_binary)
        if self.app_state.binary_img is not None and self.app_state.binary_img.current_frame is not None:
            if self.last_binary_img is not self.app_state.binary_img or self.last_base_t is not self.app_state.base_img.t:
                glTexImage3D(GL_TEXTURE_3D, 0, GL_R16UI, self.app_state.binary_img.current_frame.shape[2],
                             self.app_state.binary_img.current_frame.shape[1],
                             self.app_state.binary_img.current_frame.shape[0],
                             0, GL_RED_INTEGER, GL_UNSIGNED_SHORT,
                             self.app_state.binary_img.current_frame.astype('uint16'))
        else:
            glTexImage3D(GL_TEXTURE_3D, 0, GL_R16UI, 16, 256, 256, 0, GL_RED_INTEGER, GL_UNSIGNED_SHORT,
                         np.zeros(16 * 256 * 256))
            self.last_binary_img = None

        vertices = [
            0.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,

            1.0, 1.0,
            1.0, 0.0,
            0.0, 0.0,
        ]

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_3D, self.texture_binary)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_3D, self.texture)

        glVertexAttribPointer(self.flatten_shader.attrib.aScreenCoord, 2, GL_FLOAT, GL_FALSE, 8, vertices)
        glEnableVertexAttribArray(self.flatten_shader.attrib.aScreenCoord)
        glUniformMatrix4fv(self.flatten_shader.uniform.uM, 1, GL_FALSE, self.screen_to_texture_matrix)
        glUniform1f(self.flatten_shader.uniform.uNear, self.app_state.near_plane_screen_z)
        glUniform1f(self.flatten_shader.uniform.uFar, self.app_state.far_plane_screen_z)
        glUniform1i(self.flatten_shader.uniform.uZSamples, self.app_state.z_samples)
        glUniform1f(self.flatten_shader.uniform.uInputOffset, -self.app_state.input_min / 65535)
        glUniform1f(self.flatten_shader.uniform.uInputMultiplier,
                    65535 / max(self.app_state.input_max - self.app_state.input_min, 1))
        glUniform1i(self.flatten_shader.uniform.tTex, 1)
        glUniform1i(self.flatten_shader.uniform.tBinary, 0)

        glUniform1i(self.flatten_shader.uniform.uObjectFilter, self.app_state.mask_object)
        object_filter_mode = 0
        if self.app_state.mask_enabled:
            if self.app_state.mask_mode == 'filter':
                object_filter_mode = 1
            elif self.app_state.mask_mode == 'highlight':
                if not self.app_state.mask_highlight_blink or self.app_state.mask_highlight_blink_state:
                    object_filter_mode = 2
        glUniform1i(self.flatten_shader.uniform.uObjectFilterMode, object_filter_mode)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glDisableVertexAttribArray(self.flatten_shader.attrib.aScreenCoord)

        glActiveTexture(GL_TEXTURE0)

    def _draw_final_image(self):
        """Draws flattened image (see ``_perform_flattening``) on the screen.
        """

        self.final_shader.use()

        glClear(GL_DEPTH_BUFFER_BIT)

        vertices = [
            0.0, 0.0,
            0.0, 1.0,
            1.0, 1.0,

            1.0, 1.0,
            1.0, 0.0,
            0.0, 0.0,
        ]

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.intermediate_max_tex)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.intermediate_sum_tex)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.intermediate_nbz_tex)

        glVertexAttribPointer(self.final_shader.attrib.aScreenCoord, 2, GL_FLOAT, GL_FALSE, 8, vertices)
        glEnableVertexAttribArray(self.final_shader.attrib.aScreenCoord)
        glUniform1f(self.final_shader.uniform.scale,
                    MAX_INTERMEDIATE_FBO_RESOLUTION / self.app_state.intermediate_resolution)
        glUniform1i(self.final_shader.uniform.tMax, 0)
        glUniform1i(self.final_shader.uniform.tSum, 1)
        glUniform1i(self.final_shader.uniform.tNbz, 2)
        glUniform1f(self.final_shader.uniform.sampleSz,
                    (self.app_state.near_plane_screen_z - self.app_state.far_plane_screen_z) / self.app_state.z_samples)
        glUniform1f(self.final_shader.uniform.brightnessMax,
                    self.app_state.max_enabled and self.app_state.max_brightness)
        glUniform1f(self.final_shader.uniform.contrastMax, self.app_state.max_enabled and self.app_state.max_contrast)
        glUniform1f(self.final_shader.uniform.gammaMax, self.app_state.max_gamma)
        glUniform1f(self.final_shader.uniform.brightnessAvg,
                    self.app_state.avg_enabled and self.app_state.avg_brightness)
        glUniform1f(self.final_shader.uniform.contrastAvg, self.app_state.avg_enabled and self.app_state.avg_contrast)
        glUniform1f(self.final_shader.uniform.gammaAvg, self.app_state.avg_gamma)
        glUniform3fv(self.final_shader.uniform.colorMax, 1, self.app_state.max_color)
        glUniform3fv(self.final_shader.uniform.colorAvg, 1, self.app_state.avg_color)
        if self.app_state.mask_enabled and self.app_state.mask_mode == 'highlight':
            if not self.app_state.mask_highlight_blink or self.app_state.mask_highlight_blink_state:
                glUniform3fv(self.final_shader.uniform.binaryObjectColor, 1, self.app_state.mask_highlight_color)
                glUniform1f(self.final_shader.uniform.binarySmoothness,
                            self.app_state.binary_smoothness * self.app_state.scale)
                glUniform1f(self.final_shader.uniform.binarySampleSize, self.app_state.binary_sample_size)
                glUniform1f(self.final_shader.uniform.binaryContrast, self.app_state.binary_contrast)
                glUniform1i(self.final_shader.uniform.binaryEnabled, True)
            else:
                glUniform1i(self.final_shader.uniform.binaryEnabled, False)
        else:
            glUniform3fv(self.final_shader.uniform.binaryObjectColor, 1, self.app_state.binary_object_color)
            glUniform1f(self.final_shader.uniform.binarySmoothness,
                        self.app_state.binary_smoothness * self.app_state.scale)
            glUniform1f(self.final_shader.uniform.binarySampleSize, self.app_state.binary_sample_size)
            glUniform1f(self.final_shader.uniform.binaryContrast, self.app_state.binary_contrast)
            glUniform1i(self.final_shader.uniform.binaryEnabled, self.app_state.binary_enabled)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glDisableVertexAttribArray(self.flatten_shader.attrib.aScreenCoord)

        glActiveTexture(GL_TEXTURE0)

    def _compute_matrices(self):
        """Computes all transformation matrices that are used in drawing methods. Invoked by ``_paint``.
        """

        # The perspective transform factor below is Multiplied by 4 to compensate other transforms
        # (such as screen_to_texture etc.).
        self.screen_to_texture_matrix = transform.identity() \
            .screen_to_texture() \
            .translate([-.75, -.75, -.75]) \
            .scale([1 / self.aspect_ratio, 1, 1]) \
            .perspective(self.app_state.perspective * 4) \
            .scale(1 / self.app_state.scale) \
            .rotate_about((1, 0, 0), self.app_state.rotation[0]) \
            .rotate_about((0, 1, 0), self.app_state.rotation[1]) \
            .rotate_about((0, 0, 1), self.app_state.rotation[2]) \
            .scale([1, -1, -1]) \
            .translate([.75, .75, .75]) \
            .texture_to_screen()

        self.rotation_matrix = transform.identity() \
            .rotate_about((0, 0, -1), self.app_state.rotation[2]) \
            .rotate_about((0, 1, 0), self.app_state.rotation[1]) \
            .rotate_about((1, 0, 0), self.app_state.rotation[0])

        self.model_matrix = self.rotation_matrix \
            .scale(self.app_state.scale) \
            .perspective(self.app_state.perspective) \
            .scale([1, 1, -1]) \
            .translate([0, 0, 1]) \
            .scale([1, 1, .5]) \
            .map_z_range(self.app_state.near_plane_screen_z, self.app_state.far_plane_screen_z, -1, 1) \
            .scale([self.aspect_ratio, 1, 1])

        self.model_matrix_without_scale = self.model_matrix \
            .scale([1 / self.app_state.scale, 1 / self.app_state.scale, 1])

        self.osd_position_matrix = transform.identity() \
            .scale([.1, .1, 1]) \
            .translate([-.75, .75, 0])

        self.osd_matrix = self.osd_position_matrix.apply_to(self.model_matrix_without_scale)

        self.osd_projection_plane_indicator_matrix = \
            transform.identity() \
                .scale(2) \
                .translate([-1, -1, 0]) \
                .scale(1 / self.app_state.scale) \
                .drop_axis(2) \
                .translate([0, 0, -1]) \
                .concat(self.osd_position_matrix)

    def screen_capture_to_file(self, file_name, error_callback=None, success_callback=None):
        def cb(self2, pixels):
            self.disable_screen_capture()

            success = False
            try:
                import png

                # Convert from bytes if necessary (PyOpenGL does some conversions for us)
                if type(pixels) == bytes:
                    pixels = np.frombuffer(pixels, dtype=np.uint8).reshape(self.window_width, self.window_height, 3)

                # Convert OpenGL pixel order to PyPNG pixel order
                pixels = np.flip(pixels.reshape([pixels.shape[1], pixels.shape[0] * 3]), 0)

                # Save the image
                png.from_array(pixels, mode='RGB').save(file_name)

                success = True
            except Error as e:
                traceback.print_exc()

                if error_callback is not None:
                    error_callback(e)

            if success:
                if success_callback is not None:
                    success_callback()

        self.request_screen_capture(cb)


class HyperStackView(QOpenGLWidget, GlOperations):
    """Qt Widget providing the HyperStackView rendering functionality.
    """

    back_pressed = Signal()
    forward_pressed = Signal()
    set_default_rotation_triggered = Signal()

    def __init__(self, app_state, *args, **kwargs):
        QOpenGLWidget.__init__(self, *args, **kwargs)
        GlOperations.__init__(self, app_state)

        self._previous_mouse_x = 0
        self._previous_mouse_y = 0
        self._last_mouse_button = None

        self.mouse_scale_sensitivity = .01

        self.set_default_cursor()

    def initializeGL(self):
        GlOperations.initialize(self)

    def resizeGL(self, width, height):
        self.aspect_ratio = height / width

    def paintGL(self):
        GlOperations.paint(self)

    def wheelEvent(self, event):
        base = .15  # Scale delta of 15° wheel rotation.
        steps = event.angleDelta().y() / (15 * 8)
        factor = base * steps
        print(f"Scroll of {steps} steps, the scale change is {factor}")
        self.app_state.scale += factor

    def mousePressEvent(self, event):
        mouse_pos = QCursor.pos()
        self._previous_mouse_x = mouse_pos.x()
        self._previous_mouse_y = mouse_pos.y()
        self._last_mouse_button = event.button()

        if self._last_mouse_button == Qt.MouseButton.BackButton:
            self.back_pressed.emit()
        elif self._last_mouse_button == Qt.MouseButton.ForwardButton:
            self.forward_pressed.emit()

    def mouseMoveEvent(self, event):
        mouse_pos = QCursor.pos()
        x_delta = self._previous_mouse_x - mouse_pos.x()
        y_delta = self._previous_mouse_y - mouse_pos.y()

        if self._last_mouse_button == Qt.MouseButton.LeftButton:
            self._mouse_rotate(x_delta, y_delta)
        elif self._last_mouse_button == Qt.MouseButton.MiddleButton:
            self._mouse_scale(y_delta)

        # Try to keep the mouse in the place.
        QCursor.setPos(self._previous_mouse_x, self._previous_mouse_y)

        # Get new mouse position and update the vars.
        mouse_pos = QCursor.pos()
        self._previous_mouse_x = mouse_pos.x()
        self._previous_mouse_y = mouse_pos.y()

        # Hide the cursor.
        cursor_pixmap = QPixmap(1, 1)
        cursor_pixmap.fill(QColor.fromRgba(0x0))
        self.setCursor(QCursor(cursor_pixmap))

    def mouseReleaseEvent(self, event):
        self.set_default_cursor()

    def _mouse_rotate(self, x_delta, y_delta):
        new_x = self.app_state.rotation[0] + np.arctan(y_delta / self.height() * 2)
        direction = 1 if new_x < 0 else -1
        self.app_state.rotation = [
            new_x,
            self.app_state.rotation[1],
            self.app_state.rotation[2] - direction * np.arctan(x_delta / self.width() * 2),
        ]

    def _mouse_scale(self, y_delta):
        self.app_state.scale += y_delta * self.mouse_scale_sensitivity

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_default_rotation_triggered.emit()

    def set_default_cursor(self):
        self.setCursor(QCursor(Qt.OpenHandCursor))


class ScreenCapturePendingError(Error):
    def __init__(self):
        super().__init__("screen capture is pending")
