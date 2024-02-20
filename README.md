# typing-ex

## A python package for extended `typing` (python 3.8+)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=coverage)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=bugs)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)

## Installation
`pip install typing-ex`

## Notice

Even with all tests passed, unexpected bugs might occur on edge cases

## Frozen *[frozen.py](typing_ex/frozen.py)*

- `FrozenList`: Immutable `list`
- `FrozenDict`: Immutable `dict`
- `frozen_copy`: Create frozen copy of supported types (`Sequence`, `Set`, `Mapping`)

## TypeInfo *[type_info.py](typing_ex/type_info.py)* [Documentation](docs/TypeInfo.md)

- `TypeInfo`: provide type information and run-time type checking
  - `TypeInfo.get(t)`: alias of `TypeInfo[t]`
  - `TypeInfo.of(value)`: return a `TypeInfo` object that represents the type of `value`
  - `TypeInfo.check_union(t1, t2)`: check if union type t1 fulfill union type t2
  - `TypeInfo[t].type`: type
  - `TypeInfo[t].origin`: unsubscripted type
  - `TypeInfo[t].args`: type arguments
  - `TypeInfo[t].name`: name of type (including arguments)
  - `TypeInfo[t].check_value(value)`: check if value matches the type in type info
  - `TypeInfo[t].is_*`: check if type is _

## TypedDefaultDict *[typed_defaultdict.py](typing_ex/typed_defaultdict.py)* [Documentation](docs/TypedDefaultDict.md)

- `TypedDefaultDict`: combining features of `TypedDict` and `defaultdict` with type checking in `__init__`, `__setitem__`, `__setattr__` and `update`
  - `TypedDefaultDict.schema`: the schema dictionary: `MappingProxyType[str, NamedTuple[default: Any, type:TypeInfo]]`
  - `TypedDefaultDict.on_get_unknown_property`: called on getting unknown property
  - `TypedDefaultDict.on_set_unknown_property`: called on setting unknown property
  - `TypedDefaultDict.set`: set a property to a value without property check and type check
  - `@factorymethod(property_name: str)`: defines a factory method for property

- Attributes without type annotation or starting with underscore "_" will be treated as class variables

- Good for writing schema as a class for `JSON`/`YAML`/`XML`/etc. data which provides both static and runtime type checking. Or you can use it as a `class`, but without the need to write `__init__`

## EnumEx *[enum_ex.py](typing_ex/enum_ex.py)* [Documentation](docs/EnumEx.md)

- `EnumEx` is a `Enum` like class that support enum aliasing (keeping same value but different name).
  - `EnumEx.__iter__`: a generator of all non-alias enum instances.
  - `EnumEx.names`: a tuple of all enum names.
  - `EnumEx.values`: a tuple of all enum values.
  - `EnumEx.enums`: a tuple of all enum instances.
  - `EnumEx.value_type`: returns `__value_type__` if defined, int otherwise.

  - `EnumEx.X.value`: value of enum X
  - `EnumEx.X.name`: name of enum X (i.e. X)
  - `EnumEx.X_ALIAS.orig_name`: original name of enum X_ALIAS (i.e. X)
  - `EnumEx.X_ALIAS.origin`: origin enum of X_ALIAS (i.e. EnumEx.X)
