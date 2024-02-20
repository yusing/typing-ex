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
    Callable,
    Mapping,
    Sequence,
    Iterable,
    MutableSequence,
    MutableMapping,
    MutableSet,
    Union,
    Generic,
    Generator,
    Optional,
    List,
    Dict,
    Set,
    Tuple,
    overload,
    get_args,
    get_origin,
    final,
)
from abc import abstractmethod
from typing_extensions import Self, TypeAlias, override

if sys.version_info < (3, 10):
    UnionType = NewType("UnionType", Union)  # dummy type
else:
    from types import UnionType


AnyUnion: TypeAlias = Union[Type, UnionType, object]
AnyType: TypeAlias = Union[Type, AnyUnion, None]
__all__ = [
    "Any",
    "ClassVar",
    "DynamicClassAttribute",
    "Dict",
    "List",
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
    "Set",
    "MutableSequence",
    "MutableMapping",
    "MutableSet",
    "Callable",
    "Generic",
    "Generator",
    "Optional",
    "Self",
    "overload",
    "override",
    "get_args",
    "get_origin",
    "new_class",
    "final",
    "abstractmethod",
    "MappingProxyType",
]
