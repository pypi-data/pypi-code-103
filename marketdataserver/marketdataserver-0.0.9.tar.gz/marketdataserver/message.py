from datetime import datetime

MSG_GET = 1
MSG_GETR = 2
MSG_SUB = 3
MSG_SUBR = 4

def time2systemkey(t: datetime) -> bytes:
    return bytes(str(int(t.timestamp() * 1000 * 1000 * 1000)), encoding='utf-8')


class Field:
    def encode_int(v, size):
        res = bytearray()
        for i in range(size):
            res.append((v >> (i*8)) & 0xff)
        return res

    def decode_int(buf, size):
        res = 0
        for i in range(size):
            res |= int(buf[i]) << (i * 8)
        return res

    def __init__(self, name, type, child_field=None):
        self.name = name
        self.type = type
        self.child_field = child_field
        self.value = None
        if self.type == 'uint8_t':
            self.value = 0
        elif self.type == 'uint16_t':
            self.value = 0
        elif self.type == 'uint32_t':
            self.value = 0
        elif self.type == 'string':
            self.value = b''
        elif self.type == 'vector':
            self.value = []
        else:
            raise Exception("unknown type: ", type)
        self.encoding = 'utf-8'

    def size(self):
        if self.type == 'uint8_t':
            return 1

        elif self.type == 'uint16_t':
            return 2

        elif self.type == 'uint32_t':
            return 4

        elif self.type == 'string':
            return 4 + len(self.value)

        elif self.type == 'vector':
            size = 4
            for v in self.value:
                self.type += v.size()
            return size
        else:
            raise Exception("unknown type: ", self.type)

    def encode(self) -> bytearray:
        res = bytearray()
        if self.type == 'uint8_t':
            res += Field.encode_int(self.value, 1)
        
        elif self.type == 'uint16_t':
            res += Field.encode_int(self.value, 2)

        elif self.type == 'uint32_t':
            res += Field.encode_int(self.value, 4)

        elif self.type == 'string':
            res += Field.encode_int(len(self.value), 4)
            res += self.value

        elif self.type == 'vector':
            res += Field.encode_int(len(self.value), 4)
            for v in self.value:
                res += v.encode()
        else:
            raise Exception("unknown type: ", self.type)
        return res

    # 0: not full, -1: bad, >0: size of the field
    def decode(self, buf):
        if self.type == 'uint8_t':
            if len(buf) < 1:
                return 0
            self.value = Field.decode_int(buf, 1)
            return 1

        elif self.type == 'uint16_t':
            if len(buf) < 2:
                return 0
            self.value = Field.decode_int(buf, 2)
            return 2

        elif self.type == 'uint32_t':
            if len(buf) < 4:
                return 0
            self.value = Field.decode_int(buf, 4)
            return 4

        elif self.type == 'string':
            if len(buf) < 4:
                return 0
            ln = Field.decode_int(buf, 4)
            if len(buf) < ln + 4:
                return 0

            self.value = buf[4:4 + ln]
            return ln + 4

        elif self.type == 'vector':
            if len(buf) < 4:
                return 0

            cnt = Field.decode_int(buf, 4)
            size = 4
            self.value = []
            for i in range(cnt):
                cf = Field(self.child_field.name,
                           self.child_field.type, self.child_field.child_field)
                fs = cf.decode(buf[size:])
                if fs == 0:
                    return 0
                size += fs
                self.value.append(cf)
            return size

        else:
            raise Exception("can't decode")

    def __str__(self):
        if self.type == 'vector':
            res = self.name + ': ['
            for v in self.value:
                res += str(v) + ","
            res += ']'
            return res
        else:
            return self.name + ": " + str(self.value)


class Message:
    def __init__(self, type: int):
        self.type = Field('type', 'uint8_t')
        self.type.value = type

    def encode(self):
        res = bytearray()
        res += self.type.encode()
        for field in self.fields:
            res += field.encode()
        return res

    # 0: not full  -1: bad   >0: size of the msg
    def decode(self, buf):
        if len(buf) < 1:
            return 0

        t = Field('type', 'uint8_t')
        t.decode(buf)

        if t.value != self.type.value:
            return 0;

        size = 0
        size += self.type.decode(buf[size:])
        for field in self.fields:
            fs = field.decode(buf[size:])
            if fs == 0:
                return 0
            size += fs
        return size

    def get_field(self, field):
        fs = [self.type] + self.fields
        for f in fs:
            if field == f.name:
                return f.value
        return None

    def set_field(self, field, value):
        fs = [self.type] + self.fields
        for f in fs:
            if field == f.name:
                f.value = value
                return True
        raise Exception("no field: ", field)

    def size(self):
        fs = [self.type] + self.fields
        size = 0
        for f in fs:
            size += f.size()
        return size

    def __str__(self):
        res = '{'
        fs = [self.type] + self.fields 
        for f in fs:
            res += f.__str__() + ", "
        res += '}'
        return res

class Get(Message):
    def __init__(self, symbol: bytes = b'', data_type: bytes = b'', end_timestamp: bytes = b'', format: bytes = b'json'):
        super().__init__(MSG_GET)
        self.fields = [Field('symbol', 'string'), Field('data_type', 'string'), Field('end_timestamp', 'string'), Field('format', 'string')]
        self.set_field('symbol', symbol)
        self.set_field('data_type', data_type)
        self.set_field('end_timestamp', end_timestamp)
        self.set_field('format', format)


class GetR(Message):
    def __init__(self, data: bytes = b'', is_last: int = 0, error_code: int = 0):
        super().__init__(MSG_GETR)
        self.fields = [Field('data', 'string'), Field('is_last', 'uint8_t'), Field('error_code', 'uint16_t')]
        self.set_field('data', data)
        self.set_field('is_last', 0)
        self.set_field('error_code', error_code)

class Sub(Message):
    def __init__(self, symbol: bytes = b'', data_type: bytes = b'', format: bytes = b'json'):
        super().__init__(MSG_SUB)
        self.fields = [Field('symbol', 'string'), Field('data_type', 'string'), Field('format', 'string')]
        self.set_field('symbol', symbol)
        self.set_field('data_type', data_type)
        self.set_field('format', format)

class SubR(Message):
    def __init__(self, data: bytes = b'', is_last: int = 0, error_code: int = 0):
        super().__init__(MSG_SUBR)
        self.fields = [Field('data', 'string'), Field('error_code', 'uint16_t')]
        self.set_field('data', data)
        self.set_field('error_code', error_code)

if __name__ == '__main__':
    print(time2systemkey(datetime.now()))
    mget = Get()
    me = mget.encode()
    mget.decode(me)
    print(mget)

    mgetret = GetR()
    me = mgetret.encode()
    mgetret.decode(me)
    print(mgetret)
