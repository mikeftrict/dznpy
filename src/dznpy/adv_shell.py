"""
adv_shell - version 0.1.240108

Python module providing functionality to generate a c++ shell around a
Dezyne implementation component or system component with the ability to specify a runtime
semantics per port: Single-threaded (STS) or Multi-threaded (MTS).

Besides this advanced user-customisation it also allows the user to configure whether
the required dezyne facilties are created by the shell or provides by the user.

Example configurations:
- All provides ports STS, all requires ports MTS
- All requires ports MTS, all provides ports STS
- All requires ports MTS, mixed provides ports MTS/STS
- All provides and requires ports MTS (like dzn code --shell)

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
from dataclasses import dataclass, field
import enum
import os
from typing import List, Dict, Set, Optional

# COTS modules
from . import cpp_gen, ast, ast_view

# from dznpy import cpp_gen, ast, dzn_json_ast
from .ast import Component, System
from .ast_view import find_on_fqn
from .cpp_gen import AccessSpecifier, Comment, Constructor, Function, FunctionPrefix, \
    Fqn, MemberVariable, Namespace, Struct, TypeDesc, TypePostfix, const_param_ref_t, \
    const_param_ptr_t, void_t
from .misc_utils import EOL, TextBlock, namespaceids_t, NameSpaceIds, is_strset_instance, \
    get_basename, flatten_to_strlist

# constants
BLANK_LINE = EOL
VERSION = f'{os.path.basename(__file__)} v0.1.240108'
GEN_DO_NOT_MODIFY = 'This is generated code. DO NOT MODIFY manually.'


class AdvShellError(Exception):
    """An error occurred during building of a custom shell."""


class RuntimeSemantics(enum.Enum):
    """Enum to indicate the flovor of runtime execution semantics."""
    STS = 'Single-threaded runtime semantics'
    MTS = 'Multi-threaded runtime semantics'


# ------ dezyne port runtime semantics configuration and helper functions: ------


class PortWildcard(enum.Enum):
    """Enum to indicate how events passing the port are treated."""
    REMAINING = 'Remaining ports'
    ALL = 'All ports'
    NONE = 'None of the ports'


@dataclass(frozen=True)
class PortSelect:
    """Port selection with a wildcard or explicitly named."""
    value: PortWildcard or Set[str]

    def __post_init__(self):
        if is_strset_instance(self.value):
            if not self.value:
                raise AdvShellError('strset must not be empty')
            if '' in self.value:
                raise AdvShellError('strset must not contain an empty string')
        elif not isinstance(self.value, PortWildcard):
            raise TypeError('wrong type assigned')

    def tryget_strset(self) -> Set[str]:
        """Try to get the actual value as strset. An empty set is returned otherwise."""
        return self.value if is_strset_instance(self.value) else set()

    def is_wildcard_all(self) -> bool:
        """Check whether the port selection equals the wildcard 'ALL'."""
        return isinstance(self.value, PortWildcard) and self.value == PortWildcard.ALL

    def is_not_empty(self) -> bool:
        """Check whether the port selection is not empty, meaning it either has a strset
        with contents or the wildcard equals something else than 'NONE'."""
        return is_strset_instance(self.value) or \
            isinstance(self.value, PortWildcard) and self.value != PortWildcard.NONE

    def match_strset(self, port_name: str) -> bool:
        """Attempt to find and match the specified port_name, when value is a strset."""
        self._check_port_name(port_name)
        return is_strset_instance(self.value) and port_name in self.value

    def match_wildcard(self, port_name: str) -> bool:
        """Attempt to find and match the specified port_name, when value is a wildcard."""
        self._check_port_name(port_name)
        return isinstance(self.value, PortWildcard) and self.value != PortWildcard.NONE

    @staticmethod
    def _check_port_name(port_name: str):
        """Assert check that the specified port name argument is correct."""
        if not isinstance(port_name, str):
            raise TypeError("argument port_name type must be a string")
        if not port_name:
            raise TypeError("argument port_name must not be empty")


@dataclass(frozen=True)
class MatchedPorts:
    value: Dict[str, RuntimeSemantics]


@dataclass(frozen=True)
class PortsSemanticsCfg:
    """Data class that assigns single-threaded or multi-threaded runtime semantics to
    selected ports."""
    sts: PortSelect
    mts: PortSelect

    def __str__(self):
        if self.mts.is_wildcard_all():
            return 'All MTS'
        if self.sts.is_wildcard_all():
            return 'All STS'

        sts_explicit_ports = self.sts.tryget_strset()
        mts_explicit_ports = self.mts.tryget_strset()

        explicit_ports = []

        if sts_explicit_ports:
            explicit_ports.append(f'STS={list(sts_explicit_ports)}')

        if mts_explicit_ports:
            explicit_ports.append(f'MTS={list(mts_explicit_ports)}')

        if self.sts.value == PortWildcard.REMAINING:
            explicit_ports.append('STS=[<Remaining ports>]')

        if self.mts.value == PortWildcard.REMAINING:
            explicit_ports.append('MTS=[<Remaining ports>]')

        return ' '.join(explicit_ports)

    def __post_init__(self):
        """Check the sts- and mts port selections on configuration errors."""
        if self.sts == self.mts:
            raise AdvShellError('properties sts and mts can not have equal contents')

        if [x for x in self.sts.tryget_strset() if x in self.mts.tryget_strset()]:
            raise AdvShellError('properties sts and mts can not overlap')

        if (self.sts.is_wildcard_all() and self.mts.is_not_empty()) or \
                (self.sts.is_not_empty() and self.mts.is_wildcard_all()):
            raise AdvShellError('properties sts and mts can not overlap')

    def match(self, expected_ports: Set[str], label: str) -> Dict[str, RuntimeSemantics]:
        """Match the specified expected ports to be matched in either sts or mts PortSelects."""
        all_explicitly_configured = self.sts.tryget_strset() | self.mts.tryget_strset()
        unmatched = all_explicitly_configured - expected_ports
        if unmatched:
            raise AdvShellError(f'Configured {label} ports {sorted(unmatched)} not matched')

        result: Dict[str, RuntimeSemantics] = {}
        for port in expected_ports:
            # first match the port explicitly in the strsets, or secondly in the wildcards
            if self.sts.match_strset(port):
                result[port] = RuntimeSemantics.STS
            elif self.mts.match_strset(port):
                result[port] = RuntimeSemantics.MTS
            elif self.sts.match_wildcard(port):
                result[port] = RuntimeSemantics.STS
            elif self.mts.match_wildcard(port):
                result[port] = RuntimeSemantics.MTS

        return result


@dataclass(frozen=True)
class PortCfg:
    """User-specified configuration for the provides and requires ports of an encapsulee."""
    provides: PortsSemanticsCfg
    requires: PortsSemanticsCfg

    def __post_init__(self):
        if self.provides.sts.is_not_empty() and self.provides.mts.is_not_empty():
            raise AdvShellError('Mixed STS/MTS provides ports are currently not supported')

    def __str__(self):
        if self.provides == self.requires:
            return f'provides/requires: {self.provides}'
        return f'provides ports: {self.provides}, requires ports: {self.requires}'

    def match(self, provides_ports: Set[str], requires_ports: Set[str]) -> MatchedPorts:
        """Match the specified port names in the current onfiguration."""
        result = self.provides.match(provides_ports, 'provides')
        result.update(self.requires.match(requires_ports, 'requires'))
        return MatchedPorts(result)


def all_sts_all_mts() -> PortCfg:
    """Configure all provides ports with single-threaded runtime semantics (STS) and all
    requires ports as multi-threaded runtime semantics (MTS)."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                              mts=PortSelect(PortWildcard.NONE)),
                   requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)))


