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

# Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
# This is free software, released under the MIT License. Refer to dznpy/LICENSE.


# system modules
from typing import Optional

# dznpy modules
from ..dznpy_version import VERSION
from .. import cpp_gen
from ..ast_view import find_fqn
from ..code_gen_common import BLANK_LINE, CodeGenResult, GeneratedContent, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import AccessSpecifier, Comment
from ..misc_utils import TextBlock, get_basename
from ..support_files import strict_port, ilog, misc_utils, meta_helpers, multi_client_selector, \
    mutex_wrapped
from ..scoping import ns_ids_t

# own modules
from .common import Configuration, Recipe, CppPorts, create_encapsulee, CppElements
from .types import AdvShellError
from .port_selection import PortCfg, PortsSemanticsCfg, PortSelect, PortWildcard
from .core.processing import create_dzn_elements, create_cpp_portitf, create_facilities, \
    create_constructor, create_final_construct_fn, create_facilities_check_fn


# helper functions to create a prefined PortCfg

def all_mts() -> PortCfg:
    """Configure all provides and requires ports with multi-threaded runtime semantics (MTS).
    This is equivalent to what `dzn code --shell` generates."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)),
                   requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.NONE),
                                              mts=PortSelect(PortWildcard.ALL)))


def all_sts() -> PortCfg:
    """Configure all provides and requires ports with single-threaded runtime semantics (STS)."""
    return PortCfg(provides=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                              mts=PortSelect(PortWildcard.NONE)),
                   requires=PortsSemanticsCfg(sts=PortSelect(PortWildcard.ALL),
                                              mts=PortSelect(PortWildcard.NONE)))


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


class Builder:
    """Class to build an Advanced Shell according to a user specified configuration."""
    _recipe: Recipe

    def build(self, cfg: Configuration) -> CodeGenResult:
        """Build a custom shell according to the specified configuration."""

        fc = cfg.ast_fc

        # ---------- Prepare Dezyne Elements ----------

        # lookup encapsulee and check its type
        r = find_fqn(fc, ns_ids_t(cfg.fqn_encapsulee_name))
        if not r.items:
            raise AdvShellError(f'Encapsulee "{cfg.fqn_encapsulee_name}" not found')
        dzn_encapsulee = r.get_single_instance()

        dzn_elements = create_dzn_elements(cfg, fc, dzn_encapsulee)
        scope_fqn = dzn_elements.scope_fqn.ns_ids

        # ---------- Prepare C++ Elements ----------

        orig_file_basename = get_basename(cfg.dezyne_filename)
        custom_shell_name = f'{orig_file_basename}{cfg.output_basename_suffix}'
        target_file_basename = custom_shell_name
        namespace = cpp_gen.Namespace(ns_ids=scope_fqn)
        struct = cpp_gen.Struct(name=custom_shell_name)

        encapsulee = create_encapsulee(dzn_elements)

        sf_ns_prefix = cfg.support_files_ns_prefix
        sf_strict_port_hh = strict_port.create_header(sf_ns_prefix)
        sf_ilog_hh = ilog.create_header(sf_ns_prefix)
        sf_misc_utils_hh = misc_utils.create_header(sf_ns_prefix)
        sf_meta_helpers_hh = meta_helpers.create_header(sf_ns_prefix)
        sf_multi_client_selector_hh = multi_client_selector.create_header(sf_ns_prefix)
        sf_mutex_wrapped_hh = mutex_wrapped.create_header(sf_ns_prefix)

        support_files_ns = sf_strict_port_hh.namespace
        pp = CppPorts([create_cpp_portitf(p, struct, support_files_ns, encapsulee) for p in
                       dzn_elements.provides_ports])
        rp = CppPorts([create_cpp_portitf(p, struct, support_files_ns, encapsulee) for p in
                       dzn_elements.requires_ports])
        facilities = create_facilities(cfg.facilities_origin, struct)

        constructor = create_constructor(struct, facilities, encapsulee, pp, rp, fc)
        final_construct_fn = create_final_construct_fn(struct, pp, rp, encapsulee)
        facilities_check_fn = create_facilities_check_fn(struct, cfg.facilities_origin)

        cpp_elements = CppElements(orig_file_basename, target_file_basename, namespace, struct,
                                   constructor, final_construct_fn, facilities_check_fn, facilities,
                                   encapsulee, pp, rp, sf_strict_port_hh)

        # ---------- Generate ----------
        self._recipe = Recipe(cfg, dzn_elements, cpp_elements)

        # generate c++ code
        return CodeGenResult(files=[self._create_headerfile(),
                                    self._create_sourcefile(),
                                    sf_strict_port_hh, sf_ilog_hh, sf_misc_utils_hh,
                                    sf_meta_helpers_hh, sf_multi_client_selector_hh,
                                    sf_mutex_wrapped_hh])

    def _create_headerfile(self) -> GeneratedContent:
        """Generate a c++ headerfile according to the current recipe."""
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        header_comments = cpp_gen.CommentBlock([
            cfg.copyright,
            BLANK_LINE,
            'Advanced Shell',
            BLANK_LINE,
            self._create_creator_info_overview(),
            BLANK_LINE,
            self._create_configuration_overview(),
            BLANK_LINE,
            self._create_final_port_overview(),
            TEXT_GEN_DO_NOT_MODIFY,
        ])

        header = [header_comments,
                  BLANK_LINE,
                  cpp_gen.SystemIncludes(cpp.facilities.system_includes),
                  cpp_gen.ProjectIncludes([f'{r.cpp_elements.orig_file_basename}.hh',
                                           f'{cpp.sf_strict_port.filename}']),
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

        footer = Comment(f'Generated by: dznpy/adv_shell v{VERSION}')

        return GeneratedContent(filename=f'{cpp.target_file_basename}.hh',
                                contents=str(TextBlock([header, cpp.namespace, footer])))

    def _create_sourcefile(self) -> GeneratedContent:
        """Generate a c++ sourcefile according to the current recipe."""
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        header_comments = cpp_gen.CommentBlock([
            cfg.copyright,
            BLANK_LINE,
            'Advanced Shell',
            BLANK_LINE,
            TEXT_GEN_DO_NOT_MODIFY,
        ])

        header = [header_comments,
                  BLANK_LINE,
                  cpp_gen.SystemIncludes(['dzn/runtime.hh']),  # used by FacilitiesCheck()
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
        r = self._recipe
        cfg = r.configuration
        cpp = r.cpp_elements

        return str(TextBlock([
            'Configuration:',
            f'- Encapsulee FQN: {cfg.fqn_encapsulee_name}',
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
