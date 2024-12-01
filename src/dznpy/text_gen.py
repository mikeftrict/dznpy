"""
Module providing helpers for generating text

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
from copy import deepcopy
# system modules
from dataclasses import dataclass, field
import enum
from typing import List, Any, Optional
from typing_extensions import Self

# dznpy modules
from .misc_utils import flatten_to_strlist, is_strlist_instance, assert_t, assert_t_optional

# constants
EOL = '\n'
SPACE = ' '
TAB = '\t'
DEFAULT_INDENT_NR_SPACES = 4


def fetch_default_indent_nr_spaces():
    """Helper to fetch the actual value of the module constant, as per feature, it is a valid
    use case to override the constant. Implementation classes need to call this function instead
    of referring the constant itself to prevent having a cached value from the early beginning.
    """
    return DEFAULT_INDENT_NR_SPACES


class Indentor(enum.Enum):
    """Enum to indicate the token type to indent with."""
    SPACES = 'Spaces'
    TAB = 'Tab'


class BulletListMode(enum.Enum):
    """Enum to indicate the mode where to insert list bullets."""
    ALL = 'All lines'
    FIRST_ONLY = 'First line only'


@dataclass
class BulletList:
    """Class containing bullet list configuration options."""
    mode: BulletListMode = field(default=BulletListMode.ALL)
    glyph: str = field(default='-')


@dataclass
class Indentizer:
    """Class containing indentation configuration and funtionality to process contents."""
    indentor: Indentor = field(default=Indentor.SPACES)
    spaces_count: int = field(default_factory=fetch_default_indent_nr_spaces)
    bullet_list: Optional[BulletList] = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity and configure internal
        data members."""
        if self.indentor is Indentor.SPACES:
            self._whitespace = SPACE * self.spaces_count
        elif self.indentor is Indentor.TAB:
            self._whitespace = TAB
        else:
            raise TypeError(f'Invalid indentor specified: {self.indentor}')

        if self.bullet_list:
            assert_t_optional(self.bullet_list, BulletList)

            if self.indentor is Indentor.SPACES:
                glyph = f'{self.bullet_list.glyph} '  # the glyph with minimally 1 space postfixed
                self._bulletized_indent = f'{glyph : <{self.spaces_count}}'
                self._whitespace = ' ' * len(self._bulletized_indent)  # expand if needed

            if self.indentor is Indentor.TAB:
                self._bulletized_indent = f'{self.bullet_list.glyph}{TAB}'

    def to_list(self, contents: Any) -> List[str]:
        """Process the specified contents with indentation per dataclass configuration and
        return the result as a list of strings."""
        flattened_list = flatten_to_strlist(contents, skip_empty_strings=False)
        if not flattened_list:
            return []

        # Inner functions:
        def only_indent(line: str) -> str:
            return f'{self._whitespace}{line}' if line.strip() else ''

        def bulletize_first_only(lines: List[str]) -> List[str]:
            return [f'{self._bulletized_indent}{lines[0]}'.strip()] + \
                [f'{only_indent(x)}' for x in lines[1:]]

        def bulletize_all(lines: List[str]) -> List[str]:
            return [f'{self._bulletized_indent}{line}'.strip() for line in lines]

        # Optional: Bulletize all lines:
        if self.bullet_list and self.bullet_list.mode == BulletListMode.ALL:
            return bulletize_all(flattened_list)

        # Optional: Bulletize first line only:
        if self.bullet_list and self.bullet_list.mode == BulletListMode.FIRST_ONLY:
            return bulletize_first_only(flattened_list)

        # Or inevitably: just indent with the configured indentation characters
        return [only_indent(x) for x in flattened_list]

    def to_str(self, contents: Any) -> str:
        """Process the specified contents with indentation per dataclass configuration and
        return the result as an end-of-line delimited string."""
        return EOL.join(self.to_str(contents)) + EOL


