"""
Module providing functionality for C++ specific inquiries on the Dezyne AST and ast_view.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# system modules
from dataclasses import dataclass
from typing import List, Optional

# dznpy modules
from dznpy.ast import Event, Interface, FileContents, FormalDirection, ScopeName, SubInt, Enum, \
    Extern
from dznpy.ast_view import find_fqn
from dznpy.cpp_gen import Function, Struct, Class, Param, Fqn, TypeAsIs
from dznpy.misc_utils import assert_t, assert_union_t_optional
from dznpy.scoping import NamespaceIds


@dataclass(frozen=True)
class FormalExpanded:
    """Data class holding the type, direction and name of a formal."""
    type: TypeAsIs
    direction: FormalDirection
    name: str


@dataclass(frozen=True)
class EventExpanded:
    """Data class holding the values of an expanded Dezyne Event."""
    return_type: TypeAsIs
    name: str
    formals: List[FormalExpanded]


def expand_type_name(name: ScopeName, parent_fqn: NamespaceIds, fct: FileContents) -> TypeAsIs:
    """Helper function to expand a type (specified by its Scopename) and resolve its
    fully qualified namespace identifiers, immediately as C++."""
    assert_t(name, ScopeName)
    assert_t(parent_fqn, NamespaceIds)
    assert_t(fct, FileContents)

    find_result = find_fqn(fct, name.value, parent_fqn)

    if find_result.has_one_instance():
        inst = find_result.get_single_instance()
        if isinstance(inst, SubInt):
            return TypeAsIs('int')
        if isinstance(inst, Enum):
            return TypeAsIs(str(Fqn(inst.fqn, True)))
        if isinstance(inst, Extern):
            return TypeAsIs(inst.value.value)
        return TypeAsIs('UNRECOGNISED TYPE')

    return TypeAsIs(str(Fqn(name.value)))  # just pass-through


def expand_event(evt: Event, itf: Interface, fct: FileContents) -> EventExpanded:
    """Helper function to expand a Dezyne Event as part of an interface and resolve its
    fully qualified namespace identifiers, immediately as C++."""
    assert_t(evt, Event)
    assert_t(itf, Interface)
    assert_t(fct, FileContents)

    # expand all formals
    formals: List[FormalExpanded] = []
    for formal in evt.signature.formals.elements:
        formals.append(FormalExpanded(expand_type_name(formal.type_name, itf.fqn, fct),
                                      formal.direction,
                                      formal.name))

    return EventExpanded(return_type=expand_type_name(evt.signature.type_name, itf.fqn, fct),
                         name=evt.name,
                         formals=formals)


def get_formals(evt: EventExpanded) -> tuple[str, str]:
    """Get the formals of an Event as a tuple, immediately expressed as C++:
     - first a comma-delimited string of the event names-only (e.g. "param1, param2")
     - secondly a comma-delimited string of the event type, direction and event name,
       e.g "int param1, std::string& outputMsg"
    """
    assert_t(evt, EventExpanded)

    names_only: List[str] = []
    expanded: List[str] = []
    for formal in evt.formals:
        names_only.append(f'{formal.name}')
        formal_direction = '&' if formal.direction == FormalDirection.OUT else ''
        expanded.append(f'{formal.type}{formal_direction} {formal.name}')

    return ', '.join(names_only), ', '.join(expanded)


def create_member_function(evt: EventExpanded,
                           evt_name_prefix: str = '',
                           parent: Optional[Struct or Class] = None,
                           override: bool = False) -> Function:
    """Helper function that creates a cpp_gen Function out of an expanded Dezyne Event,
    expressed as C++ and optionally hooked up into a parent."""
    assert_t(evt, EventExpanded)
    assert_t(evt_name_prefix, str)
    assert_union_t_optional(parent, [Struct, Class])
    assert_t(override, bool)

    params: List[Param] = []
    for formal in evt.formals:
        params.append(Param(formal.type, formal.name))

    return Function(parent=parent,
                    return_type=evt.return_type,
                    name=f'{evt_name_prefix}{evt.name}',
                    params=params,
                    override=override)
