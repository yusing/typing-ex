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
    overload,
    get_args,
    get_origin,
    final,
)

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias

    UnionType = NewType("UnionType", Union)
else:
    from typing import TypeAlias
    from types import UnionType


AnyType: TypeAlias = Union[Type, UnionType, None]

__all__ = [
    "Any",
    "ClassVar",
    "DynamicClassAttribute",
    "Dict",
    "NamedTuple",
    "NewType",
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
    "overload",
    "get_args",
    "get_origin",
    "new_class",
    "final",
    "MappingProxyType",
]
