from enum import Enum
from typing_ex.builtin_typing import (
    DynamicClassAttribute,
    Type,
    ClassVar,
    Dict,
    Tuple,
    final,
    Any,
    abstractmethod,
    new_class,
)


"""
Trick static type checker
to recognize enum as EnumEx instead of __value_type__
"""


class EnumEx(Enum):
    names: ClassVar[Tuple[str]]
    values: ClassVar[Tuple]
    enums: ClassVar[Tuple["_EnumEx"]]
    value_type: ClassVar[Type]

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def value(self): ...

    @property
    @abstractmethod
    def orig_name(self) -> str: ...

    @property
    @abstractmethod
    def is_alias(self) -> bool: ...


class _ClassStorage:
    name_value_dict: Dict[str, Any]
    value_name_dict: Dict[Any, str]
    name_orig_name_dict: Dict[str, str]
    value_type: Type
    instances: Dict[str, "EnumEx"]
    class_: Type

    def __init__(self, value_type: Type, nv_dict: Dict[str, Any]) -> None:
        self.name_value_dict = nv_dict
        self.value_name_dict = {}
        self.name_orig_name_dict = {}
        self.instances = {}
        self.value_type = value_type
        for k, v in nv_dict.items():
            if not isinstance(v, value_type):
                raise ValueError(
                    f"Enum {k} has a value {v} "
                    "which does not match __value_type__: '{value_type.__name__}'"
                )
            if v not in self.value_name_dict:
                self.value_name_dict[v] = k
                self.name_orig_name_dict[k] = k
                continue
            self.name_orig_name_dict[k] = self.value_name_dict[v]

    def init_instances(self):
        for k, v in self.name_value_dict.items():
            self.instances[k] = self.class_.__create__(
                k, v, self.name_orig_name_dict[k]
            )


class EnumExMeta(type):
    def __new__(mcs, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any]):
        if name == "EnumExMeta":
            return type.__new__(mcs, name, bases, attrs)
        value_type = attrs.pop("__value_type__", None) or int
        nv_dict = {}
        for attr, v in attrs.items():
            if attr[0] != "_" and attr.isupper():
                nv_dict[attr] = v
        attrs = {k: v for k, v in attrs.items() if k not in nv_dict}
        attrs["__storage__"] = _ClassStorage(value_type, nv_dict)
        tp_enum = type.__new__(mcs, name, bases, attrs)
        tp_enum.__storage__.class_ = tp_enum
        tp_enum.__storage__.init_instances()
        return tp_enum

    def __getattr__(mcs, k: str):
        cls_storage = mcs.__storage__
        if k not in cls_storage.instances:
            raise AttributeError(k)
        return cls_storage.instances[k]

    def __iter__(mcs):
        """Iterate through non-alias enums"""
        cls_storage = mcs.__storage__
        for v in cls_storage.instances.values():
            if v.name == v.orig_name:
                yield v

    @DynamicClassAttribute
    def names(cls):
        return tuple(cls.__storage__.instances.keys())

    @DynamicClassAttribute
    def values(cls):
        return tuple(cls.__storage__.value_name_dict.keys())

    @DynamicClassAttribute
    def enums(cls):
        return tuple(cls.__storage__.instances.values())

    @DynamicClassAttribute
    def value_type(cls) -> Type:
        """all enums"""
        return cls.__storage__.value_type


class _EnumEx(metaclass=EnumExMeta):
    __slots__ = ("_name", "_value", "_orig_name")
    __value_type__: ClassVar[Type]
    __test__: ClassVar[bool] = False

    names: ClassVar[Tuple[str]]
    values: ClassVar[Tuple]
    enums: ClassVar[Tuple["EnumEx"]]
    value_type: ClassVar[Type]

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def orig_name(self) -> str:
        return self._orig_name

    @property
    def origin(self) -> "EnumEx":
        return self.__class__.__storage__.instances[self._orig_name]

    @property
    def is_alias(self) -> bool:
        return self._orig_name != self._name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._value == other._value
        if isinstance(other, self.__class__.value_type):
            return self._value == other
        raise ValueError(
            f"cannot compare enum of {self.__class__.value_type.__name__} "
            f"with {other.__class__.__name__}"
        )

    def __lt__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._value < other._value
        if isinstance(other, self.__class__.value_type):
            return self._value < other
        raise ValueError(
            f"cannot compare enum of {self.__class__.value_type.__name__} "
            f"with {other.__class__.__name__}"
        )

    def __hash__(self) -> int:
        return hash(f"{self.name}:{self.value}")

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__

    @final
    @classmethod
    def __create__(cls, *args):
        obj = object.__new__(cls)
        cls.__init__(obj, *args)
        return obj

    @final
    def __init__(self, name: str, value, orig_name: str) -> None:
        self._name = name
        self._value = value
        self._orig_name = orig_name


EnumEx = new_class("EnumEx", (_EnumEx,))  # type: ignore[misc,assignment] # noqa: F811
EnumEx.__doc__ = Enum.__doc__