def all_mts_all_sts() -> PortCfg:
    """Configure all provides ports with multi-threaded runtime semantics (MTS) and all
    requires ports as single-threaded runtime semantics (STS)."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)),
                   requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                              mts=PortSelect(PortWildcard.NONE)))


def all_mts_mixed_ts(sts_requires_ports: PortSelect,
                     mts_requires_ports: PortSelect) -> PortCfg:
    """Configure all -provides ports- with multi-threaded runtime semantics (MTS) but the
    requires ports as a mix of single or multi-threaded runtime semantics (Mixed)
    specified by user configuration."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)),
                   requires=PortsSemanticsCfg(sts=sts_requires_ports,
                                              mts=mts_requires_ports))


def all_sts_mixed_ts(sts_requires_ports: PortSelect,
                     mts_requires_ports: PortSelect) -> PortCfg:
    """Configure all -provides ports- with single-threaded runtime semantics (STS) but the
    requires ports as a mix of single or multi-threaded runtime semantics (Mixed)
    specified by user configuration."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                              mts=PortSelect(PortWildcard.NONE)),
                   requires=PortsSemanticsCfg(sts=sts_requires_ports,
                                              mts=mts_requires_ports))


def all_mts() -> PortCfg:
    """Configure all provides and requires ports with multi-threaded runtime semantics (MTS)."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)),
                   requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)))


