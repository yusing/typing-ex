import pytest
import typing_ex.type_info as type_info
from typing_ex.type_info import TypeInfo
from typing_ex.builtin_typing import (
    Union,
    UnionType,
    Optional,
    Any,
    Dict,
    Set,
    List,
)
import sys


def test_internal():
    assert type_info._get_aliased_type(list) is List
    assert type_info._get_aliased_type(List) is List
    assert type_info._get_aliased_type(Any) is Any
    assert type_info._get_unaliased_type(list) is list
    assert type_info._get_unaliased_type(List) is list
    assert type_info._get_unaliased_type(Any) is Any

    assert type_info._construct_union({int}) is int
    assert type_info._construct_union({int, str}) is Union[int, str]
    assert (
        type_info._construct_union({int, str, Dict[int, str]})
        == Union[int, str, Dict[int, str]]
    )

    if sys.version_info >= (3, 10):
        assert type_info._construct_generic(list, (int,)) == list[int]
        assert type_info._construct_generic(dict, (float, bytes)) == dict[float, bytes]
    assert type_info._construct_generic(List, (int,)) == List[int]
    assert type_info._construct_generic(Dict, (float, bytes)) == Dict[float, bytes]

    if sys.version_info >= (3, 10):
        assert type_info._is_union_type(int | str)
        assert type_info._is_union_type(int | None)
    assert type_info._is_union_type(Union[int, str])
    assert type_info._is_union_type(Union[int, None])
    assert type_info._is_union_type(Optional[int])  # same as Union[int, None]
    assert not type_info._is_union_type(int)  # same as Union[int, None]
    assert not type_info._is_union_type(None)  # same as Union[int, None]
    assert not type_info._is_union_type(Any)  # same as Union[int, None]


def test_initiate():
    with pytest.raises(RuntimeError):
        TypeInfo()
    with pytest.raises(RuntimeError):
        TypeInfo(str)


def test_check_union():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].is_union_type
        assert TypeInfo.check_union(int | str, str | int)
        assert TypeInfo.check_union(int, int | str)
        assert not TypeInfo.check_union(int | str, str)
        assert not TypeInfo.check_union(int | str, int | float)
        assert TypeInfo.check_union(Union[int, str], str | int)
        assert TypeInfo.check_union(int, Union[int, str])
        assert not TypeInfo.check_union(Union[int, str], int | float)
    assert TypeInfo[Union[int, str]].is_union_type
    assert TypeInfo[Optional[int]].is_union_type
    assert not TypeInfo[int].is_union_type
    assert not TypeInfo[None].is_union_type
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


def test_optional():
    assert TypeInfo[Optional[str]].check_value(None)
    assert TypeInfo[Optional[str]].check_value("1")
    assert not TypeInfo[Optional[str]].check_value(1)


def test_check_value_nested_type():
    assert TypeInfo[List[Dict[str, int]]].check_value([{"1": 1, "2": 2}])
    assert not TypeInfo[List[Dict[str, int]]].check_value([{"1": 1, 2: 2}])
    assert TypeInfo[List[Dict[str, int]]].check_value([])
    assert TypeInfo[List[Dict]].check_value([{1: 1.0, "2": 2}])
    assert TypeInfo[List[Dict]].check_value([])


def test_nested_optional():
    assert TypeInfo[List[Optional[Dict]]].check_value([None, {"1": 1}])
    assert TypeInfo[List[Optional[Dict]]].check_value([None, None])
    assert TypeInfo[List[Optional[Dict]]].check_value([{"1": 1}, None])
    t_test = Optional[Dict[Optional[str], Optional[int]]]
    assert TypeInfo[t_test].check_value(None)
    assert TypeInfo[t_test].check_value({"1": 1})
    assert TypeInfo[t_test].check_value({"1": 1, "2": 2})
    assert TypeInfo[t_test].check_value({None: 1, "2": None})
    assert TypeInfo[t_test].check_value({None: None, "2": None})
    assert not TypeInfo[t_test].check_value({"1": 1, 2: 2})
    assert not TypeInfo[t_test].check_value({1: None})


