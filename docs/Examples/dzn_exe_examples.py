"""
Examples of using the dzn_exe module.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# system modules
from pathlib import Path

# system-under-test
from dznpy.dzn_exe import DznPrimer, DznCmdResult, DznCommonOptions, \
    dzn_list_models, create_file_models_list, dzn_version, DznParseOptions, dzn_parse, \
    DznCodeOptions, dzn_code, dzn_json, DznVerifyOptions, dzn_verify

# constants (user configurable)
LEGACY_DZN_CMD_PATH = Path('C:\\Data\\Dezyne\\dezyne-2.11.0')
DZN_CMD_PATH = Path('C:\\SB\\dezyne-2.17.9')
ROOT_MODELS_PATH = Path('C:\\SB\\dznpy\\test\\dezyne_models\\system1')
IMPORT_DIRS = ['.', '../shared/Facilities']


def print_dzn_cmd_result(result: DznCmdResult):
    print(f'proc.cmdline   = {result.proc.cmdline}\n'
          f'proc.exit code = {result.proc.exit_code}\n'
          f'proc.stdout    = {result.proc.stdout}\n'
          f'proc.stderr    = {result.proc.stderr}\n'
          f'proc.message   = {result.proc.message}\n'
          f'message        = {result.message}\n')


def example_dzn_cmd():
    """Example of the DznPrimer class that is vital for every dzn_exe cmd execution."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    print(f'filepath    = {primer.dzn_filepath()}\n'
          f'version     = {primer.version}\n'
          f'root_folder = {primer.root_folder}')


def example_dzn_version():
    """Example of the convenience function to retrieve the version of dzn.cmd."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    result = dzn_version(primer)
    print_dzn_cmd_result(result)


def example_list_models():
    """Example of the convenience function to retrieve the list of models inside a dezyne file."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    result = dzn_list_models(primer, IMPORT_DIRS, Path('Hardware/Interfaces/IHeaterElement.dzn'))
    print_dzn_cmd_result(result)
    print(create_file_models_list(result.proc.stdout))


def example_code_json():
    """Example of the convenience function to get the JSON AST for a dezyne file."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    result = dzn_json(primer, IMPORT_DIRS, Path('Hardware/Interfaces/IHeaterElement.dzn'))
    print_dzn_cmd_result(result)


def example_just_parse():
    """Example of just parsing a dezyne file."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS)
    parse_opt = DznParseOptions(dzn_file=Path('Hardware/Interfaces/IHeaterElement.dzn'))
    result = dzn_parse(primer, common_opt, parse_opt)
    print_dzn_cmd_result(result)


def example_parse_preprocess():
    """Example of parsing and preprocessing a dezyne file into independent processable contents."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS)
    parse_opt = DznParseOptions(preprocess=True,
                                dzn_file=Path('Hardware/Interfaces/IHeaterElement.dzn'))
    result = dzn_parse(primer, common_opt, parse_opt)
    print_dzn_cmd_result(result)


def example_verify():
    """Example of verifying a dezyne file."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS, verbose=True)
    verify_opt = DznVerifyOptions(dzn_file=Path('Hardware/Interfaces/IHeaterElement.dzn'))
    result = dzn_verify(primer, common_opt, verify_opt)
    print_dzn_cmd_result(result)


def example_code():
    """Example of generate c++ code for a dezyne file and output it to stdout."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS)
    code_opt = DznCodeOptions(dzn_file=Path('Hardware/Interfaces/IHeaterElement.dzn'),
                              language='c++', output_target='-')
    result = dzn_code(primer, common_opt, code_opt)
    print_dzn_cmd_result(result)


def example_tss_code():
    """Example of generate thread-safe shell (tss) c++ code for a dezyne file and
    output it to stdout."""
    primer = DznPrimer(DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS)
    code_opt = DznCodeOptions(dzn_file=Path('ToasterSystem.dzn'),
                              language='c++', tss='My.Project.ToasterSystem', output_target='-')
    result = dzn_code(primer, common_opt, code_opt)
    print_dzn_cmd_result(result)


def example_verify_with_unsupported_options():
    """Example of requesting dzn.cmd to verify a file with options that are not supported
    by an older/legacy version of Dezyne."""
    primer = DznPrimer(LEGACY_DZN_CMD_PATH, ROOT_MODELS_PATH)
    common_opt = DznCommonOptions(import_dirs=IMPORT_DIRS, verbose=True)
    verify_opt = DznVerifyOptions(no_constraint=True, dzn_file=Path('Toaster.dzn'))
    result = dzn_verify(primer, common_opt, verify_opt)
    print_dzn_cmd_result(result)


if __name__ == "__main__":
    example_dzn_cmd()
    example_dzn_version()
    example_list_models()
    example_code_json()
    example_just_parse()
    example_parse_preprocess()
    example_verify()
    example_code()
    example_tss_code()
    example_verify_with_unsupported_options()