class FacilitiesOrigin(enum.Enum):
    """Enum to indicate the origin of the facilities."""
    IMPORT = 'Import facilities (by reference) from the user provides dzn::locator argument'
    CREATE = 'Create all facilities (dispatcher, runtime and locator)'


@dataclass
class Configuration:
    """Configuration"""
    dezyne_filename: str
    ast_fc: ast.FileContents
    output_basename_suffix: str
    fqn_encapsulee_name: NameSpaceIds
    port_cfg: PortCfg
    facilities_origin: FacilitiesOrigin
    copyright: str
    creator_info: Optional[str] = field(default=None)
    verbose: bool = field(default=False)


@dataclass(frozen=True)
class DznPortItf:
    """"Grouped Port, Interface and configured semantics."""
    port: ast.Port
    interface: ast.Interface
    semantics: RuntimeSemantics


@dataclass(frozen=True)
class DznElements:
    """DznElements."""
    file_contents: ast.FileContents
    encapsulee: ast.System or ast.Component
    scope_fqn: Fqn
    provides_ports: List[DznPortItf]
    requires_ports: List[DznPortItf]


def create_dzn_elements(cfg: Configuration, file_contents: ast.FileContents,
                        encapsulee: ast.System or ast.Component) -> DznElements:
    """Create a DznElements dataclass instance."""

    if not isinstance(encapsulee, System) and not isinstance(encapsulee, Component):
        raise AdvShellError('Only system or implementation components can be encapsulated')

    scope_fqn = encapsulee.parent_ns.fqn
    port_names = ast_view.get_port_names(encapsulee.ports)
    all_ports = cfg.port_cfg.match(port_names.provides, port_names.requires)

    provides_ports = []
    requires_ports = []
    for port in encapsulee.ports.elements:
        itf = find_on_fqn(file_contents, port.type_name.value, scope_fqn)
        if port.direction == ast.PortDirection.PROVIDES:
            provides_ports.append(DznPortItf(port, itf, all_ports.value[port.name]))
        else:
            requires_ports.append(DznPortItf(port, itf, all_ports.value[port.name]))

    return DznElements(file_contents, encapsulee, Fqn(scope_fqn), provides_ports, requires_ports)


@dataclass(frozen=True)
class Facilities:
    """Facilities."""
    origin: FacilitiesOrigin
    dispatcher: MemberVariable
    runtime: Optional[MemberVariable]
    locator: Optional[MemberVariable]
    locator_accessor_fn: Optional[Function]

    @property
    def accessors_decl(self) -> TextBlock:
        """accessors_decl"""
        accessor_fns = [fn for fn in [self.locator_accessor_fn] if fn is not None]
        acc_str = 'accessors' if len(accessor_fns) > 1 else 'accessor'
        accessors = [fn.as_decl for fn in
                     accessor_fns] if accessor_fns else Comment('<none>')

        return TextBlock([Comment(f'Facility {acc_str}'), accessors])

    @property
    def accessors_def(self) -> TextBlock:
        """accessors_def"""
        accessor_fns = [fn for fn in [self.locator_accessor_fn] if fn is not None]
        return TextBlock([fn.as_def for fn in accessor_fns]) if accessor_fns else None

    @property
    def member_variables(self) -> TextBlock:
        """member_variables"""
        member_vars = [str(mv) for mv in [self.runtime,
                                          self.dispatcher,
                                          self.locator] if mv is not None]

        return TextBlock([Comment('Facilities'), member_vars])


def create_facilities(origin: FacilitiesOrigin, scope) -> Facilities:
    """create_facilities"""
    if origin == FacilitiesOrigin.IMPORT:
        dispatcher_mv = cpp_gen.decl_var_ref_t(Fqn(['dzn', 'pump']), 'm_dispatcher')
        return Facilities(origin, dispatcher_mv, None, None, None)

    if origin == FacilitiesOrigin.CREATE:
        dispatcher_mv = cpp_gen.decl_var_t(Fqn(['dzn', 'pump']), 'm_dispatcher')
        runtime_mv = cpp_gen.decl_var_t(Fqn(['dzn', 'runtime']), 'm_runtime')
        locator_t = TypeDesc(Fqn(['dzn', 'locator']))
        locator_mv = cpp_gen.decl_var_t(locator_t.fqn, 'm_locator')

        locator_accessor_fn = Function(TypeDesc(locator_t.fqn, TypePostfix.REFERENCE),
                                       'Locator', scope=scope,
                                       contents=f'return {locator_mv.name};')

        return Facilities(origin, dispatcher_mv, runtime_mv, locator_mv, locator_accessor_fn)

    raise AdvShellError(f'Invalid argument "origin: " {origin}')


