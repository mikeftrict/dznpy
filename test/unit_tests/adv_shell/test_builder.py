"""
Testsuite validating the builder aspects of the adv_shell module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from typing import List

# system-under-test
from dznpy import ast
from dznpy.adv_shell import PortSelect, PortWildcard, all_sts_all_mts, all_mts_all_sts, \
    all_mts_mixed_ts, all_sts_mixed_ts, all_mts, all_sts, Configuration, Builder, MultiClientPortCfg
from dznpy.adv_shell.common import FacilitiesOrigin
from dznpy.adv_shell.types import AdvShellError
from dznpy.code_gen_common import GeneratedContent, CodeGenResult
from dznpy.support_files import strict_port, ilog, misc_utils, meta_helpers, \
    multi_client_selector, mutex_wrapped
from dznpy.scoping import ns_ids_t
from dznpy.json_ast import DznJsonAst

# test helpers
from common.helpers import resolve
from common.testdata import COPYRIGHT
from testdata_builder import *

# test constants
DZN_FILE1 = resolve(__file__, TOASTER_SYSTEM_JSON_FILE, '../')
DZN_FILE2 = resolve(__file__, STONE_AGE_TOASTER_FILE, '../')
DZN_FILE3 = resolve(__file__, EXCLUSIVE_TOASTER_JSON_FILE, '../')

# test data
GC_DEFAULT_DZN_STRICT_PORT_HH = strict_port.create_header()
GC_OTHERPROJECT_DZN_STRICT_PORT_HH = strict_port.create_header(ns_ids_t('Other.Project'))


# local test helpers

def get_fc(dezyne_filename) -> ast.FileContents:
    """Helper to load the JSON AST tree of a Dezyne file and proces it into FileContents data."""
    dzn_json = DznJsonAst(verbose=True).load_file(dezyne_filename)
    return dzn_json.process()


def get_filecontents(filename: str, result: CodeGenResult) -> str:
    """Helper to get the contents of the specified filename in the provided CodeGenResult.
    Raise an exception when the filename is absent."""
    for gc in result.files:
        if filename == gc.filename:
            return gc.contents
    raise RuntimeError(f'filename "{filename}" not found in CodeGenResult')


# unit tests

def assert_all_default_support_files(files: List[GeneratedContent]):
    """Assert all known support files with default namespace Dzn to be present in the
    provided CodeGenResult argument."""
    assert ilog.create_header() in files
    assert meta_helpers.create_header() in files
    assert misc_utils.create_header() in files
    assert multi_client_selector.create_header() in files
    assert mutex_wrapped.create_header() in files
    assert strict_port.create_header() in files


def test_system_component_not_found():
    """Test the scenario that the user specifies an unknown component name."""

    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('UnknownComponent'),
                        ports_cfg=all_sts_all_mts(),
                        facilities_origin=FacilitiesOrigin.IMPORT,
                        copyright=COPYRIGHT, verbose=True)

    with pytest.raises(AdvShellError) as exc:
        Builder().build(cfg)
    assert str(exc.value) == 'Encapsulee "UnknownComponent" not found'


def test_generate_all_sts_all_mts():
    """Test a system component with all STS provided and all MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('My.Project.ToasterSystem'),
                        ports_cfg=all_sts_all_mts(),
                        facilities_origin=FacilitiesOrigin.IMPORT,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('ToasterSystemAdvShell.hh', result) == HH_ALL_STS_ALL_MTS
    assert get_filecontents('ToasterSystemAdvShell.cc', result) == CC_ALL_STS_ALL_MTS
    assert_all_default_support_files(result.files)


def test_generate_all_mts_all_sts():
    """Test a system component with all MTS provided and all STS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('My.Project.ToasterSystem'),
                        ports_cfg=all_mts_all_sts(),
                        facilities_origin=FacilitiesOrigin.CREATE, copyright=COPYRIGHT,
                        support_files_ns_prefix=ns_ids_t('Other.Project'),
                        verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('ToasterSystemAdvShell.hh', result) == HH_ALL_MTS_ALL_STS
    assert get_filecontents('ToasterSystemAdvShell.cc', result) == CC_ALL_MTS_ALL_STS
    ns = ns_ids_t('Other.Project')
    assert ilog.create_header(ns) in result.files
    assert meta_helpers.create_header(ns) in result.files
    assert misc_utils.create_header(ns) in result.files
    assert multi_client_selector.create_header(ns) in result.files
    assert mutex_wrapped.create_header(ns) in result.files
    assert strict_port.create_header(ns) in result.files


def test_generate_all_mts_mixed_ts():
    """Test a system component with all MTS provided, but mixed STS/MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('My.Project.ToasterSystem'),
                        ports_cfg=all_mts_mixed_ts(
                            sts_requires_ports=PortSelect({'led'}),
                            mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('ToasterSystemAdvShell.hh', result) == HH_ALL_MTS_MIXED_TS
    assert get_filecontents('ToasterSystemAdvShell.cc', result) == CC_ALL_MTS_MIXED_TS
    assert_all_default_support_files(result.files)


def test_generate_all_sts_mixed_ts():
    """Test an impl component with all STS provided, but mixed STS/MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE2, ast_fc=get_fc(DZN_FILE2),
                        output_basename_suffix='ImplComp',
                        fqn_encapsulee_name=ns_ids_t('StoneAgeToaster'),
                        ports_cfg=all_sts_mixed_ts(
                            mts_requires_ports=PortSelect({'heater'}),
                            sts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, creator_info=CREATOR_INFO, verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('StoneAgeToasterImplComp.hh', result) == HH_ALL_STS_MIXED_TS
    assert get_filecontents('StoneAgeToasterImplComp.cc', result) == CC_ALL_STS_MIXED_TS
    assert_all_default_support_files(result.files)


def test_generate_all_mts():
    """Test a system component with all MTS provided and required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('My.Project.ToasterSystem'),
                        ports_cfg=all_mts(),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('ToasterSystemAdvShell.hh', result) == HH_ALL_MTS
    assert get_filecontents('ToasterSystemAdvShell.cc', result) == CC_ALL_MTS
    assert_all_default_support_files(result.files)


def test_generate_multiclient_selector():
    """Test a component with one provided to be generated with the MultiClientSelector feature."""

    fc = get_fc(DZN_FILE3)
    print(fc)

    mc_cfg = MultiClientPortCfg(port_name='api',
                                claim_event_name='Claim',
                                claim_granting_reply_value=ns_ids_t('Ok'),
                                release_event_name='Release')

    cfg = Configuration(dezyne_filename=DZN_FILE3, ast_fc=fc,
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=ns_ids_t('My.Project.ExclusiveToaster'),
                        ports_cfg=all_mts(mc_cfg),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert get_filecontents('ExclusiveToasterAdvShell.hh', result) == HH_ALL_MTS_MULTICLIENT
    assert get_filecontents('ExclusiveToasterAdvShell.cc', result) == CC_ALL_MTS_MULTICLIENT
    assert_all_default_support_files(result.files)
