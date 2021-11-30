# -*- coding: utf-8 -*-

import itertools
import types
import base64
import json
import zlib
import io
import gzip
import re
from collections import OrderedDict
from hashlib import md5

from fast_tracker.packages import six
from fast_tracker.common.utils import seq_id

HEXDIGLC_RE = re.compile('^[0-9a-f]+$')
DELIMITER_FORMAT_RE = re.compile('[ \t]*,[ \t]*')
PARENT_TYPE = {
    '0': 'App',
    '1': 'Browser',
    '2': 'Mobile',
}


def json_encode(obj, **kwargs):
    _kwargs = {}


    if type(b'') is type(''):  # NOQA
        _kwargs['encoding'] = 'latin-1'

    def _encode(o):
        if isinstance(o, bytes):
            return o.decode('latin-1')
        elif isinstance(o, types.GeneratorType):
            return list(o)
        elif hasattr(o, '__iter__'):
            return list(iter(o))
        raise TypeError(repr(o) + ' is not JSON serializable')

    _kwargs['default'] = _encode

    _kwargs['separators'] = (',', ':')

    _kwargs.update(kwargs)

    return json.dumps(obj, **_kwargs)


def json_decode(s, **kwargs):
    return json.loads(s, **kwargs)


def xor_cipher_genkey(key, length=None):

    return bytearray(key[:length], encoding='ascii')


def xor_cipher_encrypt(text, key):

    return bytearray([ord(c) ^ key[i % len(key)] for i, c in enumerate(text)])


def xor_cipher_decrypt(text, key):

    return bytearray([c ^ key[i % len(key)] for i, c in enumerate(text)])


def xor_cipher_encrypt_base64(text, key):

    if not isinstance(key, bytearray):
        key = xor_cipher_genkey(key)

    if isinstance(text, bytes):
        text = text.decode('latin-1')
    text = text.encode('utf-8').decode('latin-1')

    result = base64.b64encode(bytes(xor_cipher_encrypt(text, key)))

    if six.PY3:
        return result.decode('ascii')

    return result


def xor_cipher_decrypt_base64(text, key):

    if not isinstance(key, bytearray):
        key = xor_cipher_genkey(key)

    result = xor_cipher_decrypt(bytearray(base64.b64decode(text)), key)

    return bytes(result).decode('utf-8')


obfuscate = xor_cipher_encrypt_base64
deobfuscate = xor_cipher_decrypt_base64


def unpack_field(field):

    if not isinstance(field, bytes):
        field = field.encode('UTF-8')

    data = base64.decodestring(field)
    data = zlib.decompress(data)

    if isinstance(data, bytes):
        data = data.decode('Latin-1')

    data = json_decode(data)
    return data


def generate_path_hash(name, seed):

    rotated = ((seed << 1) | (seed >> 31)) & 0xffffffff

    if not isinstance(name, bytes):
        name = name.encode('UTF-8')

    path_hash = (rotated ^ int(md5(name).hexdigest()[-8:], base=16))
    return '%08x' % path_hash


def base64_encode(text):

    if isinstance(text, bytes):
        text = text.decode('latin-1')
    text = text.encode('utf-8').decode('latin-1')

    result = base64.b64encode(text.encode('utf-8'))

    if six.PY3:
        return result.decode('ascii')

    return result


def base64_decode(text):

    return base64.b64decode(text).decode('utf-8')


def gzip_compress(text):

    compressed_data = io.BytesIO()

    if six.PY3 and isinstance(text, str):
        text = text.encode('utf-8')

    with gzip.GzipFile(fileobj=compressed_data, mode='wb') as f:
        f.write(text)

    return compressed_data.getvalue()


def gzip_decompress(payload):

    data_bytes = io.BytesIO(payload)
    decoded_data = gzip.GzipFile(fileobj=data_bytes).read()
    return decoded_data.decode('utf-8')


def serverless_payload_encode(payload):

    json_encode_data = json_encode(payload)
    compressed_data = gzip_compress(json_encode_data)
    encoded_data = base64.b64encode(compressed_data)

    return encoded_data


def ensure_str(s):
    if not isinstance(s, six.string_types):
        try:
            s = s.decode('utf-8')
        except Exception:
            return
    return s


def serverless_payload_decode(text):

    if hasattr(text, 'decode'):
        text = text.decode('utf-8')

    decoded_bytes = base64.b64decode(text)
    uncompressed_data = gzip_decompress(decoded_bytes)

    data = json_decode(uncompressed_data)
    return data


