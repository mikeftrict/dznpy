"""
Testsuite validating the misc_utils module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from dataclasses import dataclass, field
from unittest import TestCase

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


class TextBlockTests(TestCase):
    @staticmethod
    def test_create_default():
        tb = TextBlock()
        assert len(tb.lines) == 0

    @staticmethod
    def test_create_with_empty_string():
        tb = TextBlock('')
        assert len(tb.lines) == 1
        assert tb.lines == ['']

    @staticmethod
    def test_create_with_empty_list():
        tb = TextBlock([])
        assert len(tb.lines) == 0
        assert str(tb) == ''

    @staticmethod
    def test_create_with_none():
        tb = TextBlock(None)
        assert len(tb.lines) == 0
        assert str(tb) == ''

    @staticmethod
    def test_create_with_string():
        tb = TextBlock('Hello\n\n')
        assert len(tb.lines) == 2
        assert tb.lines == ['Hello', '']

    @staticmethod
    def test_create_with_stringlist():
        tb = TextBlock(['Hello\n\n', 'World  \n'])
        assert len(tb.lines) == 3
        assert tb.lines == ['Hello', '', 'World  ']

    @staticmethod
    def test_add_string():
        tb = TextBlock('First')
        assert tb.add('Second\n\n') == tb, "add returns itself a la Fluent interface"
        assert len(tb.lines) == 3
        assert tb.lines == ['First', 'Second', '']

        tb.add(content='Third\n \n')
        assert len(tb.lines) == 5
        assert tb.lines == ['First', 'Second', '', 'Third', ' ']

    @staticmethod
    def test_add_stringlist():
        tb = TextBlock()
        tb.add([' Hello\n \n', 'World  \n'])
        assert len(tb.lines) == 3
        assert tb.lines == [' Hello', ' ', 'World  ']

    @staticmethod
    def test_add_other_textblock():
        tb = TextBlock('First')
        tb.add(TextBlock(['Second', 'Third']))
        assert len(tb.lines) == 3
        assert tb.lines == ['First', 'Second', 'Third']

    @staticmethod
    def test_indent_default():
        textblock = TextBlock(content=['Hello', 'There'])
        assert textblock.indent() == textblock, "ident returns itself a la Fluent interface"
        assert str(textblock) == '    Hello\n    There\n'

    @staticmethod
    def test_indent_strip_trailing_whitespace():
        """Test that an empty line will not get indented with spaces as it would yield
        unncessary trailing whitespace."""
        textblock = TextBlock(content=['Hello', '', 'There']).indent()
        assert str(textblock) == '    Hello\n\n    There\n'

    @staticmethod
    def test_indent_with_custom_nr_spaces():
        textblock = TextBlock(content=['Hello', 'There'])
        textblock.indent(Indentizer(spaces_count=2))
        assert str(textblock) == '  Hello\n  There\n'

    @staticmethod
    def test_indent_with_tab_char():
        textblock = TextBlock(content=['Hello', 'There'])
        textblock.indent(Indentizer(indentor=Indentor.TAB))
        assert str(textblock) == '\tHello\n\tThere\n'

    @staticmethod
    def test_lines_setter():
        tb = TextBlock()
        tb.lines = ['One', 'Two']
        assert len(tb.lines) == 2
        assert tb.lines == ['One', 'Two']

    @staticmethod
    def test_lines_setter_fail():
        tb = TextBlock()
        with pytest.raises(TypeError) as exc:
            tb.lines = 1
        assert str(exc.value) == 'Argument must be a list of strings'

        with pytest.raises(TypeError) as exc:
            tb.lines = ['One', 2]
        assert str(exc.value) == 'Argument must be a list of strings'

    @staticmethod
    def test_implicit_supported_input():
        tb = TextBlock(123)
        assert tb.lines == ['123']

        tb = TextBlock(['Hi', 123, None, {'key1': 'value1'}])
        assert tb.lines == ['Hi', '123', 'value1']

    @staticmethod
    def test_textblock():
        assert str(TextBlock([''])) == '\n'
        assert str(TextBlock(['', ''])) == '\n\n'
        assert str(TextBlock(['', '\n'])) == '\n\n'
        assert str(TextBlock(['\n\n', '\n\n'])) == '\n\n\n\n'
        assert str(TextBlock(['\n', '\n', '\n', '\n'])) == '\n\n\n\n'
        assert str(TextBlock([' Hello', 'There '])) == ' Hello\nThere \n'
        assert str(TextBlock(['Hello', 'There \n'])) == 'Hello\nThere \n'
        assert str(
            TextBlock(['Hi\nThere\n', 'Every\n\n', 'One\n\n'])) == 'Hi\nThere\nEvery\n\nOne\n\n'
        assert str(TextBlock(['Hi\n', 'Every\n', '\n', 'One\n\n'])) == 'Hi\nEvery\n\nOne\n\n'


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
