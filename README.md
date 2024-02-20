# typing_ex

## A python package for extended `typing` (python 3.8+)

Notice: Even with all tests passed, unexpected bugs might occur on edge cases

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=coverage)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=bugs)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=yusing_typing-ex&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=yusing_typing-ex)

## Frozen *[frozen.py](src/typing_ex/frozen.py)*

- `FrozenList`: Immutable `list`
- `FrozenDict`: Immutable `dict`
- `frozen_copy`: Create frozen copy of supported types (`Sequence`, `Set`, `Mapping`)

## TypeInfo *[type_info.py](src/typing_ex/type_info.py)*

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

```python
# type_a | type_b is only supported when python >= 3.10
TypeInfo.check_union(int | str, str | int) # True
TypeInfo.check_union(int, int | str) # True
TypeInfo.check_union(int, Union[int | str]) # True
TypeInfo.check_union(Union[int, str], Union[str, int]) # True
TypeInfo.check_union(int | str, str) # False
TypeInfo.check_union(int | str, int | float) # False
TypeInfo.check_union(Union[int, str], int | float) # False

TypeInfo.of([1, 2.0, "3"]) # == TypeInfo[list[int | float | str]]

TypeInfo[list[int | str]].name # list[int | str]
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

    ```python
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

        d = TestDict(baz="asdf")
        d._extra_props["baz"] # "asdf"
    ```

  - `TypedDefaultDict.set`: set a property to a value without property check and type check
  - `@factorymethod(property_name: str)`: defines a factory method for property
    - used when the input type is different than property type
    - factory method must have type annotation for both input and return.
    - factory method should be used inside `TypedDefaultDict`

    ```python
      class SomeDict(TypedDefaultDict):
          foo: str = "foo"
          bar: str = "bar"
          baz: str = "baz"

          @factorymethod("baz")
          def baz_factory(value: list[str]) -> CustomClass:
              return ",".join(value)
      
      d = SomeDict(foo="bla", baz=["hello", "world", "!"])
      d.foo # "bla"
      d.bar # "bar" (default value)
      d.baz # "hello world !" (converted from factory method)
    ```

- Attributes without type annotation or starting with underscore "_" will be treated as class variables

- Good for writing schema as a class for `JSON`/`YAML`/`XML`/etc. data which provides both static and runtime type checking. Or you can use it as a `class`, but without the need to write `__init__`

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