class TextBlock:
    """"A class to store, extend, indent and stringify and collection of string lines that
    together form a logical text block."""
    _header: List[str]
    _lines: List[str]
    _indentizer: Indentizer

    def __init__(self, content: Optional[Any] = None, header: Optional[Any] = None):
        """Initialize with content (e.g. an other TextBlock or other types) that will be
        flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines.
        As an option a header can be specified that will be flattened first and prepended
        to the stringized output of the TextBlock. It is skipped from indentation."""
        self._header = TextBlock(header).lines if header else []
        self._lines = []
        self.append(content)
        self._indentizer = Indentizer()

    def __str__(self) -> str:
        """"Stringify the lines to an EOL delimited and an EOL-ending string."""
        combined = self._header + self._lines if self._header else self._lines
        if not combined:
            return ''  # empty textblock

        return EOL.join(combined) + EOL

    def __add__(self, other: Any) -> Self:
        """Add the contents of this and the other instance into a new instance."""
        other_tb = TextBlock(other)
        return TextBlock(self.lines + other_tb.lines)

    def __iadd__(self, other: Any) -> Self:
        """In-place operator to add something else to the contents of this (self) instance."""
        self.append(other)
        return self

    @property
    def lines(self) -> List[str]:
        """Access the collection of text lines. Note that each list item intentionally does not
        contain any end-of-line characters."""
        return self._lines

    @lines.setter
    def lines(self, value: List[str]):
        """Set (aka overwrite) the internal lines buffer with a deepcopy of an other
        list of strings."""
        if not is_strlist_instance(value):
            raise TypeError('Argument must be a list of strings')
        self._lines = deepcopy(value)

    def append(self, content: Any) -> Self:
        """Append more content with either an other TextBlock or other types of content that will
        be flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines.
        As return value a self reference is returned (see Fluent Interface)."""
        if isinstance(content, TextBlock):
            self.lines.extend(content.lines)
        else:
            split_lines_list = []
            for stritem in flatten_to_strlist(content, skip_empty_strings=False):
                if len(stritem) > 0:
                    split_lines_list.extend(stritem.splitlines())
                else:
                    split_lines_list.append(stritem)

            self.lines.extend(flatten_to_strlist(split_lines_list, skip_empty_strings=False))

        return self

    def set_indentor(self, indentizer: Indentizer) -> Self:
        """Set a custum indentizer that will be used with indent().
        As return value a self reference is returned (see Fluent Interface)."""
        assert_t(indentizer, Indentizer)
        self._indentizer = indentizer
        return self

    def indent(self, indentizer: Optional[Indentizer] = None) -> Self:
        """Indent the internal buffer of lines and by default apply the current indentation
        options that can be adjusted with prepending a call on this class with call set_indentor().
        An optional argument allows the indentation options to be specified in one sweep.
        As return value a self reference is returned (see Fluent Interface)."""
        if indentizer:
            self.set_indentor(indentizer)
        self.lines = self._indentizer.to_list(self.lines)
        return self


###############################################################################
# Type creation functions
#

def all_dashes_t(indentor: Optional[Indentor] = Indentor.SPACES) -> Indentizer:
    """Create an indentizer with tiny indentation where all lines are prefixed with a dash
    bullet. The indentation is spaces by default, but can be optionally overridden.
    Example:

        - Line 1
        - Line 2
        - Line 3

        or when specifying Indentor.TAB:

        -\tLine 1
        -\tLine 2
        -\tLine 3

    """
    if indentor:
        return Indentizer(indentor=indentor,
                          spaces_count=2,
                          bullet_list=BulletList())
    return Indentizer(spaces_count=2,
                      bullet_list=BulletList())


def initial_dash_t(indentor: Optional[Indentor] = Indentor.SPACES) -> Indentizer:
    """Create an indentizer with tiny indentation and where only the first line is prefixed
    with a dash bullet. The indentation is spaces by default, but can be optionally overridden.
    Example:

        - Line 1
          Line 2
          Line 3

        or when specifying Indentor.TAB:

        -\tLine 1
        \tLine 2
        \tLine 3

    """
    if indentor:
        return Indentizer(indentor=indentor,
                          spaces_count=2,
                          bullet_list=BulletList(mode=BulletListMode.FIRST_ONLY))
    return Indentizer(spaces_count=2,
                      bullet_list=BulletList(mode=BulletListMode.FIRST_ONLY))
