from collections import defaultdict
from datetime import datetime
from enum import Enum
from io import BytesIO
from types import ModuleType
from typing import (
    Any,
    BinaryIO,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    TextIO,
    Tuple,
    Union,
    cast
)

Number = Union[int, float]

BinaryFile = Union[BinaryIO, str]
BinaryFileOrData = Union[BinaryIO, str, bytes]

TextFile = Union[TextIO, str]
