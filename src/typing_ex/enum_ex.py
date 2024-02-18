from __future__ import annotations
from types import DynamicClassAttribute
from typing_ex.builtin_typing import TypeAlias, ClassVar, final, Any


class EnumExMeta(type):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        if not bases:
            return type.__new__(mcs, name, bases, attrs)
        attrs.setdefault("__value_type__", int)
        value_type = attrs["__value_type__"]
        cls_storage = {}
        cls_storage["enums"] = enums = {
            attr: v for attr, v in attrs.items() if attr[0] != "_" and attr.isupper()
        }
        cls_storage["value_dict"] = value_dict = {}
        cls_storage["objs"] = {}
        attrs["__storage__"] = cls_storage
        for k, v in enums.items():
            if not isinstance(v, value_type):
                raise ValueError(f"Value {v} is not of type {value_type.__name__}")
            if v not in value_dict:
                value_dict[v] = k
        return type.__new__(mcs, name, bases, attrs)

    def __getattribute__(mcs, k: str):
        if k[0] == "_" or k in ["names", "values"]:
            return type.__getattribute__(mcs, k)
        cls_storage = mcs.__storage__
        if k not in cls_storage["enums"]:
            raise AttributeError(k)
        if k in cls_storage["objs"]:
            return cls_storage["objs"][k]
        v = cls_storage["enums"][k]
        obj = mcs._create(k, v, cls_storage["value_dict"][v])
        cls_storage["objs"][k] = obj
        return obj

    def __iter__(mcs):
        """Iterate through non-alias enums"""
        cls_storage = mcs.__storage__
        for k, v in cls_storage["enums"].items():
            if cls_storage["value_dict"][v] != k:
                continue
            yield k

    @DynamicClassAttribute
    def names(cls) -> tuple[str]:
        return tuple(cls)

    @DynamicClassAttribute
    def values(cls):
        return tuple(cls.__storage__["value_dict"].keys())


class EnumEx(metaclass=EnumExMeta):
    __slots__ = ("_name", "_value", "_orig_name")
    __value_type__: TypeAlias = int
    __storage__: ClassVar[dict[str, Any]]
    __test__: ClassVar[bool] = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> __value_type__:
        return self._value

    @property
    def orig_name(self) -> str:
        return self._orig_name

    @property
    def is_alias(self) -> bool:
        return self._orig_name != self._name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EnumEx):
            return self._value == other._value
        if isinstance(other, self.__value_type__):
            return self._value == other
        raise ValueError(f"cannot compare enum with {other.__class__.__name__}")

    def __lt__(self, other: object) -> bool:
        if isinstance(other, EnumEx):
            return self._value < other._value
        if isinstance(other, self.__value_type__):
            return self._value < other
        raise ValueError(f"cannot compare enum with {other.__class__.__name__}")

    def __hash__(self) -> int:
        return hash(f"{self.name}:{self.value}")

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__

    @final
    @classmethod
    def _create(cls, *args):
        obj = object.__new__(cls)
        cls.__init__(obj, *args)
        return obj

    @final
    def __init__(self, name: str, value: __value_type__, orig_name: str) -> None:
        self._name = name
        self._value = value
        self._orig_name = orig_name
