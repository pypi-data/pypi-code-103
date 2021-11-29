# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> #
#           < IN THE NAME OF GOD >           #
# ------------------------------------------ #
__AUTHOR__ = "ToorajJahangiri"
__EMAIL__ = "Toorajjahangiri@gmail.com"
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #

# IMPORTS TIME & TYPE
import time
from typing import Union, NamedTuple, Callable

# IMPORTS NESTED B64 ENCODE & DECODE
from b64 import ab64_encode, ab64_decode
from b64 import mb64_encode, mb64_decode
from b64 import rb64_encode, rb64_decode
from b64 import eb64_encode, eb64_decode
from b64 import lb64_encode, lb64_decode
from b64 import rab64_encode, rab64_decode
from b64 import rmb64_encode, rmb64_decode
from b64 import reb64_encode, reb64_decode
from b64 import rlb64_encode, rlb64_decode

# TEST NESTED B64 CIPHER
class Test_b64:

    def __init__(self) -> None:
        self.__result: NamedTuple = NamedTuple('result', (('passed', bool), ('name', str), ('encoded', bytes), ('decoded', bytes), ('time', str), ('hashed', bytes)))
        self.__ret: NamedTuple = NamedTuple('test', (('data', bytes), ('result', NamedTuple)))
        self.__all_test: list[Callable] = [
            self._ab64,
            self._mb64,
            self._rb64,
            self._eb64, 
            self._lb64,
            self._rab64,
            self._rmb64,
            self._reb64,
            self._rlb64,
            ]

    def test(self, data: Union[bytes, str]) -> tuple[str, tuple]:
        if isinstance(data, str):
            data = data.encode('utf-8')

        return self.__ret(data, tuple(ex(data) for ex in self.__all_test))

    def _ab64(self, data: bytes) -> bool:
        name = 'ab64'
        t1 = time.perf_counter()
        enc = ab64_encode(data)
        t2 = time.perf_counter()
        dec = ab64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _mb64(self, data: bytes) -> bool:
        name = 'mb64'
        t1 = time.perf_counter()
        enc = mb64_encode(data)
        t2 = time.perf_counter()
        dec = mb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _rb64(self, data: bytes) -> bool:
        name = 'rb64'
        t1 = time.perf_counter()
        enc = rb64_encode(data)
        t2 = time.perf_counter()
        dec = rb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _eb64(self, data: bytes) -> bool:
        name = 'eb64'
        t1 = time.perf_counter()
        enc = eb64_encode(data)
        t2 = time.perf_counter()
        dec = eb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _lb64(self, data: bytes) -> bool:
        name = 'lb64'
        t1 = time.perf_counter()
        enc = lb64_encode(data)
        t2 = time.perf_counter()
        dec = lb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _rab64(self, data: bytes) -> bool:
        name = 'rab64'
        t1 = time.perf_counter()
        enc = rab64_encode(data)
        t2 = time.perf_counter()
        dec = rab64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _rmb64(self, data: bytes) -> bool:
        name = 'rmb64'
        t1 = time.perf_counter()
        enc = rmb64_encode(data)
        t2 = time.perf_counter()
        dec = rmb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _reb64(self, data: bytes) -> bool:
        name = 'reb64'
        t1 = time.perf_counter()
        enc = reb64_encode(data)
        t2 = time.perf_counter()
        dec = reb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

    def _rlb64(self, data: bytes) -> bool:
        name = 'rlb64'
        t1 = time.perf_counter()
        enc = rlb64_encode(data)
        t2 = time.perf_counter()
        dec = rlb64_decode(enc)
        t3 = time.perf_counter()
        hashed = hash(enc)

        times = f"en_code: <{t2 - t1:.4}>de_code: <{t3 - t2:.4}>"

        if enc != data and dec == data:
            passed = True
        else:
            print(AssertionError(f'<TEST::{name}::FALSE>'))
            passed = False

        return self.__result(passed, name, enc, dec, times, hashed)

if __name__ == '__main__':
    import os.path as _path
    import json

    # PATH JSON RESULTS DATA
    RESULTS_PATH = './test/test_nested_b64.json'

    RESULT_FILE_VALID_PATH = _path.realpath(RESULTS_PATH)

    # `FALSE` MEAN ENCODED DATA NOT IN RESULTS FILE IF NEED ENCODED DATA CHANGE TO `TRUE`
    ENCODE_DATA_ADD_RESULTS = False

    # TEST DATA STRING & BYTES
    test_data = [b'T3ST!N!T', 'T3ST_STR!NG', 'H3LL0_H3LL0', b'data_DATA', b'5236989566321', b'0x45']

    # ACTIVE TEST CLASS
    tester = Test_b64()
    
    # TEST ACTION & RESULTS PUT IN THE JSON FILE
    # ALL TESTS STRING IS PROPERTY NAME & IN TO METHOD IS PROPERTY NAME
    with open(RESULT_FILE_VALID_PATH, 'w') as f:
        res_js = {}
        res_js['TEST_START'] = {'TIME':time.strftime('%X%x'), 'TEST_DATA': str(test_data)}
        counter = 0
        for it in test_data:
            t = tester.test(it)

            if ENCODE_DATA_ADD_RESULTS:
                val_res = ({'NAME':str(j.name),'PASSED':str(j.passed),'TIME':str(j.time),'ENC_HASH': str(j.hashed), 'ENCODED':j.encoded.decode('ascii')} for j in t[1])
            else:
                val_res = ({'NAME':str(j.name),'PASSED':str(j.passed),'TIME':str(j.time),'ENC_HASH': str(j.hashed)} for j in t[1])

            res_js[str(t[0])] = {i['NAME']: i for i in val_res}
            _ex = '\n\t'.join([f'<{i.name}> -> <{i.passed}> [{i.time}]' for i in t[1]])
            print(f'TEST [{counter}] [{t[0]}] :: \n\t{_ex}')
            counter += 1
        serialize = json.dumps(res_js, indent = 4)
        f.write(serialize)
