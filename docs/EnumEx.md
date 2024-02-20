# EnumEx Documentation

[EnumEx](../typing_ex/enum_ex.py) is an enhanced enumeration class for Python, extending the functionality of the builtin `Enum` class. It introduces features such as enum aliasing, where multiple names can refer to the same value, and type specification for enum values. This document outlines the public interface and usage of [EnumEx](../typing_ex/enum_ex.py).

## Overview

[EnumEx](../typing_ex/enum_ex.py) allows for the creation of enumerations where members can have aliases, meaning different names referring to the same value. It also supports specifying the type of the enum values, allowing for more than just integers. This makes [EnumEx](../typing_ex/enum_ex.py) a versatile tool for creating enumerations in Python.

## Usage

To use [EnumEx](../typing_ex/enum_ex.py), define a subclass of [EnumEx](../typing_ex/enum_ex.py) and define enumeration members as class attributes. Optionally, specify [__value_type__](../typing_ex/enum_ex.py#118%2C35-118%2C35) to enforce a specific type for enum values.

### Defining an EnumEx

```python
from typing_ex.enum_ex import EnumEx

class MyEnum(EnumEx):
    __value_type__ = str  # Optional: Specify value type
    MEMBER1 = "value1"
    MEMBER2 = "value2"
    MEMBER1_ALIAS = MEMBER1  # Alias for MEMBER1
```

### Accessing Enum Members

Enum members can be accessed using their names. Aliases will refer to the same underlying value as the member they alias.

```python
print(MyEnum.MEMBER1)  # Output: MEMBER1
print(MyEnum.MEMBER1_ALIAS)  # Output: MEMBER1_ALIAS
```

### Enum Properties

- `name`: Returns the name of the enum member.
- `value`: Returns the value of the enum member.
- `orig_name`: Returns the original name of the enum member if it's an alias, or its own name otherwise.
- `origin`: Returns the original enum member for an alias.
- `is_alias`: Indicates whether the enum member is an alias.

### Iterating Over Enum Members

Iterating over an `EnumEx` class will yield all non-alias members.

```python
for member in MyEnum:
    print(member)
```

### Enum Class Properties

- `names`: A tuple of all member names, including aliases.
- `values`: A tuple of all unique values.
- `enums`: A tuple of all enum instances, including aliases.
- `value_type`: The type of the enum values, defaulting to `int` if not specified.

## Error Handling

Attempting to access an undefined member will raise an `AttributeError`.

## Notes

- [EnumEx](../typing_ex/enum_ex.py) is designed to be compatible with Python's type hinting and static analysis tools.
- It supports Python's newer type hinting features, allowing for enums with values other than integers.

This documentation covers the public interface of [EnumEx](../typing_ex/enum_ex.py). The class also includes internal methods and properties prefixed with an underscore, which are intended for internal use and not documented here.
