#!/usr/bin/env python3

# Libervia: a Salut à Toi frontend
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Script launching Libervia server"""

from sat.core import launcher
from libervia.server.constants import Const as C


class Launcher(launcher.Launcher):
    APP_NAME=C.APP_NAME
    APP_NAME_FILE=C.APP_NAME_FILE


if __name__ == '__main__':
    Launcher.run()
