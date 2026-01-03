"""
Module providing helpers for executing dzn(.cmd) and processing its output.

Copyright (c) 2025-2026 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import re
import sys
from dataclasses import field, dataclass
from pathlib import Path
from typing import List, Optional

# dznpy modules
from .misc_utils import assert_t, ProcessResult, run_subprocess, flatten_to_strlist, raii_cd
from .versioning import DznVersion


class UnsupportedDznOption(Exception):
    """A specified option is not supported in the version of Dezyne being executed."""


class DznPrimer:
    """Data class storing the primer attributes of running dzn.cmd."""
    __slots__ = ['_dzn_path', '_dzn_version', '_root_folder']

    def __init__(self, dzn_path: Path, root_folder: Path):
        assert_t(dzn_path, Path)
        self._dzn_path = dzn_path
        self.root_folder = root_folder

        proc_result = run_subprocess([self.dzn_filepath(), '--version'])
        if not proc_result.succeeded():
            raise RuntimeError(f'Failed to inquire {self.dzn_filepath()} '
                               f'its version. {proc_result.stderr}')
        self._dzn_version = DznVersion(proc_result.stdout)

    @property
    def root_folder(self) -> Path:
        """Return the root folder of models, from where relatively imports are based on."""
        return self._root_folder

    @root_folder.setter
    def root_folder(self, value: Path):
        """Set a new namespace instance."""
        assert_t(value, Path)
        self._root_folder = value

    @property
    def version(self) -> DznVersion:
        """Return the version of dzn.cmd specified."""
        return self._dzn_version

    def dzn_filepath(self) -> str:
        """Return the full filepath of dzn.cmd."""
        return str((Path(self._dzn_path) / self.dzn_cmd_name()).resolve())

    @staticmethod
    def dzn_cmd_name() -> str:
        """Return the OS dependent name of the dzn executable."""
        if sys.platform.startswith("win"):
            return 'dzn.cmd'
        return 'dzn'


@dataclass(frozen=True)
class DznCommonOptions:
    """Data class storing common options applicable many/all commands of dzn.cmd."""
    skip_wfc: bool = field(default=False)
    threads: Optional[int] = field(default=None)
    verbose: bool = field(default=False)
    version: bool = field(default=False)
    import_dirs: list[str] = field(default_factory=list)

    def imports(self) -> List[str]:
        """Return a list of imports prefixed and separated by '-I' eg ['-I', 'foo', '-I', 'bar']."""
        return [item for i in self.import_dirs for item in ('-I', i)] if self.import_dirs else []


@dataclass(frozen=True)
class DznParseOptions:
    """Data class storing parse options."""
    dzn_file: Path
    list_models: bool = field(default=False)
    preprocess: bool = field(default=False)
    output_target: Optional[Path] = field(default=None)  # '-' for stdout or a folder path


@dataclass(frozen=True)
class DznVerifyOptions:
    """Data class storing verify options."""
    dzn_file: Path
    no_constraint: bool = field(default=False)
    no_unreachable: bool = field(default=False)
    queue_size: Optional[int] = field(default=None)
    queue_size_defer: Optional[int] = field(default=None)
    queue_size_external: Optional[int] = field(default=None)


@dataclass(frozen=True)
class DznCodeOptions:
    """Data class storing code (generation) options."""
    dzn_file: Path
    language: Optional[str] = field(default=None)
    tss: List[str] = field(default_factory=list)
    output_target: Optional[Path] = field(default=None)  # '-' for stdout or a folder path


###############################################################################
# dzn.cmd execution related types
#


@dataclass(frozen=True)
class DznCmdResult:
    """Data class storing the result of a dzn process task execution."""
    proc: ProcessResult
    message: str


###############################################################################
# Abstracted dzn.cmd related types
#

@dataclass(frozen=True)
class DznFileModelsList:
    """Data class storing the occurrences of model types found in a Dezyne file."""
    components: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    foreigns: List[str] = field(default_factory=list)
    systems: List[str] = field(default_factory=list)

    def is_verifiable(self) -> bool:
        """Indicate whether the file can be verified depending on the types of models inside."""
        return bool(self.components or self.interfaces)

    def is_generatable(self) -> bool:
        """Indicate that Dezyne can always be asked to generate code for every Dzn file."""
        return True

    def is_wfc_only(self) -> bool:
        """Indicate whether only a well-formedness check can be performed."""
        return bool(not self.components and not self.interfaces and (self.systems or self.foreigns))

    def __str__(self) -> str:
        return (f'Components: {", ".join(self.components)}\n'
                f'Interfaces: {", ".join(self.interfaces)}\n'
                f'Foreigns: {", ".join(self.foreigns)}\n'
                f'Systems: {", ".join(self.systems)}\n')


###############################################################################
# Type creation functions
#

def create_file_models_list(parse_l_output: str) -> DznFileModelsList:
    """List the models that are present in a Dezyne file by returning an instance of the
    type DznFileModelsList."""

    # Temporary lists to collect names
    components = []
    interfaces = []
    foreigns = []
    systems = []

    pattern = re.compile(r'(?P<name>\S+)\s+(?P<type>interface|component|foreign|system)',
                         re.MULTILINE)
    for match in pattern.finditer(parse_l_output):
        name = match.group("name")
        kind = match.group("type")
        if kind == "component":
            components.append(name)
        elif kind == "interface":
            interfaces.append(name)
        elif kind == "foreign":
            foreigns.append(name)
        elif kind == "system":
            systems.append(name)

    return DznFileModelsList(components=components, interfaces=interfaces,
                             foreigns=foreigns, systems=systems)


###############################################################################
# Functions that map to dzn.cmd command calls
#


def dzn_version(primer: DznPrimer) -> DznCmdResult:
    """Convenience helper function to execute 'dzn.cmd --version'."""
    with raii_cd(primer.root_folder):
        opt = DznCommonOptions(version=True)
        proc_result = run_subprocess(create_dzn_cmdless_args(primer, opt))
        msg = 'Requesting Dezyne version failed' if not proc_result.succeeded() else None
        return DznCmdResult(proc=proc_result, message=msg)


def dzn_list_models(primer: DznPrimer, import_dirs: list[str], dzn_file: Path) -> DznCmdResult:
    """Convenience helper function to execute 'dzn.cmd parse -l <dzn_file>'."""
    with raii_cd(primer.root_folder):
        try:
            common_opt = DznCommonOptions(import_dirs=import_dirs)
            parse_opt = DznParseOptions(dzn_file=dzn_file, list_models=True)
            args = create_dzn_parse_args(primer, common_opt, parse_opt)
            proc_result = run_subprocess(args)
            msg = 'Listing Dezyne file models failed' if not proc_result.succeeded() else None
            return DznCmdResult(proc=proc_result, message=msg)
        except UnsupportedDznOption as exc:
            return reply_option_error(exc)


def dzn_json(primer: DznPrimer, import_dirs: list[str], dzn_file: Path) -> DznCmdResult:
    """Convenience helper function to execute 'dzn.cmd parse -l <dzn_file>'."""
    with raii_cd(primer.root_folder):
        try:
            common_opt = DznCommonOptions(import_dirs=import_dirs)
            code_opt = DznCodeOptions(language='json', dzn_file=dzn_file, output_target=Path('-'))
            args = create_dzn_code_args(primer, common_opt, code_opt)
            proc_result = run_subprocess(args)
            msg = 'Getting JSON AST for Dezyne file failed' if not proc_result.succeeded() else None
            return DznCmdResult(proc=proc_result, message=msg)
        except UnsupportedDznOption as exc:
            return reply_option_error(exc)


def dzn_parse(primer: DznPrimer, common_opt: DznCommonOptions,
              parse_opt: DznParseOptions) -> DznCmdResult:
    """Generic execution of 'dzn.cmd <common_opt> parse <parse_opt>'."""
    with raii_cd(primer.root_folder):
        try:
            args = create_dzn_parse_args(primer, common_opt, parse_opt)
            proc_result = run_subprocess(args)
            msg = 'Parsing Dezyne file failed' if not proc_result.succeeded() else None
            return DznCmdResult(proc=proc_result, message=msg)
        except UnsupportedDznOption as exc:
            return reply_option_error(exc)


def dzn_code(primer: DznPrimer, common_opt: DznCommonOptions,
             code_opt: DznCodeOptions) -> DznCmdResult:
    """Generic execution of 'dzn.cmd <common_opt> code <code_opt>'."""
    with raii_cd(primer.root_folder):
        try:
            args = create_dzn_code_args(primer, common_opt, code_opt)
            proc_result = run_subprocess(args)
            msg = 'Generate code for Dezyne file failed' if not proc_result.succeeded() else None
            return DznCmdResult(proc=proc_result, message=msg)
        except UnsupportedDznOption as exc:
            return reply_option_error(exc)


def dzn_verify(primer: DznPrimer, common_opt: DznCommonOptions,
               verify_opt: DznVerifyOptions) -> DznCmdResult:
    """Generic execution of 'dzn.cmd <common_opt> code <code_opt>'."""
    with raii_cd(primer.root_folder):
        try:
            args = create_dzn_verify_args(primer, common_opt, verify_opt)
            proc_result = run_subprocess(args)
            msg = 'Verifying Dezyne file failed' if not proc_result.succeeded() else None
            return DznCmdResult(proc=proc_result, message=msg)
        except UnsupportedDznOption as exc:
            return reply_option_error(exc)


def reply_option_error(exc: UnsupportedDznOption) -> DznCmdResult:
    """Create a DznCmdResult that indicates an error in specified dezyne options."""
    return DznCmdResult(proc=ProcessResult('', 2, '', ''),
                        message=f'Error in specified options; {exc.args[0]}')


###############################################################################
# Internal functions that create the dzn.cmd executable arguments
#

def create_common_options_args(primer: DznPrimer, common_opt: DznCommonOptions) -> List[str]:
    """Generic helper function to create a list of arguments according to the specified
    common options."""
    opt = common_opt  # short alias
    args = ['--skip-wfc'] if opt.skip_wfc else []
    args += [f'--threads={opt.threads}'] if opt.threads else []
    args += ['--verbose'] if opt.verbose else []
    args += ['--version'] if opt.version else []

    args_str = ' '.join(flatten_to_strlist(args))

    if opt.skip_wfc and primer.version < DznVersion('2.12.0'):
        raise UnsupportedDznOption('--skip-wfc is only supported as of dezyne 2.12.0'
                                   f' args: {args_str}')

    if opt.threads and primer.version < DznVersion('2.19.0'):
        raise UnsupportedDznOption('--threads is only supported as of dezyne 2.19.0'
                                   f' args: {args_str}')
    return args


def create_dzn_cmdless_args(primer: DznPrimer, common_opt: DznCommonOptions) -> List[str]:
    """Create the dzn.cmd args without specifying a command."""
    args = [primer.dzn_filepath()]
    args += create_common_options_args(primer, common_opt)
    return args


def create_dzn_parse_args(primer: DznPrimer, common_opt: DznCommonOptions,
                          parse_opt: DznParseOptions) -> List[str]:
    """Create the dzn.cmd args for the parse command."""
    opt = parse_opt  # short alias
    args = [primer.dzn_filepath()] + create_common_options_args(primer, common_opt)
    args += ['parse'] + common_opt.imports()
    args += ['--list-models'] if opt.list_models else []
    args += ['--preprocess'] if opt.preprocess else []
    args += ['-o', f'{opt.output_target}'] if opt.output_target else []
    args += [str(opt.dzn_file)]
    return args


def create_dzn_verify_args(primer: DznPrimer, common_opt: DznCommonOptions,
                           verify_opt: DznVerifyOptions) -> List[str]:
    """Create the dzn.cmd args for the verify command."""
    opt = verify_opt  # short alias
    args = [primer.dzn_filepath()] + create_common_options_args(primer, common_opt)
    args += ['verify'] + common_opt.imports()
    args += ['--no-constraint'] if opt.no_constraint else []
    args += ['--no-unreachable'] if opt.no_unreachable else []
    args += [f'--queue-size={opt.queue_size}'] if opt.queue_size else []
    args += [f'--queue-size-defer={opt.queue_size_defer}'] if opt.queue_size_defer else []
    args += [f'--queue-size-external={opt.queue_size_external}'] if opt.queue_size_external else []
    args += [str(opt.dzn_file)]

    args_str = ' '.join(flatten_to_strlist(args))

    if opt.no_constraint and primer.version < DznVersion('2.17.0'):
        raise UnsupportedDznOption('--no-constraint is only supported as of dezyne 2.17.0'
                                   f' args: {args_str}')

    if opt.no_unreachable and primer.version < DznVersion('2.17.0'):
        raise UnsupportedDznOption('--no-unreachable is only supported as of dezyne 2.17.0'
                                   f' args: {args_str}')

    if opt.queue_size_defer and (primer.version < DznVersion('2.16.5') or
                                 primer.version == DznVersion('2.17.0') or
                                 primer.version == DznVersion('2.17.1')):
        raise UnsupportedDznOption('--queue-size-defer is only supported as of dezyne 2.16.5'
                                   f' (2.17.0 and 2.17.1 excluded) args: {args_str}')

    if opt.queue_size_external and (primer.version < DznVersion('2.16.5') or
                                    primer.version == DznVersion('2.17.0') or
                                    primer.version == DznVersion('2.17.1')):
        raise UnsupportedDznOption('--queue-size-external is only supported as of dezyne 2.16.5'
                                   f' (2.17.0 and 2.17.1 excluded) args: {args_str}')
    return args


def create_dzn_code_args(primer: DznPrimer, common_opt: DznCommonOptions,
                         code_opt: DznCodeOptions) -> List[str]:
    """Create the dzn.cmd args for the code command."""
    args = [primer.dzn_filepath()] + create_common_options_args(primer, common_opt)
    args += ['code'] + common_opt.imports()
    args += [f'--language={code_opt.language}'] if code_opt.language else []
    args += [f'--shell={s}' for s in code_opt.tss]
    args += ['-o', f'{code_opt.output_target}'] if code_opt.output_target else []
    args += [str(code_opt.dzn_file)]
    return args
