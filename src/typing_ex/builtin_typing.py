"""import builtin types"""

import sys
from types import MappingProxyType, DynamicClassAttribute, new_class
from typing import (
    Any,
    NamedTuple,
    NewType,
    Type,
    TypeVar,
    ClassVar,
    Union,
    Mapping,
    Sequence,
    Iterable,
    Callable,
    Generic,
    Optional,
    Dict,
    Tuple,
    overload,
    get_args,
    get_origin,
    final,
)
from typing_extensions import Self, TypeAlias

if sys.version_info < (3, 10):
    UnionType = NewType("UnionType", Union)  # dummy type
else:
    from types import UnionType


AnyType: TypeAlias = Union[Type, UnionType, None]
AnyUnion: TypeAlias = Union[Type, UnionType, object]
__all__ = [
    "Any",
    "ClassVar",
    "DynamicClassAttribute",
    "Dict",
    "NamedTuple",
    "NewType",
    "Tuple",
    "Type",
    "TypeVar",
    "TypeAlias",
    "Union",
    "UnionType",
    "Mapping",
    "Sequence",
    "Iterable",
    "Callable",
    "Generic",
    "Optional",
    "Self",
    "overload",
    "get_args",
    "get_origin",
    "new_class",
    "final",
    "MappingProxyType",
]
