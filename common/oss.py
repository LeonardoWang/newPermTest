__all__ = [
    'open_bucket',
    'oss_read',
    'oss_write',
    'oss_find',
    'oss_read_apk',
]


from .importtypes import *
from .logins import *

import oss2

from io import IOBase
import logging


logging.getLogger('oss2').setLevel(logging.WARNING)


_auth: Optional[oss2.Auth] = None
_bkts: Dict[str, oss2.Bucket] = { }

def open_bucket(bucket) -> oss2.Bucket:
    global _auth
    if _auth is None:
        _auth = oss2.Auth(OssKeyId, OssKeySecret)
    if bucket not in _bkts:
        _bkts[bucket] = oss2.Bucket(_auth, OssEndpoint, bucket)
    return _bkts[bucket]


def oss_read(bucket: str, key: str) -> Optional[bytes]:
    try:
        ret = open_bucket(bucket).get_object(key).read()
        assert type(ret) is bytes
        return ret
    except oss2.exceptions.NoSuchKey:
        return None


def oss_write(bucket: str, key: str, data: BinaryFileOrData) -> None:
    if isinstance(data, bytes):
        open_bucket(bucket).put_object(key, data)
    elif isinstance(data, str):
        open_bucket(bucket).put_object_from_file(key, data)
    else:
        assert isinstance(data, IOBase)
        open_bucket(bucket).put_object(key, data)


def oss_find(bucket: str, prefix: str) -> Optional[str]:
    l = open_bucket(bucket).list_objects(prefix)
    assert not l.is_truncated and len(l.object_list) <= 1
    if l.object_list:
        return l.object_list[0].key
    else:
        return None


def oss_read_apk(pkg: str, md5: Union[str, bytes], sha256: Union[str, bytes, None] = None) -> Optional[bytes]:
    if isinstance(md5, bytes):
        md5 = md5.hex()

    if isinstance(sha256, bytes):
        sha256 = sha256.hex()
    elif sha256 is None:
        from .sql import query
        sql = 'select sha256 from apk where pkg=%s and md5=%s'
        sha = query('main', sql, (pkg, bytes.fromhex(md5)))
        if sha is None:
            return None
        sha256 = sha.hex()

    key = '{}/{}-{}.apk'.format(pkg, md5, sha256)
    return oss_read('lxapk', key)
