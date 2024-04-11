"""
Testsuite validating the generated support files by the adv_shell module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# dznpy modules
from dznpy.misc_utils import namespaceids_t

# system-under-test
from dznpy.support_files import strict_port

# Test data
from common.testdata import COPYRIGHT
from testdata_support_files import *


# unit tests

def test_create_strict_port_hh_with_namespace_ok():
    result = strict_port.create_header(COPYRIGHT, namespaceids_t('My.Name.Space'))
    assert result.namespace == ['My', 'Name', 'Space', 'Dzn']
    assert result.filename == 'My_Name_Space_Dzn_StrictPort.hh'
    assert result.contents == HH_MYNAMESPACE_DZN_STRICT_PORT
    assert 'namespace My::Name::Space::Dzn {' in result.contents


def test_create_strict_port_hh_default_ok():
    result = strict_port.create_header(COPYRIGHT)
    assert result.namespace == ['Dzn']
    assert result.filename == 'Dzn_StrictPort.hh'
    assert result.contents == HH_DEFAULT_DZN_STRICT_PORT
    assert 'namespace Dzn {' in result.contents


def test_create_strict_port_hh_fail():
    with pytest.raises(TypeError) as exc:
        strict_port.create_header(COPYRIGHT, 123)
    assert str(exc.value) == 'namespace_prefix is of incorrect type'