@dataclass(frozen=True)
class CppEncapsulee:
    member_var: MemberVariable or None
    name: str

    def __str__(self):
        return str(TextBlock([Comment(f'The encapsulated component "{self.name}"'),
                              self.member_var]))


def create_encapsulee(dzn_elements: DznElements) -> CppEncapsulee:
    """create_encapsulee"""
    return CppEncapsulee(cpp_gen.decl_var_t(Fqn(dzn_elements.encapsulee.fqn, True), 'm_encapsulee'),
                         dzn_elements.encapsulee.name)


@dataclass(frozen=True)
class CppPortItf:
    dzn_port_itf: DznPortItf
    type: TypeDesc
    accessor_fn: Function
    member_var: Optional[MemberVariable]

    @property
    def name(self) -> str:
        """Get the name of the port"""
        return self.dzn_port_itf.port.name

    @property
    def accessor_fn_call(self) -> str:
        """Get the C++ call of the accessor function."""
        return f'{self.accessor_fn.name}()'

    @property
    def accessor_as_decl(self) -> str:
        return self.accessor_fn.as_decl

    @property
    def accessor_as_def(self) -> str:
        return self.accessor_fn.as_def


@dataclass
class CppPorts:
    ports: List[CppPortItf]

    def __post_init__(self):
        if len({x.dzn_port_itf.port.direction for x in self.ports}) > 1:
            raise ValueError('Only a single direction for all ports in the same set is allowed')

    @property
    def direction(self) -> str:
        direction = {x.dzn_port_itf.port.direction for x in self.ports}
        return direction.pop().value if direction else '?'

    @property
    def mts_ports(self):
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.MTS]

    @property
    def sts_ports(self):
        return [p for p in self.ports if p.dzn_port_itf.semantics == RuntimeSemantics.STS]

    @property
    def accessors_decl(self) -> TextBlock:
        nr_ports = len(self.ports)
        acc_str = 'accessors' if nr_ports > 1 else 'accessor'
        comment = f'{self.direction} port {acc_str}' if nr_ports else None
        accessors = [port.accessor_as_decl for port in
                     self.ports] if nr_ports > 0 else Comment('<none>')

        return TextBlock([Comment(comment), accessors])

    @property
    def accessors_def(self) -> TextBlock:
        return TextBlock(BLANK_LINE.join([port.accessor_as_def for port in self.ports]))

    @property
    def member_variables(self) -> TextBlock:
        nr_ports = len([x for x in self.ports if x.member_var is not None])
        port_str = 'ports' if nr_ports > 1 else 'port'
        comment = f'Boundary {self.direction.lower()}-{port_str} (MTS) to reroute inwards events'
        member_vars = [str(p.member_var) for p in self.ports if p.member_var is not None]

        return TextBlock([Comment(comment),
                          member_vars if member_vars else Comment('<none>')])


def create_cpp_portitf(dzn: DznPortItf, scope: cpp_gen.Struct,
                       encapsulee: CppEncapsulee) -> CppPortItf:
    """create_cpp_portitf"""
    t = TypeDesc(Fqn(dzn.interface.fqn, prefix_root_ns=True))
    fn_prefix = f'{dzn.port.direction.value}'
    cap_name = dzn.port.name[0].upper() + dzn.port.name[1:]

    if dzn.semantics == RuntimeSemantics.STS:
        # pass-through mode
        member_var = None
        accessor_fn = Function(TypeDesc(t.fqn, TypePostfix.REFERENCE),
                               f'{fn_prefix}{cap_name}', scope=scope,
                               contents=f'return {encapsulee.member_var.name}.{dzn.port.name};')

    elif dzn.semantics == RuntimeSemantics.MTS:
        # reroute mode, requires an own instance of the port
        mv_prefix = 'm_pp' if dzn.port.direction == ast.PortDirection.PROVIDES else 'm_rp'
        member_var = MemberVariable(t, f'{mv_prefix}{cap_name}')
        accessor_fn = Function(TypeDesc(t.fqn, TypePostfix.REFERENCE),
                               f'{fn_prefix}{cap_name}', scope=scope,
                               contents=f'return {member_var.name};')
    else:
        raise ValueError('unknown runtime semantics')

    return CppPortItf(dzn, t, accessor_fn, member_var)


