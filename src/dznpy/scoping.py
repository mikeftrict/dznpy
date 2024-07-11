"""
Module providing classes and functions to create and inspect constructs of scoping (namespaces).

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import List, Any, Optional
from typing_extensions import Self

# dznpy modules
from .misc_utils import is_strlist_instance

###############################################################################
# Types
#

# type alias for namespace identification which is represented by a list of strings
NameSpaceIds = List[str]


class NamespaceTrail:
    """Class that provides composite-pattern of building and traversing an hierarchical
    trail of namespace identifiers."""

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
    def fqn(self) -> Optional[NameSpaceIds]:
        """Get the fully qualified namespace identifiers as of this class instance and all
        its parents."""
        fqn_items = []
        if self._parent is not None:
            parent_fqn = self._parent.fqn
            if parent_fqn is not None:
                fqn_items.extend(parent_fqn)

        if self._scope_name is not None:
            fqn_items.append(self._scope_name)

        return fqn_items if fqn_items else None

    def fqn_member_name(self, member_name: NameSpaceIds) -> NameSpaceIds:
        """Get the fully qualified namespace identifiers of this class instance plus
        the specified namespace identifiers of argument 'member_name'."""
        result = []
        fqn = self.fqn
        if fqn is not None:
            result.extend(fqn)
        result.extend(member_name)
        return result


###############################################################################
# Type creation functions
#

def namespaceids_t(value: Any) -> NameSpaceIds:
    """Create a NameSpaceIds from an argument such as a dot delimited string or a list
    of strings where each string is an identifier of the namespace trail."""
    if is_namespaceids_instance(value):
        return value
    if isinstance(value, str):
        if '.' not in value:
            return [value]
        if is_namespaceids_instance(value.split('.')):
            return value.split('.')
    raise TypeError(f'"{value}" is not a valid NamespaceIds type')


###############################################################################
# Type checking functions
#

def assert_namespaceids_instance(value: Any):
    """Check whether the argument matches the NameSpaceIds type. Will raise TypeError on
    detected failures."""
    if not is_strlist_instance(value):
        raise TypeError('The argument is not a NameSpaceIds type')


def is_namespaceids_instance(value: Any) -> bool:
    """Check whether the argument matches the NameSpaceIds type. Returns either True or False."""
    return is_strlist_instance(value)


###############################################################################
# Miscellaneous functions
#


def scope_resolution_order(searchable: NameSpaceIds,
                           calling_scope: Optional[NameSpaceIds]) -> List[NameSpaceIds]:
    """Create a list of resolutions to allow finding 'searchable' starting in calling_scope which
    is considered the inner scope. The resulting list has an ordening from inter to outer scope."""
    assert_namespaceids_instance(searchable)
    current_scope = calling_scope.copy() if calling_scope else []
    assert_namespaceids_instance(current_scope)

    result = [current_scope + searchable]
    while current_scope:
        current_scope.pop()
        result.append(current_scope + searchable)

    return result
