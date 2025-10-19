"""
Module providing common definitions used by the other modules in the adv_shell subpackage.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
import enum
from typing import List, Optional

# dznpy modules
from .. import cpp_gen, ast
from ..cpp_gen import Comment, Constructor, Function, MemberVariable, Fqn, Namespace, Struct, \
    TypeDesc
from ..misc_utils import plural, flatten_to_strlist
from ..scoping import NamespaceIds
from ..text_gen import BLANK_LINE, GeneratedContent, TextBlock

# own modules
from .types import RuntimeSemantics
from .port_selection import PortsCfg


@dataclass(frozen=True)
class CodeGenResult:
    """Data class containing a list of artifacts as a result of code generation."""
    files: List[GeneratedContent]


@dataclass(frozen=True)
class MultiClientPortCfgFixture:
    """Dataclass comprising the fixture of the processed user specified multi client port
     configuration."""
    claim_event: ast.Event
    claim_granting_reply: NamespaceIds
    release_event: ast.Event

    def __str__(self):
        """Stringify the dataclass items as a human friendly readable textblock."""
        return f'claim_event={self.claim_event.name}, ' \
               f'claim_granting_reply={self.claim_granting_reply}, ' \
               f'release_event={self.release_event.name}'


@dataclass(frozen=True)
class DznPortItf:
    """Data class grouping Dezyne AST Port, Interface and configured semantics."""
    port: ast.Port
    interface: ast.Interface
    semantics: RuntimeSemantics
    multiclient: Optional[MultiClientPortCfgFixture] = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if self.multiclient and self.semantics != RuntimeSemantics.MTS:
            raise ValueError(f'Port "{self.port.name}": Multiclient port configuration is '
                             'only allowed for MTS ports')


@dataclass(frozen=True)
class CppPortItf:
    """Data class grouping Dezyne PortItf with a corresponding C++ accessor function.
    On rerouting the port via the dispatcher, this container provides the associated class member
    variable."""
    dzn_port_itf: DznPortItf
    type: TypeDesc
    accessor_fn: Function
    accessor_target: str
    member_var: Optional[MemberVariable] = field(default=None)

    @property
    def name(self) -> str:
        """Get the name of the port"""
        return self.dzn_port_itf.port.name

    @property
    def cap_name(self) -> str:
        """Get the name of the port with the first character capitalized."""
        return self.name[0].upper() + self.name[1:]

    @property
    def is_multiclient(self) -> bool:
        """Get the name of the port"""
        return self.dzn_port_itf.multiclient is not None

    def accessor_as_decl(self) -> TextBlock:
        """Generate the C++ declaration of the port accessor"""
        return self.accessor_fn.as_decl()

    def accessor_as_def(self) -> TextBlock:
        """Generate the C++ definition of the port accessor"""
        return self.accessor_fn.as_def()


class FacilitiesOrigin(enum.Enum):
    """Enum to indicate the origin of the facilities."""
    IMPORT = 'Import facilities (by reference) from the user provided dzn::locator argument'
    CREATE = 'Create all facilities (dispatcher, runtime and locator)'


# pylint: disable=too-many-instance-attributes
@dataclass
class Configuration:
    """Data class containing the user specified configuration for generating an Advanced Shell."""
    dezyne_filename: str
    ast_fc: ast.FileContents
    output_basename_suffix: str
    fqn_encapsulee_name: NamespaceIds
    ports_cfg: PortsCfg
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
        """Postcheck the constructed data class members on validity."""
        if len({x.dzn_port_itf.port.direction for x in self.ports}) > 1:
            raise ValueError('Only a single direction for all ports in the same set is allowed')

    @property
    def direction(self) -> str:
        """Determine the unisono direction of all ports, either 'Requires' or 'Provides'."""
        direction = {x.dzn_port_itf.port.direction for x in self.ports}
        return direction.pop().value if direction else '?'

    @property
    def mts_ports(self) -> List[CppPortItf]:
        """Return a list of all ports matching Multi-threaded semantics (MTS)."""
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.MTS]

    @property
    def sts_ports(self) -> List[CppPortItf]:
        """Return a list of all ports matching Single-threaded semantics (STS)."""
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.STS]

    @property
    def accessors_decl(self) -> TextBlock:
        """Generate C++ port accessor declarations for all ports."""
        if not self.ports:
            return TextBlock()

        comment = Comment(f'{self.direction} port {plural("accessor", self.ports)}')
        accessors = [str(port.accessor_as_decl()) for port in
                     self.ports] if self.ports else Comment('<none>')

        return TextBlock([comment, accessors])

    @property
    def accessors_def(self) -> TextBlock:
        """Generate C++ port accessor definitions for all ports."""
        if not self.ports:
            return TextBlock()

        return TextBlock(BLANK_LINE.join([str(port.accessor_as_def()) for port in self.ports]))

    @property
    def rerouting_class_members(self) -> Optional[TextBlock]:
        """Generate C++ class member declarations for rerouting (of ports)."""

        # distil the plain and multiclient ports
        plain_rerouting_ports = [p for p in self.ports if
                                 p.member_var is not None and not p.dzn_port_itf.multiclient]

        multiclient_rerouting_ports = [p for p in self.ports if
                                       p.member_var is not None and p.dzn_port_itf.multiclient]

        # plain port rerouting
        tb1 = TextBlock()
        if self.ports:
            comment = Comment(
                f'Boundary {self.direction.lower()}-{plural("port", plain_rerouting_ports)}'
                ' (MTS) to reroute inwards events')
            member_vars = [str(p.member_var) for p in plain_rerouting_ports]
            tb1 += [comment, member_vars if member_vars else Comment('<none>')]

        # multiclient rerouting
        comment = Comment(
            f'Boundary {self.direction.lower()}-{plural("port", multiclient_rerouting_ports)}'
            ' (MTS) to reroute inwards events and redirect outwards events to multi clients')
        member_vars = [str(p.member_var) for p in multiclient_rerouting_ports]
        tb2 = TextBlock([comment, member_vars]) if member_vars else None

        if tb1 and not tb2:
            return tb1

        if not tb1 and tb2:
            return tb2

        if tb1 and tb2:
            return TextBlock([tb1, BLANK_LINE, tb2])

        return None

    def has_multiclient_port(self) -> bool:
        """Indicate whether a multiclient port is present."""
        return any(x.is_multiclient for x in self.ports)


@dataclass
class CppHelperMethods:
    """Data class comprising C++ methods to support the Advanced Shell mechanics."""
    label: str
    public: List[Function] = field(default_factory=list)
    private: List[Function] = field(default_factory=list)

    @staticmethod
    def _def(functions: List[Function]) -> Optional[TextBlock]:
        """Generate public C++ port helper definitions as a TextBlock."""
        helpers = flatten_to_strlist([fn.as_def() for fn in functions])
        if not helpers:
            return None

        return TextBlock([helpers])

    def _decl(self, functions: List[Function]) -> Optional[TextBlock]:
        """Generate public C++ port helper declarations as a TextBlock."""
        helpers = flatten_to_strlist([fn.as_decl() for fn in functions])
        if not helpers:
            return None

        if self.label:
            return TextBlock([Comment(f'{self.label} {plural("helper", helpers)}'), helpers])

        return TextBlock([helpers])

    @property
    def public_decl(self) -> Optional[TextBlock]:
        """Generate public C++ port helper declarations as a TextBlock."""
        return self._decl(self.public)

    @property
    def public_def(self) -> Optional[TextBlock]:
        """Generate public C++ helper method definitions as a TextBlock."""
        return self._def(self.public)

    @property
    def private_decl(self) -> Optional[TextBlock]:
        """Generate private C++ helper method declarations as a TextBlock."""
        return self._decl(self.private)

    @property
    def private_def(self) -> Optional[TextBlock]:
        """Generate private C++ helper method definitions as a TextBlock."""
        return self._def(self.private)


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
        accessors = [fn.as_decl() for fn in
                     accessor_fns] if accessor_fns else Comment('<none>')

        return TextBlock([Comment(f'Facility {plural("accessor", accessor_fns)}'),
                          accessors])

    @property
    def accessors_def(self) -> TextBlock:
        """Create a C++ textblock with the definition of the accessors."""
        accessor_fns = [fn for fn in [self.locator_accessor_fn] if fn is not None]
        return TextBlock([fn.as_def() for fn in accessor_fns]) if accessor_fns else None

    @property
    def member_variables(self) -> TextBlock:
        """Create a C++ textblock with the declaration of the facilities as member variables."""
        member_vars = [mv.as_decl() for mv in [self.runtime,
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
    dzn: DznElements

    def __str__(self):
        return str(TextBlock([Comment(f'The encapsulated component "{self.name}"'),
                              self.member_var]))


def create_encapsulee(dzn_elements: DznElements) -> CppEncapsulee:
    """Helper function to create an C++ encapsulee data class"""
    return CppEncapsulee(cpp_gen.decl_var_t(Fqn(dzn_elements.encapsulee.fqn, True), 'm_encapsulee'),
                         dzn_elements.encapsulee.name, dzn_elements)


@dataclass(frozen=True)
class SupportFiles:
    """Data class as container for Support Files generated C++ content."""
    strict_port: GeneratedContent
    ilog: GeneratedContent
    misc_utils: GeneratedContent
    meta_helpers: GeneratedContent
    multi_client_selector: GeneratedContent
    mutex_wrapped: GeneratedContent

    def as_list(self) -> List[GeneratedContent]:
        """Retrieve a list of the support files theirs generated content."""
        return [self.strict_port, self.ilog, self.misc_utils, self.meta_helpers,
                self.multi_client_selector, self.mutex_wrapped]


# pylint: disable=too-many-instance-attributes
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
    provides_port_helpers: CppHelperMethods
    support_files: SupportFiles


@dataclass(frozen=True)
class Recipe:
    """Data class grouping the ingredients for the recipe to generate an Advanced Shell."""
    configuration: Configuration
    dzn_elements: DznElements
    cpp_elements: CppElements
