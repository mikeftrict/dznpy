"""
Testsuite validating the dzn_exe module

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
from typing import Tuple

# system modules
import os
import pytest
from unittest.mock import patch, MagicMock

# system-under-test
from dznpy.dzn_exe import *

# test data
from testdata_dzn_exe import *

# OS-dependent test data
DZN_PATH = 'C:\\dzn' if sys.platform.startswith("win") else '/usr/bin'
DZN_CMD_FILEPATH = str(Path(DZN_PATH) / 'dzn.cmd') if sys.platform.startswith("win") else str(Path(DZN_PATH) / 'dzn')
V2_11_0 = '2.11.0'
V2_12_0 = '2.12.0'
V2_13_0 = '2.13.0'
V2_14_0 = '2.14.0'
V2_15_0 = '2.15.0'
V2_16_4 = '2.16.4'
V2_16_5 = '2.16.5'
V2_17_0 = '2.17.0'
V2_17_1 = '2.17.1'
V2_17_9 = '2.17.9'
V2_18_0 = '2.18.0'
V2_19_0 = '2.19.0'
DZN_FILE = Path('model.dzn')


# module level patching
@pytest.fixture(autouse=True)
def patch_path_resolve():
    """Automatically patch Path.resolve() for all tests."""
    with patch.object(Path, "resolve", return_value=Path(DZN_CMD_FILEPATH)):
        yield


@pytest.fixture(autouse=True)
def patch_os_chdir():
    """Automatically patch os.chdir() for all tests."""
    with patch.object(os, "chdir"):
        yield


def test_create_file_models_list_ok():
    """Test the default good weather behaviour."""
    sut: DznFileModelsList = create_file_models_list(DZN_PARSE_L_OUTPUT)
    assert sut.systems == ['My.Project.ToasterSystem']
    assert sut.interfaces == ['My.IExclusiveToaster']
    assert sut.components == ['My.Project.Toaster', 'SecondToaster']
    assert sut.foreigns == ['Facilities.Timer']


def test_file_models_list_str():
    """Test the stringification of a DznFileModelsList."""
    sut: DznFileModelsList = create_file_models_list(DZN_PARSE_L_OUTPUT)
    assert str(sut) == DZN_FILE_MODELS_LIST_STR


def test_file_models_list():
    """Test various compositions of the DznFileModelsList data class and its functions."""
    sut1 = DznFileModelsList()
    assert sut1.is_verifiable() == False
    assert sut1.is_generatable() == True
    assert sut1.is_wfc_only() == False

    sut2 = DznFileModelsList(interfaces=['IBar'])
    assert sut2.is_verifiable() == True
    assert sut2.is_generatable() == True
    assert sut2.is_wfc_only() == False

    sut3 = DznFileModelsList(components=['Hello'])
    assert sut3.is_verifiable() == True
    assert sut3.is_generatable() == True
    assert sut3.is_wfc_only() == False

    sut4 = DznFileModelsList(systems=['Sys'])
    assert sut4.is_verifiable() == False
    assert sut4.is_generatable() == True
    assert sut4.is_wfc_only() == True

    sut5 = DznFileModelsList(systems=['Sys'], components=['Hello'], interfaces=['IBar'])
    assert sut5.is_verifiable() == True
    assert sut5.is_generatable() == True
    assert sut5.is_wfc_only() == False

    sut6 = DznFileModelsList(foreigns=['MyFC'])
    assert sut6.is_verifiable() == False
    assert sut6.is_generatable() == True
    assert sut6.is_wfc_only() == True

    sut7 = DznFileModelsList(foreigns=['MyFC'], components=['Hello'], interfaces=['IBar'])
    assert sut7.is_verifiable() == True
    assert sut7.is_generatable() == True
    assert sut7.is_wfc_only() == False


def create_dzn_primer(mocked_version: str) -> Tuple[DznPrimer, DznCommonOptions]:
    """Create an instance of DznPrimer with caller customizations."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=mocked_version, stderr='', returncode=0)
        primer = DznPrimer(dzn_path=Path(DZN_CMD_FILEPATH), root_folder=Path('models'))
        return primer, DznCommonOptions(import_dirs=['../Inc'])


