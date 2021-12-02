'''
CoffeeScript enum writer

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

class CoffeeEnumWriter(EnumWriter):
    def __init__(self):
        super().__init__()

    def write(self, _w, definition):
        name = definition['name']
        default = definition['default']
        errorval = definition.get('error', -1)
        coffeedef = definition.get('coffee',{})
        valcount = len(definition['values'].keys())

        w = IndentWriter(_w, 
            indent_chars=coffeedef.get('indent_chars', '    '))

        w.writeline('###')
        if 'notes' in definition:
            for line in definition['notes'].split('\n'):
                w.writeline(f'# {line.strip()}')
        w.writeline(f'# @enumdef: {name}')
        w.writeline(f'###')
        with w.writeline(f'export class {name}' if coffeedef.get('export', False) else f'class {name}'):
            w.writeline(f'@_DEFAULT: {default!r}')
            w.writeline(f'@_ERROR: {errorval!r}')

            if definition.get('flags', False):
                w.writeline('@NONE: 0')

            for k, vpak in definition['values'].items():
                v=self._get_value_for(vpak)
                meaning=self._get_meaning_for(vpak)
                if meaning != '':
                    w.writeline('###')
                    w.writeline('# '+meaning.strip())
                    w.writeline('###')
                w.writeline(f'@{k}: {v!r}')

            if definition.get('flags', False):
                w.writeline()
                with w.writeline('@ValueToStrings: (val) ->'):
                    w.writeline('o = []')
                    with w.writeline(f'for bitidx in [0...{valcount}]'):
                        w.writeline('switch (1 << bitidx) & val')
                        written=set()
                        for k, vpak in definition['values'].items():
                            v = self._get_value_for(vpak)
                            if v in written:
                                continue
                            written.add(v)
                            with w.writeline(f'when {v!r}'):
                                w.writeline(f'o.push {v!r}')
                        w.writeline('o')

                w.writeline()
                with w.writeline('@StringsToValue: (valarr) ->'):
                    with w.writeline('o = 0'):
                        with w.writeline('for flagname in valarr'):
                            w.writeline('o |= @StringToValue flagname')
                    w.writeline('o')

            w.writeline()
            with w.writeline('@ValueToString: (val, sep=", ", start_end="") ->'):
                if definition.get('flags', False):
                    w.writeline('o = @ValueToStrings(val).join sep')
                else:
                    w.writeline('o = null')
                    with w.writeline('switch val'):
                        written=set()
                        for k, vpak in definition['values'].items():
                            v=self._get_value_for(vpak)
                            if v in written:
                                continue
                            written.add(v)
                            with w.writeline(f'when {v!r}'):
                                w.writeline(f'o = {k!r}')
                    with w.writeline('if start_end.length == 1'):
                        w.writeline('return start_end + o + start_end')
                    with w.writeline('if start_end.length == 2'):
                        w.writeline('return start_end[0] + o + start_end[1]')
                w.writeline('o')

            w.writeline()
            with w.writeline('@StringToValue: (key) ->'):
                with w.writeline('switch key'):
                    written=set()
                    for k, vpak in definition['values'].items():
                        if k in written:
                            continue
                        written.add(k)
                        v=self._get_value_for(vpak)
                        with w.writeline(f'when {k!r}'):
                            w.writeline(f'return {v!r}')
                w.writeline(f'{errorval!r}')

            w.writeline()
            keys = ', '.join([repr(x) for x in definition['values'].keys()])
            w.writeline(f'@Keys: -> [{keys}]')

            w.writeline()
            values = ', '.join([repr(self._get_value_for(x)) for x in definition['values'].values()])
            w.writeline(f'@Values: -> [{values}]')

            w.writeline()
            w.writeline(f'@Count: -> {valcount}')

            if not definition.get('flags', False):
                vals = [self._get_value_for(x) for x in definition['values'].values()]
                minval = min(vals)
                maxval = max(vals)
                
                w.writeline()
                w.writeline(f'@Min: -> {minval!r}')

                w.writeline()
                w.writeline(f'@Max: -> {maxval!r}')
            else:
                allofem=0
                for x in definition['values'].values():
                    allofem |= self._get_value_for(x)
                w.writeline()
                w.writeline(f'@All: -> {allofem}')
