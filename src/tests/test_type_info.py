from __future__ import annotations
from typing_ex.type_info import TypeInfo, Union
from typing_ex.builtin_typing import UnionType
import sys


def test_check_union():
    if sys.version_info >= (3, 10):
        assert TypeInfo.check_union(int | str, str | int)
        assert TypeInfo.check_union(int, int | str)
        assert not TypeInfo.check_union(int | str, str)
        assert not TypeInfo.check_union(int | str, int | float)
        assert TypeInfo.check_union(Union[int, str], str | int)
        assert TypeInfo.check_union(int, Union[int | str])
        assert not TypeInfo.check_union(Union[int, str], int | float)

    assert TypeInfo.check_union(Union[int, str], Union[str, int])
    assert not TypeInfo.check_union(Union[int, str], str)
    assert not TypeInfo.check_union(Union[int, str], Union[int, float])
    assert not TypeInfo.check_union(Union[int, str], Union[int, float])


def test_check_value():
    if sys.version_info >= (3, 10):
        assert TypeInfo[dict[int, str]].check_value({1: "2"})
        assert TypeInfo[dict[str, int | str]].check_value({"1": 1, "2": "2"})
        assert TypeInfo[list[int | str]].check_value([1, "2", "3"])
        assert not TypeInfo[int | str].check_value(1.0)
        assert not TypeInfo[dict[int, str]].check_value({"2": "2"})
        assert not TypeInfo[dict[int, int | str]].check_value({"2": 2, "3": "3"})
        assert not TypeInfo[dict[int, str]].check_value({1.0: "2"})
        assert not (TypeInfo[list[int | str]].check_value([1.0, "2", "3"]))
    assert TypeInfo[int].check_value(1)
    assert TypeInfo[Union[int, str]].check_value(1)
    assert TypeInfo[Union[int, str]].check_value("1")
    assert not TypeInfo[int].check_value(1.0)


def test_type_name():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].name == "int | str"
        assert TypeInfo[dict[int, float]].name == "dict[int, float]"
        assert TypeInfo[Union[int, str]].name == "int | str"
    else:
        assert TypeInfo[Union[int, str]].name == "typing.Union[int, str]"
    assert TypeInfo[int].name == "int"
    assert TypeInfo[None].name == "None"
    assert str(TypeInfo[str]) == "str"


def test_type_origin():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].origin is UnionType
        assert TypeInfo[dict[int, str]].origin is dict
        assert TypeInfo[Union[int, str]].origin is UnionType
    else:
        assert TypeInfo[Union[int, str]].origin is Union
    assert TypeInfo[int].origin is int
    assert TypeInfo[None].origin is None


def test_type_args():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].args == (int, str)
        assert TypeInfo[dict[int, float]].args == (int, float)
    assert TypeInfo[int].args == ()
    assert TypeInfo[Union[int, float]].args == (int, float)
    assert TypeInfo[None].args == ()