def reroute_in_events(port: CppPortItf, facilities: Facilities, encapsulee: CppEncapsulee,
                      fc: ast.FileContents) -> str:
    result = []
    for event in [e for e in port.dzn_port_itf.interface.events.elements if
                  e.direction == ast.EventDirection.IN]:
        in_formals = [f for f in event.signature.formals.elements if
                      f.direction == ast.FormalDirection.IN]

        args = []
        for i in event.signature.formals.elements:
            ext_type = find_on_fqn(fc, i.type_name.value, port.dzn_port_itf.interface.fqn)
            if not isinstance(ext_type, ast.Extern):
                raise AdvShellError(f'Extern type {i.type_name} not found')

            opt_ref = '&' if i.direction != ast.FormalDirection.IN else ''
            args.append(f'{ext_type.value.value}{opt_ref} {i.name}')

        captures_by_value = ''.join(f', {x.name}' for x in in_formals)
        stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
        call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

        txt = f'{port.accessor_fn_call}.in.{event.name} = [&]{stdfunction_arguments} {{\n' \
              f'    return dzn::shell({facilities.dispatcher.name}, [&{captures_by_value}] ' \
              f'{{ return {encapsulee.member_var.name}.{port.name}.in.{event.name}' \
              f'({call_arguments}); }});\n' \
              '};'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def reroute_out_events(port: CppPortItf, facilities: Facilities, encapsulee: CppEncapsulee,
                       fc: ast.FileContents) -> str:
    """Create C++ code to reroute out events."""
    result = []
    for event in [e for e in port.dzn_port_itf.interface.events.elements if
                  e.direction == ast.EventDirection.OUT]:
        if [f for f in event.signature.formals.elements if
            f.direction == ast.FormalDirection.OUT]:
            raise AdvShellError('Out events can not have out parameter argument')
        in_formals = [f for f in event.signature.formals.elements if
                      f.direction == ast.FormalDirection.IN]

        args = []
        for i in event.signature.formals.elements:
            ext_type = find_on_fqn(fc, i.type_name.value, port.dzn_port_itf.interface.fqn)
            if not isinstance(ext_type, ast.Extern):
                raise AdvShellError(f'Extern type {i.type_name} not found')

            args.append(f'{ext_type.value.value} {i.name}')

        captures_by_value = ''.join(f', {x.name}' for x in in_formals)
        stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
        call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

        txt = f'{port.accessor_fn_call}.out.{event.name} = [&]{stdfunction_arguments} {{\n' \
              f'    return {facilities.dispatcher.name}([&{captures_by_value}] ' \
              f'{{ return {encapsulee.member_var.name}.{port.name}.out.{event.name}' \
              f'({call_arguments}); }});\n' \
              '};'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def create_constructor(scope, facilities: Facilities, encapsulee: CppEncapsulee,
                       provides_ports: CppPorts, requires_ports: CppPorts,
                       fc: ast.FileContents) -> Constructor:
    """Create C++ code for the constructor"""

    # populate the member initialization list (mil)
    # -------------------------------------

    # construct or import the required dezyne facilities, construct the encapsulee
    if facilities.origin == FacilitiesOrigin.CREATE:
        p_locator = const_param_ref_t(['dzn', 'locator'], 'prototypeLocator')
        mil = [f'{facilities.locator.name}(std::move(FacilitiesCheck({p_locator.name}).clone()'
               f'.set({facilities.runtime.name})'
               f'.set({facilities.dispatcher.name})))',
               f'{encapsulee.member_var.name}({facilities.locator.name})']
    elif facilities.origin == FacilitiesOrigin.IMPORT:
        p_locator = const_param_ref_t(['dzn', 'locator'], 'locator')
        mil = [f'{facilities.dispatcher.name}(FacilitiesCheck({p_locator.name}).get<dzn::pump>())',
               f'{encapsulee.member_var.name}({p_locator.name})']
    else:
        raise AdvShellError(f'Invalid argument "origin: " {facilities.origin}')

    p_shell_name = const_param_ref_t(['std', 'string'], 'shellName')

    # construct the (MTS) boundary ports
    mts_pp, mts_rp = (provides_ports.mts_ports, requires_ports.mts_ports)
    mil.extend([f'{p.member_var.name}({encapsulee.member_var.name}.{p.name})' for p in mts_pp])
    mil.extend([f'{p.member_var.name}({encapsulee.member_var.name}.{p.name})' for p in mts_rp])

    # populate the definition of the constructor
    # ------------------------------------------
    encapsulee_mv = encapsulee.member_var.name
    rerouted_in_events = flatten_to_strlist([reroute_in_events(p, facilities, encapsulee, fc)
                                             for p in mts_pp])
    rerouted_out_events = flatten_to_strlist([reroute_out_events(p, facilities, encapsulee, fc)
                                              for p in mts_rp])

    contents = TextBlock([
        Comment('Complete the component meta info of the encapsulee and its ports that '
                'are configured for MTS'),
        f'{encapsulee_mv}.dzn_meta.name = {p_shell_name.name};',
        [f'{encapsulee_mv}.{p.name}.meta.require.name = "{p.name}";' for p in mts_pp],
        [f'{encapsulee_mv}.{p.name}.meta.provide.name = "{p.name}";' for p in mts_rp],
        BLANK_LINE,
        Comment('Reroute in-events of boundary provides ports (MTS) via the dispatcher'),
        rerouted_in_events if rerouted_in_events else Comment('<None>'),
        BLANK_LINE,
        Comment('Reroute out-events of boundary requires ports (MTS) via the dispatcher'),
        rerouted_out_events if rerouted_out_events else Comment('<None>'),
    ])

    return Constructor(scope, params=[p_locator, p_shell_name],
                       member_initlist=mil, contents=str(contents))


