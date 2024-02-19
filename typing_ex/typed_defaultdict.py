from typing_ex.builtin_typing import (
    Any,
    NamedTuple,
    Mapping,
    MappingProxyType,
    Optional,
    Type,
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
            f"is not of type {expected_type.name}"
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

    def __getattr__(mcs, k: str):
        if k not in mcs._schema:
            raise AttributeError(k)
        return mcs._schema[k].default


# no more metaclass conflict warning from mypy
_TypedDefaultDict: Type = type.__new__(type, "TypedDefaultDict", (dict,), {})


class TypedDefaultDict(_TypedDefaultDict, metaclass=TypedDefaultDictMeta):

    @property
    def schema(self) -> Schema:
        return self._schema

    def update(self, fields: Optional[Mapping[str, Any]] = None, /, **kwargs):
        super().update(self._get_fields(fields, **kwargs))

    def on_get_unknown_property(self, k) -> Any:
        raise UnknownPropertyError(k)

    def on_set_unknown_property(self, k: str, v: Any) -> Any:
        raise UnknownPropertyError(k)

    def set(self, k: str, v: Any) -> None:
        super().__setitem__(k, v)

    def __init__(self, fields: Optional[Mapping[str, Any]] = None, /, **kwargs):
        super().__init__(self._get_fields(fields, **kwargs))

    def __getitem__(self, k: str):
        if k in self:
            return super().__getitem__(k)
        if k in self._schema:
            return self._schema[k].default
        return self.on_get_unknown_property(k)

    def __setitem__(self, k: str, v: Any):
        if self._check_property(k):
            self._check_value_type(k, v)
            super().__setitem__(k, v)
            return
        v = self.on_set_unknown_property(k, v)
        if v is not None:
            super().__setitem__(k, v)

    __getattr__ = __getitem__
    __setattr__ = __setitem__

    def _check_property(self, k: str) -> bool:
        if not isinstance(k, str):
            raise TypeError("property name must be a string")
        if k == _SCHEMA_ATTR:
            raise ReservedPropertyError(k)
        return k in self._schema

    def _check_value_type(self, k: str, v: Any):
        if not self._schema[k].type.check_value(v):
            raise PropertyValueError(k, v, self._schema[k].type)

    def _verify_data(self, data: Mapping[str, Any]) -> Mapping[str, Any]:
        remove_keys = []
        for k, v in data.items():
            if self._check_property(k):
                self._check_value_type(k, v)
                continue
            v = self.on_set_unknown_property(k, v)
            if v is None:
                remove_keys.append(k)
            else:
                data[k] = v
        return {k: v for k, v in data.items() if k not in remove_keys}

    def _get_fields(
        self, data: Optional[Mapping[str, Any]] = None, /, **kwargs
    ) -> Mapping[str, Any]:
        if data and kwargs:
            raise ValueError("data and kwargs cannot be used together")
        if data and not isinstance(data, Mapping):
            raise TypeError("data must be a mapping")
        else:
            return self._verify_data(data or kwargs or {})
