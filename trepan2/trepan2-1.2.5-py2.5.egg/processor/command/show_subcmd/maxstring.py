# -*- coding: utf-8 -*-
#   Copyright (C) 2009-2010, 2012, 2015 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

# Our local modules
from trepan.processor.command import base_subcmd as Mbase_subcmd


class ShowMaxString(Mbase_subcmd.DebuggerShowIntSubcommand):
    """**show maxstring***

Show maximum string length to use in string-oriented output

See also:
--------

`set maxstring`"""
    min_abbrev = len('maxs')
    short_help = 'Show max string length printed'
    pass
