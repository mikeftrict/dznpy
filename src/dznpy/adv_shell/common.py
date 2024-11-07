"""
Module providing common definitions used by the other modules in the adv_shell subpackage.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
import enum
from typing import List, Optional

# dznpy modules
from .. import cpp_gen, ast
from ..code_gen_common import BLANK_LINE, GeneratedContent
from ..cpp_gen import Comment, Constructor, Function, MemberVariable, Fqn, Namespace, Struct, \
    TypeDesc
from ..misc_utils import TextBlock, plural
from ..scoping import NamespaceIds

# own modules
from .types import RuntimeSemantics
from .port_selection import PortCfg


@dataclass(frozen=True)
class DznPortItf:
    """"Data class grouping Dezyne AST Port, Interface and configured semantics."""
    port: ast.Port
    interface: ast.Interface
    semantics: RuntimeSemantics


@dataclass(frozen=True)
class CppPortItf:
    """"Data class grouping Dezyne PortItf with a C++ accessor function and
    possibly associated class member variable."""
    dzn_port_itf: DznPortItf
    type: TypeDesc
    accessor_fn: Function
    accessor_target: str
    member_var: Optional[MemberVariable]

    @property
    def name(self) -> str:
        """Get the name of the port"""
        return self.dzn_port_itf.port.name

    @property
    def accessor_as_decl(self) -> str:
        """Generate the C++ declaration of the port accessor"""
        return self.accessor_fn.as_decl

    @property
    def accessor_as_def(self) -> str:
        """Generate the C++ definition of the port accessor"""
        return self.accessor_fn.as_def


class FacilitiesOrigin(enum.Enum):
    """Enum to indicate the origin of the facilities."""
    IMPORT = 'Import facilities (by reference) from the user provided dzn::locator argument'
    CREATE = 'Create all facilities (dispatcher, runtime and locator)'


@dataclass
class Configuration:
    """Data class containing the user specified configuration for generating an Advanced Shell."""
    dezyne_filename: str
    ast_fc: ast.FileContents
    output_basename_suffix: str
    fqn_encapsulee_name: NamespaceIds
    port_cfg: PortCfg
    facilities_origin: FacilitiesOrigin
    copyright: str
    support_files_ns_prefix: Optional[NamespaceIds] = field(default=None)
    creator_info: Optional[str] = field(default=None)
    verbose: bool = field(default=False)


@dataclass
class CppPorts:
    """Data class comprising a list of CppPortItf instances with helpers to generate
    c++ code elements."""
    ports: List[CppPortItf]

    def __post_init__(self):
        if len({x.dzn_port_itf.port.direction for x in self.ports}) > 1:
            raise ValueError('Only a single direction for all ports in the same set is allowed')

    @property
    def direction(self) -> str:
        """Determine the unisono direction of all ports, either 'Requires' or 'Provides'."""
        direction = {x.dzn_port_itf.port.direction for x in self.ports}
        return direction.pop().value if direction else '?'

    @property
    def mts_ports(self) -> List:
        """Return a list of all ports matching Multi-threaded semantics (MTS)."""
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.MTS]

    @property
    def sts_ports(self):
        """Return a list of all ports matching Single-threaded semantics (STS)."""
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.STS]

    @property
    def accessors_decl(self) -> TextBlock:
        """Generate C++ port accessor declarations for all ports."""
        comment = Comment(f'{self.direction} port {plural("accessor", self.ports)}')
        accessors = [port.accessor_as_decl for port in
                     self.ports] if self.ports else Comment('<none>')

        return TextBlock([comment, accessors])

    @property
    def accessors_def(self) -> TextBlock:
        """Generate C++ port accessor definitions for all ports."""
        return TextBlock(BLANK_LINE.join([port.accessor_as_def for port in self.ports]))

    @property
    def member_variables(self) -> TextBlock:
        """Generate C++ member variable (mv) declarations for ports that require rerouting."""
        ports_with_mv = [p for p in self.ports if p.member_var is not None]
        comment = Comment(f'Boundary {self.direction.lower()}-{plural("port", ports_with_mv)}'
                          ' (MTS) to reroute inwards events')
        member_vars = [str(p.member_var) for p in ports_with_mv]

        return TextBlock([comment, member_vars if member_vars else Comment('<none>')])


@dataclass(frozen=True)
class Facilities:
    """Data class grouping the self created Dezyne C++ facilities and associated declarations
    and definitions."""
    origin: FacilitiesOrigin
    dispatcher: MemberVariable
    runtime: Optional[MemberVariable]
    locator: Optional[MemberVariable]
    locator_accessor_fn: Optional[Function]

    @property
    def accessors_decl(self) -> TextBlock:
        """Create a C++ textblock with the declaration of the accessors."""
        accessor_fns = [fn for fn in [self.locator_accessor_fn] if fn is not None]
        accessors = [fn.as_decl for fn in
                     accessor_fns] if accessor_fns else Comment('<none>')

        return TextBlock([Comment(f'Facility {plural("accessor", accessor_fns)}'), accessors])

    @property
    def accessors_def(self) -> TextBlock:
        """Create a C++ textblock with the definition of the accessors."""
        accessor_fns = [fn for fn in [self.locator_accessor_fn] if fn is not None]
        return TextBlock([fn.as_def for fn in accessor_fns]) if accessor_fns else None

    @property
    def member_variables(self) -> TextBlock:
        """Create a C++ textblock with the declaration of the facilities as member variables."""
        member_vars = [str(mv) for mv in [self.runtime,
                                          self.dispatcher,
                                          self.locator] if mv is not None]

        return TextBlock([Comment('Facilities'), member_vars])

    @property
    def system_includes(self) -> List[str]:
        """Create a list of the required (Dezyne) header file includes depending on
        which facility is being declared by the advanced shell itself."""
        result = ['dzn/locator.hh', 'dzn/pump.hh']
        if self.runtime:
            result.append('dzn/runtime.hh')
        return result


@dataclass(frozen=True)
class DznElements:
    """Data class providing the model of the dezyne elements required for the Advanced Shell."""
    file_contents: ast.FileContents
    encapsulee: ast.System or ast.Component
    scope_fqn: Fqn
    provides_ports: List[DznPortItf]
    requires_ports: List[DznPortItf]


@dataclass(frozen=True)
class CppEncapsulee:
    """Data class comprising attributes of a C++ encapsulee."""
    member_var: MemberVariable
    name: str

    def __str__(self):
        return str(TextBlock([Comment(f'The encapsulated component "{self.name}"'),
                              self.member_var]))


def create_encapsulee(dzn_elements: DznElements) -> CppEncapsulee:
    """Helper function to create an C++ encapsulee data class"""
    return CppEncapsulee(cpp_gen.decl_var_t(Fqn(dzn_elements.encapsulee.fqn, True), 'm_encapsulee'),
                         dzn_elements.encapsulee.name)


@dataclass(frozen=True)
class CppElements:
    """Data class providing the model of the C++ elements required for the Advanced Shell."""
    orig_file_basename: str
    target_file_basename: str
    namespace: Namespace
    struct: Struct
    constructor: Constructor
    final_construct_fn: Function
    facilities_check_fn: Function
    facilities: Facilities
    encapsulee: CppEncapsulee
    provides_ports: CppPorts
    requires_ports: CppPorts
    sf_strict_port: GeneratedContent  # support file 'Dzn_StrictPort'


@dataclass(frozen=True)
class Recipe:
    """Data class grouping the ingredients for the recipe to generate an Advanced Shell."""
    configuration: Configuration
    dzn_elements: DznElements
    cpp_elements: CppElements
