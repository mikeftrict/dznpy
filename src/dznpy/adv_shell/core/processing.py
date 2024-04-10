"""
Module implementing the core processing of advanced shell.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules

# dznpy modules
from ... import cpp_gen, ast, ast_view
from ...ast import Component, System
from ...ast_view import find_on_fqn
from ...cpp_gen import Comment, Constructor, Function, FunctionPrefix, Fqn, MemberVariable, \
    TypeDesc, TypePostfix, const_param_ref_t, const_param_ptr_t, void_t
from ...misc_utils import flatten_to_strlist, NameSpaceIds, TextBlock

# own modules
from ..common import BLANK_LINE, Configuration, CppPortItf, DznPortItf, \
    FacilitiesOrigin, DznElements, Facilities, CppEncapsulee, CppPorts
from ..types import AdvShellError, RuntimeSemantics


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
            if not port.injected.value:  # filter out injected required ports
                requires_ports.append(DznPortItf(port, itf, all_ports.value[port.name]))

    return DznElements(file_contents, encapsulee, Fqn(scope_fqn), provides_ports, requires_ports)


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


def create_cpp_portitf(dzn: DznPortItf, scope: cpp_gen.Struct, support_files_ns: NameSpaceIds,
                       encapsulee: CppEncapsulee) -> CppPortItf:
    """create_cpp_portitf"""
    t = TypeDesc(Fqn(dzn.interface.fqn, prefix_root_ns=True))
    fn_prefix = f'{dzn.port.direction.value}'
    cap_name = dzn.port.name[0].upper() + dzn.port.name[1:]

    if dzn.semantics == RuntimeSemantics.STS:
        # pass-through mode
        member_var = None
        wrap_strict_sts = TypeDesc(
            Fqn(support_files_ns + [f'Sts<{TypeDesc(t.fqn)}>'], prefix_root_ns=True))
        accessor_target = f'{encapsulee.member_var.name}.{dzn.port.name}'
        accessor_fn = Function(wrap_strict_sts,
                               f'{fn_prefix}{cap_name}', scope=scope,
                               contents=f'return {{{accessor_target}}};')
    elif dzn.semantics == RuntimeSemantics.MTS:
        # reroute mode, requires an own instance of the port
        mv_prefix = 'm_pp' if dzn.port.direction == ast.PortDirection.PROVIDES else 'm_rp'
        member_var = MemberVariable(t, f'{mv_prefix}{cap_name}')
        wrap_strict_sts = TypeDesc(
            Fqn(support_files_ns + [f'Mts<{TypeDesc(t.fqn)}>'], prefix_root_ns=True))
        accessor_target = f'{member_var.name}'
        accessor_fn = Function(wrap_strict_sts,
                               f'{fn_prefix}{cap_name}', scope=scope,
                               contents=f'return {{{accessor_target}}};')
    else:
        raise ValueError('unknown runtime semantics')

    return CppPortItf(dzn, t, accessor_fn, accessor_target, member_var)


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

        txt = f'{port.accessor_target}.in.{event.name} = [&]{stdfunction_arguments} {{\n' \
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

        txt = f'{port.accessor_target}.out.{event.name} = [&]{stdfunction_arguments} {{\n' \
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

    p_shell_name = const_param_ref_t(['std', 'string'], 'encapsuleeInstanceName', '""')

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
        [f'{p.accessor_target}.check_bindings();' for p in all_pp],
        [f'{p.accessor_target}.check_bindings();' for p in all_rp],
        BLANK_LINE,

        Comment('Copy the out-functors of the boundary provides-ports (MTS) to the '
                'respective ports of the encapsulated component'),
        [f'{encapsulee_mv}.{p.name}.out = {p.accessor_target}.out;'
         for p in mts_pp] if mts_pp else Comment('<none>'),
        BLANK_LINE,

        Comment('Copy the in-functors of the boundary requires-ports (MTS) to the '
                'respective ports of the encapsulated component'),
        [f'{encapsulee_mv}.{p.name}.in = {p.accessor_target}.in;'
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
