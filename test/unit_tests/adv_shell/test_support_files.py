"""
Testsuite covering the adv_shell/core/support_files python module - version 0.2.240304

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
import pytest

# system-under-test
from dznpy.misc_utils import namespaceids_t
from dznpy.adv_shell.core.support_files import create_strict_ports_headerfile

# Test data
from testdata_support_files import *
from testdata_builder import COPYRIGHT


# unit tests

def test_create_strict_port_hh_with_namespace_ok():
    result = create_strict_ports_headerfile(COPYRIGHT, namespaceids_t('My.Name.Space'))
    assert result.namespace == ['My', 'Name', 'Space', 'Dzn']
    assert result.filename == 'My_Name_Space_Dzn_StrictPort.hh'
    assert result.contents == HH_MYNAMESPACE_DZN_STRICT_PORT
    assert 'namespace My::Name::Space::Dzn {' in result.contents


def test_create_strict_port_hh_default_ok():
    result = create_strict_ports_headerfile(COPYRIGHT)
    assert result.namespace == ['Dzn']
    assert result.filename == 'Dzn_StrictPort.hh'
    assert result.contents == HH_DEFAULT_DZN_STRICT_PORT
    assert 'namespace Dzn {' in result.contents


def test_create_strict_port_hh_fail():
    with pytest.raises(TypeError) as exc:
        create_strict_ports_headerfile(COPYRIGHT, 123)
    assert str(exc.value) == 'namespace_prefix is of incorrect type'
