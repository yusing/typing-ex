# TypeInfo Documentation

[TypeInfo](../typing_ex/type_info.py) is a Python class designed to provide detailed type information, including support for generic types and union types. It is part of a custom module that extends Python's built-in typing capabilities. This documentation outlines the public interface and usage of [TypeInfo](../typing_ex/type_info.py).

## Overview

[TypeInfo](../typing_ex/type_info.py) offers a way to introspect types in Python, including complex types like generics (`List[int]`, `Dict[str, int]`) and unions (`int | str` in Python 3.10+, `Union[int, str]` in earlier versions). It provides properties and methods to access the underlying type information, such as the type's origin, its arguments, and whether it represents a union type.

## Usage

`TypeInfo` should not be instantiated directly. Instead, use the `TypeInfo.get()` class method or the `TypeInfo[]` syntax to obtain a `TypeInfo` instance for a given type.

### Getting TypeInfo Instances

```python
from typing_ex.type_info import TypeInfo

# For a simple type
int_info = TypeInfo[int]

# For a generic type
list_int_info = TypeInfo[List[int]]

# For a union type
union_info = TypeInfo[Union[int, str]] # (Python < 3.10)
union_info = TypeInfo[int | str] # (Python 3.10+)

# Using the get() method
dict_info = TypeInfo.get(Dict[str, int])
```

### Properties

- `type`: Returns the type associated with the `TypeInfo` instance.
- `origin`: Returns the origin of the type (e.g., the base type for generics).
- `args`: Returns a tuple of the type's arguments (e.g., element types for generics).
- `name`: Returns a string representation of the type.
- `is_union_type`: Indicates whether the type is a union type.
- `is_mapping`, `is_set`, `is_sequence`: Indicate whether the type is a mapping, set, or sequence, respectively.

### Methods

- `is_subclass(t_super)`: Checks if the type is a subclass of `t_super`.
- `check_union(t1, t2)`: Class method to check if union type `t1` fulfills the union type `t2`.
- `is_type(t)`: Checks if the `TypeInfo` instance represents the exact type `t`.
- `check_value(value)`: Checks if the given value conforms to the type.
- `of(value)`: Class method to get a `TypeInfo` instance based on the value's type, including generic arguments.

### Examples

```python
from typing_ex.type_info import TypeInfo

# Check if a value matches a specific type
assert TypeInfo[int].check_value(10)

# Work with generic types
assert TypeInfo[List[int]].check_value([1, 2, 3])

# Union types
assert TypeInfo[int | str].check_value("hello") # (Python 3.10+)
assert TypeInfo[Union[int, str]] .check_value("hello") # (Python < 3.10)

# Nested types
assert TypeInfo[Dict[str, List[int]]].check_value({"numbers": [1, 2, 3]})

# TypeInfo.of
TypeInfo.of([1, 2.0, "3"]) # == TypeInfo[List[int | str | float]]
```

## Notes

- `TypeInfo` leverages Python's typing module and extends its functionality to provide more detailed type information.
- It supports Python's newer type hinting features, including union types with the `|` operator introduced in Python 3.10.
- The class is designed to be used with built-in types and types from the `typing` module.

This documentation covers the public interface of `TypeInfo`. The class also includes internal methods and properties prefixed with an underscore, which are intended for internal use and not documented here.
