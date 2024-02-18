import pytest
from typing_ex.typed_defaultdict import PropertyValueError, TypedDefaultDict
from typing_ex.builtin_typing import Optional
from typing import List


class Dict(TypedDefaultDict):
    image: Optional[str] = None
    mounts: List[str] = []
    foo: str = "bar"


class DictNoDV(TypedDefaultDict):
    foo: str
    bar: int


def test_default_values():
    assert Dict.image is None
    assert Dict.mounts == []
    assert Dict.foo == "bar"
    assert DictNoDV.foo is None
    assert DictNoDV.bar is None


def test_init_getattr_getitem():
    d = Dict(image="foo", mounts=["foo", "bar"])
    assert d["image"] == "foo", d["image"]
    assert d["foo"] == "bar", d["foo"]  # default value
    assert d["mounts"] == ["foo", "bar"], d["mounts"]
    assert d.image == "foo", d.image
    assert d.foo == "bar", d.foo  # default value
    assert d.mounts == ["foo", "bar"], d.mounts


def test_invalid_property_type():
    with pytest.raises(PropertyValueError):
        Dict(image="foo", mounts=["foo", 1])


class DictWithPropertiesAndMethods(TypedDefaultDict):
    foo: str = "foo"
    bar: str = "bar"

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


def test_properties_and_methods():

    assert DictWithPropertiesAndMethods.foo_bar_cls_method() == "foobar"
    assert DictWithPropertiesAndMethods.foo_bar_static_method() == "foobar"
    test_dict = DictWithPropertiesAndMethods(foo="bar", bar="foo")
    assert test_dict.foo_bar == "barfoo"
    assert test_dict.foo_bar_method() == "barfoo"
    assert test_dict.foo_bar_cls_method() == "foobar"
    assert test_dict.foo_bar_static_method() == "foobar"
