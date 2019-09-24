__all__ = [
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'exception',
]


from .importtypes import *

import logging
import os
import sys


_fmt = '%(asctime)s [%(levelname)s] %(message)s'
_datefmt = '%Y-%m-%d %H:%M:%S'
_formatter = logging.Formatter(_fmt, _datefmt)


def debug(*args: Any) -> None:
    _log(logging.DEBUG, args)

def info(*args: Any) -> None:
    _log(logging.INFO, args)

def warning(*args: Any) -> None:
    _log(logging.WARNING, args)

def error(*args: Any) -> None:
    _log(logging.ERROR, args)

def critical(*args: Any) -> None:
    _log(logging.CRITICAL, args)
    sys.exit(1)

def exception(exc: Exception) -> None:
    if _logger is None: _init()
    cast(logging.Logger, _logger).exception(exc)


_logger: Optional[logging.Logger] = None


def _init() -> None:
    global _logger
    _logger = logging.getLogger('lx')
    _logger.setLevel(logging.DEBUG)

    os.makedirs('log', exist_ok = True)
    prog = sys.argv[0].replace('.py', '')
    path = os.path.join('log', '{}-{}'.format(prog, os.getpid()))

    with open(path, 'a') as f:
        f.write('# ' + ' '.join(sys.argv) + '\n')

    handler = logging.FileHandler(path)
    handler.setFormatter(_formatter)
    _logger.addHandler(handler)

    if sys.stdout.isatty():
        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setFormatter(_formatter)
        _logger.addHandler(handler2)


def _log(level: int, args: Iterable[Any]) -> None:
    if _logger is None: _init()
    msg = ' '.join(str(arg) for arg in args)
    cast(logging.Logger, _logger).log(level, msg)
