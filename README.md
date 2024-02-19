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

- `TypedDefaultDict`: combining features of `TypedDict` and `defaultdict` with type checking in `__init__`, `__setitem__`, `__setattr__` and `update`
  - `TypedDefaultDict.schema`: the schema dictionary: `MappingProxyType[str, NamedTuple[default: Any, type:TypeInfo]]`
  - `TypedDefaultDict.on_get_unknown_property`: called on getting unknown property
  - `TypedDefaultDict.on_set_unknown_property`: called on setting unknown property
  - `TypedDefaultDict.set`: set a property to a value without property check and type check

- Attributes without type annotation or starting with underscore "_" will be treated as class variables

- You can override `on_get_unknown_property` and `on_set_unknown_property` to override the behavior when getting or setting unknown property, raises `UnknownPropertyError` by default.
  - `on_get_unknown_property(k)`: either raise an error or return a value based on k
  - `on_set_unknown_property(k, v)`: raise an error / return a value based on `(k, v)` to set `k` to new value / process and return `None` to ignore

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

# example overriding on_*_unknown_property
class TestDict(TypedDefaultDict):
    foo: str = "foo"
    bar: str = "bar"

    _extra_props: dict[str, Any] = {} # class variable

    @override
    def on_get_unknown_property(self, k) -> Any:
        raise AttributeError(k)

    @override
    def on_set_unknown_property(self, k: str, v: Any) -> Any:
        self._extra_props[k] = v
        return None
```

## EnumEx *[enum_ex.py](src/typing_ex/enum_ex.py)*

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
