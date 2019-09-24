from dex import Dex

from io import BytesIO
from typing import List, Union
from zipfile import ZipFile

import hashlib

class Apk:
    def __init__(self, apk_file: Union[str, bytes]) -> None:
        self.dex_list : List[str] = [ ]

        if isinstance(apk_file, str):  # filename
            self.zf: ZipFile = ZipFile(apk_file)
        elif isinstance(apk_file, bytes):  # data
            self.zf: ZipFile = ZipFile(BytesIO(apk_file))
        else:
            raise RuntimeError('Unexpected APK type: %s' % type(apk_file))

        files = self.zf.namelist()
        if 'classes.dex' not in files: return
        self.dex_list.append('classes.dex')

        i = 2
        while ('classes%d.dex' % i) in files:
            self.dex_list.append('classes%d.dex' % i)
            i += 1

        self._iter_index: int = 0


    def __iter__(self):
        return self


    def __next__(self):
        if self._iter_index >= len(self.dex_list):
            raise StopIteration
        else:
            self._iter_index += 1
            dex_name = self.dex_list[self._iter_index - 1]
            return Dex(self.zf.read(dex_name))
