import pytest
from typing_ex.type_info import TypeInfo
from typing_ex.typed_defaultdict import (
    FactoryReturnValueError,
    FactoryTypeError,
    PropertyValueError,
    ReservedPropertyError,
    TypedDefaultDict,
    UnknownPropertyError,
    factorymethod,
)
from typing_ex.builtin_typing import Any, Optional, Dict, List, override


class DictDefault(TypedDefaultDict):
    image: Optional[str] = None
    mounts: List[str] = []
    foo: str = "bar"

class DictNoDV(TypedDefaultDict):
    foo: str
    bar: int

def test_schema():
    assert "image" in DictDefault.schema
    assert "mounts" in DictDefault.schema
    assert "foo" in DictDefault.schema
    assert DictDefault.schema == {
        "image": (None, TypeInfo[Optional[str]]),
        "mounts": ([], TypeInfo[List[str]]),
        "foo": ("bar", TypeInfo[str]),
    }

    assert "foo" in DictNoDV.schema
    assert "bar" in DictNoDV.schema
    assert DictNoDV.schema == {
        "foo": (None, TypeInfo[str]),
        "bar": (None, TypeInfo[int]),
    }

def test_default_values():
    assert DictDefault.image is None
    assert DictDefault.mounts == []
    assert DictDefault.foo == "bar"
    assert DictNoDV.foo is None
    assert DictNoDV.bar is None


def test_init_getattr_getitem():
    d = DictDefault(image="foo", mounts=["foo", "bar"])
    assert d["image"] == "foo", d["image"]
    assert d["foo"] == "bar", d["foo"]  # default value
    assert d["mounts"] == ["foo", "bar"], d["mounts"]
    assert d.image == "foo", d.image
    assert d.foo == "bar", d.foo  # default value
    assert d.mounts == ["foo", "bar"], d.mounts


def test_unknown_property():
    d = DictDefault()
    with pytest.raises(UnknownPropertyError):
        d.abc
    with pytest.raises(UnknownPropertyError):
        d.abc = 1234
    with pytest.raises(UnknownPropertyError):
        d["abc"] = 1234
    with pytest.raises(UnknownPropertyError):
        d.update({
            "abc": 1234
        })
    d.set("abc", 1234) # set does not raise UnknownPropertyError

def test_reserved_property():
    with pytest.raises(ReservedPropertyError):
        DictDefault(_schema=1)
    with pytest.raises(ReservedPropertyError):
        d = DictDefault()
        d._schema = 1
    with pytest.raises(ReservedPropertyError):
        d["_schema"] = 1
    with pytest.raises(ReservedPropertyError):
        d.update({
            "_schema": 1
        })
    with pytest.raises(ReservedPropertyError):
        d.set("_schema", 1)

def test_invalid_property_type():
    with pytest.raises(PropertyValueError):
        DictDefault(image="foo", mounts=["foo", 1])


class DictWithPropertiesAndMethods(TypedDefaultDict):
    foo: str = "foo"
    bar: str = "bar"

    _extra_props: Dict[str, Any] = {}

    @property
    def foo_bar(self) -> str:
        return self.foo + self.bar

    def foo_bar_method(self) -> str:
        return self.foo + self.bar

    @classmethod
    def foo_bar_cls_method(cls) -> str:
        return cls.foo + cls.bar

    @staticmethod
    def foo_bar_static_method() -> str:
        return DictWithPropertiesAndMethods.foo + DictWithPropertiesAndMethods.bar

    @override
    def on_get_unknown_property(self, k) -> Any:
        raise RuntimeError(f"hello {k}")

    @override
    def on_set_unknown_property(self, k: str, v: Any):
        self._extra_props[k] = v


def test_properties_and_methods():

    assert DictWithPropertiesAndMethods.foo_bar_cls_method() == "foobar"
    assert DictWithPropertiesAndMethods.foo_bar_static_method() == "foobar"
    test_dict = DictWithPropertiesAndMethods(foo="bar", bar="foo")
    assert test_dict.foo_bar == "barfoo"
    assert test_dict.foo_bar_method() == "barfoo"
    assert test_dict.foo_bar_cls_method() == "foobar"
    assert test_dict.foo_bar_static_method() == "foobar"


def test_overridden_set_unknown_prop():
    test_dict = DictWithPropertiesAndMethods(foo="bar", bar="foo")
    test_dict.update(baz="baz", baf="baf")
    assert test_dict._extra_props["baz"] == "baz"
    assert test_dict._extra_props["baf"] == "baf"
    test_dict.update({"bar": "bararara", "bab": 2})
    assert test_dict.bar == "bararara"
    assert test_dict._extra_props["bab"] == 2


def test_overridden_get_unknown_prop():
    test_dict = DictWithPropertiesAndMethods()
    with pytest.raises(RuntimeError, match="hello baz"):
        baz = test_dict.baz
    with pytest.raises(RuntimeError, match="hello baf"):
        baf = test_dict["baf"]


def test_set():
    test_dict = DictWithPropertiesAndMethods()
    test_dict.set("blablabla", {"a": 1, "b": 2})
    assert test_dict.blablabla["a"] == 1
    assert test_dict.blablabla["b"] == 2


class Child(TypedDefaultDict):
    name: str
    gender: str
    age: int


class Parent(TypedDefaultDict):
    name: str
    children: List[Child]

    @factorymethod("children")
    def children_factory(v: List[dict]) -> List[Child]:
        return [Child(**c) for c in v]


def test_factory():
    nested = Parent(
        name="foo",
        children=[
            dict(name="bar", gender="male", age=10),
            dict(name="baz", gender="female", age=20),
        ],
    )
    assert nested.name == "foo"
    assert len(nested.children) == 2
    assert nested.children[0].name == "bar"
    assert nested.children[0].gender == "male"
    assert nested.children[0].age == 10
    assert nested.children[1].name == "baz"
    assert nested.children[1].gender == "female"
    assert nested.children[1].age == 20


def test_invalid_factory():
    with pytest.raises(FactoryTypeError, match="annotation"):

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory(v) -> str:
                return v

    with pytest.raises(FactoryTypeError, match="annotation"):

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory(v: str):
                return v

    with pytest.raises(FactoryTypeError, match="must have at least one parameter"):

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory():
                return

    with pytest.raises(FactoryTypeError, match="cannot have more than one parameter"):

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory(a: int, b: str):
                return

    with pytest.raises(
        FactoryReturnValueError,
        match="factory for property 'foo' "
        "does not return type 'str', "
        "but 'int' instead",
    ): # return annotation does not match type annatation of `foo`

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory(v: str) -> int:
                return int(v)

    with pytest.raises(
        FactoryReturnValueError,
        match="factory for property 'foo' "
        "does not return type 'str', "
        "but 'int' instead",
    ): # match annotation but return wrong type

        class InvalidDict(TypedDefaultDict):
            foo: str

            @factorymethod("foo")
            def foo_factory(v: str) -> str:
                return int(v)

        InvalidDict(foo="123")
