"""
Testsuite validating the misc_utils module

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from dataclasses import dataclass, field

# system-under-test
from dznpy.misc_utils import *


def test_check_is_str_set():
    assert is_strset_instance({'My', 'Project'}) is True
    assert is_strset_instance(set()) is True

    assert is_strset_instance({'One', 2, 3}) is False
    assert is_strset_instance(None) is False


def test_flatten_to_strlist():
    # test with 'skip_empty_strings' by default on true
    assert flatten_to_strlist(['One']) == ['One']
    assert flatten_to_strlist({'Another': 'One'}, skip_empty_strings=False) == ['One']
    assert flatten_to_strlist('One') == ['One']
    assert flatten_to_strlist(1) == ['1']
    assert flatten_to_strlist(3.14) == ['3.14']
    assert flatten_to_strlist(None) == []
    assert flatten_to_strlist(['One', '', 'Two']) == ['One', 'Two']
    assert flatten_to_strlist(['One', 2]) == ['One', '2']
    assert flatten_to_strlist(['One', [2, 3], [''], 'X']) == ['One', '2', '3', 'X']
    assert flatten_to_strlist([None, 'One', {}]) == ['One']
    assert flatten_to_strlist([{123: 'One', 456: None}, ['Y']]) == ['One', 'Y']

    # test with 'skip_empty_strings' on false
    assert flatten_to_strlist('', skip_empty_strings=False) == ['']
    assert flatten_to_strlist([''], skip_empty_strings=False) == ['']
    assert flatten_to_strlist(None, skip_empty_strings=False) == []
    assert flatten_to_strlist({'Another': ''}, skip_empty_strings=False) == ['']
    assert flatten_to_strlist(['One', '', 'Two'], skip_empty_strings=False) == ['One', '', 'Two']
    assert flatten_to_strlist(['One', [''], 'X'], skip_empty_strings=False) == ['One', '', 'X']
    assert flatten_to_strlist([{123: '', 456: None}, ['Y']], skip_empty_strings=False) == ['', 'Y']


def test_newlined_list_items():
    """Test the expected behaviour of composing a new-line-delimited string from a list"""
    assert newlined_list_items([1, 2, 3]) == '1\n2\n3'
    assert newlined_list_items(['One', 2, 3.14]) == 'One\n2\n3.14'
    assert newlined_list_items([]) == '\n'


def test_plural_ok():
    """Validate the good weather scenarios of the plural function that makes a plural string
    from a singular noun when a provided collection contains more than one element."""
    no_elements = []
    single_element = [1]
    multiple_elements = [1, 2]
    single_noun = 'include'
    plural_noun = 'includes'
    assert plural(single_noun, multiple_elements) == plural_noun
    assert plural(single_noun, single_element) == single_noun
    assert plural(single_noun, no_elements) == single_noun, 'empty collection leads to single noun'

    # special postfix cases
    assert plural('bonus', multiple_elements) == 'bonuses'
    assert plural('inbox', multiple_elements) == 'inboxes'
    assert plural('buzz', multiple_elements) == 'buzzes'
    assert plural('class', multiple_elements) == 'classes'
    assert plural('bush', multiple_elements) == 'bushes'
    assert plural('approach', multiple_elements) == 'approaches'


def test_plural_fail():
    """Validate the bad weather scenarios of the plural function."""
    multiple_elements = [1, 2]

    with pytest.raises(TypeError) as exc:
        plural('', multiple_elements)
    assert str(exc.value) == 'Argument single_noun can not be empty'

    with pytest.raises(TypeError) as exc:
        plural(123, multiple_elements)
    assert str(exc.value) == 'Argument single_noun must be a string type'

    with pytest.raises(TypeError) as exc:
        plural('Python', 'string_not_allowed_as_collection')
    assert str(exc.value) == 'Argument collection must be a collection type (str excluded)'

    with pytest.raises(TypeError) as exc:
        plural('Python', 123)
    assert str(exc.value) == 'Argument collection must be a collection type (str excluded)'

    with pytest.raises(TypeError) as exc:
        plural('Python', None)
    assert str(exc.value) == 'Argument collection must be a collection type (str excluded)'


###############################################################################
# Tests for assert_t() and assert_t_optional()
#
# Local test data:
@dataclass
class Top:
    """Example of a super class."""
    member: str = field(default_factory=str)


class Sub(Top):
    """Example of a subclass."""
    pass


def test_assert_t_builtin_ok():
    """Test valid scenarios of the assert_t() function."""
    sut = float(1.23)
    assert_t(sut, float)


def test_assert_t_superclass_ok():
    """Test valid scenarios of the assert_t() function."""
    sut = Top()
    assert_t(sut, Top)


def test_assert_t_subclass_ok():
    """Test valid scenarios of the assert_t() function."""
    sut = Sub()
    assert_t(sut, Sub)
    assert_t(sut, Top)  # asserting on its super class is also ok


def test_assert_t_arguments_fail():
    """Test scenarios of invalid arguments."""
    with pytest.raises(ValueError) as exc:
        assert_t(None, float)
    assert str(exc.value) == 'Value argument is None and therefore it can not be asserted.'

    with pytest.raises(ValueError) as exc:
        assert_t('Test', None)
    assert str(exc.value) == 'Expected type argument is None and therefore assertion is impossible.'


def test_assert_t_fails():
    """Test scenarios of failing type assertions."""
    with pytest.raises(TypeError) as exc:
        assert_t('Some text', float)
    assert str(
        exc.value) == """Value argument "Some text" is not equal to the expected type: <class 'float'>, actual type found: <class 'str'>."""


def test_assert_t_optional_builtin_ok():
    """Test valid scenarios of the assert_t_optional() function."""
    assert_t_optional(None, float)
    sut = float(1.23)
    assert_t_optional(sut, float)


def test_assert_t_optional_superclass_ok():
    """Test valid scenarios of the assert_t_optional() function."""
    assert_t_optional(None, Top)
    sut = Top()
    assert_t_optional(sut, Top)


def test_assert_t_optional_subclass_ok():
    """Test valid scenarios of the assert_t_optional() function."""
    assert_t_optional(None, Sub)
    sut = Sub()
    assert_t_optional(sut, Sub)
    assert_t_optional(sut, Top)  # asserting on its super class is also ok


def test_assert_t_optional_arguments_fail():
    """Test scenarios of invalid arguments."""
    assert_t_optional(None, float)  # intentionally confirm that None is a valid argument

    with pytest.raises(ValueError) as exc:
        assert_t_optional('Test', None)
    assert str(exc.value) == 'Expected type argument is None and therefore assertion is impossible.'


def test_assert_t_optional_fails():
    """Test scenarios of failing type assertions."""
    with pytest.raises(TypeError) as exc:
        assert_t_optional('Some text', float)
    assert str(
        exc.value) == """Value argument "Some text" is not equal to the expected type: <class 'float'>, actual type found: <class 'str'>."""


def test_assert_union_t_superclass_ok():
    """Test valid scenario of the assert_union_t() function."""
    sut = Top()
    assert_union_t(sut, [Top, Sub])


def test_assert_union_t_superclass_fail1():
    """Test failing scenario of the assert_union_t() function when omitting a value parameter."""

    with pytest.raises(ValueError) as exc:
        assert_union_t(None, [Top, Sub])
    assert str(exc.value) == 'Value argument is None and therefore it can not be asserted.'


def test_assert_union_t_superclass_fail2():
    """Test failing scenario of the assert_union_t() function when omitting a valid types list."""
    sut = Top()
    with pytest.raises(ValueError) as exc:
        assert_union_t(sut, [])
    assert str(exc.value) == 'No valid types specified and therefore assertion is impossible.'


def test_assert_union_t_superclass_fail3():
    """Test failing scenario of the assert_union_t() function when omitting a value parameter."""
    sut = Top()
    with pytest.raises(TypeError) as exc:
        assert_union_t(sut, [Sub])
    assert str(exc.value) == '''Value argument "Top(member='')" is not equal to any expected types: ["<class 'test_misc_utils.Sub'>"].'''


def test_trim_list():
    """Test trimming a list from true-ish empty items at the start and end of the list.
    Boolean false, zero integer, zero float and zero complex values are excluded from trimming."""

    example = ['', 0, '', 'One', '', 'Two', 'Three', '', None]

    assert trim_list(example) == [0, '', 'One', '', 'Two', 'Three']
    assert trim_list(example, end_only=True) == ['', 0, '', 'One', '', 'Two', 'Three']
    assert trim_list([]) == []
    assert trim_list([True]) == [True]
    assert trim_list([False]) == [False]
    assert trim_list([False, True, False]) == [False, True, False]
    assert trim_list([0]) == [0]
    assert trim_list([0.0]) == [0.0]
    assert trim_list([complex(0j)]) == [complex(0j)]
