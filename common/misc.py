__all__ = [
    'args',
    'execute',
    'json',
    'md5',
    'now',
    'sleep',
]


from .importtypes import *

from datetime import datetime
import hashlib
from json import dumps
import subprocess
import sys
import time


args = sys.argv

def json(json_obj: Any, pretty = False) -> str:
    """Dump a JSON object, and prettify result if "pretty" is True"""
    if pretty:
        return dumps(json_obj, ensure_ascii = False, indent = 4, sort_keys = True)
    else:
        return dumps(json_obj, ensure_ascii = False, sort_keys = True)

def now() -> float:
    """Get timestamp of current time"""
    return datetime.now().timestamp()

def sleep(seconds: float) -> None:
    """Sleep for seconds (if it is greater than 0)"""
    if seconds > 0:
        time.sleep(seconds)


def _open_binary_file(f: BinaryFile) -> BinaryIO:
    if isinstance(f, str):
        return open(f, 'rb')
    else:
        return f

def md5(file_or_data: BinaryFileOrData) -> bytes:
    """Calculate MD5 checksum of file or blob"""
    engine = hashlib.md5()
    if isinstance(file_or_data, bytes):  # is binary data
        engine.update(file_or_data)
    else:
        file_ = _open_binary_file(file_or_data)
        for chunk in iter(lambda: file_.read(4096), bytes()):
            engine.update(chunk)
    return engine.digest()

def execute(cmd: Union[str, List[str]]) -> Tuple[List[str], List[str], int]:
    if isinstance(cmd, str):
        cmd_ = cmd.split()
    else:
        cmd_ = cmd
    p = subprocess.run(cmd, capture_output = True)
    ret = p.returncode
    out = p.stdout.decode().split('\n')
    err = p.stderr.decode().split('\n')
    if not out[-1]: out = out[:-1]
    if not err[-1]: err = err[:-1]
    return (out, err, ret)
