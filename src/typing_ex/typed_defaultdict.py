from typing_ex.builtin_typing import (
    Any,
    NamedTuple,
    Mapping,
    MappingProxyType,
    Optional,
    TypeAlias,
)
from typing_ex.type_info import TypeInfo

_SCHEMA_ATTR = "_schema"

PropertyDVTTuple = NamedTuple(
    "PropertyDVTTuple", [("default", Any), ("type", TypeInfo)]
)

Schema: TypeAlias = "MappingProxyType[str, PropertyDVTTuple]"


class PropertyValueError(Exception):
    def __init__(self, property_name: str, value: Any, expected_type: TypeInfo):
        self.property_name = property_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(
            f"value for property '{property_name}'"
            "is not of type {expected_type.name}"
        )


class UnknownPropertyError(Exception):
    def __init__(self, property_name: str):
        self.property_name = property_name
        super().__init__(f"unknown property '{property_name}'")


class ReservedPropertyError(Exception):
    def __init__(self, property_name: str):
        self.property_name = property_name
        super().__init__(f"property '{property_name}' is reserved")


def _ns_handler(ns: dict):
    annotations = {
        k: v for k, v in ns.get("__annotations__", {}).items() if k[0] != "_"
    }  # filter out private members
    if any(isinstance(annotation, str) for annotation in annotations.values()):
        raise RuntimeError(
            "TypedDefaultDict cannot be used with "
            "'from __future__ import annotations'"
        )
    schema = {
        k: PropertyDVTTuple(ns.get(k), TypeInfo[annotations[k]])
        for k in annotations.keys()
    }
    ns = {k: v for k, v in ns.items() if k not in schema}
    ns["_schema"] = MappingProxyType(schema)
    return ns


class TypedDefaultDictMeta(type):
    def __new__(mcs, name, bases, ns):
        if not bases:
            return type.__new__(mcs, name, bases, ns)
        return type.__new__(mcs, name, bases, _ns_handler(ns))

    def __getattribute__(mcs, k: str):
        if k == "_schema":
            return super().__getattribute__(k)
        if k in mcs._schema:
            return mcs._schema[k].default
        return super().__getattribute__(k)


class TypedDefaultDict(dict, metaclass=TypedDefaultDictMeta):

    @property
    def schema(self) -> Schema:
        return self._schema

    def __init__(self, data: Optional[dict] = None, /, **kwargs):
        if data and kwargs:
            raise ValueError("data and kwargs cannot be used together")
        if data and not isinstance(data, Mapping):
            raise TypeError("data must be a mapping")
        else:
            data = data or kwargs
        if not data:
            raise ValueError("data or kwargs must be provided")
        self._verify_data(data)
        super().__init__(data)

    def __getattr__(self, k: str):
        if k in self._schema:
            return self.__getitem__(k)
        return super().__getattribute__(k)

    def __setattr__(self, k: str, v: Any):
        if k == _SCHEMA_ATTR:
            raise ReservedPropertyError(k)
        if k in self._schema:
            self.__setitem__(k, v)
            return
        super().__setattr__(k, v)

    def __getitem__(self, k: str):
        self._check_property(k)
        if k in self:
            return super().__getitem__(k)
        return self._schema[k].default

    def __setitem__(self, k: str, v: Any):
        self._check_property(k)
        self._check_value_type(k, v)
        super().__setitem__(k, v)

    @classmethod
    def _check_property(cls, k: str):
        if k == _SCHEMA_ATTR:
            raise ReservedPropertyError(k)
        if k not in cls._schema:
            raise UnknownPropertyError(k)

    @classmethod
    def _check_value_type(cls, k: str, v: Any):
        if not cls._schema[k].type.check_value(v):
            raise PropertyValueError(k, v, cls._schema[k].type)

    @classmethod
    def _verify_data(cls, data: Mapping[str, Any]):
        for k, v in data.items():
            cls._check_property(k)
            cls._check_value_type(k, v)
