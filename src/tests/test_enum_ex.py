from typing_ex.enum_ex import EnumEx


class TestEnum(EnumEx):
    A = 0
    B = 1
    A_ALIAS = A
    A_ALIAS2 = 0
    B_ALIAS = 1
    B_ALIAS2 = B
    C = 456


def test_int_enum():
    assert TestEnum.A == 0
    assert TestEnum.B == 1
    assert TestEnum.C == 456
    assert TestEnum.A_ALIAS == 0
    assert TestEnum.A_ALIAS == TestEnum.A
    assert TestEnum.A_ALIAS2 == TestEnum.A_ALIAS
    assert TestEnum.A.name == "A"
    assert TestEnum.B.name == "B"
    assert TestEnum.A_ALIAS.name == "A_ALIAS"
    assert TestEnum.A_ALIAS2.name == "A_ALIAS2"
    assert TestEnum.A_ALIAS.orig_name == "A"
    assert TestEnum.B_ALIAS.orig_name == "B"
    assert TestEnum.A < TestEnum.B
    assert TestEnum.A < TestEnum.C
    assert TestEnum.A != TestEnum.B
    assert TestEnum.A != TestEnum.C
    assert TestEnum.B != TestEnum.C
    assert TestEnum.A == TestEnum.A
    assert TestEnum.C == TestEnum.C
    assert TestEnum.values == (0, 1, 456), TestEnum.values


class TestStrEnum(EnumEx):
    __value_type__ = str
    FOO = "foo"
    BAR = "bar"
    BAZ = "baz"
    FOO_ALIAS = FOO
    BAR_ALIAS = BAR
    BAZ_ALIAS = BAZ


def test_iter_enum():
    assert tuple(TestStrEnum) == (
        TestStrEnum.FOO,
        TestStrEnum.BAR,
        TestStrEnum.BAZ,
    ), tuple(
        TestStrEnum
    )  # aliases are skipped


def test_names():
    assert TestStrEnum.names == (
        "FOO",
        "BAR",
        "BAZ",
        "FOO_ALIAS",
        "BAR_ALIAS",
        "BAZ_ALIAS",
    ), TestStrEnum.names


def test_values():
    assert TestStrEnum.values == ("foo", "bar", "baz"), TestStrEnum.values


def test_enums():
    assert list(TestStrEnum.enums) == [
        TestStrEnum.FOO,
        TestStrEnum.BAR,
        TestStrEnum.BAZ,
        TestStrEnum.FOO_ALIAS,
        TestStrEnum.BAR_ALIAS,
        TestStrEnum.BAZ_ALIAS,
    ], TestStrEnum.enums
