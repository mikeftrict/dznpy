"""
dznpy/misc_utils - version 0.2.240304

Python module providing miscellaneous utility functions.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
import enum
import os
from typing import Any, List, Optional
from typing_extensions import Self

# constants
EOL = '\n'
SPACE = ' '

# type alias for namespace identification which is represented by a list of strings
NameSpaceIds = List[str]


def assert_namespaceids_instance(value: Any):
    """Check whether the argument matches the NameSpaceIds type. Will raise TypeError on
    detected failures."""
    if not is_strlist_instance(value):
        raise TypeError('The argument is not a NameSpaceIds type')


def is_namespaceids_instance(value: Any) -> bool:
    """Check whether the argument matches the NameSpaceIds type. Returns either True or False."""
    return is_strlist_instance(value)


def is_strlist_instance(value: Any) -> bool:
    """Check whether the argument matches the list of strings type. Returns either True or False.
    Note that an empty list is also a positive match."""
    if not isinstance(value, list):
        return False

    return not [x for x in value if not isinstance(x, str)]


def is_strset_instance(value: Any) -> bool:
    """Check whether the argument matches the set of strings type. Returns either True or False.
    Note that an empty list is also a positive match."""
    if not isinstance(value, set):
        return False

    return not [x for x in value if not isinstance(x, str)]


def namespaceids_t(value: Any) -> NameSpaceIds:
    """Create a NameSpaceIds from an argument"""
    if is_namespaceids_instance(value):
        return value
    if isinstance(value, str):
        if '.' not in value:
            return [value]
        if is_namespaceids_instance(value.split('.')):
            return value.split('.')
    raise TypeError(f'"{value}" is not a valid NamespaceIds type')


def get_basename(filename):
    """Get the basename of the specified filename. That is, without file extension
    and without any path prefix."""
    return os.path.splitext(os.path.basename(filename))[0]


def scope_resolution_order(searchable: NameSpaceIds,
                           calling_scope: Optional[NameSpaceIds]) -> List[NameSpaceIds]:
    """Create a list of resolutions to find searchable starting in calling_scope (the inner scope)
    to the outer scope."""
    assert_namespaceids_instance(searchable)
    current_scope = calling_scope.copy() if calling_scope else []
    assert_namespaceids_instance(current_scope)

    result = [current_scope + searchable]
    while current_scope:
        current_scope.pop()
        result.append(current_scope + searchable)

    return result


def plural(singular_noun: str, ref_collection: Any) -> str:
    """Generate a plural form of a single noun when the referenced collection contains more
    than 1 item. The collection type can not be a string."""

    # check preconditions
    if not singular_noun:
        raise TypeError('Argument single_noun can not be empty')
    if not isinstance(singular_noun, str):
        raise TypeError('Argument single_noun must be a string type')
    if not hasattr(ref_collection, "__iter__") or isinstance(ref_collection, str):
        raise TypeError('Argument collection must be a collection type (str excluded)')

    # process
    if len(ref_collection) > 1:
        addition = 's'
        if singular_noun[-1] in ['s', 'x', 'z'] or singular_noun[-2::] in ['ss', 'sh', 'ch']:
            addition = 'es'
        return f'{singular_noun}{addition}'
    else:
        return singular_noun


class NamespaceTrail:
    """NamespaceTrail"""

    def __init__(self, parent: Self = None, scope_name: str = None):
        if parent is not None and scope_name is None:
            raise ValueError('scope_name required when constructing with a parent')
        if parent is None and scope_name is not None:
            raise ValueError('parent required when constructing with a scope_name')
        self._parent = parent
        self._scope_name = scope_name

    def __repr__(self):
        fqn = self.fqn
        return 'NamespaceTrail(<root namespace>)' if fqn is None else f'NamespaceTrail({fqn})'

    def __str__(self):
        fqn = self.fqn
        return '' if fqn is None else '.'.join(fqn)

    @property
    def scope_name(self) -> str or None:
        """Get scope name."""
        return self._scope_name

    @property
    def fqn(self) -> NameSpaceIds or None:
        """Get the fully qualified namespace identifiers/trail."""
        fqn_items = []
        if self._parent is not None:
            parent_fqn = self._parent.fqn
            if parent_fqn is not None:
                fqn_items.extend(parent_fqn)

        if self._scope_name is not None:
            fqn_items.append(self._scope_name)

        return fqn_items if len(fqn_items) > 0 else None

    def fqn_member_name(self, member_name: NameSpaceIds) -> NameSpaceIds:
        """Create a fully qualified name for a specified member_name."""
        result = []
        fqn = self.fqn
        if fqn is not None:
            result.extend(fqn)
        result.extend(member_name)
        return result


class Indentor(enum.Enum):
    """Enum to indicate the token type to indent with."""
    SPACES = 'Spaces'
    TAB = 'Tab'


class TextBlock:
    """"A class to store, extend, indent and stringify and collection of string lines that
    together form a logical text block."""
    _lines: List[str]

    def __init__(self, content: Any = None):
        """Initialize with content (either an other TextBlock or other types) that will be
        flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines."""
        self._lines = []
        if content is None:
            return
        self.add(content)

    @property
    def lines(self) -> List[str]:
        """Access the collection of text lines."""
        return self._lines

    @lines.setter
    def lines(self, value: List[str]):
        if not isinstance(value, list):
            raise TypeError('Argument must be a list of strings')
        if [x for x in value if not isinstance(x, str)]:
            raise TypeError('Argument must be a list of strings')
        self._lines = value

    def add(self, content: Any) -> Self:
        """Add more content with either an other TextBlock or other types of content that will be
        flattened first to a stringized 1-dimensional list where each individual string item is
        split into substrings on presence of newlines. As return value a self reference is returned
        (see Fluent Interface)."""
        if isinstance(content, TextBlock):
            self.lines.extend(content.lines)
        else:
            split_lines_list = []
            for x in flatten_to_strlist(content, skip_empty_strings=False):
                if len(x) > 0:
                    split_lines_list.extend(x.splitlines())
                else:
                    split_lines_list.append(x)

            self.lines.extend(flatten_to_strlist(split_lines_list, skip_empty_strings=False))

        return self

    def indent(self, indentor: Indentor = Indentor.SPACES, spaces_count: int = 4) -> Self:
        """Indent the contents one Indentor increment. As return value a self reference is returned
        (see Fluent Interface)."""
        if indentor is Indentor.SPACES:
            tab_chars = ' ' * spaces_count
        elif indentor is Indentor.TAB:
            tab_chars = '\t'
        else:
            raise TypeError(f'Invalid indentor specified: {indentor}')

        def tabify(item: str) -> str:
            return f'{tab_chars}{item}' if item else ''

        self.lines = [tabify(item) for item in self.lines]
        return self

    def __str__(self):
        """"Stringify the lines to an EOL delimited and an EOL-ending string."""
        return EOL.join(self.lines) + EOL


def flatten_to_strlist(value: Any, skip_empty_strings: bool = True) -> List[str]:
    """Flatten and stringify the argument into a final 1-dimensional list of strings. Encountered
    list and dictionary items are recursively processed. Where for dictionaries only the values
    are considered. Other types than lists or dictionaries will be stringified with str().
    Empty values like empty lists/dictionaries, empty strings and items that equal None are
    skipped by default. Skipping of empty strings can be disabled."""
    result = []
    if isinstance(value, list):
        for listitem in value:
            result.extend(flatten_to_strlist(listitem, skip_empty_strings))
    elif isinstance(value, dict):
        for dictitem in value.values():
            result.extend(flatten_to_strlist(dictitem, skip_empty_strings))
    elif isinstance(value, str):
        if skip_empty_strings and len(value) == 0:
            return result
        result.append(value)
    else:
        if value is None:
            return result
        result.append(str(value))
    return result


def newlined_list_items(list_items: list) -> str:
    """Create a textblock of stringized list items each separated by a new line."""
    return '\n'.join([str(item) for item in list_items]) if len(list_items) > 0 else '\n'
