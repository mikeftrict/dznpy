"""
Module providing classes and functions to create and inspect constructs of scoping (namespaces).

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Any, Optional
from typing_extensions import Self

# dznpy modules
from .misc_utils import assert_t, assert_t_optional, is_strlist_instance


###############################################################################
# Types
#


class NamespaceIdsTypeError(TypeError):
    """The user specified parameter argument can not be directly accepted or transformed into
    namespace identifiers. Ensure each namespace identifier conforms to the regular expression
    format '[a-zA-Z_][a-zA-Z0-9_]*'."""


@dataclass(frozen=True)
class NamespaceIds:
    """Data class that contains the identifiers that together form a namespace or are parts
    that can be combined with other NamespaceIds instances to become a namespace or FQN."""
    items: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if not is_strlist_instance(self.items):
            raise NamespaceIdsTypeError(f'"{self.items}" is not a list of zero or more strings')

        for identifier in self.items:
            if not re.fullmatch('^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
                raise NamespaceIdsTypeError(f'namespace id "{identifier}" is invalid')

    def __str__(self):
        return '.'.join(self.items)

    def __add__(self, other: Self) -> Self:
        """Add the contents of this and the other instance into a new instance."""
        assert_t(other, NamespaceIds)
        return NamespaceIds(items=self.items + other.items)

    def __iadd__(self, other: Self) -> Self:
        """In-place operator to add the other instance to the contents of this (self) instance."""
        assert_t(other, NamespaceIds)
        self.items.extend(other.items)
        return self


@dataclass
class NamespaceTree:
    """Class that follows a composite-pattern of building and upwardly navigating an hierarchical
    tree of namespace identifiers nodes. The top of this tree is considered the root-namespace
    which means it has no parent and no scope name (both None).
    At each node the full trail to this top with fqn() can be queried. Also at each node a query
    for a trail to the top can be performed with a user addressed NamespaceIds instance. In such
    case the user provided namespace identifiers instance is mapped onto the current node."""
    parent: Optional[Self] = field(default=None)
    scope_name: Optional[NamespaceIds] = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        assert_t_optional(self.parent, NamespaceTree)
        assert_t_optional(self.scope_name, NamespaceIds)

        # either both properties are None or both set
        if self.parent is not None and self.scope_name is None:
            raise ValueError('scope_name required when constructing with a parent')
        if self.parent is None and self.scope_name is not None:
            raise ValueError('parent required when constructing with a scope_name')

    def __str__(self):
        fqn = self.fqn
        return f'{fqn}' if fqn else ''

    @property
    def fqn(self) -> NamespaceIds:
        """Get the 'fully qualified namespace identifiers' (FQN) of this class instance
        precluding all parent scope names. If the current node is the top of the tree then
        an empty NamespaceIds instance is replied."""
        fqn_items: List[NamespaceIds] = []
        if self.parent:
            parent_fqn = self.parent.fqn
            if parent_fqn:
                fqn_items.append(parent_fqn)

        if self.scope_name:
            fqn_items.append(self.scope_name)

        return sum_namespaceids_items(fqn_items)

    def fqn_member_name(self, member_name: NamespaceIds) -> NamespaceIds:
        """Get the fully qualified namespace identifiers of the user specified NamespaceIds
        instance projected onto this node of NamespaceTree instance."""
        assert_t(member_name, NamespaceIds)
        if self.fqn:
            return self.fqn + member_name
        return member_name


###############################################################################
# Type creation functions
#

def namespaceids_t(value: Any) -> NamespaceIds:
    """(Try to) create an instance of the NamespaceIds type from any type of argument such as a
    list of strings, dot- or '::'-delimited strings or eventually from a single string/identifier.
    Will raise a NamespaceIdsTypeError when failing to create. Each identifier must conform
    to the regular expression as defined by the NamespaceIds dataclass."""
    if isinstance(value, NamespaceIds):
        return value  # on correct type just pass-through

    if is_strlist_instance(value):
        return NamespaceIds(items=value)  # try passing through a list of strings

    if not isinstance(value, str):
        raise NamespaceIdsTypeError(f'Can not create NamespaceIds from argument "{value}"')

    if not value:
        return NamespaceIds(items=[])  # create an empty NamespaceIds

    if '.' in value:
        return NamespaceIds(items=value.split('.'))  # try dot-delimited string

    if '::' in value:
        return NamespaceIds(items=value.split('::'))  # try C++ nested namespace string

    return NamespaceIds(items=[value])  # try entire string as one identifier


def ns_ids_t(value: Any) -> NamespaceIds:
    """Shorthand alias for calling the namespaceids_t() type creation function."""
    return namespaceids_t(value)


###############################################################################
# Type helper functions
#


def sum_namespaceids_items(items: List[NamespaceIds]) -> NamespaceIds:
    """Sum/concatenate all NamespaceIds items in the specified list, from left (first item
    in the list) to right (last list item). Strict checking is applied on the argument.
    An empty list results in an empty NamespaceIds instance."""
    if not isinstance(items, list):
        raise NamespaceIdsTypeError(f'Argument "{items}" is not a list')

    result = NamespaceIds()
    for item in items:
        assert_t(item, NamespaceIds)
        result += item
    return result


###############################################################################
# Module functions
#


def scope_resolution_order(searchable: NamespaceIds,
                           calling_scope: Optional[NamespaceIds]) -> List[NamespaceIds]:
    """Create a list of resolutions to allow finding 'searchable' starting in calling_scope (if
    any). 'calling_scope' (or empty) is considered the inner scope. The resulting list has an
    ordering from inner scope (deepest level) to outer scope.
    More information: https://en.cppreference.com/w/cpp/language/unqualified_lookup"""
    assert_t(searchable, NamespaceIds)
    assert_t_optional(calling_scope, NamespaceIds)
    current_scope = deepcopy(calling_scope) if calling_scope else namespaceids_t([])

    result = [current_scope + searchable]
    while current_scope.items:
        current_scope.items.pop()
        result.append(current_scope + searchable)

    return result
