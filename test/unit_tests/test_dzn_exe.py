"""
Testsuite validating the dzn_exe module

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from typing import Any

# system-under-test
from dznpy.dzn_exe import *

# test data
from testdata_dzn_exe import *


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
