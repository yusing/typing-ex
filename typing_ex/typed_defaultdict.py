from typing_ex.builtin_typing import (
    Any,
    NamedTuple,
    Mapping,
    MappingProxyType,
    Optional,
    Type,
    TypeAlias,
    Dict,
    Callable,
    DynamicClassAttribute,
)
from typing_ex.type_info import TypeInfo
import inspect

_SCHEMA_ATTR = "_schema"

PropertyDVTTuple = NamedTuple(
    "PropertyDVTTuple", [("default", Any), ("type", TypeInfo)]
)

FactoryCallable: TypeAlias = Callable[[Any], Any]
Factory: TypeAlias = Dict[str, "FactoryMethod"]
Schema: TypeAlias = Mapping[str, PropertyDVTTuple]


class TypedDefaultDictError(Exception):
    """Base class for all exceptions raised by TypedDefaultDict."""

    pass


class PropertyValueError(TypedDefaultDictError):
    def __init__(self, property_name: str, value: Any, expected_type: TypeInfo):
        self.property_name = property_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(
            f"value for property '{property_name}' "
            f"is not of type {expected_type}, "
            f"but '{TypeInfo.of(value)}'"
        )


class UnknownPropertyError(TypedDefaultDictError):
    def __init__(self, property_name: str):
        self.property_name = property_name
        super().__init__(f"unknown property '{property_name}'")


class ReservedPropertyError(TypedDefaultDictError):
    def __init__(self, property_name: str):
        self.property_name = property_name
        super().__init__(f"property '{property_name}' is reserved")


class FactoryReturnValueError(TypedDefaultDictError):
    def __init__(
        self, property_name: str, factory_method_or_value: Any, expected_type: TypeInfo
    ):
        self.property_name = property_name
        self.expected_type = expected_type
        if isinstance(factory_method_or_value, FactoryMethod):
            self.return_type = TypeInfo[factory_method_or_value.return_annotation]
        else:
            self.return_type = TypeInfo.of(factory_method_or_value)
        super().__init__(
            f"factory for property '{property_name}' "
            f"does not return type '{expected_type}', "
            f"but '{self.return_type}' instead"
        )


class FactoryTypeError(TypedDefaultDictError):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class FactoryMethod:
    def __init__(self, fn: FactoryCallable, prop_name: str, sig: inspect.Signature):
        self.fn = fn
        self.prop_name = prop_name
        self.sig = sig

    @property
    def input_type(self):
        return tuple(self.sig.parameters.values())[0].annotation

    @property
    def return_annotation(self):
        return self.sig.return_annotation

    def __call__(self, value: Any):
        return self.fn(value)

    def verify(self):
        if len(self.sig.parameters) > 1:
            raise FactoryTypeError("factory method cannot have more than one parameter")
        if not self.sig.parameters:
            raise FactoryTypeError("factory method must have at least one parameter")
        if self.sig.return_annotation is inspect.Signature.empty:
            raise FactoryTypeError("factory method must have a return annotation")
        if self.input_type is inspect.Signature.empty:
            raise FactoryTypeError(
                "parameter of factory method must have an annotation"
            )

    def check_input(self, value: Any):
        if not TypeInfo[self.input_type].check_value(value):
            raise PropertyValueError(self.prop_name, value, self.input_type)


def _ns_handler(ns: dict):
    annotations = {
        k: v for k, v in ns.get("__annotations__", {}).items() if k[0] != "_"
    }  # filter out private members
    if any(isinstance(annotation, str) for annotation in annotations.values()):
        raise RuntimeError(
            "TypedDefaultDict cannot be used with "
            "'from __future__ import annotations'"
        )
    schema: Schema = MappingProxyType(
        {
            k: PropertyDVTTuple(ns.get(k), TypeInfo[annotations[k]])
            for k in annotations.keys()
        }
    )
    ns = {k: v for k, v in ns.items() if k not in schema}
    ns["_schema"] = schema
    if "__factory__" in ns:
        raise FactoryTypeError("do not set __factory__, " "use @factorymethod instead")
    factory: Factory = {}
    for k, v in tuple(ns.items()):
        if isinstance(v, FactoryMethod):
            ns.pop(k)
            if not schema[v.prop_name].type.is_type(v.return_annotation):
                raise FactoryReturnValueError(v.prop_name, v, schema[v.prop_name].type)
            factory[v.prop_name] = v
    ns["__factory__"] = factory
    return ns


class _TypedDefaultDictMeta(type):
    def __new__(mcs, name, bases, ns):
        if not bases:
            return type.__new__(mcs, name, bases, ns)
        tp_dict = type.__new__(mcs, name, bases, _ns_handler(ns))
        return tp_dict

    def __getattr__(mcs, k: str):
        if k not in mcs._schema:
            raise AttributeError(k)
        return mcs._schema[k].default

    @DynamicClassAttribute
    def schema(cls) -> Schema:
        return cls._schema


# no more metaclass conflict warning from mypy
_TypedDefaultDict: Type = type.__new__(type, "TypedDefaultDict", (dict,), {})


class TypedDefaultDict(_TypedDefaultDict, metaclass=_TypedDefaultDictMeta):
    schema: Schema

    def update(self, fields: Optional[Mapping[str, Any]] = None, /, **kwargs):
        """
        perform type check, and call factory methods if needed.\n
        then update the dictionary with the given fields and/or kwargs.
        """
        super().update(self._get_fields(fields, **kwargs))

    def on_get_unknown_property(self, k) -> Any:
        raise UnknownPropertyError(k)

    def on_set_unknown_property(self, k: str, v: Any) -> Any:
        raise UnknownPropertyError(k)

    def set(self, k: str, v: Any) -> None:
        if k == _SCHEMA_ATTR:
            raise ReservedPropertyError(k)
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
            v = self._check_value(k, v)
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

    def _check_value(self, k: str, v: Any):
        has_factory = k in self.__factory__
        if k in self.__factory__:
            factory = self.__factory__[k]
            # check if value matches
            # the annotation of the factory method
            factory.check_input(v)
            v = factory(v)
        ti = self._schema[k].type
        if not ti.check_value(v):
            if has_factory:
                raise FactoryReturnValueError(k, v, ti)
            raise PropertyValueError(k, v, ti)
        return v

    def _verify_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        remove_keys = []
        for k, v in data.items():
            if self._check_property(k):
                data[k] = self._check_value(k, v)
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
            return self._verify_data(dict(data or kwargs) or {})

    __factory__: Factory


def factorymethod(prop: str, /):
    def inner(f: FactoryMethod):
        sig = FactoryMethod(f, prop, inspect.signature(f))
        sig.verify()
        return sig

    return inner