def test_create_dzn_cmdless_args_ok():
    """Test valid scenarios."""
    primer, _ = create_dzn_primer(V2_19_0)

    assert create_dzn_cmdless_args(primer, DznCommonOptions(skip_wfc=True)) == \
           [DZN_CMD_FILEPATH, '--skip-wfc']

    assert create_dzn_cmdless_args(primer, DznCommonOptions(threads=4)) == \
           [DZN_CMD_FILEPATH, '--threads=4']

    assert create_dzn_cmdless_args(primer, DznCommonOptions(verbose=True)) == \
           [DZN_CMD_FILEPATH, '--verbose']

    assert create_dzn_cmdless_args(primer, DznCommonOptions(version=True)) == \
           [DZN_CMD_FILEPATH, '--version']

    assert create_dzn_cmdless_args(primer, DznCommonOptions(skip_wfc=True, threads=4,
                                                            verbose=True, version=True)) == \
           [DZN_CMD_FILEPATH, '--skip-wfc', '--threads=4', '--verbose', '--version']


@pytest.mark.parametrize("version", [V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_17_0, V2_18_0])
def test_create_dzn_cmdless_args_skip_wfc_ok(version):
    """Test scenarios in which the option --skip-wfc is ok."""
    primer, _ = create_dzn_primer(version)
    create_dzn_cmdless_args(primer, DznCommonOptions(skip_wfc=True))


@pytest.mark.parametrize("version", [V2_11_0])
def test_create_dzn_cmdless_args_skip_wfc_fail(version):
    """Test scenarios in which the option --skip-wfc is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, _ = create_dzn_primer(version)
        create_dzn_cmdless_args(primer, DznCommonOptions(skip_wfc=True))

    assert str(exc.value) == '--skip-wfc is only supported as of dezyne 2.12.0 args: --skip-wfc'


@pytest.mark.parametrize("version", [V2_11_0, V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_17_0, V2_18_0])
def test_create_dzn_cmdless_args_threads_fail(version):
    """Test scenarios in which the option --threads is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, _ = create_dzn_primer(version)
        create_dzn_cmdless_args(primer, DznCommonOptions(threads=4))

    assert str(exc.value) == '--threads is only supported as of dezyne 2.19.0 args: --threads=4'


def test_create_dzn_parse_args_ok():
    """Test valid scenarios."""
    primer, common_opt = create_dzn_primer(V2_17_9)

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', 'model.dzn']

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(list_models=True, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', '--list-models', 'model.dzn']

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(preprocess=True, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', '--preprocess', 'model.dzn']

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(output_target='-', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', '-o', '-', 'model.dzn']

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(output_target='gen/', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', '-o', 'gen/', 'model.dzn']


def test_create_dzn_parse_args_corner_cases():
    """Test cornercases that theoretically seems to be possible but may be rejected by dzn.cmd"""
    primer, common_opt = create_dzn_primer(V2_17_9)

    assert create_dzn_parse_args(primer, common_opt, DznParseOptions(list_models=True, preprocess=True,
                                                                     output_target='gen/', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'parse', '-I', '../Inc', '--list-models', '--preprocess', '-o', 'gen/', 'model.dzn']


def test_create_dzn_verify_args_ok():
    """Test valid scenarios."""
    primer, common_opt = create_dzn_primer(V2_17_9)

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_constraint=True, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--no-constraint', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_unreachable=True, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--no-unreachable', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size=3, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--queue-size=3', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_defer=4, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--queue-size-defer=4', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_external=5, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--queue-size-external=5', 'model.dzn']

    assert create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_constraint=True, no_unreachable=True,
                                                                       queue_size=3, queue_size_defer=4,
                                                                       queue_size_external=5, dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'verify', '-I', '../Inc', '--no-constraint', '--no-unreachable',
            '--queue-size=3', '--queue-size-defer=4', '--queue-size-external=5', 'model.dzn']


@pytest.mark.parametrize("version", [V2_17_0, V2_17_1, V2_17_9, V2_18_0, V2_19_0])
def test_create_dzn_verify_args_no_constraint_ok(version):
    """Test scenarios in which the option --no-constraint is ok."""
    primer, common_opt = create_dzn_primer(version)
    create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_constraint=True, dzn_file=DZN_FILE))


@pytest.mark.parametrize("version", [V2_17_0, V2_17_1, V2_17_9, V2_18_0, V2_19_0])
def test_create_dzn_verify_args_no_unreachable_ok(version):
    """Test scenarios in which the option --no-unreachable is ok."""
    primer, common_opt = create_dzn_primer(version)
    create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_unreachable=True, dzn_file=DZN_FILE))


@pytest.mark.parametrize("version", [V2_16_5, V2_17_9, V2_18_0, V2_19_0])
def test_create_dzn_verify_args_queue_size_defer_ok(version):
    """Test scenarios in which the option --queue-size-defer is ok."""
    primer, common_opt = create_dzn_primer(version)
    create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_defer=3, dzn_file=DZN_FILE))


