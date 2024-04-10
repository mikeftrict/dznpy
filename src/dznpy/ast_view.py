"""
Module providing functionality to access and search in a Dezyne AST.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass
from typing import Any, Optional, Set

# dznpy modules
from .ast import FileContents, PortDirection, Ports
from .misc_utils import NameSpaceIds, scope_resolution_order


@dataclass(frozen=True)
class PortNames:
    provides: Set[str]
    requires: Set[str]


def find_on_fqn(fc: FileContents, item_fqn: NameSpaceIds,
                as_of_scope: Optional[NameSpaceIds]) -> Optional[Any]:
    """Find the first item instance identified on its fully qualified name in the file
    contents, resolution will traverse from inner to outer scope until it is found or
    None when not found. Check the return type. Note that in Dezyne each item and its
    fqn are unique."""
    resolution_order = scope_resolution_order(searchable=item_fqn, calling_scope=as_of_scope)

    for container in [fc.components, fc.enums, fc.externs, fc.foreigns,
                      fc.interfaces, fc.subints, fc.systems]:
        for lookup in resolution_order:
            for element in container:
                if element.fqn == lookup:
                    return element  # return early on the first found item

    return None  # item not found


def find(fc: FileContents, model_name: str) -> list:
    """Find the item instance(s) identified by its name (without namespacing) in the file contents.
    Check the resulting list for found item(s) and their type."""
    result = []
    for container in [fc.components, fc.enums, fc.externs, fc.foreigns,
                      fc.interfaces, fc.subints, fc.systems]:
        for element in container:
            if model_name == element.name.value[0]:
                result.append(element)

    return result


def get_port_names(ports: Ports) -> PortNames:
    provides = set()
    requires = set()

    for port in ports.elements:
        if port.direction == PortDirection.PROVIDES:
            provides.add(port.name)
        if port.direction == PortDirection.REQUIRES:
            requires.add(port.name)

    return PortNames(provides=provides, requires=requires)
