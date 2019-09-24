from __future__ import annotations

from ctypes import cdll, c_char_p, c_int32, POINTER
import os
from typing import *


def _load_libdex_so(dirs):
    for dir_ in dirs:
        so_path = os.path.join(dir_, 'libdex.so')
        if os.path.isfile(so_path):
            return cdll.LoadLibrary(so_path)
    return cdll.LoadLibrary('libdex.so')

cur_path = os.path.dirname(__file__)
install_path = os.path.expanduser('~/.local/lib')
libdex = _load_libdex_so([cur_path, install_path])


# These functions are defined in `capi.h/cpp`

libdex.load_dex_file.argtypes = [ c_char_p ]
libdex.load_dex_file.restype = c_int32

libdex.load_dex_data.argtypes = [ c_char_p, c_int32 ]
libdex.load_dex_data.restype = c_int32

libdex.release_dex.argtypes = [ c_int32 ]
libdex.release_dex.restype = None

libdex.get_string_count.argtypes = [ c_int32 ]
libdex.get_string_count.restype = c_int32

libdex.get_string.argtypes = [ c_int32, c_int32 ]
libdex.get_string.restype = c_char_p

libdex.get_raw_string.argtypes = [c_int32, c_int32 ]
libdex.get_raw_string.restype = c_char_p

libdex.get_class_count.argtypes = [ c_int32 ]
libdex.get_class_count.restype = c_int32

libdex.get_class_name.argtypes = [ c_int32, c_int32 ]
libdex.get_class_name.restype = c_char_p

libdex.get_methods_count.argtypes = [ c_int32, c_int32 ]
libdex.get_methods_count.restype = c_int32

libdex.get_method_full_name.argtypes = [ c_int32, c_int32 ]
libdex.get_method_full_name.restype = c_char_p

libdex.get_class_method_full_name.argtypes = [ c_int32, c_int32, c_int32 ]
libdex.get_class_method_full_name.restype = c_char_p

libdex.get_field_full_name.argtypes = [ c_int32, c_int32 ]
libdex.get_field_full_name.restype = c_char_p

libdex.get_const_strings.argtypes = [ c_int32, c_int32, c_int32 ]
libdex.get_const_strings.restype = POINTER(c_int32)

libdex.get_invoked_methods.argtypes = [ c_int32, c_int32, c_int32 ]
libdex.get_invoked_methods.restype = POINTER(c_int32)

libdex.get_read_fields.argtypes = [ c_int32, c_int32, c_int32 ]
libdex.get_read_fields.restype = POINTER(c_int32)

libdex.get_repackage_features.argtypes = [ c_int32, c_int32 ]
libdex.get_repackage_features.restype = POINTER(c_int32)

libdex.get_class_repackage_features.argtypes = [ c_int32, c_int32, c_int32 ]
libdex.get_class_repackage_features.restype = POINTER(c_int32)

def _decode_int_array(ptr) -> List[int]:
    ret = [ ]
    for i in range(ptr[0]):
        ret.append(ptr[i + 1])
    return ret


def _decode_features(arr, level):
    if len(arr) == 0 or arr[0] >= 0: return arr
    assert arr[0] == level - 1, (arr[0], level)

    ret = [ ]
    last = 0
    for i in range(1, len(arr)):
        if arr[i] == level - 1:
            ret.append(_decode_features(arr[last + 1 : i], level - 1))
            last = i
    ret.append(_decode_features(arr[last + 1 : ], level - 1))
    return ret


