"""
Module representing the Abstract Syntax Tree (AST) and Elements of a Dezyne model

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
import enum
from typing import Any, List, Optional

# dznpy modules
from .misc_utils import assert_t, flatten_to_strlist
from .scoping import NamespaceIds, NamespaceTree
from .text_gen import TextBlock


@dataclass(frozen=True)
class ScopeName:
    """ScopeName"""
    value: NamespaceIds

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        assert_t(self.value, NamespaceIds)

    def __str__(self):
        """Get a dot delimited string of all scope name identifiers."""
        return '.'.join(self.value.items)


@dataclass(frozen=True)
class EndPoint:
    """EndPoint"""
    port_name: str
    instance_name: str = None  # optional


@dataclass(frozen=True)
class Binding:
    """Binding"""
    left: EndPoint
    right: EndPoint


@dataclass(frozen=True)
class Bindings:
    """Bindings"""
    elements: List[Binding] = field(default_factory=list)


@dataclass(frozen=True)
class Comment:
    """Comment"""
    value: str


@dataclass(frozen=True)
class Data:
    """Data"""
    value: str


@dataclass(frozen=True)
class Extern:
    """Extern"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    value: Data


class FormalDirection(enum.Enum):
    """Enum to indicate the direction of a formal."""
    IN = 'In'
    OUT = 'Out'
    INOUT = 'InOut'


class EventDirection(enum.Enum):
    """Enum to indicate the direction of an event."""
    IN = 'In'
    OUT = 'Out'


@dataclass(frozen=True)
class Fields:
    """Fields"""
    elements: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Enum:
    """Enum"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    fields: Fields


@dataclass(frozen=True)
class Filename:
    """Filename"""
    name: str


@dataclass(frozen=True)
class Formal:
    """Formal"""
    name: str
    type_name: ScopeName
    direction: FormalDirection


@dataclass(frozen=True)
class Formals:
    """Formals"""
    elements: List[Formal] = field(default_factory=list)


@dataclass(frozen=True)
class Import:
    """Import"""
    name: str


@dataclass(frozen=True)
class Injected:
    """Injected"""
    value: bool


@dataclass(frozen=True)
class Instance:
    """Instance"""
    name: str
    type_name: ScopeName


@dataclass(frozen=True)
class Instances:
    """Instances"""
    elements: List[Instance] = field(default_factory=list)


@dataclass(frozen=True)
class Namespace:
    """Namespace"""
    scope_name: ScopeName
    elements: list


class PortDirection(enum.Enum):
    """Enum to indicate the direction of a port."""
    REQUIRES = 'Requires'
    PROVIDES = 'Provides'


@dataclass(frozen=True)
class Port:
    """Port"""
    name: str
    type_name: ScopeName
    direction: PortDirection
    formals: Formals
    injected: Injected


@dataclass(frozen=True)
class Ports:
    """Ports"""
    elements: List[Port] = field(default_factory=list)


@dataclass(frozen=True)
class Range:
    """Range"""
    from_int: int
    to_int: int


@dataclass(frozen=True)
class Root:
    """Root"""
    comment: Comment  # [>=2.16.2]
    elements: list
    working_dir: Optional[str]  # present: [2.12.0 - 2.18.4], absent [2.11, >=2.19]


@dataclass(frozen=True)
class SubInt:
    """SubInt"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    range: Range


@dataclass(frozen=True)
class Signature:
    """Signature"""
    type_name: ScopeName
    formals: Formals


@dataclass(frozen=True)
class Event:
    """Event"""
    name: str
    signature: Signature
    direction: EventDirection


@dataclass(frozen=True)
class Events:
    """Events"""
    elements: List[Event] = field(default_factory=list)


@dataclass(frozen=True)
class Types:
    """Types"""
    elements: List[Any] = field(default_factory=list)

    @property
    def enums(self) -> List[Enum]:
        """Get all enums from the element list."""
        return [item for item in self.elements if isinstance(item, Enum)]

    @property
    def subints(self) -> List[SubInt]:
        """Get all enums from the element list."""
        return [item for item in self.elements if isinstance(item, SubInt)]


@dataclass(frozen=True)
class Component:
    """Component"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    ports: Ports


@dataclass(frozen=True)
class Foreign:
    """Foreign"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    ports: Ports


@dataclass(frozen=True)
class Interface:
    """Interface"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    ns_trail: NamespaceTree
    name: ScopeName
    types: Types
    events: Events


@dataclass(frozen=True)
class System:
    """System"""
    fqn: NamespaceIds
    parent_ns: NamespaceTree
    name: ScopeName
    ports: Ports
    instances: Instances
    bindings: Bindings


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class FileContents:
    """FileContents"""
    components: List[Component] = field(default_factory=list)
    enums: List[Enum] = field(default_factory=list)
    externs: List[Extern] = field(default_factory=list)
    filenames: List[Filename] = field(default_factory=list)
    foreigns: List[Foreign] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)
    interfaces: List[Interface] = field(default_factory=list)
    subints: List[SubInt] = field(default_factory=list)
    systems: List[System] = field(default_factory=list)

    def __repr__(self):
        return str(TextBlock(content=flatten_to_strlist(
            [self.components, self.enums, self.externs,
             self.filenames, self.foreigns, self.imports,
             self.interfaces, self.subints, self.systems])))


###############################################################################
# Type helper functions
#

def assert_filecontents_t(value: Any):
    """Assert the specified argument equals the FileContents type. Otherwise, raise a TypeError."""
    if not isinstance(value, FileContents):
        raise TypeError(f'Value "{value}" is not a FileContents type')
