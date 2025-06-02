"""
Module implementing the core processing of advanced shell.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# system modules
from typing import Optional

# dznpy modules
from ... import cpp_gen, ast, ast_view
from ...ast import Component, System, Event, EventDirection
from ...ast_view import find_fqn, FindError
from ...cpp_gen import Comment, Constructor, Function, FunctionPrefix, Fqn, fqn_t, MemberVariable, \
    TypeDesc, TypePostfix, const_param_ref_t, const_param_ptr_t, void_t, TemplateArg
from ...misc_utils import flatten_to_strlist, assert_t_optional, plural
from ...scoping import NamespaceIds, ns_ids_t
from ...text_gen import BLANK_LINE, chunk, cond_chunk, TextBlock, TB

# own modules
from ..common import Configuration, CppPortItf, DznPortItf, \
    FacilitiesOrigin, DznElements, Facilities, CppEncapsulee, CppPorts, MultiClientPortCfgFixture, \
    SupportFiles, CppHelperMethods
from ..port_selection import MultiClientPortCfg
from ..types import AdvShellError, RuntimeSemantics, MultiClientCfgError


def create_dzn_elements(cfg: Configuration, fct: ast.FileContents,
                        encapsulee: ast.System or ast.Component) -> DznElements:
    """Create a DznElements dataclass instance."""

    if not isinstance(encapsulee, System) and not isinstance(encapsulee, Component):
        raise AdvShellError('Only system or implementation components can be encapsulated')

    scope_fqn = encapsulee.parent_ns.fqn
    port_names = ast_view.portnames_t(encapsulee.ports)
    all_ports = cfg.ports_cfg.match(port_names.provides, port_names.requires)

    provides_ports = []
    requires_ports = []
    for port in encapsulee.ports.elements:
        find_result = find_fqn(fct, port.type_name.value, scope_fqn)
        itf = find_result.get_single_instance(ast.Interface)

        if port.direction == ast.PortDirection.PROVIDES:
            # check multi client configuration for this port
            mc_fixture = check_multiclient_cfg(cfg.ports_cfg.multiclient, port.name, itf, fct)
            provides_ports.append(DznPortItf(port, itf, all_ports.value[port.name], mc_fixture))
        else:
            if not port.injected.value:  # filter out injected required ports
                requires_ports.append(DznPortItf(port, itf, all_ports.value[port.name]))

    # post check whether a multiclient port configuration has actually been matched
    if cfg.ports_cfg.multiclient:
        if not any(p.multiclient for p in provides_ports):
            raise AdvShellError(f'Port "{cfg.ports_cfg.multiclient.port_name}" not found '
                                'for Multiclient port configuration')

    return DznElements(fct, encapsulee, Fqn(scope_fqn), provides_ports, requires_ports)


def check_multiclient_cfg(cfg: Optional[MultiClientPortCfg],
                          candidate_port_name: str,
                          itf: ast.Interface,
                          fct: ast.FileContents) -> Optional[MultiClientPortCfgFixture]:
    """Check the user specified Multi-Client port configuration on valid values and return
    a final fixture as a result. When parameter 'cfg' is empty an empty fixture is returned.
    On validation errors an exception will be raised."""
    assert_t_optional(cfg, MultiClientPortCfg)

    # early return when a configuration is absent
    if not cfg:
        return None

    # early return when the canditate port is not matching the configuration
    if candidate_port_name != cfg.port_name:
        return None

    # lookup the event that matches the configured claim event name
    matched_claim_events = [e for e in itf.events.elements if e.name == cfg.claim_event_name]
    if not matched_claim_events:
        raise MultiClientCfgError(f'Claim event name "{cfg.claim_event_name}" not found')
    found_claim_event = matched_claim_events[0]

    # lookup the return type of the claim event
    enum_instance: ast.Enum
    try:
        find_result = find_fqn(fct, found_claim_event.signature.type_name.value, itf.fqn)
        enum_instance = find_result.get_single_instance(ast.Enum)
    except FindError as exc:
        raise MultiClientCfgError(
            'Only Enum as return type of the claim event is supported.') from exc

    # lookup the return value of the found enum
    enum_value = ns_ids_t(cfg.claim_granting_reply_value.items[0])
    if str(enum_value) not in enum_instance.fields.elements:
        raise MultiClientCfgError(f'"{cfg.claim_granting_reply_value}" is not a valid value of the'
                                  f' "{enum_instance.fqn}" return type')

    # lookup the event that matches the configured release event name
    matched_release_events = [e for e in itf.events.elements if e.name == cfg.release_event_name]
    if not matched_release_events:
        raise MultiClientCfgError(f'Release event name "{cfg.release_event_name}" not found')
    found_release_event = matched_release_events[0]

    return MultiClientPortCfgFixture(claim_event=found_claim_event,
                                     claim_granting_reply=enum_instance.fqn + enum_value,
                                     release_event=found_release_event)


def create_facilities(origin: FacilitiesOrigin, scope) -> Facilities:
    """create_facilities"""
    if origin == FacilitiesOrigin.IMPORT:
        dispatcher_mv = cpp_gen.decl_var_ref_t(fqn_t('dzn.pump'), 'm_dispatcher')
        return Facilities(origin, dispatcher_mv, None, None, None)

    if origin == FacilitiesOrigin.CREATE:
        dispatcher_mv = cpp_gen.decl_var_t(fqn_t('dzn.pump'), 'm_dispatcher')
        runtime_mv = cpp_gen.decl_var_t(fqn_t('dzn.runtime'), 'm_runtime')
        locator_t = TypeDesc(fqn_t('dzn.locator'))
        locator_mv = cpp_gen.decl_var_t(locator_t.fqname, 'm_locator')

        locator_accessor_fn = Function(
            return_type=TypeDesc(locator_t.fqname, postfix=TypePostfix.REFERENCE),
            name='Locator',
            parent=scope,
            contents=TB(f'return {locator_mv.name};'))

        return Facilities(origin, dispatcher_mv, runtime_mv, locator_mv, locator_accessor_fn)

    raise AdvShellError(f'Invalid argument "origin: " {origin}')


def create_cpp_port_helpers(label: str, cpp_ports: CppPorts, support_files_ns: NamespaceIds,
                            scope: cpp_gen.Struct, fct: ast.FileContents) -> CppHelperMethods:
    """Create an instance of CppHelperMethods according to the specified caller arguments."""
    public_fns = []
    private_fns = []

    for port in cpp_ports.ports:
        def client_identifiers_fn(cpp_port: CppPortItf):
            """Create the public GetClientIdentifiers() helper function."""

            ci_fqn = Fqn(support_files_ns + ns_ids_t('ClientIdentifier'), True)
            return Function(return_type=TypeDesc(fqname=Fqn(ns_ids_t('std.vector')),
                                                 template_arg=TemplateArg(ci_fqn)),
                            name=f'Get{cpp_port.cap_name}ClientIdentifiers',
                            parent=scope,
                            contents=TB(
                                f'return {cpp_port.accessor_target}.GetClientIdentifiers();'),
                            cav='const')

        def initialize_port_fn(cpp_port: CppPortItf):
            """Create the private InitializePort<name>() helper function."""
            dzn = cpp_port.dzn_port_itf
            return_type = TypeDesc(Fqn(dzn.interface.fqn, True))

            return Function(return_type=TypeDesc(return_type.fqname),
                            name=f'InitializePort{cpp_port.cap_name}',
                            params=[const_param_ref_t(
                                fqn_t(support_files_ns + ns_ids_t('ClientIdentifier'),
                                      prefix_root_ns=True), 'identifier')],
                            parent=scope,
                            contents=initialize_port_impl(cpp_port, support_files_ns, fct))

        if port.dzn_port_itf.multiclient:
            public_fns.append(client_identifiers_fn(port))
            private_fns.append(initialize_port_fn(port))

    return CppHelperMethods(label, public_fns, private_fns)


def create_cpp_portitf(dzn: DznPortItf, scope: cpp_gen.Struct, support_files_ns: NamespaceIds,
                       encapsulee: CppEncapsulee, sfs: SupportFiles) -> CppPortItf:
    """Create an instance of CppPortItf according to the specified caller arguments."""
    typ = TypeDesc(Fqn(dzn.interface.fqn, True))
    fn_prefix = f'{dzn.port.direction.value}'
    cap_name = dzn.port.name[0].upper() + dzn.port.name[1:]

    def sts():
        # pass-through mode
        strict_port_type = TypeDesc(fqname=Fqn(support_files_ns + ns_ids_t('Sts'), True),
                                    template_arg=TemplateArg(typ.fqname))
        member_var = None
        accessor_target = f'{encapsulee.member_var.name}.{dzn.port.name}'
        accessor_fn = Function(return_type=strict_port_type,
                               name=f'{fn_prefix}{cap_name}',
                               parent=scope,
                               contents=TB(f'return {{{accessor_target}}};'))
        return CppPortItf(dzn, typ, accessor_fn, accessor_target, member_var)

    def mts_plain():
        # reroute mode, requires an own port instance
        strict_port_type = TypeDesc(fqname=Fqn(support_files_ns + ns_ids_t('Mts'), True),
                                    template_arg=TemplateArg(typ.fqname))
        mv_prefix = 'm_pp' if dzn.port.direction == ast.PortDirection.PROVIDES else 'm_rp'
        member_var = MemberVariable(typ, f'{mv_prefix}{cap_name}')
        accessor_target = f'{member_var.name}'
        accessor_fn = Function(return_type=strict_port_type,
                               name=f'{fn_prefix}{cap_name}',
                               parent=scope,
                               contents=TB(f'return {{{accessor_target}}};'))
        return CppPortItf(dzn, typ, accessor_fn, accessor_target, member_var)

    def mts_with_multiclient_selector():
        # multiclient reroute mode, requires an own port instance including the multiclient selector
        mc_t = TypeDesc(fqname=Fqn(support_files_ns + ns_ids_t('MultiClientSelector'), True),
                        template_arg=TemplateArg(Fqn(dzn.interface.fqn, True)))
        strict_port_type = TypeDesc(fqname=Fqn(support_files_ns + ns_ids_t('Mts'), True),
                                    template_arg=TemplateArg(typ.fqname))
        mv_prefix = 'm_pp'  # only provides ports can be multiclient
        member_var = MemberVariable(mc_t, f'{mv_prefix}{cap_name}')
        accessor_target = f'{member_var.name}'
        accessor_fn = \
            Function(return_type=strict_port_type,
                     name=f'{fn_prefix}MultiClient{cap_name}',
                     params=[const_param_ref_t(
                         fqn_t(sfs.multi_client_selector.namespace + ns_ids_t(
                             'ClientIdentifier'), prefix_root_ns=True), 'identifier')],
                     parent=scope,
                     contents=TB(
                         f'return {{{accessor_target}.Index(identifier).dznPort}};'))

        return CppPortItf(dzn, typ, accessor_fn, accessor_target, member_var)

    if dzn.semantics == RuntimeSemantics.STS:
        return sts()
    if dzn.semantics == RuntimeSemantics.MTS and not dzn.multiclient:
        return mts_plain()
    if dzn.semantics == RuntimeSemantics.MTS and dzn.multiclient:
        return mts_with_multiclient_selector()

    raise ValueError('unknown runtime semantics')


def initialize_port_impl(port: CppPortItf,
                         support_files_ns: NamespaceIds, fct: ast.FileContents) -> TextBlock:
    """Create C++ code for the implementation of function InitializePortNNN()."""
    dzn = port.dzn_port_itf
    tb1 = [chunk(initialize_port_localvar_snippet(port, support_files_ns))]
    tb2 = []
    tb3 = ['return port;']

    for event in [e for e in dzn.interface.events.elements if
                  e.direction == EventDirection.IN]:
        if event == dzn.multiclient.claim_event:
            tb2.append(initialize_port_claim_snippet(port, dzn.multiclient, fct))
        elif event == dzn.multiclient.release_event:
            tb2.append(initialize_port_release_snippet(port, dzn.multiclient, fct))
        else:
            tb2.append(stdref_in_event(port, event))

    return TextBlock([tb1, chunk(tb2), tb3])


def initialize_port_localvar_snippet(port: CppPortItf, support_files_ns: NamespaceIds) -> str:
    """Create C++ snippet for declaring and defining the local 'port' variable that will
      be returned to the caller. Example:

        auto port(::Dzn::CreatePort<::My::IExclusiveToaster>("api", "arbiterApi"));

    """
    dzn = port.dzn_port_itf
    create_port = Fqn(support_files_ns + ns_ids_t('CreatePort'), True)
    cpp_port_type = Fqn(dzn.interface.fqn, True)
    arbiter_port_name = 'arbiter' + port.name[0].upper() + port.name[1:]
    return f'auto port({create_port}<{cpp_port_type}>("{port.name}", "{arbiter_port_name}"));'


def initialize_port_claim_snippet(port: CppPortItf, multiclient: MultiClientPortCfgFixture,
                                  fct: ast.FileContents) -> TextBlock:
    """Create C++ snippet for assigning a lambda for the port's claim in-event. Example:

        port.in.Claim = [&, identifier](PIncident& incident) {
            const auto r = m_ppApi.Arbitered().in.Claim(incident);
            if (r == Result::Ok) m_ppApi.Select(identifier);
            return r;
        };
    """
    dzn = port.dzn_port_itf
    event = multiclient.claim_event
    fqn_reply = Fqn(multiclient.claim_granting_reply, prefix_root_ns=True)

    args = []
    for i in event.signature.formals.elements:
        res = find_fqn(fct, i.type_name.value, dzn.interface.fqn)
        ext_type = res.get_single_instance()
        opt_ref = '&' if i.direction != ast.FormalDirection.IN else ''
        args.append(f'{ext_type.value.value}{opt_ref} {i.name}')

    stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
    call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

    lambda_body = TextBlock(
        [f'const auto r = {port.accessor_target}.Arbitered().in.{event.name}({call_arguments});',
         f'if (r == {fqn_reply}) {port.accessor_target}.Select(identifier);',
         'return r;'])

    return TextBlock([f'port.in.{event.name} = [&, identifier]{stdfunction_arguments} {{',
                      f'{lambda_body.indent()}',
                      '};'])


def initialize_port_release_snippet(port: CppPortItf, multiclient: MultiClientPortCfgFixture,
                                    fct: ast.FileContents) -> TextBlock:
    """Create C++ snippet for assigning a lambda for the port's release in-event. Example:

        port.in.Release = [&, identifier] {
            m_ppApi.Arbitered().in.Release();
            m_ppApi.Deselect(identifier);
        };
    """
    dzn = port.dzn_port_itf
    event = multiclient.release_event

    args = []
    for i in event.signature.formals.elements:
        res = find_fqn(fct, i.type_name.value, dzn.interface.fqn)
        ext_type = res.get_single_instance()
        opt_ref = '&' if i.direction != ast.FormalDirection.IN else ''
        args.append(f'{ext_type.value.value}{opt_ref} {i.name}')

    stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
    call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

    lambda_body = TextBlock([f'{port.accessor_target}.Arbitered().in.Release({call_arguments});',
                             f'{port.accessor_target}.Deselect(identifier);'])

    return TextBlock([f'port.in.{event.name} = [&, identifier]{stdfunction_arguments} {{',
                      f'{lambda_body.indent()}',
                      '};'])


def reroute_in_events(port: CppPortItf, facilities: Facilities, encapsulee: CppEncapsulee,
                      fct: ast.FileContents) -> Optional[str]:
    """Create C++ code to reroute in-events of boundary provides ports via the dispatcher. Example:

        m_ppApi.in.Cancel = [&] {
            return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
        };
        ...etc...
    """

    result = []
    for event in [e for e in port.dzn_port_itf.interface.events.elements if
                  e.direction == ast.EventDirection.IN]:
        in_formals = [f for f in event.signature.formals.elements if
                      f.direction == ast.FormalDirection.IN]

        args = []
        for i in event.signature.formals.elements:
            res = find_fqn(fct, i.type_name.value, port.dzn_port_itf.interface.fqn)
            ext_type = res.get_single_instance()
            opt_ref = '&' if i.direction != ast.FormalDirection.IN else ''
            args.append(f'{ext_type.value.value}{opt_ref} {i.name}')

        captures_by_value = ''.join(f', {x.name}' for x in in_formals)
        stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
        call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

        accessor_target = f'{port.accessor_target}'
        accessor_target += '()' if port.dzn_port_itf.multiclient else ''

        txt = f'{accessor_target}.in.{event.name} = [&]{stdfunction_arguments} {{\n' \
              f'    return dzn::shell({facilities.dispatcher.name}, [&{captures_by_value}] ' \
              f'{{ return {encapsulee.member_var.name}.{port.name}.in.{event.name}' \
              f'({call_arguments}); }});\n' \
              '};'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def reroute_out_events(port: CppPortItf, facilities: Facilities, encapsulee: CppEncapsulee,
                       fct: ast.FileContents) -> Optional[str]:
    """Create C++ code to reroute out-events of boundary required ports via the dispatcher. Example:

        m_rpCord.out.Disconnected = [&](Sub::MyLongNamedType param) {
            return m_dispatcher([&, param] { return m_encapsulee.cord.out.Disconnected(param); });
        };
        ...etc...
    """
    result = []
    for event in [event for event in port.dzn_port_itf.interface.events.elements if
                  event.direction == ast.EventDirection.OUT]:

        in_formals = [formal for formal in event.signature.formals.elements if
                      formal.direction == ast.FormalDirection.IN]

        args = []
        for i in event.signature.formals.elements:
            res = find_fqn(fct, i.type_name.value, port.dzn_port_itf.interface.fqn)
            ext_type = res.get_single_instance()
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


def stdref_provides_out_events(port: CppPortItf, encapsulee: CppEncapsulee) -> Optional[str]:
    """Create C++ code to stdref out-events of boundary provides ports directly to
    the encapsulee associated port. Example:

        m_encapsulee.api.in.Ok = std::ref(m_ppApi.in.Ok);
        ...etc...
    """
    result = []
    for event in [event for event in port.dzn_port_itf.interface.events.elements if
                  event.direction == ast.EventDirection.OUT]:
        txt = f'{encapsulee.member_var.name}.{port.name}.out.{event.name} = ' \
              f'std::ref({port.accessor_target}.out.{event.name});'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def stdref_requires_in_events(port: CppPortItf, encapsulee: CppEncapsulee) -> Optional[str]:
    """Create C++ code to stdref in-events of boundary requires ports directly to
    the encapsulee associated port. Example:

        m_encapsulee.cord.in.Initialize = std::ref(m_rpCord.in.Initialize);
        ...etc...
    """
    result = []
    for event in [event for event in port.dzn_port_itf.interface.events.elements if
                  event.direction == ast.EventDirection.IN]:
        txt = f'{encapsulee.member_var.name}.{port.name}.in.{event.name} = ' \
              f'std::ref({port.accessor_target}.in.{event.name});'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def reroute_multiclient_out_events(port: CppPortItf, fct: ast.FileContents) -> Optional[str]:
    """Create C++ code to reroute out-events of the encapsulee to the MultiClientSelector facility.
    Example:

        m_ppApi().out.Fail = [&](PIncident incident) {
            auto lockAndData = m_ppApi.CurrentClient();
            if (lockAndData->has_value()) lockAndData->value().get().dznPort.out.Fail(incident);
        };
        ...etc...

    """
    result = []
    for event in [event for event in port.dzn_port_itf.interface.events.elements if
                  event.direction == ast.EventDirection.OUT]:
        args = []
        for i in event.signature.formals.elements:
            res = find_fqn(fct, i.type_name.value, port.dzn_port_itf.interface.fqn)
            ext_type = res.get_single_instance()
            args.append(f'{ext_type.value.value} {i.name}')

        stdfunction_arguments = '(' + ', '.join(args) + ')' if args else ''
        call_arguments = ', '.join([arg.name for arg in event.signature.formals.elements])

        txt = f'{port.accessor_target}().out.{event.name} = [&]{stdfunction_arguments} {{\n' \
              f'    auto lockAndData = {port.accessor_target}.CurrentClient();\n' \
              '    if (lockAndData->has_value()) lockAndData->value().get().dznPort.out.' \
              f'{event.name}({call_arguments});\n' \
              '};'

        result.append(txt)

    return str(TextBlock(result)) if result else None


def stdref_in_event(port: CppPortItf, event: Event) -> TextBlock:
    """Create C++ snippet for assigning a referenced lambda for the port's generic in-event.
    Example:

        port.in.Initialize = std::ref(m_ppApi.in.Initialize); // by default

        port.in.Cancel = std::ref(m_ppApi().in.Cancel); // for a multiclient arbitered port 'api'

    """
    arbitered = '()' if port.is_multiclient else ''
    return TextBlock(
        [f'port.in.{event.name} = '
         f'std::ref({port.accessor_target}{arbitered}.in.{event.name});'])


def create_constructor(scope, facilities: Facilities,
                       encapsulee: CppEncapsulee,
                       provides_ports: CppPorts,
                       requires_ports: CppPorts,
                       fct: ast.FileContents,
                       sfs: SupportFiles
                       ) -> Constructor:
    """Create C++ code for the constructor"""

    # populate the member initialization list (mil)
    # -------------------------------------

    # construct or import the required dezyne facilities, construct the encapsulee
    if facilities.origin == FacilitiesOrigin.CREATE:
        p_locator = const_param_ref_t(fqn_t('dzn.locator'), 'prototypeLocator')
        mil = [f'{facilities.locator.name}(std::move(FacilitiesCheck({p_locator.name}).clone()'
               f'.set({facilities.runtime.name})'
               f'.set({facilities.dispatcher.name})))',
               f'{encapsulee.member_var.name}({facilities.locator.name})']
    elif facilities.origin == FacilitiesOrigin.IMPORT:
        p_locator = const_param_ref_t(fqn_t('dzn.locator'), 'locator')
        mil = [f'{facilities.dispatcher.name}(FacilitiesCheck({p_locator.name}).get<dzn::pump>())',
               f'{encapsulee.member_var.name}({p_locator.name})']
    else:
        raise AdvShellError(f'Invalid argument "origin: " {facilities.origin}')

    p_opt_multiclient_log = const_param_ref_t(
        fqn_t(sfs.ilog.namespace + ns_ids_t('ILog'), prefix_root_ns=True),
        'multiclientLog') if provides_ports.has_multiclient_port() else None
    p_shell_name = const_param_ref_t(fqn_t('std.string'), 'encapsuleeInstanceName', '""')

    # construct the (MTS) boundary ports
    mts_pp, mts_rp = (provides_ports.mts_ports, requires_ports.mts_ports)

    for prt in mts_pp:
        if prt.dzn_port_itf.multiclient:
            mil.append(
                f'{prt.member_var.name}(multiclientLog, "{prt.name}",'
                f' [this](const auto& identifier)'
                f' {{ return InitializePort{prt.cap_name}(identifier); }})')
        else:
            mil.append(f'{prt.member_var.name}({encapsulee.member_var.name}.{prt.name})')

    mts_rp = requires_ports.mts_ports
    mil.extend([f'{p.member_var.name}({encapsulee.member_var.name}.{p.name})' for p in mts_rp])

    # populate the definition of the constructor
    # ------------------------------------------
    encapsulee_mv = encapsulee.member_var.name

    rerouted_boundary_in_events = flatten_to_strlist(
        [reroute_in_events(p, facilities, encapsulee, fct) for p in mts_pp if
         not p.dzn_port_itf.multiclient])

    rerouted_boundary_out_events = flatten_to_strlist(
        [reroute_out_events(p, facilities, encapsulee, fct) for p in mts_rp])

    rerouted_multiclient_in_events = flatten_to_strlist(
        [reroute_in_events(p, facilities, encapsulee, fct) for p in mts_pp if
         p.dzn_port_itf.multiclient])

    rerouted_multiclient_out_events = flatten_to_strlist(
        [reroute_multiclient_out_events(p, fct) for p in mts_pp if
         p.dzn_port_itf.multiclient])

    stdrefd_mts_boundary_out_events = flatten_to_strlist(
        [stdref_provides_out_events(p, encapsulee) for p in mts_pp if
         not p.dzn_port_itf.multiclient])

    stdrefd_mts_boundary_in_events = flatten_to_strlist(
        [stdref_requires_in_events(p, encapsulee) for p in mts_rp])

    tmp = []
    for mc_port in [pp for pp in mts_pp if pp.is_multiclient]:
        for event in mc_port.dzn_port_itf.interface.events.elements:
            if event.direction == EventDirection.OUT:
                tmp.append(f'{encapsulee_mv}.{mc_port.name}.out.{event.name} = '
                           f'std::ref({mc_port.accessor_target}().out.{event.name});')
    stdrefd_encapsulee_out_events = flatten_to_strlist(tmp)

    contents = TextBlock([
        chunk([Comment('Complete the component meta info of the encapsulee and its ports that '
                       'are configured for MTS'),
               f'{encapsulee_mv}.dzn_meta.name = {p_shell_name.name};',
               [f'{encapsulee_mv}.{p.name}.meta.require.name = "{p.name}";' for p in mts_pp],
               [f'{encapsulee_mv}.{p.name}.meta.provide.name = "{p.name}";' for p in mts_rp]
               ]),

        chunk(Comment(['Boundary provides ports (MTS) initialization:', '-' * 45])),
        cond_chunk(None, Comment('<None>' if not mts_pp else None), None, all_or_nothing=True),

        cond_chunk(Comment('Reroute in-events of boundary provides ports (MTS) via the dispatcher '
                           'to the encapsulee'),
                   rerouted_boundary_in_events, None, all_or_nothing=True),

        cond_chunk(Comment('Reference out-events of boundary provides ports (MTS) to '
                           'the respective ports of the encapsulee'),
                   stdrefd_mts_boundary_out_events, None, all_or_nothing=True),

        cond_chunk(Comment('Reroute in-events of the internal arbitered multiclient port via the '
                           'dispatcher to the encapsulee'),
                   rerouted_multiclient_in_events, None, all_or_nothing=True),

        cond_chunk(Comment('Reroute out-events of the internal arbitered multiclient port via the '
                           'MultiClientSelector facility to the current Client having the claim'),
                   rerouted_multiclient_out_events, None, all_or_nothing=True),

        cond_chunk(Comment('Reference out-events of the encapsulee to the internal arbitered '
                           'multiclient port'),
                   stdrefd_encapsulee_out_events, None, all_or_nothing=True),

        chunk(Comment(['Boundary requires ports (MTS) initialization:', '-' * 45])),
        cond_chunk(None, Comment('<None>' if not mts_rp else None), None, all_or_nothing=True),

        cond_chunk(Comment('Reroute out-events of boundary requires ports (MTS)'
                           ' via the dispatcher'),
                   rerouted_boundary_out_events, None, all_or_nothing=True),

        cond_chunk(Comment('Reference in-events of boundary requires ports (MTS) to '
                           'the respective ports of the encapsulee'),
                   stdrefd_mts_boundary_in_events, None, all_or_nothing=True, appendix=None),

    ])

    return Constructor(parent=scope,
                       params=[p_locator, p_opt_multiclient_log, p_shell_name],
                       member_initlist=mil,
                       contents=contents.trim())


def create_final_construct_fn(scope: cpp_gen.Struct, provides_ports: CppPorts,
                              requires_ports: CppPorts, encapsulee: CppEncapsulee) -> Function:
    """Create c++ code for the FinalConstruct method."""
    param = const_param_ptr_t(fqn_t('dzn.meta'), 'parentComponentMeta', 'nullptr')
    fnc = Function(return_type=void_t(), name='FinalConstruct',
                   parent=scope, params=[param])

    all_pp = provides_ports.ports
    all_rp = requires_ports.ports
    encapsulee_mv = encapsulee.member_var.name

    final_construct_calls = [f'{p.accessor_target}.FinalConstruct();' for p in all_pp if
                             p.dzn_port_itf.multiclient]

    fnc.contents = TextBlock([

        [Comment(f'Call final construct on multiclient {plural("port", final_construct_calls)}'),
         final_construct_calls,
         BLANK_LINE] if final_construct_calls else None,

        Comment('Check the bindings of all boundary ports'),
        [f'{p.accessor_target}.check_bindings();' for p in all_pp if
         not p.dzn_port_itf.multiclient],
        [f'{p.accessor_target}.check_bindings();' for p in all_rp],

        BLANK_LINE,

        Comment('Complete the encapsulated component meta information and check the bindings '
                'of all encapsulee ports'),
        f'{encapsulee_mv}.dzn_meta.parent = {param.name};',
        f'{encapsulee_mv}.check_bindings();',
    ])
    return fnc


def create_facilities_check_fn(scope: cpp_gen.Struct,
                               facilities_origin: FacilitiesOrigin) -> Function:
    """Create c++ code for the FacilitiesCheck() method."""
    param = const_param_ref_t(fqn_t('dzn.locator'), 'locator')
    fnc = Function(return_type=param.type, name='FacilitiesCheck', params=[param],
                   prefix=FunctionPrefix.STATIC, parent=scope)

    if facilities_origin == FacilitiesOrigin.CREATE:
        fnc.contents = TextBlock([
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
        fnc.contents = TextBlock([
            Comment('This class imports the required facilities that must be provided by the user '
                    'via the locator argument.'),
            BLANK_LINE,
            'if (locator.try_get<dzn::pump>() == nullptr) throw std::runtime_error('
            f'"{scope.name}: Dispatcher missing (dzn::pump)");',
            'if (locator.try_get<dzn::runtime>() == nullptr) throw std::runtime_error('
            f'"{scope.name}: Dezyne runtime missing (dzn::runtime)");',
            BLANK_LINE,
            'return locator;'
        ])

    return fnc
