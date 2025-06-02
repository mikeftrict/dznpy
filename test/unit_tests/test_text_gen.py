"""
Testsuite validating the misc_utils module

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# system-under-test
import dznpy.text_gen
from dznpy.scoping import ns_ids_t
from dznpy.text_gen import *

# test data
from testdata_text_gen import *


# test helpers
class RaiiOverrideDefaultIndentNrSpacesConstant:
    """Context manager that will override and restore module constant
    DEFAULT_INDENT_NR_SPACES (Raii)."""

    def __init__(self, new_value: int):
        self._previous_value = dznpy.text_gen.DEFAULT_INDENT_NR_SPACES
        dznpy.text_gen.DEFAULT_INDENT_NR_SPACES = new_value

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        dznpy.text_gen.DEFAULT_INDENT_NR_SPACES = self._previous_value


###############################################################################
# Module constants
#

def test_module_constants_value():
    """Test the default values of the module constants."""
    assert dznpy.text_gen.EOL == '\n'
    assert dznpy.text_gen.BLANK_LINE == '\n'
    assert dznpy.text_gen.SPACE == ' '
    assert dznpy.text_gen.TAB == '\t'
    assert dznpy.text_gen.DEFAULT_INDENT_NR_SPACES == 4
    assert dznpy.text_gen.DO_NOT_MODIFY == 'This is generated content. DO NOT MODIFY manually.'


###############################################################################
# TextBlock type tests (includes some type creation functions)
#


def test_textblock_create_default():
    """Test default construction."""
    tb = TextBlock()
    assert len(tb.lines) == 0


def test_textblock_create_with_empty_string():
    """Test construction with an empty string."""
    tb = TextBlock('')
    assert len(tb.lines) == 1
    assert tb.lines == ['']


def test_textblock_create_with_empty_list():
    """Test construction with an empty list."""
    tb = TextBlock([])
    assert len(tb.lines) == 0
    assert str(tb) == ''


def test_textblock_create_with_none():
    """Test construction with None as parameter."""
    tb = TextBlock(None)
    assert len(tb.lines) == 0
    assert str(tb) == ''


def test_textblock_create_with_string():
    """Test construction with a simple string including EOL characters."""
    tb = TextBlock('Hello\n\n')
    assert len(tb.lines) == 2
    assert tb.lines == ['Hello', '']


def test_textblock_create_with_stringlist():
    """Test construction with a list of strings including EOL characters."""
    tb = TextBlock(['Hello\n\n', 'World  \n'])
    assert len(tb.lines) == 3
    assert tb.lines == ['Hello', '', 'World  ']


def test_textblock_create_with_random_content():
    """Test creation with a random content that is stringifiable with the
    requirements of flatten_to_strlist() from misc_utils."""
    content = {'one': [1, 2],
               'two': 'Duo',
               'three': 33,
               'four': ''}
    tb = TextBlock(content)
    assert tb.lines == ['1', '2', 'Duo', '33', '']


def test_textblock_add_other_textblock():
    """Test the in-place operator with adding another TextBlock."""
    tb = TextBlock('First') + TextBlock('Second')
    assert len(tb.lines) == 2
    assert tb.lines == ['First', 'Second']


def test_textblock_inplace_add_other_textblock():
    """Test the in-place operator with adding another TextBlock."""
    tb = TextBlock('First')
    tb += TextBlock('Second')
    assert len(tb.lines) == 2
    assert tb.lines == ['First', 'Second']


def test_textblock_inplace_add_other_type():
    """Test the in-place operator with adding some other type that is stringifiable with the
    requirements of flatten_to_strlist() from misc_utils."""
    tb = TextBlock('First')
    tb += {2: 'Hi', 'Three': 'World'}  # try a dictionary
    assert len(tb.lines) == 3
    assert tb.lines == ['First', 'Hi', 'World']


def test_textblock_append_string():
    """Test the append() function directly with a string."""
    tb = TextBlock('First')
    assert tb.append('Second\n\n') == tb, "add returns itself a la Fluent interface"
    assert len(tb.lines) == 3
    assert tb.lines == ['First', 'Second', '']

    tb.append(content='Third\n \n')
    assert len(tb.lines) == 5
    assert tb.lines == ['First', 'Second', '', 'Third', ' ']


def test_textblock_append_stringlist():
    """Test the append() function directly with a string list."""
    tb = TextBlock()
    tb.append([' Hello\n \n', 'World  \n'])
    assert len(tb.lines) == 3
    assert tb.lines == [' Hello', ' ', 'World  ']


def test_textblock_append_other_textblock():
    """Test the append() function directly with an other TextBlock."""
    tb = TextBlock('First')
    tb.append(TextBlock(['Second', 'Third']))
    assert len(tb.lines) == 3
    assert tb.lines == ['First', 'Second', 'Third']


def test_textblock_lines_setter():
    """Test setting the lines buffer directly. The lines are cloned to leave the original untouched."""
    my_lines = ['One', 'Two']
    tb = TextBlock()
    tb.lines = my_lines
    assert tb.lines == ['One', 'Two']

    # change the original list of strings, that must not affected the TextBlock
    my_lines[0] = 'Een'
    assert tb.lines == ['One', 'Two']


def test_textblock_lines_setter_fail():
    """Test setting the lines buffer must happen with the correct list-of-strings type."""
    tb = TextBlock()
    with pytest.raises(TypeError) as exc:
        tb.lines = 1
    assert str(exc.value) == 'Argument must be a list of strings'

    with pytest.raises(TypeError) as exc:
        tb.lines = ['One', 2]
    assert str(exc.value) == 'Argument must be a list of strings'


def test_textblock_strings_with_eols():
    """Test a bunch of constructor parameters that include various combinations of the EOL character."""
    assert str(TextBlock([''])) == '\n'
    assert str(TextBlock(['', ''])) == '\n\n'
    assert str(TextBlock(['', '\n'])) == '\n\n'
    assert str(TextBlock(['\n\n', '\n\n'])) == '\n\n\n\n'
    assert str(TextBlock(['\n', '\n', '\n', '\n'])) == '\n\n\n\n'
    assert str(TextBlock([' Hello', 'There '])) == ' Hello\nThere \n'
    assert str(TextBlock(['Hello', 'There \n'])) == 'Hello\nThere \n'
    assert str(TextBlock(['Hi\nThere\n', 'Every\n\n', 'One\n\n'])) == 'Hi\nThere\nEvery\n\nOne\n\n'
    assert str(TextBlock(['Hi\n', 'Every\n', '\n', 'One\n\n'])) == 'Hi\nEvery\n\nOne\n\n'


def test_textblock_indent_default():
    """Test the default indentation with the default number of 4 spaces."""
    tb = TextBlock(content=SIMPLE_TB).indent()
    assert str(tb) == SIMPLE_TB_DEFAULT_INDENT_SPACES
    assert tb.indent() == tb, "ident() returns its own class instance a la Fluent interface"


def test_textblock_indent_default_but_overridden_module_default():
    """Test the 'default' indentation with overriding the module constant. This feature can
    be handy when a using project prefers and installs a default from the very beginning with
    the intention to project it onto all further use."""
    with RaiiOverrideDefaultIndentNrSpacesConstant(2):
        tb = TextBlock(content=SIMPLE_TB).indent()
        assert str(tb) == SIMPLE_TB_OVERRIDDEN_DEFAULT_INDENT_SPACES


def test_textblock_indent_strip_trailing_whitespace():
    """Test explicitly that an empty line will not get indented with spaces as it would yield
    unnecessary trailing whitespace."""
    tb = TextBlock(content=['line 1', '']).indent()
    assert str(tb) == '    line 1\n\n'


def test_textblock_indent_with_custom_nr_spaces():
    """Test spaces indentation with a custom Indentizer configuration.
    Also, the set_indentor() needs to return Self."""
    tb = TextBlock(content=['Hello', 'There'])
    assert tb.set_indentor(Indentizer(spaces_count=2)) == tb, "set_indentor() returns its own class instance a la Fluent interface"
    assert str(tb.indent()) == '  Hello\n  There\n'


def test_textblock_indent_with_tab_char():
    """Test tabs indentation with a custom Indentizer configuration."""
    tb = TextBlock(content=SIMPLE_TB)
    tb.set_indentor(Indentizer(indentor=Indentor.TAB))
    assert str(tb.indent()) == SIMPLE_TB_INDENT_TAB


def test_textblock_indent_list_bullets_default_all_lines():
    """Test default indentation with bullets for all lines."""
    ind = Indentizer(bullet_list=BulletList())
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_DEFAULT_LISTBULLET_ALL_LINES


def test_textblock_indent_list_bullets_first_line_only():
    """Test default indentation with a bullet for the first line only."""
    ind = Indentizer(bullet_list=BulletList(mode=BulletListMode.FIRST_ONLY))
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_DEFAULT_LISTBULLET_FIRST_ONLY


def test_textblock_indent_list_bullets_custom_glyph_all_lines():
    """Test default indentation with bullets for all lines with a custom glyph."""
    ind = Indentizer(bullet_list=BulletList(glyph='>>'))
    assert str(TextBlock(content=SIMPLE_TB).indent(ind)) == \
           SIMPLE_TB_CUSTOM_GLYPH_LISTBULLET_ALL_LINES


def test_textblock_indent_list_bullets_fatglyph_all_lines():
    """Test indentation with bullets for all lines, but with a glyph that is longer
    than the default indentation. As a consequence the overall indent will grow
    correspondly."""
    ind = Indentizer(bullet_list=BulletList(glyph='fatglyph'))
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_DEFAULT_LISTBULLET_FATGLYPH_ALL_LINES


def test_textblock_tab_indent_list_bullets_all_lines():
    """Test tab indentation with bullets for all lines."""
    ind = Indentizer(indentor=Indentor.TAB, bullet_list=BulletList())
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_TAB_LISTBULLET_ALL_LINES


def test_textblock_tab_indent_list_bullets_first_line_only():
    """Test tab indentation with a bullet for the first line only."""
    ind = Indentizer(indentor=Indentor.TAB, bullet_list=BulletList(mode=BulletListMode.FIRST_ONLY))
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_TAB_LISTBULLET_FIRST_ONLY


def test_textblock_tab_indent_list_bullets_fatglyph_all_lines():
    """Test tab indentation with bullets for all lines, but with a glyph that can be or not be
    larger than the tab-width of a text viewer, which is unknown to the library. Therefor no
    expanding correction is attempted like with the spaces variant."""
    ind = Indentizer(indentor=Indentor.TAB, bullet_list=BulletList(glyph='fatglyph'))
    tb = TextBlock(content=SIMPLE_TB).set_indentor(ind)

    assert str(tb.indent()) == SIMPLE_TB_TAB_LISTBULLET_FATGLYPH_ALL_LINES


def test_textblock_indent_list_bullets_with_header():
    """Test a textblock with a header, with default indentation and bullets for all lines."""
    ind = Indentizer(bullet_list=BulletList())
    tb = TextBlock(content=SIMPLE_TB, header='My header:')

    assert str(tb.indent(ind)) == SIMPLE_TB_DEFAULT_HEADER_LISTBULLET_ALL_LINES


def test_textblock_indent_list_bullets_with_fat_header():
    """Test a textblock with a multiline header, with default indentation and bullets for all lines."""
    ind = Indentizer(bullet_list=BulletList(mode=BulletListMode.FIRST_ONLY))

    # variant 1
    assert str(TextBlock(content=SIMPLE_TB, header=FAT_HEADER).indent(ind)) == \
           SIMPLE_TB_DEFAULT_FAT_HEADER_LISTBULLET_FIRST_ONLY

    # variant 2
    assert str(TextBlock(content=SIMPLE_TB, header=TextBlock(FAT_HEADER)).indent(ind)) == \
           SIMPLE_TB_DEFAULT_FAT_HEADER_LISTBULLET_FIRST_ONLY


def test_textblock_default_type_creation_function_all_dashes():
    """Test the default type creation function create an Indentizer with tiny indentation
    and all lines prefixed with a dash (-) glyph."""

    # variant 1
    assert str(TextBlock(content=SIMPLE_TB).set_indentor(all_dashes_t()).indent()) == \
           SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_ALL_DASHES

    # variant 2
    assert str(TextBlock(content=SIMPLE_TB).indent(all_dashes_t())) == \
           SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_ALL_DASHES


def test_textblock_default_type_creation_function_first_line_dash_only():
    """Test the default type creation function create an Indentizer with tiny indentation
    where only the first line is prefixed with a dash (-) glyph."""

    # variant 1
    assert str(TextBlock(content=SIMPLE_TB).set_indentor(initial_dash_t()).indent()) == \
           SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_INITIAL_DASH

    # variant 2
    assert str(TextBlock(content=SIMPLE_TB).indent(initial_dash_t())) == \
           SIMPLE_TB_DEFAULT_TYPE_CREATION_FUNCTION_INITIAL_DASH


def test_textblock_tab_type_creation_function_all_dashes():
    """Test the tabbed type creation function create an Indentizer with tab indentation
    and all lines prefixed with a dash (-) glyph."""
    assert str(TextBlock(content=SIMPLE_TB).indent(all_dashes_t(Indentor.TAB))) == \
           SIMPLE_TB_TAB_LISTBULLET_ALL_LINES


def test_textblock_tab_type_creation_function_first_line_dash_only():
    """Test the tabbed type creation function create an Indentizer with tab indentation
    where only the first line is prefixed with a dash (-) glyph."""
    assert str(TextBlock(content=SIMPLE_TB).indent(initial_dash_t(Indentor.TAB))) == \
           SIMPLE_TB_TAB_LISTBULLET_FIRST_ONLY


def test_textblock_trimming():
    """Test trimming of a textblock from empty lines at the start and at the end of the
    current lines buffer."""
    assert str(TextBlock(SIMPLE_TB).trim()) == str(TextBlock(SIMPLE_TB))
    assert str(TextBlock(TRIMMABLE_TB).trim()) == str(TextBlock(SIMPLE_TB))
    assert str(TextBlock(TRIMMABLE_TB).trim(end_only=True)) == str(TextBlock(END_TRIMMED_TB))


def test_textblock_chunk_spacing_add():
    """Test the chunk_spacing mode of TextBlock where added content will be preambled with
    spacing (EOL by default). Final result will be chunks of text with spacing in between."""
    tb1 = TextBlock(content='line 1\nline 2', header=None, chunk_spacing=EOL)
    assert str(tb1) == 'line 1\nline 2\n'
    tb2 = TextBlock(content='line 3\nline 4')
    tb3 = tb1 + tb2
    assert tb3.is_chunk_spacing == True, 'Final TB took over chunk spacing'
    assert str(tb3) == CHUNK_SPACED_TB

    # when altering the original textblocks, the new one stays unaffected
    tb1 += 'extra'
    assert str(tb3) == CHUNK_SPACED_TB
    tb2 += 'addition'
    assert str(tb3) == CHUNK_SPACED_TB


def test_textblock_chunk_spacing_iadd():
    """Test the chunk_spacing mode of TextBlock where inline added content will be preambled with
    spacing (EOL by default). Final result will be chunks of text with spacing in between."""
    tb = TextBlock(content=None, header=None, chunk_spacing=EOL)
    tb += 'Line 1\nLine 2'
    assert str(tb) == 'Line 1\nLine 2\n'
    tb += 'Line 3'
    assert str(tb) == 'Line 1\nLine 2\n\nLine 3\n'


def test_generated_content():
    """Test creation with the minimum amount of arguments. Expect a hash calculated on
    the contents."""
    sut = GeneratedContent(filename='filename.txt', contents='Hi There\n')
    assert sut.filename == 'filename.txt'
    assert sut.contents == 'Hi There\n'
    assert sut.namespace is None


def test_generated_content_with_ns():
    """Test creation with the extra specification of a namespace, that is expected to be
    part in the dataclass as member."""
    sut = GeneratedContent('filename.txt', 'Hi There\n', namespace=ns_ids_t('My.Project'))
    assert sut.namespace == NamespaceIds(['My', 'Project'])


###############################################################################
# GeneratedContent type
#


def test_generated_content_class():
    """Test the GeneratedContent dataclass on good and bad weather scenarios."""
    contents = '// My single liner (comment ;-)'
    expected_hash = 'd21aa5dc311a931886366b2212be2bbb'

    assert GeneratedContent('Filename.cpp', contents).hash == expected_hash
    assert GeneratedContent('Filename.cpp', contents, ns_ids_t('My.Inner.Space')).hash == expected_hash

    with pytest.raises(TypeError) as exc:
        GeneratedContent(123, contents)
    assert """Value argument "123" is not equal to the expected type: <class 'str'>""" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        GeneratedContent('Filename.cpp', 456)
    assert """Value argument "456" is not equal to the expected type: <class 'str'>""" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        GeneratedContent('Filename.cpp', contents, 789)
    assert """Value argument "789" is not equal to the expected type: <class 'dznpy.scoping.NamespaceIds'>""" in str(exc.value)


###############################################################################
# Miscellaneous functions
#

def test_chunk():
    """Test chunking content into content with a default and a custom appendix.
    Note that the content must not be empty, otherwise None is returned."""
    assert isinstance(chunk(SIMPLE_TB), TextBlock), 'The return type is a TextBlock'

    assert str(chunk(SIMPLE_TB)) == CHUNKED_TB
    assert str(chunk(SIMPLE_TB, appendix=['123', '456', '789'])) == CUSTOM_CHUNKED_TB
    assert str(chunk(0)) == '0\n\n'

    assert chunk('') is None
    assert chunk(None) is None
    assert chunk([]) is None
    assert chunk({}) is None


def test_cond_chunk():
    """Test chunking content into content with a default and a custom appendix.
    Note that the content must not be empty, otherwise None is returned."""
    assert isinstance(cond_chunk('MyPreAmble', SIMPLE_TB, '<None>'), TextBlock), 'The return type is a TextBlock'
    assert str(cond_chunk('', SIMPLE_TB, '')) == CHUNKED_TB, 'Same as calling just chunk()'

    assert str(cond_chunk('MyPreAmble', SIMPLE_TB, '<None>')) == DEFAULT_COND_CHUNKED_TB
    assert str(cond_chunk('MyPreAmble', None, '<None>')) == DEFAULT_COND_CHUNKED_TB_EMPTY_CONTENTS
    assert str(cond_chunk('MyPreAmble', '', '<None>', appendix=['123', '456', '789'])) == CUSTOM_COND_CHUNKED_TB_EMPTY_CONTENTS
    assert str(cond_chunk('MyPreAmble', {}, '<AllOrNothing>', all_or_nothing=True)) == ALL_OR_NOTHING_COND_CHUNKED_TB_EMPTY_CONTENTS
    assert cond_chunk('MyPreAmble', None, None, all_or_nothing=True) is None
