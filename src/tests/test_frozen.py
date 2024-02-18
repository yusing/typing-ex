from typing_ex.frozen import FrozenDict, FrozenList, frozen_copy
import pytest


def test_frozen_list():
    assert frozen_copy([1, 2, 3]) == [1, 2, 3]
    assert frozen_copy((1, 2, 3)) == (1, 2, 3)
    assert frozen_copy({1, 2, 3}) == {1, 2, 3}
    assert frozen_copy({1: 1, 2: 2, 3: 3}) == {1: 1, 2: 2, 3: 3}

    frozen_list = FrozenList([1, 2, 3])
    assert frozen_copy(frozen_list) == frozen_list
    assert frozen_copy(frozen_copy(frozen_list)) == frozen_list
    with pytest.raises(RuntimeError):
        frozen_list.append(1)  # appending to frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.extend([1, 2])  # extending frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.insert(0, 1)  # inserting to frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.pop()  # popping from frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.remove(1)  # removing from frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.reverse()  # reversing frozen list is forbidden
    with pytest.raises(RuntimeError):
        frozen_list.sort()  # sorting frozen list is forbidden


def test_frozen_dict():
    frozen_dict = FrozenDict({"a": 1, "b": 2})
    assert frozen_copy(frozen_dict) == frozen_dict
    assert frozen_copy(frozen_copy(frozen_dict)) == frozen_dict
    with pytest.raises(RuntimeError):
        frozen_dict["a"] = 1  # appending to frozen dict is forbidden
    with pytest.raises(RuntimeError):
        frozen_dict.update({"a": 1})  # updating frozen dict is forbidden
    with pytest.raises(RuntimeError):
        frozen_dict.pop("a")  # popping from frozen dict is forbidden
    with pytest.raises(RuntimeError):
        frozen_dict.popitem()  # popping from frozen dict is forbidden
    with pytest.raises(RuntimeError):
        frozen_dict.clear()  # clearing frozen dict is forbiddenn
    with pytest.raises(RuntimeError):
        frozen_dict.setdefault("a")
