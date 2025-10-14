"""
Module providing miscellaneous simple utility functions.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List


def assert_t(value: Any, expected_type: Any):
    """Assert the user specified value has a type that equals (or is a subclass of) the specified
    expected_type argument. Otherwise, a TypeError exception is raised.
    ValueError exceptions are raised when the function arguments are invalid."""
    if value is None:
        raise ValueError('Value argument is None and therefore it can not be asserted.')

    if expected_type is None:
        raise ValueError('Expected type argument is None and therefore assertion is impossible.')

    if not isinstance(value, expected_type):
        raise TypeError(f'Value argument "{value}" is not equal to the expected type: '
                        f'{expected_type}, actual type found: {type(value)}.')


def assert_t_optional(value: Any, expected_type: Any):
    """Assert the user specified value has a type that equals (or is a subclass of) the specified
    expected_type argument -OR- the user specified value equals None, meaning it is optional.
    On inequality a TypeError exception is raised.
    ValueError exceptions are raised when the function arguments are invalid."""
    if value is None:
        return
    assert_t(value, expected_type)


def assert_union_t(value: Any, valid_types: List[Any]):
    """Assert the user specified value has a type that equals (or is a subclass of) one of
    the specified types in the valid_types list argument. Otherwise, a TypeError exception
    is raised. ValueError exceptions are raised when the function arguments are invalid."""
    if value is None:
        raise ValueError('Value argument is None and therefore it can not be asserted.')

    if not valid_types:
        raise ValueError('No valid types specified and therefore assertion is impossible.')

    if not any(isinstance(value, valid_type) for valid_type in valid_types):
        raise TypeError(f'Value argument "{value}" is not equal to any expected types: '
                        f'{flatten_to_strlist(valid_types)}.')


def assert_union_t_optional(value: Any, valid_types: List[Any]):
    """Same as assert_union_t, but value is allowed to indicate None, meaning it is optional.
    """
    if value is None:
        return
    assert_union_t(value, valid_types)


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

        if str(value):  # skip appending empty strings
            result.append(str(value))

    return result


def get_basename(filename: str) -> str:
    """Get the basename of the specified filename. That is, without file extension
    and without any path prefix."""
    return os.path.splitext(os.path.basename(filename))[0]


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


def newlined_list_items(list_items: list) -> str:
    """Create a textblock of stringized list items each separated by a new line."""
    return '\n'.join([str(item) for item in list_items]) if list_items else '\n'


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

    return singular_noun


@contextmanager
def raii_cd(path: Path):
    """Change current directory and restore the original when exiting the context."""
    orig_directory = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(orig_directory)  # restore


def trim_list(list_to_trim: list, end_only: bool = False) -> list:
    """Return a trimmed list at the start and end from 'Python empty' items except that
    boolean false, zero integer, zero float and zero complex values are excluded from trimming.
    As an option only trim the end of the list with 'end_only' set to True.
    """
    assert_t(list_to_trim, list)
    lst = list_to_trim

    def is_trimmable(value: Any) -> bool:
        """Inner function to mark a value to be logically trimmable. Exclude zero number and
        false bool values and from the python if check whether it is 'empty'."""
        if isinstance(value, (bool, int, float, complex)):
            return False
        return not value

    if not end_only:
        while lst and is_trimmable(lst[0]):
            lst = lst[1:]

    while lst and is_trimmable(lst[-1]):
        lst = lst[:-1]

    return lst
