#!/usr/bin/env python3
# coding:utf-8
import time
import deb822
import six

import re
pkg_fields = ['Package', 'Version', 'Architecture', 'Source',
              'Filename', 'Depends', 'Pre-depends', 'Provides', 'MD5sum', 'Size']
pkg_field_pattern = re.compile(r'^(?P<key>' + '|'.join(pkg_fields) + '): (?P<value>.+)',
                               re.M)
pkg_field_pattern = re.compile(r'^(?P<key>[^\s:]*): (?P<value>.+)',
                               re.M)
source_version_pattern = re.compile(r'(.+) \((.+)\)')

import sys
packages = sys.argv[1]

sections = open(packages).read().split('\n\n')

# The key is non-whitespace, non-colon characters before any colon.
key_part = r"^(?P<key>[^: \t\n\r\f\v]+)\s*:\s*"
single = re.compile(key_part + r"(?P<data>\S.*?)\s*$")
multi = re.compile(key_part + r"$")
multidata = re.compile(r"^\s(?P<data>.+?)\s*$")

class NewDeb822(deb822.Deb822):
    def _internal_parser(self,
                         sequence,      # type: IterableDataSourceType
                         fields=None,   # type: Optional[List[str]]
                         strict=None,   # type: Optional[Dict]
                         ):

        def wanted_field(f):
            # type: (str) -> bool
            return fields is None or f in fields

        if isinstance(sequence, (six.string_types, bytes)):
            sequence = sequence.splitlines()

        curkey = None
        content = ""

        for linebytes in self.gpg_stripped_paragraph(
                self._skip_useless_lines(sequence), strict):
            line = self.decoder.decode(linebytes)

            m = single.match(line)
            if m:
                if curkey:
                    self[curkey] = content

                if not wanted_field(m.group('key')):
                    curkey = None
                    continue

                curkey = m.group('key')
                content = m.group('data')
                continue

            m = multi.match(line)
            if m:
                if curkey:
                    self[curkey] = content

                if not wanted_field(m.group('key')):
                    curkey = None
                    continue

                curkey = m.group('key')
                content = ""
                continue

            m = multidata.match(line)
            if m:
                content += '\n' + line   # XXX not m.group('data')?
                continue

        if curkey:
            self[curkey] = content

time0 = time.time()

for text in sections:
    if not text.strip():
        continue
    data = dict(re.findall(pkg_field_pattern, text))
    # print(data['Description'])
    # sys.exit(0)
    if 'Source' in data:
        source = data['Source']
        try:
            # 有的包版本号与源码版本号不一样
            sourcename, sourceversion = re.match(
                source_version_pattern, source).groups()
            data['Source'] = sourcename
            data['SourceVersion'] = sourceversion
        except:
            data['SourceVersion'] = data['Version']
    else:
        data['Source'] = data['Package']
        data['SourceVersion'] = data['Version']

time1 = time.time()

for text in sections:
    if not text.strip():
        continue
    data = deb822.Deb822(text)

time2 = time.time()

for text in sections:
    if not text.strip():
        continue
    data = NewDeb822(text)

time3 = time.time()

print(time1 - time0)
print(time2 - time1)
print(time3 - time2)