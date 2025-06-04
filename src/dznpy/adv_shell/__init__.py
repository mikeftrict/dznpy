"""
Package providing functionality to generate a c++ shell around a Dezyne component with
the ability to specify a runtime semantics per port: Single-threaded (STS) or Multi-threaded (MTS).
When MTS is specified for a port, adv_shell generates c++ code that inserts an port that will
redirect inbound events via the dispatcher (dzn::pump).
This is equivalent to `dzn.cmd code --shell`. But with the major difference that dzn.cmd by default
generates MTS redirection for **all** ports; while with adv_shell you can specify selectively.
Besides wrapping a System Component (like dzn.cmd), advanced shell also supports wrapping
an Implementation Component.

Lastly, advanced shell allows the user to configure whether the required dezyne facilties such as
(dzn::pump and dzn::runtime) are created by the advanced shell instance or provided by the user.
This latter scenario allows for building and hooking up Dezyne subsystems in a modular fashion
where the whole must run with a single dispatcher.

Example configurations:
- All provides ports STS, all requires ports MTS
- All requires ports MTS, all provides ports STS
- All requires ports MTS, mixed provides ports MTS/STS
- All provides and requires ports MTS (like dzn code --shell)
"""

# Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
# This is free software, released under the MIT License. Refer to dznpy/LICENSE.


# system modules
from typing import Optional, List

# dznpy modules
from ..dznpy_version import VERSION
from .. import cpp_gen
from ..ast_view import find_fqn
from ..cpp_gen import AccessSpecifier, Comment
from ..misc_utils import get_basename
from ..support_files import strict_port, ilog, misc_utils, meta_helpers, multi_client_selector, \
    mutex_wrapped
from ..scoping import ns_ids_t
from ..text_gen import BLANK_LINE, chunk, DO_NOT_MODIFY, GeneratedContent, TextBlock, TB, EOL

# own modules
from .common import CodeGenResult, Configuration, Recipe, CppPorts, create_encapsulee, \
    CppElements, SupportFiles, CppPortItf
from .types import AdvShellError
from .port_selection import PortsCfg, PortsSemanticsCfg, PortSelect, PortWildcard, \
    MultiClientPortCfg
from .core.processing import create_dzn_elements, create_cpp_portitf, create_facilities, \
    create_constructor, create_final_construct_fn, create_facilities_check_fn, \
    create_cpp_port_helpers


# helper functions to create a prefined PortsCfg

def all_mts(multiclient: Optional[MultiClientPortCfg] = None) -> PortsCfg:
    """Configure all provides and requires ports with multi-threaded runtime semantics (MTS).
    This is equivalent to what `dzn code --shell` generates."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                               mts=PortSelect(PortWildcard.ALL)),
                    requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                               mts=PortSelect(PortWildcard.ALL)),
                    multiclient=multiclient)


def all_sts() -> PortsCfg:
    """Configure all provides and requires ports with single-threaded runtime semantics (STS)."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                               mts=PortSelect(PortWildcard.NONE)),
                    requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                               mts=PortSelect(PortWildcard.NONE)))


def all_sts_all_mts() -> PortsCfg:
    """Configure all provides ports with single-threaded runtime semantics (STS) and all
    requires ports as multi-threaded runtime semantics (MTS)."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                               mts=PortSelect(PortWildcard.NONE)),
                    requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                               mts=PortSelect(PortWildcard.ALL)))


def all_mts_all_sts(multiclient: Optional[MultiClientPortCfg] = None) -> PortsCfg:
    """Configure all provides ports with multi-threaded runtime semantics (MTS) and all
    requires ports as single-threaded runtime semantics (STS)."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                               mts=PortSelect(PortWildcard.ALL)),
                    requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                               mts=PortSelect(PortWildcard.NONE)),
                    multiclient=multiclient)


