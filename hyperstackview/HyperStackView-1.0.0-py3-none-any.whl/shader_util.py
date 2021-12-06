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

import io

from OpenGL.GL import *
from OpenGL.GL import __dict__ as gl_functions
from PySide6.QtCore import *

"""Various OpenGL shader loading and compilation utilities.
"""

class BasicShaderProgram:
    """Represents OpenGL shader program and provides methods for compilation and linking.
    """

    def __init__(self):
        self.program_id = glCreateProgram()

        self.attrib = _CachingLocator(self, "Attrib")
        self.uniform = _CachingLocator(self, "Uniform")

        self.shaders = []

    def add_shader(self, source, type):
        shader_id = glCreateShader(type)
        glShaderSource(shader_id, [source])
        glCompileShader(shader_id)
        glAttachShader(self.program_id, shader_id)
        self.shaders.append(shader_id)

    def add_shader_from_file(self, file_path, type):
        with io.open(file_path, 'r') as file:
            source = file.read()

            self.add_shader(source, type)

    def link(self):
        glLinkProgram(self.program_id)

    def use(self):
        glUseProgram(self.program_id)

    def delete(self):
        for shader_id in self.shaders:
            glDeleteShader(shader_id)

        glDeleteProgram(self.program_id)

    def swap(self, new_program):
        """Replaces this shader program with the new_program.

        Values from the new_program will be moved to this shader program. The new_program object should not be used
        anymore.
        """

        self.delete()

        self.program_id = new_program.program_id
        self.shaders = new_program.shaders

        # Clear location caches
        self.attrib.clear_cache()
        self.uniform.clear_cache()


class _CachingLocator:
    """Provides cached interface for retrieving OpenGL shader variables.
    """

    def __init__(self, shader_program, pointer_type):
        self._cache = {}
        self.shader_program = shader_program
        self.pointer_type = pointer_type

    def __getattr__(self, name):
        method = gl_functions[f'glGet{self.pointer_type}Location']
        assert (method is not None)

        if name in self._cache:
            return self._cache[name]

        location = method(self.shader_program.program_id, name)
        self._cache[name] = location
        return location

    def __hasattr__(self, name):
        return getattr(self, name) != -1

    def clear_cache(self):
        self._cache = {}


class ExternalFileShader(BasicShaderProgram):
    """``BasicShaderProgram`` that is loaded from file and can be optinoally reloaded and recompiled of file
    modification."""

    def __init__(self, shader_paths, auto_reload=False):
        BasicShaderProgram.__init__(self)

        self.shader_paths = shader_paths
        self._needs_reload = False

        def mark_reload(_):
            self._needs_reload = True

        if auto_reload:
            self._watcher = QFileSystemWatcher([self.shader_paths[t] for t in self.shader_paths])
            self._watcher.fileChanged.connect(mark_reload)
        else:
            self._watcher = None

        self.compile_files()

    def compile_files(self):
        for shader_type, path in dict(self.shader_paths).items():
            self.add_shader_from_file(path, shader_type)
        self.link()

    def use(self):
        if self._needs_reload:
            new_shader_program = ExternalFileShader(self.shader_paths, auto_reload=False)
            self.swap(new_shader_program)

            self._needs_reload = False

        super().use()
