# typing_ex

## A python package for extended `typing` (python 3.8+)

Notice: *yet to be heavily tested*, only simple tests are passed.

## Frozen *[frozen.py](src/typing_ex/frozen.py)*

- `FrozenList`: Immutable `list`
- `FrozenDict`: Immutable `dict`
- `frozen_copy`: Create frozen copy of supported types (`Sequence`, `Set`, `Mapping`)

## TypeInfo *[type_info.py](src/typing_ex/type_info.py)*

- `TypeInfo`: provide type information and run-time type checking
  - `TypeInfo[...].type`: type
  - `TypeInfo[...]..origin`: unsubscripted type
  - `TypeInfo[...]..args`: type arguments
  - `TypeInfo[...]..name`: name of type (including arguments)
  - `TypeInfo.check_union(t1, t2)`: check if union type t1 fulfill union type t2
  - `TypeInfo[...].check_value(value)`: check if value matches the type in type info
  - `TypeInfo[...].is_*`: check if type is _

```python
# type_a | type_b is only supported when python >= 3.10
TypeInfo[list[int | str]].name # list[int | str]
TypeInfo.check_union(int | str, str | int) # True
TypeInfo.check_union(int, int | str) # True
TypeInfo.check_union(int, Union[int | str]) # True
TypeInfo.check_union(Union[int, str], Union[str, int]) # True
TypeInfo.check_union(int | str, str) # False
TypeInfo.check_union(int | str, int | float) # False
TypeInfo.check_union(Union[int, str], int | float) # False
TypeInfo[int | str].check_value(123) # True
TypeInfo[list[int | str]].check_value([1, "2", 3]) # True
TypeInfo[list[int]].check_value([1, "2", 3]) # False
TypeInfo[list[int | str]].check_value([1.0, "2", 3]) # False
```

## TypedDefaultDict *[typed_defaultdict.py](src/typing_ex/typed_defaultdict.py)*

- `TypedDefaultDict`: combining features of `TypedDict` and `defaultdict` with type checking in `__init__`, `__setitem__` and `__setattr__`

- Good for writing schema as a class for `JSON`/`YAML`/`XML`/etc. data which provides both static and runtime type checking.

```python
class TestDict(TypedDefaultDict):
    foo: str | None = "bar" # default value is "bar"
    bar: list[str] = [] # default value is []

testdict = TestDict()
testdict["foo"] # "bar"
testdict.foo # "bar"
testdict.bar # []
# check type and unexpected properties on assignment
testdict.abcd # raises `UnknownPropertyError`
testdict.foo = 123 # raises `PropertyValueError`
testdict = TestDict( # raises `PropertyValueError`
    foo = 123
)

# example of loading from JSON
with open("test.json", "r") as f:
    # will also check on init
    testdict = TestDict(json.load(f))
```

## EnumEx *[enum_ex.py](src/typing_ex/enum_ex.py)*

- `EnumEx` is a `Enum` like class that support enum aliasing (keeping same value but different name).
  - `EnumEx.__iter__`: a generator of all non-alias enum instances.
  - `EnumEx.names`: a tuple of all enum names.
  - `EnumEx.values`: a tuple of all enum values.
  - `EnumEx.enums`: a tuple of all enum instances.
  - `EnumEx.value_type`: returns `__value_type__` if defined, int otherwise.

```python
class AliasedEnum(EnumEx):
    __value_type__ = str # default is int
    foo = "1"
    foo2 = foo # alias
    bar = "2"
    bar2 = bar # alias

foo.name # "foo"
foo.value # 1

foo2.name # "foo2"
foo2.value # 1
foo2.orig_name # "foo"

bar2.name # "bar2"
bar2.value # 2
bar2.orig_name # "bar"
```
