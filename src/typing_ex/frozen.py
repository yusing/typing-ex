from __future__ import annotations
from typing_ex.builtin_typing import Generic, Mapping, Sequence, TypeVar, Dict

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def _immutable(self, *_, **__):
    raise RuntimeError("invalid assignment on frozen type")


class FrozenType(Generic[_T]):
    pass


class FrozenList(list, FrozenType[list]):
    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    remove = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    reverse = _immutable
    sort = _immutable


class FrozenDict(Dict[_KT, _VT], FrozenType[Dict[_KT, _VT]], Generic[_KT, _VT]):
    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable


def frozen_copy(obj):
    if isinstance(obj, Mapping):
        return FrozenDict(obj)
    elif isinstance(obj, list):
        return FrozenList(obj)
    elif isinstance(obj, set):
        return frozenset(obj)
    else:
        return obj
