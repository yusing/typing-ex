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

## Notice

Even with all tests passed, unexpected bugs might occur on edge cases

## Project Overview

I made this for fun, and also as a dependency for my other project [docker-playbook](https://github.com/yusing/docker-playbook) (working in progress).

If you found any bug, or have any suggestions, please let me know.

## Target Audience

People who want more strict type checking and less runtime errors / bugs.

## Comparison

[typeguard](https://github.com/agronholm/typeguard) provides runtime type checking for functions and class methods with `@typeguard` decorator. This project aims to enforce type annotation instead.

[mypy](https://github.com/python/mypy) provides static type checking, a good companion for this project to provide both static and runtime type checking.

## Installation

`pip install typing-ex`

## Modules/Classes

All Docs in [docs](docs/) (AI generated with small modification, may be incomplete)

### TypeInfo *[type_info.py](typing_ex/type_info.py)* [Documentation](docs/TypeInfo.md)

`TypeInfo` provides type information and run-time type checking, no more `isinstance`, `issubclass`, `is`, `==` mess.

Useful when you want to check / assert variable type in runtime.

`TypeInfo` provides type information and run-time type checking

- `TypeInfo.get(t)`: alias of `TypeInfo[t]`
- `TypeInfo.of(value)`: return a `TypeInfo` object that represents the type of `value`
- `TypeInfo.check_union(t1, t2)`: check if union type t1 fulfill union type t2
- `TypeInfo[t].type`: type
- `TypeInfo[t].origin`: unsubscripted type
- `TypeInfo[t].args`: type arguments
- `TypeInfo[t].name`: name of type (including arguments)
- `TypeInfo[t].check_value(value)`: check if value matches the type in type info
- `TypeInfo[t].is_*`: check if type is _

### TypedDefaultDict *[typed_defaultdict.py](typing_ex/typed_defaultdict.py)* [Documentation](docs/TypedDefaultDict.md)

`TypedDefaultDict` combines features of `TypedDict` and `defaultdict` with type checking in `__init__`, `__setitem__`, `__setattr__` and `update()`

It is similar to `pydantic.BaseModel`

- `TypedDefaultDict.schema`: the schema dictionary: `MappingProxyType[str, NamedTuple[default: Any, type:TypeInfo]]`
- `TypedDefaultDict.on_get_unknown_property`: called on getting unknown property
- `TypedDefaultDict.on_set_unknown_property`: called on setting unknown property
- `TypedDefaultDict.set`: set a property to a value without property check and type check
- `@factorymethod(property_name: str)`: defines a factory method for property

- Attributes without type annotation or starting with underscore "_" will be treated as class variables

- Good for writing schema as a class for `JSON`/`YAML`/`XML`/etc. data which provides both static and runtime type checking.

- You can use it to make new classes too, no more `__init__()`!

### EnumEx *[enum_ex.py](typing_ex/enum_ex.py)* [Documentation](docs/EnumEx.md)

`EnumEx` is a `Enum` like class that support enum aliasing (keeping same value but different name). Useful if you want to output a different name but with same internal implementation.

- `EnumEx.__iter__`: a generator of all non-alias enum instances.
- `EnumEx.names`: a tuple of all enum names.
- `EnumEx.values`: a tuple of all enum values.
- `EnumEx.enums`: a tuple of all enum instances.
- `EnumEx.value_type`: returns `__value_type__` if defined, int otherwise.

- `EnumEx.X.value`: value of enum X
- `EnumEx.X.name`: name of enum X (i.e. X)
- `EnumEx.X_ALIAS.orig_name`: original name of enum X_ALIAS (i.e. X)
- `EnumEx.X_ALIAS.origin`: origin enum of X_ALIAS (i.e. EnumEx.X)

```python
class ActionEnum(EnumEx):
    __value_type__ = int  # Optional: Specify value type (defaults to `int`)
    STOP = 0
    CREATE = 1
    START = CREATE # Alias for CREATE
    UPDATE = 2
    RESTART = UPDATE # Alias for RESTART
print(Action.CREATE)  # Output: CREATE 
print(Action.START)  # Output: START
print(Action.START.orig_name)  # Output: CREATE
print(MyEnum.START.value)  # Output: 1

class Action:
    action :ActionEnum
    def start(self): ...
    def stop(self): ...
    def restart(self): ...
    def execute(self):
        with ProgressBar() as progress:
            progress.text = f"{action.name.lower()}ing..."
            getattr(self, action.orig_name.lower())()
            progress.text = "Done"
```

### Frozen *[frozen.py](typing_ex/frozen.py)*

Useful when you want to lock data after processing, without static type checker complaining (i.e. when casting it to `tuple`)

- `FrozenList`: Immutable `list`
- `FrozenDict`: Immutable `dict`
- `frozen_copy`: Create frozen copy of supported types (`Sequence`, `Set`, `Mapping`)