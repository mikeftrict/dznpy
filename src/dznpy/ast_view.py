"""
Module providing functionality to search a Dezyne abstract syntax tree for instances and
to distillate comprised information and views.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass
from typing import Any, Optional, Set, List

# dznpy modules
from .misc_utils import assert_t
from .ast import FileContents, PortDirection, Ports, assert_filecontents_t, Component, Enum, \
    Extern, Foreign, Interface, SubInt, System, Event, EventDirection
from .scoping import NamespaceIds, scope_resolution_order


###############################################################################
# Types
#

class FindError(Exception):
    """An error occurred while finding a Dezyne AST instance or instances according
    to the user specified search criteria."""


@dataclass(frozen=True)
class FindResult:
    """Dataclass comprising the results of finding Dezyne AST instances. Along with helpful
    functions to query the result."""
    items: List[Any]

    @property
    def valid_types(self) -> List[Any]:
        """Return the list of valid Dezyne ASD types that can be contained in the FindResult."""
        return [Component, Enum, Extern, Foreign, Interface, SubInt, System]

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if not isinstance(self.items, list):
            raise TypeError('The type of property "items" must be a list')

        for item in self.items:
            if not any(isinstance(item, valid_type) for valid_type in self.valid_types):
                raise TypeError(f'item {item} does not match one of the valid_types')

    def has_one_instance(self, ast_typehint: Optional[Any] = None) -> bool:
        """Check whether the result contains exactly 1 instance."""
        found = len(self.items) == 1
        if not found:
            return False

        if ast_typehint is None:
            return found

        # assert the type of the found instance
        if ast_typehint not in self.valid_types:
            raise FindError('Argument ast_typehint does not match one of the valid_types')

        return isinstance(self.items[0], ast_typehint)

    def get_single_instance(self, ast_typehint: Optional[Any] = None) -> Any:
        """The result is asserted to have only one instance, which is returned."""
        if not self.items:
            raise FindError('The result contains no instance(s) at all')

        if len(self.items) > 1:
            raise FindError('The result contains more than one instance')

        if ast_typehint is None:
            return self.items[0]

        # assert the type of the found instance
        if ast_typehint not in self.valid_types:
            raise FindError('Argument ast_typehint does not match one of the valid_types')

        if not isinstance(self.items[0], ast_typehint):
            raise FindError(f'The found instance does not match the ast typehint {ast_typehint}')

        return self.items[0]


@dataclass(frozen=True)
class PortNames:
    """Dataclass comprising a set of provides port names and a set of requires port names."""
    provides: Set[str]
    requires: Set[str]


###############################################################################
# Type creation functions
#

def portnames_t(ports: Ports) -> PortNames:
    """Create an instance of PortNames according to the user specified Ports. The function
    distinguishes requires from provides ports."""
    assert_t(ports, Ports)
    provides = set()
    requires = set()

    for port in ports.elements:
        if port.direction == PortDirection.PROVIDES:
            provides.add(port.name)
        if port.direction == PortDirection.REQUIRES:
            requires.add(port.name)

    return PortNames(provides=provides, requires=requires)


###############################################################################
# Module functions
#

def find_fqn(fct: FileContents, ns_ids: NamespaceIds,
             as_of_inner_scope: Optional[NamespaceIds] = None) -> FindResult:
    """Find instance(s) in the Dezyne AST FileContents (but Filename and Import excluded) whose
    Fully Qualified Name equals the specified NamespaceIds argument. The 'as_of_inner_scope'
    argument will apply a scope resolution order to search for the instance (see also
    https://en.cppreference.com/w/cpp/language/unqualified_lookup).
    An example of this is the scenario when finding interfaces AST instances of a component that
    may reside in the same parent or higher namespace.
    A list of all found instances is returned where the first item is the first one matching."""
    assert_filecontents_t(fct)
    assert_t(ns_ids, NamespaceIds)
    resolution_order = scope_resolution_order(ns_ids, as_of_inner_scope)
    result = []

    for container in [fct.components, fct.enums, fct.externs, fct.foreigns,
                      fct.interfaces, fct.subints, fct.systems]:
        for element in container:
            for lookup in resolution_order:
                if element.fqn == lookup:
                    result.append(element)
                    break

    return FindResult(items=result)


def find_any(fct: FileContents, endswith_ids: NamespaceIds) -> FindResult:
    """Find all instances (but Filename and Import excluded) in the Dezyne AST FileContents whose
    Fully Qualified Name ends with the specified NamespaceIds argument.
    A list of all found instances is returned."""
    assert_filecontents_t(fct)
    assert_t(endswith_ids, NamespaceIds)
    result = []
    nr_ids = len(endswith_ids.items)

    for container in [fct.components, fct.enums, fct.externs, fct.foreigns,
                      fct.interfaces, fct.subints, fct.systems]:
        for element in container:
            if element.fqn.items[-nr_ids:] == endswith_ids.items:
                result.append(element)

    return FindResult(items=result)


def get_in_events(itf: Interface) -> List[Event]:
    """Helper function to get all in-direction-ed events of a Dezyne interface."""
    assert_t(itf, Interface)
    return [evt for evt in itf.events.elements if evt.direction == EventDirection.IN]


def get_out_events(itf: Interface) -> List[Event]:
    """Helper function to get all out-direction-ed events of a Dezyne interface."""
    assert_t(itf, Interface)
    return [evt for evt in itf.events.elements if evt.direction == EventDirection.OUT]


def get_itf_name(itf: Interface) -> str:
    """Helper function to get the name of a Dezyne interface."""
    assert_t(itf, Interface)
    result = str(itf.name.value)
    if len(itf.name.value.items) > 1:
        raise NameError(f'Interface name "{result}" should be a single identifier')
    return result
