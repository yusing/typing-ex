import pytest
from typing_ex.typed_defaultdict import PropertyValueError, TypedDefaultDict
from typing_ex.builtin_typing import Any, Optional, Dict, List, override


class DictDefault(TypedDefaultDict):
    image: Optional[str] = None
    mounts: List[str] = []
    foo: str = "bar"


class DictNoDV(TypedDefaultDict):
    foo: str
    bar: int


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
