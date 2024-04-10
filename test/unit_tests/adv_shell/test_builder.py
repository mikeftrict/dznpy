"""
Testsuite validating the builder aspects of the adv_shell module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import os
import pytest

# system-under-test
from dznpy import ast
from dznpy.adv_shell import PortSelect, PortWildcard, all_sts_all_mts, all_mts_all_sts, \
    all_mts_mixed_ts, all_sts_mixed_ts, all_mts, Configuration, Builder, \
    FacilitiesOrigin, GeneratedContent as GC
from dznpy.adv_shell.types import AdvShellError
from dznpy.misc_utils import namespaceids_t
from dznpy.json_ast import DznJsonAst

# Test data
from testdata_builder import *
from testdata_support_files import HH_DEFAULT_DZN_STRICT_PORT, HH_OTHERPROJECT_STRICT_PORT


# test helpers

def resolve(fn: str) -> str:
    """Get the absolute path of Dezyne test files relative to this file to be independent
    of how and from where py.test is run."""
    return os.path.abspath(f'{__file__}/../../../dezyne_models/{fn}')


def get_fc(dezyne_filename) -> ast.FileContents:
    """Helper to load the JSON AST tree of a Dezyne file and proces it into FileContents data."""
    dzn_json = DznJsonAst(verbose=True).load_file(dezyne_filename)
    return dzn_json.process()


# test constants

DZN_FILE1 = resolve(TOASTER_SYSTEM_JSON_FILE)
DZN_FILE2 = resolve(STONE_AGE_TOASTER_FILE)


# unit tests

def test_system_component_not_found():
    """Test the scenario that the user specifies an unknown component name."""

    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=namespaceids_t('UnknownComponent'),
                        port_cfg=all_sts_all_mts(),
                        facilities_origin=FacilitiesOrigin.IMPORT,
                        copyright=COPYRIGHT, verbose=True)

    with pytest.raises(AdvShellError) as exc:
        Builder().build(cfg)
    assert str(exc.value) == "Encapsulee ['UnknownComponent'] not found"


def test_generate_all_sts_all_mts():
    """Test a system component with all STS provided and all MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                        port_cfg=all_sts_all_mts(),
                        facilities_origin=FacilitiesOrigin.IMPORT,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert result.files == [GC('ToasterSystemAdvShell.hh', HH_ALL_STS_ALL_MTS),
                            GC('ToasterSystemAdvShell.cc', CC_ALL_STS_ALL_MTS),
                            GC('Dzn_StrictPort.hh', HH_DEFAULT_DZN_STRICT_PORT, ['Dzn'])]


def test_generate_all_mts_all_sts():
    """Test a system component with all MTS provided and all STS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                        port_cfg=all_mts_all_sts(),
                        facilities_origin=FacilitiesOrigin.CREATE, copyright=COPYRIGHT,
                        support_files_ns_prefix=namespaceids_t('Other.Project'),
                        verbose=True)

    result = Builder().build(cfg)
    assert result.files == [GC('ToasterSystemAdvShell.hh', HH_ALL_MTS_ALL_STS),
                            GC('ToasterSystemAdvShell.cc', CC_ALL_MTS_ALL_STS),
                            GC('Other_Project_Dzn_StrictPort.hh', HH_OTHERPROJECT_STRICT_PORT,
                               ['Other', 'Project', 'Dzn'])]


def test_generate_all_mts_mixed_ts():
    """Test a system component with all MTS provided, but mixed STS/MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                        port_cfg=all_mts_mixed_ts(
                            sts_requires_ports=PortSelect({'led'}),
                            mts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert result.files == [GC('ToasterSystemAdvShell.hh', HH_ALL_MTS_MIXED_TS),
                            GC('ToasterSystemAdvShell.cc', CC_ALL_MTS_MIXED_TS),
                            GC('Dzn_StrictPort.hh', HH_DEFAULT_DZN_STRICT_PORT, ['Dzn'])]


def test_generate_all_sts_mixed_ts():
    """Test an impl component with all STS provided, but mixed STS/MTS required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE2, ast_fc=get_fc(DZN_FILE2),
                        output_basename_suffix='ImplComp',
                        fqn_encapsulee_name=namespaceids_t('StoneAgeToaster'),
                        port_cfg=all_sts_mixed_ts(
                            mts_requires_ports=PortSelect({'heater'}),
                            sts_requires_ports=PortSelect(PortWildcard.REMAINING)),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, creator_info=CREATOR_INFO, verbose=True)

    result = Builder().build(cfg)
    assert result.files == [GC('StoneAgeToasterImplComp.hh', HH_ALL_STS_MIXED_TS),
                            GC('StoneAgeToasterImplComp.cc', CC_ALL_STS_MIXED_TS),
                            GC('Dzn_StrictPort.hh', HH_DEFAULT_DZN_STRICT_PORT, ['Dzn'])]


def test_generate_all_mts():
    """Test a system component with all MTS provided and required ports."""
    cfg = Configuration(dezyne_filename=DZN_FILE1, ast_fc=get_fc(DZN_FILE1),
                        output_basename_suffix='AdvShell',
                        fqn_encapsulee_name=namespaceids_t('My.Project.ToasterSystem'),
                        port_cfg=all_mts(),
                        facilities_origin=FacilitiesOrigin.CREATE,
                        copyright=COPYRIGHT, verbose=True)

    result = Builder().build(cfg)
    assert result.files == [GC('ToasterSystemAdvShell.hh', HH_ALL_MTS),
                            GC('ToasterSystemAdvShell.cc', CC_ALL_MTS),
                            GC('Dzn_StrictPort.hh', HH_DEFAULT_DZN_STRICT_PORT, ['Dzn'])]