@pytest.mark.parametrize("version", [V2_16_5, V2_17_9, V2_18_0, V2_19_0])
def test_create_dzn_verify_args_queue_size_external_ok(version):
    """Test scenarios in which the option --queue-size-external is ok."""
    primer, common_opt = create_dzn_primer(version)
    create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_external=3, dzn_file=DZN_FILE))


@pytest.mark.parametrize("version", [V2_11_0, V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_16_5])
def test_create_dzn_verify_args_no_constraint_fail(version):
    """Test scenarios in which the option --no-constraint is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, common_opt = create_dzn_primer(version)
        create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_constraint=True, dzn_file=DZN_FILE))

    assert str(exc.value) == (f'--no-constraint is only supported as of dezyne 2.17.0 args: {DZN_CMD_FILEPATH} '
                              'verify -I ../Inc --no-constraint model.dzn')


@pytest.mark.parametrize("version", [V2_11_0, V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_16_5])
def test_create_dzn_verify_args_no_unreachable_fail(version):
    """Test scenarios in which the option --no-unreachable is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, common_opt = create_dzn_primer(version)
        create_dzn_verify_args(primer, common_opt, DznVerifyOptions(no_unreachable=True, dzn_file=DZN_FILE))

    assert str(exc.value) == (f'--no-unreachable is only supported as of dezyne 2.17.0 args: {DZN_CMD_FILEPATH} '
                              'verify -I ../Inc --no-unreachable model.dzn')


@pytest.mark.parametrize("version", [V2_11_0, V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_17_0, V2_17_1])
def test_create_dzn_verify_args_queue_size_defer_fail(version):
    """Test scenarios in which the option --queue-size-defer is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, common_opt = create_dzn_primer(version)
        create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_defer=3, dzn_file=DZN_FILE))

    assert str(exc.value) == ('--queue-size-defer is only supported as of dezyne 2.16.5 (2.17.0 and 2.17.1 '
                              f'excluded) args: {DZN_CMD_FILEPATH} verify -I ../Inc --queue-size-defer=3 model.dzn')


@pytest.mark.parametrize("version", [V2_11_0, V2_12_0, V2_13_0, V2_14_0, V2_15_0, V2_16_4, V2_17_0, V2_17_1])
def test_create_dzn_verify_args_queue_size_external_fail(version):
    """Test scenarios in which the option --queue-size-external is not supported."""
    with pytest.raises(UnsupportedDznOption) as exc:
        primer, common_opt = create_dzn_primer(version)
        create_dzn_verify_args(primer, common_opt, DznVerifyOptions(queue_size_external=3, dzn_file=DZN_FILE))

    assert str(exc.value) == ('--queue-size-external is only supported as of dezyne 2.16.5 (2.17.0 and 2.17.1 '
                              f'excluded) args: {DZN_CMD_FILEPATH} verify -I ../Inc --queue-size-external=3 model.dzn')


def test_create_dzn_code_args_ok():
    """Test valid scenarios."""
    primer, common_opt = create_dzn_primer(V2_17_9)

    assert create_dzn_code_args(primer, common_opt, DznCodeOptions(dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'code', '-I', '../Inc', 'model.dzn']

    assert create_dzn_code_args(primer, common_opt, DznCodeOptions(language='c++', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'code', '-I', '../Inc', '--language=c++', 'model.dzn']

    assert create_dzn_code_args(primer, common_opt, DznCodeOptions(tss='My.Toaster', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'code', '-I', '../Inc', '--shell=My.Toaster', 'model.dzn']

    assert create_dzn_code_args(primer, common_opt, DznCodeOptions(output_target='gen/', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'code', '-I', '../Inc', '-o', 'gen/', 'model.dzn']

    assert create_dzn_code_args(primer, common_opt, DznCodeOptions(language='c++', tss='My.Toaster',
                                                                   output_target='gen/', dzn_file=DZN_FILE)) == \
           [DZN_CMD_FILEPATH, 'code', '-I', '../Inc', '--language=c++', '--shell=My.Toaster', '-o', 'gen/', 'model.dzn']


def test_dzn_version_ok():
    """Test a good weather scenario."""
    primer, _ = create_dzn_primer(V2_19_0)
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=V2_19_0, stderr='', returncode=0)
        result = dzn_version(primer)
        assert result.proc.succeeded() == True
        assert result.proc.stdout == V2_19_0


def test_dzn_version_fail():
    """Test a failing scenarios."""
    primer, _ = create_dzn_primer(V2_17_9)
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout='', stderr='', returncode=2)
        result = dzn_version(primer)
        assert result.proc.succeeded() == False
        assert result.proc.exit_code == 2
