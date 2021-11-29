from __future__ import annotations
from types import FunctionType
from typing import cast
from cp93pytools.methodtools import cached_property
import inspect
import re


class HelpIndex:
    '''
    @section
        Help and examples
    '''

    @classmethod
    def help_index(cls, show_all=False, silent=False, show_docs=True):
        # Inspect the source code
        src = inspect.getsource(cls)
        D = vars(cls)

        re_sect = r'(?:\n *(@section(?:.|[ \n])+?)(?:\'\'\'|\"\"\"))'
        re_meth = r'(?:def +(.*?\( *self.*?\)):)'
        re_cmeth = r'(?:def +(.*?\( *cls.*?\)):)'
        tokens = re.findall('|'.join((re_meth, re_cmeth, re_sect)), src)

        # Group sections and get docs when available
        sections = []
        methodsOf = {}
        section = '(no section)'
        for f, g, sec in tokens:
            f = f or g
            if f:
                methodsOf[section] = methodsOf.get(section, [])
                name = f[:f.index('(')]

                if name not in D:
                    #print('skipped', name)
                    continue
                func = D[name]
                header = ''

                if isinstance(func, cached_property):
                    header = f'@cached_property\n'
                    func = func._method
                elif isinstance(func, property):
                    header = f'@property\n'
                    func = func.fget
                elif isinstance(func, classmethod):
                    header = f'@classmethod\n'
                    func = func.__func__
                doc = func.__doc__ or ''

                if isinstance(func, FunctionType):
                    sig = inspect.signature(func)
                    full_f = f'{header}def {name}{sig}:'
                else:
                    full_f = f'{header}def {f}:'

                doc = '\n'.join(l.strip() for l in doc.split('\n'))
                methodsOf[section].append((full_f, doc))
            else:
                sections.append((section, methodsOf.get(section, [])))
                section = sec.replace('@section', '').strip()
        sections.append((section, methodsOf.get(section, [])))

        # Write a readable output
        out = []
        for i, (sec, methods) in enumerate(sections):
            out.append(f'\n@section {i}. {sec}\n\n')
            for f, docs in methods:
                underscore = f.startswith(
                    'def _') and not f.startswith('def __')
                if show_all or not underscore or (not underscore and docs):
                    f = '\n'.join(' ' * 4 + s for s in f.split('\n'))
                    docs = '\n'.join(' ' * 8 + s for s in docs.split('\n'))
                    out.append(f'{f}\n')
                    if show_docs:
                        out.append(f'{docs}\n')
                        if docs.strip():
                            out.append('\n')
                    else:
                        out.append('\n')
        out = ''.join(out)

        return (sections, out) if silent else print(out)