def decode_fast_header(encoded_header, encoding_key):
    decoded_header = None
    if encoded_header:
        try:
            decoded_header = json_decode(deobfuscate(
                    encoded_header, encoding_key))
        except Exception:
            pass

    return decoded_header


def convert_to_cat_metadata_value(nr_headers):
    if not nr_headers:
        return None

    payload = json_encode(nr_headers)
    cat_linking_value = base64_encode(payload)
    return cat_linking_value


class DistributedTracePayload(dict):

    version = (0, 1)

    def text(self):
        return json_encode(self)

    @classmethod
    def from_text(cls, value):
        d = json_decode(value)
        return cls(d)

    def http_safe(self):
        return base64_encode(self.text())

    @classmethod
    def from_http_safe(cls, value):
        text = base64_decode(value)
        return cls.from_text(text)

    @classmethod
    def decode(cls, payload):
        if isinstance(payload, dict):
            return cls(payload)

        decoders = (cls.from_http_safe, cls.from_text)
        for decoder in decoders:
            try:
                payload = decoder(payload)
            except:
                pass
            else:
                return payload


class W3CTraceParent(dict):

    def text(self):
        if 'id' in self:
            guid = self['id']
        else:
            guid = seq_id()

        return '00-{}-{}-{:02x}'.format(
            self['tr'].lower().zfill(32),
            guid,
            int(self.get('sa', 0)),
        )

    @classmethod
    def decode(cls, payload):
        # Only traceparent with at least 55 chars should be parsed
        if len(payload) < 55:
            return None

        fields = payload.split('-', 4)

        # Expect that there are at least 4 fields
        if len(fields) < 4:
            return None

        version = fields[0]

        # version must be a valid 2-char hex digit
        if len(version) != 2 or not HEXDIGLC_RE.match(version):
            return None

        # Version 255 is invalid
        if version == 'ff':
            return None

        # Expect exactly 4 fields if version 00
        if version == '00' and len(fields) != 4:
            return None

        # Check field lengths and values
        for field, expected_length in zip(fields[1:4], (32, 16, 2)):
            if len(field) != expected_length or not HEXDIGLC_RE.match(field):
                return None

        # trace_id or parent_id of all 0's are invalid
        trace_id, parent_id = fields[1:3]
        if parent_id == '0' * 16 or trace_id == '0' * 32:
            return None

        return cls(tr=trace_id, id=parent_id)


class W3CTraceState(OrderedDict):

    def text(self, limit=32):
        return ','.join(
                    '{}={}'.format(k, v)
                    for k, v in itertools.islice(self.items(), limit))

    @classmethod
    def decode(cls, tracestate):
        entries = DELIMITER_FORMAT_RE.split(tracestate.rstrip())

        vendors = cls()
        for entry in entries:
            vendor_value = entry.split('=', 2)
            if (len(vendor_value) != 2 or
                    any(len(v) > 256 for v in vendor_value)):
                continue

            vendor, value = vendor_value
            vendors[vendor] = value

        return vendors


class NrTraceState(dict):
    FIELDS = ('ty', 'ac', 'ap', 'id', 'tx', 'sa', 'pr')

    def text(self):
        pr = self.get('pr', '')
        if pr:
            pr = ('%.6f' % pr).rstrip('0').rstrip('.')

        payload = '-'.join((
            '0-0',
            self['ac'],
            self['ap'],
            self.get('id', ''),
            self.get('tx', ''),
            '1' if self.get('sa') else '0',
            pr,
            str(self['ti']),
        ))
        return '{}@nr={}'.format(
            self.get('tk', self['ac']),
            payload,
        )

    @classmethod
    def decode(cls, payload, tk):
        fields = payload.split('-', 9)
        if len(fields) >= 9 and all(fields[:4]) and fields[8]:
            data = cls(tk=tk)

            try:
                data['ti'] = int(fields[8])
            except:
                return

            for name, value in zip(cls.FIELDS, fields[1:]):
                if value:
                    data[name] = value

            if data['ty'] in PARENT_TYPE:
                data['ty'] = PARENT_TYPE[data['ty']]
            else:
                return

            if 'sa' in data:
                if data['sa'] == '1':
                    data['sa'] = True
                elif data['sa'] == '0':
                    data['sa'] = False
                else:
                    data['sa'] = None

            if 'pr' in data:
                try:
                    data['pr'] = float(fields[7])
                except:
                    data['pr'] = None

            return data
