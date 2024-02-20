import sys
import typing
import builtins

from typing_ex.builtin_typing import (
    Type,
    UnionType,
    Union,
    MappingProxyType,
    Iterable,
    Mapping,
    Sequence,
    Tuple,
    Set,
    Dict,
    Any,
    AnyType,
    AnyUnion,
    get_args,
    get_origin,
    final,
)


def _get_any_info():
    info = MappingProxyType(dict(type=Any, origin=Any, args=()))
    obj = type.__new__(
        TypeInfo,
        "Any",
        (type,),
        {"_info": info, "name": "Any", "check_value": lambda v: True},
    )
    return obj


def _get_none_info():
    info = MappingProxyType(dict(type=None, origin=None, args=()))
    obj = type.__new__(
        TypeInfo,
        "None",
        (type,),
        {"_info": info, "name": "None", "check_value": lambda v: v is None},
    )
    return obj


def _construct_union(types: Set[type]) -> type:
    if len(types) == 1:
        return next(iter(types))
    return Union[tuple(types)]  # type: ignore


def _get_aliased_type(t: type) -> type:
    if not hasattr(t, "__name__"):
        return t
    t_name = t.__name__.capitalize()
    if hasattr(typing, t_name):
        return getattr(typing, t_name)
    return t


def _get_unaliased_type(t: type) -> type:
    t_name = repr(t).lower().split(".")[-1]
    if hasattr(builtins, t_name):
        likely_t = getattr(builtins, t_name)
        if isinstance(likely_t, type):
            return likely_t
    return t


if sys.version_info >= (3, 10):

    def _construct_generic(t: type, args: Tuple[type, ...]) -> type:
        return t[args]

else:

    def _construct_generic(t: type, args: Tuple[type, ...]) -> type:
        return _get_aliased_type(t)[args]


def _is_union_type(t: AnyType):
    if sys.version_info >= (3, 10):
        return isinstance(t, UnionType) or get_origin(t) is Union
    return t is Union or get_origin(t) is Union


def _is_subclass(t_origin: AnyType, t_super: AnyType):
    if t_origin is None or t_origin == Any:
        return False
    return issubclass(_get_unaliased_type(t_origin), t_super)


class TypeInfoMeta(type):
    @staticmethod
    def __getitem__(t):
        return TypeInfo.get(t)


@final
class TypeInfo(type, metaclass=TypeInfoMeta):
    _instances: Dict[type, "TypeInfo"]
    _type_name_dict: Dict[AnyType, str] = {}
    _info: Dict[str, Any]

    __test__ = False

    @classmethod
    def get(mcs, t):
        """Get TypeInfo object from type `t`"""
        if t in TypeInfo._instances:
            return TypeInfo._instances[t]
        origin = get_origin(t)
        args = get_args(t)
        info = {
            "type": t,
            "origin": origin or t,
            "args": args,
        }
        obj = type.__new__(
            mcs,
            TypeInfo._type_name(t, origin, args),
            (type,),
            {"_info": MappingProxyType(info)},
        )
        mcs._instances[t] = obj
        return obj

    @staticmethod
    def of(value: Any) -> "TypeInfo":
        """
        Get TypeInfo object from value `value`, including generic arguments.\n
        Generic arguments support is only for builtin types.\n
        (i.e.) List, Set, Dict, Tuple, etc.
        """
        if isinstance(value, TypeInfo):
            return value
        if value is None:
            return _get_none_info()
        t = type(value)
        args: Tuple[AnyType, ...] = ()
        if isinstance(value, Mapping):
            tk = set()
            tv = set()
            for k, v in value.items():
                tk.add(TypeInfo.of(k).type)
                tv.add(TypeInfo.of(v).type)
            args = (_construct_union(tk), _construct_union(tv))
        elif isinstance(value, Iterable):
            tv = set()
            for v in value:
                if isinstance(v, t):  # str[...] -> str
                    return TypeInfo.get(t)
                tv.add(TypeInfo.of(v).type)
            args = (_construct_union(tv),)
        if args:
            return TypeInfo.get(_construct_generic(t, args))
        return TypeInfo.get(t)

    @property
    def type(cls) -> Type:
        return cls._info["type"]

    @property
    def origin(cls) -> Type:
        return cls._info["origin"]

    @property
    def args(cls) -> Tuple[Any, ...]:
        return cls._info["args"]

    @property
    def name(cls) -> str:
        return cls._type_name(cls.type, cls.origin, cls.args)

    @property
    def is_union_type(cls) -> bool:
        return _is_union_type(cls.type)

    @property
    def is_mapping(cls) -> bool:
        return _is_subclass(cls.origin, Mapping)

    @property
    def is_set(cls) -> bool:
        return _is_subclass(cls.origin, set)

    @property
    def is_sequence(cls) -> bool:
        return _is_subclass(cls.origin, Sequence)

    def is_subclass(cls, t_super: AnyType) -> bool:
        return _is_subclass(cls.origin, t_super)

    @staticmethod
    def check_union(t1: AnyUnion, t2: AnyUnion) -> bool:
        """
        Check if the union type `t1` fulfills the union type `t2`.

        This function determines if all types in `t1` are present in `t2`. It first checks if `t1` is a union type,
        and if so, it compares the arguments of both `t1` and `t2` to ensure they are of equal length and that all
        arguments in `t1` are present in `t2`. If `t2` is a union type and `t1` is not, it checks if `t1` is one of
        the types in `t2`.

        Parameters:
            t1 (AnyUnion): The first union type to check.
            t2 (AnyUnion): The second union type to check against.

        Returns:
            bool: True if `t1` fulfills `t2`, False otherwise.
        """
        if _is_union_type(t1):
            t1_args = get_args(t1)
            t2_args = get_args(t2)
            return len(t1_args) == len(t2_args) and all(
                arg in t2_args for arg in t1_args
            )
        if _is_union_type(t2):
            return t1 in get_args(t2)
        return False

    def is_type(cls, t: AnyType):
        """check if TypeInfo is exact type `t`"""
        return cls.type is t or cls.type == t

    def check_value(cls, value) -> bool:
        if value is None and cls.type is None:
            return True
        if cls.is_union_type:
            return any(cls.get(t).check_value(value) for t in cls.args)
        try:
            if not isinstance(value, cls.type):
                return False
        except TypeError:
            if not isinstance(value, cls.origin):
                return False
        if not isinstance(value, Iterable):
            return not cls.args
        if not cls.args:
            return True
        if isinstance(value, Mapping):
            for k, v in value.items():
                if not cls.get(cls.args[0]).check_value(k):
                    return False
                if not cls.get(cls.args[1]).check_value(v):
                    return False
            return True
        if isinstance(value, Iterable):
            if len(cls.args) != 1:
                raise TypeError(f"Unsupported type: {cls.name}")
            arg_type = cls.args[0]
            for item in value:
                if not cls.get(arg_type).check_value(item):
                    return False
            return True
        return True

    def __iter__(cls):
        for k, v in cls._info.items():
            yield f"{k} = {v}"

    def __str__(cls) -> str:
        return str(cls.name)

    __repr__ = __str__

    @staticmethod
    def _type_name(t: AnyType, origin: AnyType, args: Tuple[AnyType, ...]):
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

    def __new__(self, *args, **kwargs):
        raise RuntimeError(
            "do not instantiate TypeInfo, use TypeInfo[] or TypeInfo.get()"
        )


TypeInfo._instances = {Any: _get_any_info(), None: _get_none_info()}
