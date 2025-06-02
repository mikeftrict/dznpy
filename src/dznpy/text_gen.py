"""
Module providing helpers for generating text

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
import hashlib
from copy import deepcopy
# system modules
from dataclasses import dataclass, field
import enum
from typing import List, Any, Optional
from typing_extensions import Self

# dznpy modules
from .misc_utils import assert_t, assert_t_optional, flatten_to_strlist, is_strlist_instance, \
    trim_list
from .scoping import NamespaceIds

# constants
EOL = '\n'
BLANK_LINE = EOL  # alias
SPACE = ' '
TAB = '\t'
DEFAULT_INDENT_NR_SPACES = 4
DO_NOT_MODIFY = 'This is generated content. DO NOT MODIFY manually.'


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
    """Class containing indentation configuration and functionality to process contents."""
    indentor: Indentor = field(default=Indentor.SPACES)
    spaces_count: int = field(default_factory=fetch_default_indent_nr_spaces)
    bullet_list: Optional[BulletList] = field(default=None)

    def __post_init__(self):
        """Post check the constructed data class members on validity and configure internal
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
    """A class to store, extend, indent and stringify a collection of string lines that
    together form a logical text block."""
    _header: List[str]
    _lines: List[str]
    _indentizer: Indentizer
    _chunk_spaces: List[str]
    _cfg_chunk_spacing: Optional[str]

    def __init__(self,
                 content: Optional[Any] = None,
                 header: Optional[Any] = None,
                 chunk_spacing: Optional[str] = None):
        """Initialize with optional content (e.g. another TextBlock or other types) that will be
        flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines.
        As a second option a header can be specified that will be flattened first and prepended
        to the stringized output of the TextBlock. It is skipped from indentation."""
        self._header = TextBlock(header).lines if header else []
        self._lines = []
        self._indentizer = Indentizer()
        assert_t_optional(chunk_spacing, str)
        self._cfg_chunk_spacing = chunk_spacing
        self._chunk_spaces = chunk_spacing.splitlines() if chunk_spacing is not None else []
        self.append(content)

    def __str__(self) -> str:
        """Stringify the lines to an EOL delimited and an EOL-ending string."""
        combined = self._header + self._lines if self._header else self._lines
        if not combined:
            return ''  # empty textblock

        return EOL.join(combined) + EOL

    def __add__(self, other: Any) -> Self:
        """Add the contents of this and the other instance into a new instance."""
        result = TextBlock(self.lines, self._header, self._cfg_chunk_spacing)
        result += TextBlock(other)
        return result

    def __iadd__(self, other: Any) -> Self:
        """In-place operator to add something else to the contents of this (self) instance."""
        self.append(other)
        return self

    def _extend_lines(self, content: List[str]):
        """Private method to extend the lines buffer, accounting for chunk spacing."""
        if self.lines and self._chunk_spaces and content:
            self.lines.extend(self._chunk_spaces)

        self.lines.extend(content)

    @property
    def is_chunk_spacing(self) -> bool:
        """Probe whether chunk spacing is active for this textblock instance."""
        return bool(self._chunk_spaces)

    @property
    def lines(self) -> List[str]:
        """Access the collection of text lines. Note that each list item intentionally does not
        contain any end-of-line characters."""
        return self._lines

    @lines.setter
    def lines(self, value: List[str]):
        """Set (aka overwrite) the internal lines buffer with a deepcopy of another
        list of strings."""
        if not is_strlist_instance(value):
            raise TypeError('Argument must be a list of strings')
        self._lines = deepcopy(value)

    def append(self, content: Any) -> Self:
        """Append more content with either another TextBlock or other types of content that will
        be flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines.
        As return value a self reference is returned (see Fluent Interface)."""
        if isinstance(content, TextBlock):
            self._extend_lines(content.lines)
        else:
            split_lines_list = []
            for stritem in flatten_to_strlist(content, skip_empty_strings=False):
                if len(stritem) > 0:
                    split_lines_list.extend(stritem.splitlines())
                else:
                    split_lines_list.append(stritem)

            self._extend_lines(flatten_to_strlist(split_lines_list, skip_empty_strings=False))

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

    def trim(self, end_only: bool = False):
        """Trim the internal buffer from empty lines at the start and at the end.
        Optionally trim only empty lines at the end with 'end_only' set to True.
        As return value a self reference is returned (see Fluent Interface)."""
        self.lines = trim_list(self.lines, end_only)
        return self


# A shortcut alias for the TextBlock class
TB = TextBlock


@dataclass(frozen=True)
class GeneratedContent:
    """Data class containing generated content, its md5 hash, a designated filename and
    an optional namespace indication."""
    filename: str
    contents: str
    namespace: Optional[NamespaceIds] = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        assert_t(self.filename, str)
        assert_t(self.contents, str)
        assert_t_optional(self.namespace, NamespaceIds)

    @property
    def hash(self):
        """Get the hash of the contents."""
        return hashlib.md5(self.contents.encode('utf-8')).hexdigest().lower()


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


###############################################################################
# Module functions
#


def chunk(content: Any, appendix: Any = BLANK_LINE) -> Optional[TextBlock]:
    """Pour the stringifiable contents into a textblock as a chunk with an "appendix"
    (which is a blank line by default, that can be customized).

    Examples with the TextBlock depicted between <start> and <end>:

    <start (default)>
    Line 1
    Line 2

    <end>

    <start (custom 2 liner appendix)>
    Line 1
    Line 2
    custom-appendix-line-1
    custom-appendix-line-2
    <end>
    """
    true_contents = flatten_to_strlist(content)
    true_appendix = flatten_to_strlist(appendix)
    return TextBlock([content, true_appendix]) if true_contents else None


def cond_chunk(preamble: Any, content: Any, empty_response: Any, appendix: Any = BLANK_LINE,
               all_or_nothing: bool = False) -> Optional[TextBlock]:
    """Pour the stringifiable "preamble + contents" into a textblock as a chunk
    with an "appendix" (which is a blank line by default, that can be customized).

    Alternatively when the content appears to be 'empty', a different textblock that is a
    stringified "preamble + empty_response" with an appendix is returned.

    Finally, on specifying True for "all_or_nothing", only the literal "empty_response" is
    returned when the "content' appears to be 'empty'.

    Examples with the TextBlock depicted between <start> and <end>:

    <start (where contents has values)>
    My Preamble:
    Line 1
    Line 2

    <end>

    <start (where contents is empty)>
    My Preamble:
    my-empty-response

    <end>

    <start (where contents is empty, all_or_nothing=True>
    my-empty-response

    <end>

    <start (where contents has values, and a custom 2 liner appendix)>
    My Preamble:
    Line 1
    Line 2
    custom-appendix-line-1
    custom-appendix-line-2
    <end>
    """
    true_preamble = flatten_to_strlist(preamble)
    true_contents = flatten_to_strlist(content)
    true_empty_response = flatten_to_strlist(empty_response)

    if all_or_nothing and not true_contents:
        return TextBlock(empty_response) if empty_response else None

    return chunk([true_preamble, content], appendix) if true_contents else chunk(
        [true_preamble, true_empty_response], appendix)