def test_any():
    assert TypeInfo[Any].check_value(1)
    assert TypeInfo[Any].check_value("123")
    assert TypeInfo[List[Any]].check_value([1, 2, 3])
    assert TypeInfo[List[Any]].check_value([1.0, 2.0, 3.0])
    assert TypeInfo[Dict[str, Any]].check_value({"1": 1, "2": "2", "3": 3.0})
    assert TypeInfo[Dict[Any, str]].check_value({1: "1", "2": "2", 3.0: "3"})
    assert TypeInfo[Dict[Any, Any]].check_value({1.0: 1, "2": [2], 3.0: b"3"})
    assert not TypeInfo[List[Any]].check_value({1, 2, 3.0})
    assert not TypeInfo[List[Any]].check_value(123)
    assert not TypeInfo[Dict[str, Any]].check_value({"1": 1, 2: "2", "3": 3})
    assert not TypeInfo[Dict[Any, str]].check_value({1: "1", 2: "2", 3.0: 3})


def test_type_name():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].name == "int | str"
        assert TypeInfo[Union[int, str]].name == "int | str"
    else:
        assert TypeInfo[Union[int, str]].name == "typing.Union[int, str]"
    assert TypeInfo[Dict[int, float]].name == "typing.Dict[int, float]"
    assert TypeInfo[int].name == "int"
    assert TypeInfo[None].name == "None"
    assert str(TypeInfo[str]) == "str"


def test_type_origin():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].origin is UnionType
        assert TypeInfo[Union[int, str]].origin is UnionType
    else:
        assert TypeInfo[Union[int, str]].origin is Union
    assert TypeInfo[Dict[int, str]].origin is dict
    assert TypeInfo[int].origin is int
    assert TypeInfo[None].origin is None


def test_type_args():
    if sys.version_info >= (3, 10):
        assert TypeInfo[int | str].args == (int, str)
    assert TypeInfo[Dict[int, float]].args == (int, float)
    assert TypeInfo[int].args == ()
    assert TypeInfo[Union[int, float]].args == (int, float)
    assert TypeInfo[None].args == ()


def test_of():
    assert TypeInfo.of(None).type is None
    assert TypeInfo.of(1).type is int
    assert TypeInfo.of("1").type is str
    assert TypeInfo.of(1.0).type is float
    if sys.version_info >= (3, 10):
        assert TypeInfo.of([1, 2, 3]).type == list[int]
        assert TypeInfo.of([1, 2.0, 3]).type == list[Union[int, float]]
        assert (
            TypeInfo.of({1: 1.0, "2": 1, 3.0: 1.0}).type
            == dict[Union[int, str, float], Union[int, float]]
        )
        assert TypeInfo.of({1, 2.0, "3"}).type == set[Union[int, str, float]]
    else:
        assert TypeInfo.of([1, 2, 3]).type == List[int]
        assert TypeInfo.of([1, 2.0, 3]).type == List[Union[int, float]]
        assert (
            TypeInfo.of({1: 1.0, "2": 1, 3.0: 1.0}).type
            == Dict[Union[int, str, float], Union[int, float]]
        )
        assert TypeInfo.of({1, 2.0, "3"}).type == Set[Union[int, str, float]]


def test_is():
    assert TypeInfo[Dict].is_mapping
    assert TypeInfo[dict].is_mapping
    assert TypeInfo[Dict[str, Any]].is_mapping
    assert TypeInfo[List].is_sequence
    assert TypeInfo[str].is_sequence
    assert TypeInfo[List[int]].is_sequence
    assert TypeInfo[Set].is_set
    assert TypeInfo[set].is_set
    assert TypeInfo[Dict].is_type(Dict)
    assert TypeInfo[List[int]].is_type(List[int])

    assert not TypeInfo[List[int]].is_type(List)
    assert not TypeInfo[List].is_mapping
    assert not TypeInfo[List[str]].is_mapping
    assert not TypeInfo[List].is_set
    assert not TypeInfo[Dict].is_sequence
    assert not TypeInfo[int].is_sequence
    assert not TypeInfo[None].is_sequence
    assert not TypeInfo[Any].is_sequence


def test_raise_init_or_new():
    with pytest.raises(RuntimeError):
        TypeInfo()
