"""
Testsuite validating the dzn_exe module

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# system-under-test
from dznpy.versioning import *

# test data
from testdata_dzn_exe import *


def test_dznpy_version():
    """Test the current version of dznpy."""
    assert str(DZNPY_VERSION) == '1.3.DEV'


def test_copyright():
    """Test the contents of dznpy copyright."""
    assert str(DZNPY_COPYRIGHT) == '''Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
'''


def test_dzn_version_strings_ok():
    """Test valid version strings of what dzn.cmd can output."""
    assert str(DznVersion(DZN_VERSION_OUTPUT1)) == '2.17.9'
    assert str(DznVersion(DZN_VERSION_OUTPUT2)) == '2.18.3.563-596a7f'


def test_dzn_version_strings_fail():
    """Test invalid version string."""
    with pytest.raises(TypeError) as exc:
        DznVersion('BOGUS')
    assert str(exc.value) == 'No valid version-format "x.y.z[.dev-tag]" found in string: BOGUS'


def test_version_details():
    """Test the details of a DznVersion instance."""
    sut = DznVersion('2.18.3.563-596a7f')
    assert sut.major == 2
    assert sut.minor == 18
    assert sut.revision == 3
    assert sut.dev_tag == '563-596a7f'


def test_compare_version_instances_ok():
    """Test comparison logic between two instances of DznVersion."""
    assert DznVersion('2.18.3') != DznVersion('2.17.8')
    assert DznVersion('2.18.3') == DznVersion('2.18.3')
    assert DznVersion('2.18.3') >= DznVersion('2.18.3')
    assert DznVersion('2.18.4') >= DznVersion('2.18.3')
    assert DznVersion('2.18.4') > DznVersion('2.18.3')
    assert DznVersion('2.18.3') <= DznVersion('2.18.3')
    assert DznVersion('2.18.2') <= DznVersion('2.18.3')
    assert DznVersion('2.18.2') < DznVersion('2.18.3')
    assert DznVersion('0.0.1') < DznVersion('2.18.3')


def test_compare_version_instances_fail():
    """Test comparison logic between DznVersion and other types, which must fail."""
    with pytest.raises(TypeError) as exc:
        DznVersion('2.18.3') == 123
    assert str(exc.value) == "The 'other' instance must be of type DznVersion"

    with pytest.raises(TypeError) as exc:
        DznVersion('2.18.3') < 'bogus'
    assert str(exc.value) == "The 'other' instance must be of type DznVersion"
