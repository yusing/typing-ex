from __future__ import annotations
import sys
from typing_ex.builtin_typing import (
    Type,
    TypeVar,
    UnionType,
    Union,
    MappingProxyType,
    Iterable,
    Callable,
    Mapping,
    Sequence,
    Any,
    AnyType,
    get_args,
    get_origin,
)

_ValueType = TypeVar("_ValueType")


class TypeInfoMeta(type):
    @staticmethod
    def __getitem__(t):
        return TypeInfo.get(t)


class TypeInfo(type, metaclass=TypeInfoMeta):
    _instances: dict[type, "TypeInfo"] = {}
    _type_name_dict: dict[type, str] = {}
    _info: dict[str, Any]

    __test__ = False

    @classmethod
    def get(mcs, t):
        if t in TypeInfo._instances:
            return TypeInfo._instances[t]
        origin = get_origin(t)
        args = get_args(t)
        info = MappingProxyType(
            {
                "type": t,
                "origin": origin or t,
                "args": args,
            }
        )
        obj = type.__new__(
            mcs,
            TypeInfo._type_name(t, origin, args),
            (type,),
            {"_info": info},
        )
        mcs._instances[t] = obj
        return obj

    @property
    def type(cls) -> Type:
        return cls._info["type"]

    @property
    def origin(cls) -> Type:
        return cls._info["origin"]

    @property
    def args(cls) -> tuple[Any, ...]:
        return cls._info["args"]

    @property
    def name(cls) -> str:
        return cls._type_name(cls.type, cls.origin, cls.args)

    @property
    def is_union_type(cls) -> bool:
        return cls._is_union_type(cls.type, cls.origin)

    @property
    def is_mapping(cls) -> bool:
        return issubclass(cls.origin, Mapping)

    @property
    def is_set(cls) -> bool:
        return issubclass(cls.origin, set)

    @property
    def is_sequence(cls) -> bool:
        return issubclass(cls.origin, Sequence)

    @staticmethod
    def check_union(
        t1: Type | UnionType | object, t2: Type | UnionType | object
    ) -> bool:
        if TypeInfo._is_union_type(t1, t1):
            t1_args = get_args(t1)
            t2_args = get_args(t2)
            return len(t1_args) == len(t2_args) and all(
                arg in t2_args for arg in t1_args
            )
        if TypeInfo._is_union_type(t2, t2):
            return t1 in get_args(t2)
        return False

    def check_value(cls, value) -> bool:
        if value is None:
            return cls.type is None
        if cls.is_union_type:
            return issubclass(type(value), cls.args)
        try:
            if not isinstance(value, cls.type):
                return False
        except TypeError:
            if not isinstance(value, cls.origin):
                return False
        if not isinstance(value, Iterable):
            return not cls.args
        for item in cls._iter_value(value):
            if not cls._check_values(cls.args, item):
                return False
        return True

    def __iter__(cls):
        for k, v in cls._info.items():
            yield f"{k} = {v}"

    def __str__(cls) -> str:
        return str(cls.name)

    __repr__ = __str__

    @staticmethod
    def _check_args(
        args1: tuple[AnyType, ...],
        types_or_values: tuple[_ValueType, ...],
        check_fn: Callable[[AnyType, _ValueType], bool],
    ):
        if not args1:
            return True
        if not types_or_values:
            return False
        return all(
            check_fn(arg_a, arg_b) for arg_a, arg_b in zip(args1, types_or_values)
        )

    @staticmethod
    def _check_values(args: tuple[AnyType, ...], values: tuple[_ValueType, ...]):
        return TypeInfo._check_args(
            args, values, lambda arg, value: TypeInfo[arg].check_value(value)
        )

    def _iter_value(cls, value: Any):
        assert isinstance(value, Iterable)
        if isinstance(value, Mapping):
            it = iter(value.items())
        else:
            it = iter(value)
        for item in it:
            yield item if isinstance(item, Iterable) else [item]

    @staticmethod
    def _type_name(t, origin, args):
        if t is None:
            return "None"
        if t in TypeInfo._type_name_dict:
            return TypeInfo._type_name_dict[t]
        if not origin and not args:
            t_name = t.__name__
        else:
            t_name = str(t)
        TypeInfo._type_name_dict[t] = t_name
        return t_name

    @staticmethod
    def _is_union_type(t_cls, t_origin):
        if sys.version_info >= (3, 10):
            return isinstance(t_cls, UnionType) or get_origin(t_origin) is Union
        return get_origin(t_cls) is Union or get_origin(t_origin) is Union
