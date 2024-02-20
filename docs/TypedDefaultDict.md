# TypedDefaultDict Documentation

[TypedDefaultDict](../typing_ex/typed_defaultdict.py) is a Python class that extends the functionality of Python's built-in type, allowing for type annotations and default values for dictionary keys. It provides a way to define a schema for a dictionary, where each key has a specific type and an optional default value. This document outlines the public interface and usage of [TypedDefaultDict](../typing_ex/typed_defaultdict.py).

## Overview

[TypedDefaultDict](../typing_ex/typed_defaultdict.py) uses Python's type annotations to enforce type checks at runtime. It allows for specifying default values for keys, which are used if a key is not present in the dictionary. Additionally, it supports factory methods for more complex initialization logic.

## Usage

To use [TypedDefaultDict](../typing_ex/typed_defaultdict.py), define a subclass and annotate your dictionary keys with their expected types. You can also assign default values to keys directly in the class definition.

### Defining a TypedDefaultDict

```python
from typing_ex.typed_defaultdict import TypedDefaultDict
from typing import Optional, List

class MyDict(TypedDefaultDict):
    key1: str = "default value"
    key2: Optional[int] # = None
    key3: List[str] = []
```

### Instantiation and Access

```python
# kwargs way
my_dict = MyDict(key1="value1", key2=10)

# dict way
my_dict = MyDict({
    "key1": "value1",
    "key2": 10
})

print(my_dict["key1"])  # Output: value1
print(my_dict.key2)  # Output: 10
print(my_dict.key3)  # Output: []
```

### Factory Methods

For keys requiring complex initialization, define a factory method using the `@factorymethod` decorator. The factory method takes a value and returns an initialized object of the specified type.

Factory method must has proper input and return type annotation.

Errors will be raised if input value type or return type mismatched their annotation

```python
from typing_ex.typed_defaultdict import factorymethod

class MyDict(TypedDefaultDict):
    complex_key: List[int]

    @factorymethod("complex_key")
    def complex_key_factory(value: list) -> List[int]:
        return [int(x) for x in value]

my_dict = MyDict(complex_key=["1", "2", "3"])
print(my_dict.complex_key)  # Output: [1, 2, 3]
```

## Error Handling

`TypedDefaultDict` raises specific exceptions for various error conditions:

- `UnknownPropertyError`: Raised when accessing or setting an undefined key.
- `ReservedPropertyError`: Raised when attempting to use a reserved property name.
- `PropertyValueError`: Raised when a value does not match the expected type.
- `FactoryReturnValueError`: Raised when a factory method returns a value of the wrong type.
- `FactoryTypeError`: Raised for errors related to factory method definitions.

## Overriding Behavior

You can override the behavior for unknown properties by implementing the `on_get_unknown_property` and `on_set_unknown_property` methods.

```python
class MyDict(TypedDefaultDict):
    @override
    def on_get_unknown_property(self, k) -> Any:
        # Custom behavior for getting an unknown property
        pass

    @override
    def on_set_unknown_property(self, k: str, v: Any):
        # Custom behavior for setting an unknown property
        # Must return a non-None value
        return v
```

## Notes

- `TypedDefaultDict` is designed to work with Python's type annotations, providing runtime type checking and default values for dictionary keys.
- It supports Python's newer type hinting features, including generics and optional types.
- The class is designed to be used with built-in types and types from the `typing` module.

This documentation covers the public interface of `TypedDefaultDict`. The class also includes internal methods and properties prefixed with an underscore, which are intended for internal use and not documented here.
