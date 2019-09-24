__all__ = [
    'file_exists',
    'find',
    'ls',
    'mkdir',
    'open_resource',
    'path_in_dir',
    'path_join',
    'read_lines',
    'rm',
    'save_file',
    'save_json',
]


from .importtypes import *
from .misc import json

import inspect
import itertools
import os


def file_exists(path: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(path)

def find(path: str) -> List[str]:
    """Recursively list all *files* in a directory; the result is sorted"""
    ret: List[str] = [ ]
    for root, _, files in os.walk(path):
        ret += [ os.path.join(root, f) for f in files ]
    return sorted(ret)

def ls(path: str) -> List[str]:
    """List contents of a directory; the result is sorted"""
    return sorted(os.listdir(path))

def mkdir(path: str) -> None:
    os.makedirs(path, exist_ok = True)

def rm(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def open_resource(file_name: str) -> TextIO:
    """Open a resource file located besides caller's source file"""
    py_file = inspect.stack(0)[1].filename
    path = os.path.dirname(os.path.realpath(py_file))
    return open(os.path.join(path, file_name))

def path_in_dir(path: str, directory: str) -> bool:
    """Check if path is located in directory directly or indirectly"""
    path = os.path.abspath(path)
    directory = os.path.abspath(directory)
    return path == directory or path.startswith(directory + '/')

def path_join(*args: str) -> str:
    """Join path parts"""
    return os.path.join(*args)

def read_lines(file_: TextFile, strip: bool = True) -> List[str]:
    """Read all lines from a file"""
    if isinstance(file_, str):
        lines = list(open(file_))
    else:
        lines = list(file_)
    if strip:
        lines = [ l.strip() for l in lines ]
    return lines

def save_file(file_name: str, data: Union[str, bytes]) -> None:
    """Save data (text or binary) to file; the path will be prepared automatically"""
    os.makedirs(os.path.dirname(file_name), exist_ok = True)
    if isinstance(data, str):
        open(file_name, 'w').write(data)
    elif isinstance(data, bytes):
        open(file_name, 'wb').write(data)
    elif data is None:
        raise RuntimeError('data is None')
    else:
        raise RuntimeError('Unexpected data type {}'.format(type(data)))

def save_json(file_name: str, json_obj: Any) -> None:
    save_file(file_name, json(json_obj, pretty = True))