def all_mts_mixed_ts(sts_requires_ports: PortSelect,
                     mts_requires_ports: PortSelect,
                     multiclient: Optional[MultiClientPortCfg] = None) -> PortsCfg:
    """Configure all -provides ports- with multi-threaded runtime semantics (MTS) but the
    requires ports as a mix of single or multi-threaded runtime semantics (Mixed)
    specified by user configuration."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                               mts=PortSelect(PortWildcard.ALL)),
                    requires=PortsSemanticsCfg(sts=sts_requires_ports,
                                               mts=mts_requires_ports),
                    multiclient=multiclient)


def all_sts_mixed_ts(sts_requires_ports: PortSelect,
                     mts_requires_ports: PortSelect) -> PortsCfg:
    """Configure all -provides ports- with single-threaded runtime semantics (STS) but the
    requires ports as a mix of single or multi-threaded runtime semantics (Mixed)
    specified by user configuration."""
    return PortsCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                               mts=PortSelect(PortWildcard.NONE)),
                    requires=PortsSemanticsCfg(sts=sts_requires_ports,
                                               mts=mts_requires_ports))


class Builder:
    """Class to build an Advanced Shell according to a user specified configuration."""
    _recipe: Recipe

    def build(self, cfg: Configuration) -> CodeGenResult:
        """Build a custom shell according to the specified configuration."""

        # ---------- Prechecks ----------

        # lookup encapsulee and check its type
        find_result = find_fqn(cfg.ast_fc, ns_ids_t(cfg.fqn_encapsulee_name))
        if not find_result.items:
            raise AdvShellError(f'Encapsulee "{cfg.fqn_encapsulee_name}" not found')
        dzn_encapsulee = find_result.get_single_instance()

        # ---------- Prepare Dezyne Elements ----------

        dzn_elements = create_dzn_elements(cfg, cfg.ast_fc, dzn_encapsulee)
        scope_fqn = dzn_elements.scope_fqn.ns_ids

        # ---------- Prepare C++ Elements ----------

        orig_file_basename = get_basename(cfg.dezyne_filename)
        custom_shell_name = f'{orig_file_basename}{cfg.output_basename_suffix}'
        target_file_basename = custom_shell_name
        namespace = cpp_gen.Namespace(ns_ids=scope_fqn)
        struct = cpp_gen.Struct(name=custom_shell_name)

        encapsulee = create_encapsulee(dzn_elements)

        sf_ns_prefix = cfg.support_files_ns_prefix
        sfs = SupportFiles(strict_port=strict_port.create_header(sf_ns_prefix),
                           ilog=ilog.create_header(sf_ns_prefix),
                           misc_utils=misc_utils.create_header(sf_ns_prefix),
                           meta_helpers=meta_helpers.create_header(sf_ns_prefix),
                           multi_client_selector=multi_client_selector.create_header(sf_ns_prefix),
                           mutex_wrapped=mutex_wrapped.create_header(sf_ns_prefix))

        support_files_ns = sfs.strict_port.namespace

        ppo = CppPorts(
            [create_cpp_portitf(p, struct, support_files_ns, encapsulee, sfs) for p in
             dzn_elements.provides_ports])
        rpo = CppPorts(
            [create_cpp_portitf(p, struct, support_files_ns, encapsulee, sfs) for p in
             dzn_elements.requires_ports])

        helper_methods = create_cpp_port_helpers('Provides port', ppo, support_files_ns,
                                                 struct, cfg.ast_fc)

        facilities = create_facilities(cfg.facilities_origin, struct)

        constructor = create_constructor(struct, facilities, encapsulee, ppo, rpo, cfg.ast_fc, sfs)
        final_construct_fn = create_final_construct_fn(struct, ppo, rpo, encapsulee)
        facilities_check_fn = create_facilities_check_fn(struct, cfg.facilities_origin)

        cpp_elements = CppElements(orig_file_basename, target_file_basename, namespace, struct,
                                   constructor, final_construct_fn, facilities_check_fn, facilities,
                                   encapsulee, ppo, rpo, helper_methods, sfs)

        # ---------- Generate ----------
        self._recipe = Recipe(cfg, dzn_elements, cpp_elements)

        # generate c++ code
        return CodeGenResult(files=[self._create_headerfile(),
                                    self._create_sourcefile()] + sfs.as_list())

    def _create_headerfile(self) -> GeneratedContent:
        """Generate a c++ headerfile according to the current recipe."""
        rec = self._recipe
        cfg = rec.configuration
        cpp = rec.cpp_elements

        header_comments = cpp_gen.Comment([
            cfg.copyright,
            BLANK_LINE,
            'Advanced Shell',
            BLANK_LINE,
            self._create_creator_info_overview(),
            BLANK_LINE,
            self._create_configuration_overview(),
            BLANK_LINE,
            self._create_final_port_overview(),
            DO_NOT_MODIFY,
        ])

        project_includes_list = [f'{rec.cpp_elements.orig_file_basename}.hh',
                                 f'{cpp.support_files.strict_port.filename}']
        if cfg.ports_cfg.multiclient:
            project_includes_list.extend([f'{cpp.support_files.ilog.filename}',
                                          f'{cpp.support_files.multi_client_selector.filename}'])

        header = [header_comments,
                  BLANK_LINE,
                  cpp_gen.SystemIncludes(cpp.facilities.system_includes),
                  cpp_gen.ProjectIncludes(project_includes_list),
                  BLANK_LINE]

        public_section = cpp_gen.AccessSpecifiedSection(
            access_specifier=AccessSpecifier.ANONYMOUS,
            contents=TB(chunk_spacing=EOL) + \
                     TB([cpp.constructor.as_decl(),
                         cpp.final_construct_fn.as_decl()]) + \
                     cpp.facilities.accessors_decl + \
                     cpp.provides_ports.accessors_decl + \
                     cpp.provides_port_helpers.public_decl + \
                     cpp.requires_ports.accessors_decl)

        private_section = cpp_gen.AccessSpecifiedSection(
            access_specifier=AccessSpecifier.PRIVATE,
            contents=TB(chunk_spacing=EOL) + \
                     TB([cpp.facilities.member_variables,
                         cpp.facilities_check_fn.as_decl()]) + \
                     cpp.encapsulee + \
                     cpp.provides_ports.rerouting_class_members + \
                     cpp.provides_port_helpers.private_decl + \
                     cpp.requires_ports.rerouting_class_members)

        # fill the struct declaration with the public and private sections
        cpp.struct.decl_contents = TB(chunk_spacing=EOL) + \
                                   public_section + \
                                   private_section

        cpp.namespace.contents = TB(str(cpp.struct))

        footer = Comment(f'Generated by: dznpy/adv_shell v{VERSION}')

        return GeneratedContent(filename=f'{cpp.target_file_basename}.hh',
                                contents=str(TextBlock([header, cpp.namespace, footer])))

    def _create_sourcefile(self) -> GeneratedContent:
        """Generate a c++ sourcefile according to the current recipe."""
        rec = self._recipe
        cfg = rec.configuration
        cpp = rec.cpp_elements

        header_comments = cpp_gen.Comment([
            cfg.copyright,
            BLANK_LINE,
            'Advanced Shell',
            BLANK_LINE,
            DO_NOT_MODIFY,
        ])

        header = [header_comments,
                  BLANK_LINE,
                  cpp_gen.SystemIncludes(['dzn/runtime.hh']),  # used by FacilitiesCheck()
                  cpp_gen.ProjectIncludes([f'{cpp.target_file_basename}.hh']),
                  BLANK_LINE]

        # fill the struct declaration with the public and private sections
        cpp.namespace.contents = TB([BLANK_LINE,
                                     chunk(cpp.facilities_check_fn.as_def()),
                                     chunk(cpp.constructor.as_def()),
                                     chunk(cpp.final_construct_fn.as_def()),
                                     chunk(cpp.facilities.accessors_def),
                                     chunk(cpp.provides_ports.accessors_def),
                                     chunk(cpp.provides_port_helpers.public_def),
                                     chunk(cpp.requires_ports.accessors_def),
                                     chunk(cpp.provides_port_helpers.private_def),
                                     ])

        footer = Comment(f'Generated by: dznpy/adv_shell v{VERSION}')

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
        rec = self._recipe
        cfg = rec.configuration
        cpp = rec.cpp_elements

        return str(TextBlock([
            'User configuration:',
            f'- Encapsulee FQN: {cfg.fqn_encapsulee_name}',
            f'- Source file basename: {cpp.orig_file_basename}',
            f'- Target file basename: {cpp.target_file_basename}',
            f'- Dezyne facilities: {cfg.facilities_origin.value}',
            f'- Ports{"" if cfg.ports_cfg.multiclient else " (none multiclient)"}:',
            TextBlock(cfg.ports_cfg).indent(),
        ]))

    def _create_final_port_overview(self) -> str:
        """Create the final port overview."""
        cpp = self._recipe.cpp_elements

        def port_info(ports: List[CppPortItf], label: str) -> Optional[TextBlock]:
            """Stringify the list of ports in a human friendly readable textblock."""

            if not ports:
                return None

            all_ports = []
            for prt in ports:
                itf_name = prt.dzn_port_itf.interface.name
                multiclient = prt.dzn_port_itf.multiclient

                if multiclient:
                    itf_str = f'*MultiClient* {itf_name} (with {multiclient})'
                else:
                    itf_str = itf_name

                all_ports.append(f'> {prt.name}: {itf_str}')

            return chunk(TextBlock([f'- {label}:', TextBlock(all_ports).indent()]))

        return str(TextBlock([
            'Final configuration:',
            port_info(cpp.provides_ports.sts_ports, 'Provides ports (Single-threaded)'),
            port_info(cpp.provides_ports.mts_ports, 'Provides ports (Multi-threaded)'),
            port_info(cpp.requires_ports.sts_ports, 'Requires ports (Single-threaded)'),
            port_info(cpp.requires_ports.mts_ports, 'Requires ports (Multi-threaded)'),
        ]))