def create_final_construct_fn(scope: cpp_gen.Struct, provides_ports: CppPorts,
                              requires_ports: CppPorts, encapsulee: CppEncapsulee) -> Function:
    """Create c++ code for the FinalConstruct method."""
    param = const_param_ptr_t(['dzn', 'meta'], 'parentComponentMeta', 'nullptr')
    fn = Function(return_type=void_t(), name='FinalConstruct',
                  scope=scope, params=[param])

    all_pp, mts_pp = (provides_ports.ports, provides_ports.mts_ports)
    all_rp, mts_rp = (requires_ports.ports, requires_ports.mts_ports)
    encapsulee_mv = encapsulee.member_var.name

    fn.contents = TextBlock([
        Comment('Check the bindings of all boundary ports'),
        [f'{p.accessor_fn_call}.check_bindings();' for p in all_pp],
        [f'{p.accessor_fn_call}.check_bindings();' for p in all_rp],
        BLANK_LINE,

        Comment('Copy the out-functors of the boundary provides-ports (MTS) to the '
                'respective ports of the encapsulated component'),
        [f'{encapsulee_mv}.{p.name}.out = {p.accessor_fn_call}.out;'
         for p in mts_pp] if mts_pp else Comment('<none>'),
        BLANK_LINE,

        Comment('Copy the in-functors of the boundary requires-ports (MTS) to the '
                'respective ports of the encapsulated component'),
        [f'{encapsulee_mv}.{p.name}.in = {p.accessor_fn_call}.in;'
         for p in mts_rp] if mts_rp else Comment('<none>'),
        BLANK_LINE,

        Comment('Complete the encapsulated component meta information and check the bindings '
                'of all encapsulee ports'),
        f'{encapsulee_mv}.dzn_meta.parent = {param.name};',
        f'{encapsulee_mv}.check_bindings();',
    ])
    return fn


def create_facilities_check_fn(scope: cpp_gen.Struct,
                               facilities_origin: FacilitiesOrigin) -> Function:
    """Create c++ code for the FacilitiesCheck() method."""
    param = const_param_ref_t(['dzn', 'locator'], 'locator')
    fn = Function(return_type=param.type_desc, name='FacilitiesCheck', params=[param],
                  prefix=FunctionPrefix.STATIC, scope=scope)

    if facilities_origin == FacilitiesOrigin.CREATE:
        fn.contents = TextBlock([
            Comment('This class creates the required facilities. But in case the user provided '
                    'locator argument already contains some or\nall facilities, it indicates an '
                    'execution deployment error. Important: each threaded subsystem has its own '
                    'exclusive\ninstances of the dispatcher and dezyne runtime facilities. They '
                    'can never be shared with other threaded subsystems.'),
            BLANK_LINE,
            'if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error('
            f'"{scope.name}: Overlapping dispatcher found (dzn::pump)");',
            'if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error('
            f'"{scope.name}: Overlapping Dezyne runtime found (dzn::runtime)");',
            BLANK_LINE,
            'return locator;'
        ])
    elif facilities_origin == FacilitiesOrigin.IMPORT:
        fn.contents = TextBlock([
            Comment('This class imports the requires facilities that must be provided by the user '
                    'via the locator argument.'),
            BLANK_LINE,
            'if (locator.try_get<dzn::pump>() == nullptr) throw std::runtime_error('
            f'"{scope.name}: Dispatcher missing (dzn::pump)");',
            'if (locator.try_get<dzn::runtime>() == nullptr) throw std::runtime_error('
            f'"{scope.name}: Dezyne runtime missing (dzn::runtime)");',
            BLANK_LINE,
            'return locator;'
        ])

    return fn