class Dex:
    def __init__(self, dex_file: Union[str, bytes]) -> None:
        """Load a DEX file.
        dex_file: path (str) or data (bytes) of a DEX file
        """
        if isinstance(dex_file, str):  # filename
            self.id: int = libdex.load_dex_file(dex_file.encode('utf8'))
        elif isinstance(dex_file, bytes):  # data
            assert len(dex_file) < (2 ** 31)
            self.id: int = libdex.load_dex_data(dex_file, len(dex_file))
            self._data_ref = dex_file  # tell CPython do not release the bytes object
        else:
            raise RuntimeError('dex_file has wrong type %s' % type(dex_file))

        assert self.id >= 0

        string_cnt = libdex.get_string_count(self.id)
        self._strings: List[Union[str, bytes, None]] = [ None ] * string_cnt

        class_cnt = libdex.get_class_count(self.id)
        self.classes: List[DexClass] = [ DexClass(self, i) for i in range(class_cnt) ]

    def __del__(self):
        libdex.release_dex(self.id)

    def get_string(self, string_id: int, check: bool = True) -> Union[str, bytes, None]:
        if self._strings[string_id] is None:
            self._strings[string_id] = libdex.get_string(self.id, string_id).decode('utf8')
            if self._strings[string_id] is None:
                self._strings[string_id] = libdex.get_raw_string(self.id, string_id)
                if check: raise UnicodeError('DEX string is not MUTF-8 encoded')
        return self._strings[string_id]

    def strings(self) -> List[Union[str, bytes, None]]:
        self._strings = [ self.get_string(i) for i in range(len(self._strings)) ]
        return self._strings

    def get_method_name(self, method_id: int) -> str:
        return libdex.get_method_full_name(self.id, method_id).decode('utf8')

    def get_field_name(self, field_id: int) -> str:
        return libdex.get_field_full_name(self.id, field_id).decode('utf8')

    def get_repackage_features(self, ordered: bool = False):
        ptr = libdex.get_repackage_features(self.id, 1 if ordered else 0)
        arr = _decode_int_array(ptr)
        return _decode_features(arr, 0)


class DexClass:
    def __init__(self, dex: Dex, id_: int) -> None:
        self.dex = dex
        self.id = id_
        self._name: Optional[str] = None
        self._methods: Optional[List[DexMethod]] = None

    def name(self) -> str:
        if self._name is None:
            name_bytes = libdex.get_class_name(self.dex.id, self.id)
            self._name = name_bytes.decode('utf8')
        return cast(str, self._name)

    def methods(self) -> List[DexMethod]:
        if self._methods is None:
            method_cnt = libdex.get_methods_count(self.dex.id, self.id)
            self._methods = [ DexMethod(self, i) for i in range(method_cnt) ]
        return self._methods

    def get_repackage_features(self, ordered: bool = False):
        ptr = libdex.get_class_repackage_features(self.dex.id, self.id, 1 if ordered else 0)
        arr = _decode_int_array(ptr)
        ret = _decode_features(arr, 0)
        assert len(ret) == 1
        return ret[0]


class DexMethod:
    def __init__(self, class_: DexClass, idx: int) -> None:
        self.dex = class_.dex
        self.class_ = class_
        self.idx = idx
        self._name: Optional[str] = None

    def name(self) -> str:
        if self._name is None:
            name_bytes = libdex.get_class_method_full_name(self.dex.id, self.class_.id, self.idx)
            self._name = name_bytes.decode('utf8')
        return cast(str, self._name)

    def get_const_string_ids(self) -> List[int]:
        ptr = libdex.get_const_strings(self.dex.id, self.class_.id, self.idx)
        return _decode_int_array(ptr)

    def get_const_strings(self) -> List[Union[str, bytes, None]]:
        ids = self.get_const_string_ids()
        return [ self.dex.get_string(i) for i in ids ]

    def get_invoked_method_ids(self) -> List[int]:
        ptr = libdex.get_invoked_methods(self.dex.id, self.class_.id, self.idx)
        return _decode_int_array(ptr)

    def get_invoked_methods(self) -> List[str]:
        ids = self.get_invoked_method_ids()
        return [ self.dex.get_method_name(i) for i in ids ]

    def get_read_field_ids(self) -> List[int]:
        ptr = libdex.get_read_fields(self.dex.id, self.class_.id, self.idx)
        return _decode_int_array(ptr)

    def get_read_fields(self) -> List[str]:
        ids = self.get_read_field_ids()
        return [ self.dex.get_field_name(i) for i in ids ]



def test(file_name):
    data = open(file_name, 'rb').read()
    dex = Dex(data)
    for class_ in dex.classes:
        print(class_.name())
        for method in class_.methods():
            print('    ' + method.name())
            #print('        %s' % method.get_const_string_ids())
            #for im in method.get_invoked_methods():
            #    print('        ' + im)
            #for f in method.get_read_fields():
            #    print('        ' + f)
        #f = class_.get_repackage_features()
        #print(f)

import sys

if __name__ == '__main__':
    if len(sys.argv) == 1:
        test('classes.dex')
    else:
        test(sys.argv[1])
