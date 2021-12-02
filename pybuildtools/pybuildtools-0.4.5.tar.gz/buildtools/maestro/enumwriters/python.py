'''
BLURB GOES HERE.

Copyright (c) 2015 - 2021 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
from buildtools.indentation import IndentWriter
from .enumwriter import EnumWriter
from typing import Any
class PythonEnumWriter(EnumWriter):
    def _writeStaticConst(self, w: IndentWriter, key: str, value: Any) -> None:
        w.writeline(f'{key} = {value!r}')

    def write(self, _w, definition: dict):
        name = definition['name']
        pydef = definition.get('python',{})
        w = IndentWriter(_w, indent_chars='    ')
        w.writeline('# @generated')
        w.writeline('import enum')
        with w.writeline('class {}({}):'.format(name, pydef.get('extends', 'enum.IntEnum'))):
            if definition.get('flags', False):
                self._writeStaticConst(w, 'NONE', 0)

            if not definition.get('flags', False):
                #if isinstance(self.parent._get_value_for(next(iter(definition['values'].values()))), (int, float)):
                #    self._writeStaticConst(w, 'MIN', min([self.parent._get_value_for(x) for x in definition['values'].values()]))
                #    self._writeStaticConst(w, 'MAX', max([self.parent._get_value_for(x) for x in definition['values'].values()]))
                pass
            else:
                allofem=0
                for x in definition['values'].values():
                    allofem |= self.parent._get_value_for(x)
                w.writeline( "'''")
                w.writeline(f' b{allofem:032b}')
                w.writeline(f'0x{allofem:0X}')
                w.writeline( "'''")
                self._writeStaticConst(w, 'ALL', allofem)

            for k,vpak in definition['values'].items():
                v=self.parent._get_value_for(vpak)
                meaning=self.parent._get_meaning_for(vpak)
                if meaning and len(meaning) > 0:
                    w.writeline( "'''")
                    w.writeline(meaning)
                    w.writeline( "'''")
                self._writeStaticConst(w, k, v)
            if not definition.get('hide-default', False):
                self._writeStaticConst(w, '__default', definition.get('default',0))