@dataclass(frozen=True)
class CppElements:
    """CppElements"""
    orig_file_basename: str
    target_file_basename: str
    namespace: Namespace
    struct: Struct
    # container: Container
    constructor: Constructor
    final_construct_fn: Function
    facilities_check_fn: Function
    facilities: Facilities
    encapsulee: CppEncapsulee
    provides_ports: CppPorts
    requires_ports: CppPorts


@dataclass(frozen=True)
class Recipe:
    """Recipe"""
    configuration: Configuration
    dzn_elements: DznElements
    cpp_elements: CppElements


@dataclass(frozen=True)
class GeneratedContent:
    """GeneratedContent"""
    filename: str
    contents: str


@dataclass(frozen=True)
class CodeGenResult:
    """CodeGenResult"""
    hh: GeneratedContent
    cc: GeneratedContent


class Builder:
    """Builder"""
    _recipe: Recipe

    def build(self, cfg: Configuration) -> CodeGenResult:
        """Build a custom shell according to the specified configuration."""

        fc = cfg.ast_fc

        # ---------- Prepare Dezyne Elements ----------

        # lookup encapsulee and check its type
        dzn_encapsulee = find_on_fqn(fc, namespaceids_t(cfg.fqn_encapsulee_name), [])
        if dzn_encapsulee is None:
            raise AdvShellError(f'Encapsulee {cfg.fqn_encapsulee_name} not found')

        dzn_elements = create_dzn_elements(cfg, fc, dzn_encapsulee)
        scope_fqn = dzn_elements.scope_fqn.ns_ids

        # ---------- Prepare C++ Elements ----------

        orig_file_basename = get_basename(cfg.dezyne_filename)
        custom_shell_name = f'{orig_file_basename}{cfg.output_basename_suffix}'
        target_file_basename = custom_shell_name
        namespace = cpp_gen.Namespace(ns_ids=scope_fqn)
        struct = cpp_gen.Struct(name=custom_shell_name)

        encapsulee = create_encapsulee(dzn_elements)
        pp = CppPorts(
            [create_cpp_portitf(p, struct, encapsulee) for p in dzn_elements.provides_ports])
        rp = CppPorts(
            [create_cpp_portitf(p, struct, encapsulee) for p in dzn_elements.requires_ports])
        facilities = create_facilities(cfg.facilities_origin, struct)

        constructor = create_constructor(struct, facilities, encapsulee, pp, rp, fc)
        final_construct_fn = create_final_construct_fn(struct, pp, rp, encapsulee)
        facilities_check_fn = create_facilities_check_fn(struct, cfg.facilities_origin)

        cpp_elements = CppElements(orig_file_basename, target_file_basename, namespace, struct,
                                   constructor, final_construct_fn,
                                   facilities_check_fn, facilities, encapsulee, pp, rp)

        # ---------- Generate ----------
        self._recipe = Recipe(cfg, dzn_elements, cpp_elements)

        # generate c++ code
        return CodeGenResult(hh=self._create_headerfile(), cc=self._create_sourcefile())

    def _create_headerfile(self) -> GeneratedContent:
        """Generate a c++ headerfile according to the current recipe."""
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        header_comments = cpp_gen.CommentBlock([
            cfg.copyright,
            BLANK_LINE,
            GEN_DO_NOT_MODIFY,
            BLANK_LINE,
            self._create_creator_info_overview(),
            BLANK_LINE,
            self._create_configuration_overview(),
            BLANK_LINE,
            self._create_final_port_overview()
        ])

        header = [header_comments,
                  BLANK_LINE,
                  cpp_gen.SystemIncludes(['dzn/pump.hh']),
                  cpp_gen.ProjectIncludes([f'{r.cpp_elements.orig_file_basename}.hh']),
                  BLANK_LINE]

        public_section = TextBlock([cpp.constructor.as_decl,
                                    cpp.final_construct_fn.as_decl,
                                    BLANK_LINE,
                                    cpp.facilities.accessors_decl,
                                    BLANK_LINE,
                                    cpp.provides_ports.accessors_decl,
                                    BLANK_LINE,
                                    cpp.requires_ports.accessors_decl,
                                    ])

        private_section = TextBlock([cpp.facilities.member_variables,
                                     cpp.facilities_check_fn.as_decl,
                                     BLANK_LINE,
                                     cpp.encapsulee,
                                     BLANK_LINE,
                                     cpp.provides_ports.member_variables,
                                     BLANK_LINE,
                                     cpp.requires_ports.member_variables,
                                     ])

        # fill the struct declaration with the public and private sections
        cpp.struct.contents = TextBlock([
            cpp_gen.AccessSpecifiedSection(
                access_specifier=AccessSpecifier.ANONYMOUS,
                contents=public_section),
            BLANK_LINE,
            cpp_gen.AccessSpecifiedSection(
                access_specifier=AccessSpecifier.PRIVATE,
                contents=private_section)
        ])
        cpp.namespace.contents = str(cpp.struct)

        footer = Comment(f'Version: {VERSION}')

        return GeneratedContent(filename=f'{cpp.target_file_basename}.hh',
                                contents=str(TextBlock([header, cpp.namespace, footer])))

    def _create_sourcefile(self) -> GeneratedContent:
        """Generate a c++ sourcefile according to the current recipe."""
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        header = [cpp_gen.CommentBlock([cfg.copyright, BLANK_LINE, GEN_DO_NOT_MODIFY]),
                  BLANK_LINE,
                  cpp_gen.ProjectIncludes([f'{cpp.target_file_basename}.hh']),
                  BLANK_LINE]

        # fill the struct declaration with the public and private sections
        cpp.namespace.contents = [BLANK_LINE,
                                  cpp.facilities_check_fn.as_def,
                                  BLANK_LINE,
                                  cpp.constructor.as_def,
                                  BLANK_LINE,
                                  cpp.final_construct_fn.as_def,
                                  BLANK_LINE,
                                  cpp.facilities.accessors_def,
                                  BLANK_LINE,
                                  cpp.provides_ports.accessors_def,
                                  BLANK_LINE,
                                  cpp.requires_ports.accessors_def,
                                  BLANK_LINE,
                                  ]

        footer = Comment(f'Version: {VERSION}')

        return GeneratedContent(filename=f'{cpp.target_file_basename}.cc',
                                contents=str(TextBlock([header, cpp.namespace, footer])))

    def _create_creator_info_overview(self) -> Optional[str]:
        """Create the creator information overview"""
        cfg = self._recipe.configuration

        return str(TextBlock([
            'Creator information:',
            TextBlock(cfg.creator_info).indent() if cfg.creator_info else '<none>',
        ]))

    def _create_configuration_overview(self) -> str:
        """Create the configuration overview"""
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        return str(TextBlock([
            'Configuration:',
            f'- Encapsulee FQN: {".".join(cfg.fqn_encapsulee_name)}',
            f'- Source file basename: {cpp.orig_file_basename}',
            f'- Target file basename: {cpp.target_file_basename}',
            f'- Dezyne facilities: {cfg.facilities_origin.value}',
            f'- Port semantics: {cfg.port_cfg}',
        ]))

    def _create_final_port_overview(self) -> str:
        """Create the final port overview."""
        cpp = self._recipe.cpp_elements

        def port_and_itf_name(ports) -> str:
            return '\n'.join([f'- {p.name}: {p.dzn_port_itf.interface.name}' for p in ports])

        provides_sts = port_and_itf_name(cpp.provides_ports.sts_ports)
        provides_mts = port_and_itf_name(cpp.provides_ports.mts_ports)
        requires_sts = port_and_itf_name(cpp.requires_ports.sts_ports)
        requires_mts = port_and_itf_name(cpp.requires_ports.mts_ports)

        return str(TextBlock([
            f'Provides ports (Single-threaded):\n{provides_sts}\n\n' if provides_sts else None,
            f'Provides ports (Multi-threaded):\n{provides_mts}\n\n' if provides_mts else None,
            f'Requires ports (Single-threaded):\n{requires_sts}\n\n' if requires_sts else None,
            f'Requires ports (Multi-threaded):\n{requires_mts}\n\n' if requires_mts else None,
        ]))
