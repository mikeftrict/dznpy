"""
Testsuite validating the output of generated support file: StrictPort.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# dznpy modules
from dznpy.scoping import ns_ids_t, NamespaceIds, NamespaceIdsTypeError

# systems-under-test
from dznpy.support_files import strict_port as sut

# Test data
from common.testdata import *
from dznpy.dznpy_version import VERSION


def template_hh(ns_prefix: str) -> str:
    return """\
// Dezyne Strict Port
//
// Description: helping constructs to ensure correct interconnection of Dezyne ports based
//              on their runtime semantics. Lean on the compiler to yield errors when a developer
//              (mistakenly) attempts to tie two ports that have different semantics.
//
// Contents:
// - Port enclosures to explicitly indicate the implied runtime semantics. An enclosure stores a
//   reference to the original Dezyne port instance.
// - Port interconnect functions that require correct argument types.
//
// Example:
//
// given a normal port and make it strict 'MTS' and 'STS' inline:
//
//     IMyService m_dznPort{<port-meta>};
//     """ f'{ns_prefix}' """Dzn::Mts<IMyService> strictMtsPort{m_dznPort};
//     """ f'{ns_prefix}' """Dzn::Sts<IMyService> strictStsPort{m_dznPort};
//
// return a strict 'STS' port as function return:
//
//     """ f'{ns_prefix}' """Dzn::Sts<IMyService> GetStrictPort()
//     {
//        return {m_dznPort};
//     }
//
// interconnect two strict ports:
//
//     """ f'{ns_prefix}' """Dzn::ConnectPorts( strictStsPort, GetStrictPort() ); // Ok
//     """ f'{ns_prefix}' """Dzn::ConnectPorts( strictMtsPort, GetStrictPort() ); // Error, during compilation
//
//
// This is generated code. DO NOT MODIFY manually.
//
// Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
// This is free software, released under the MIT License. Refer to dznpy/LICENSE.

namespace """ f'{ns_prefix}' """Dzn {

// Enclosure for a port that conforms to Single-threaded Runtime Semantics (STS)
template <typename P>
struct Sts
{
    P& port;
};

// Enclosure for a port that conforms to Multi-threaded Runtime Semantics (MTS)
template <typename P>
struct Mts
{
    P& port;
};

template <typename P>
void ConnectPorts(Sts<P> provided, Sts<P> required)
{
    connect(provided.port, required.port);
}

template <typename P>
void ConnectPorts(Mts<P> provided, Mts<P> required)
{
    connect(provided.port, required.port);
}

} // namespace """ f'{ns_prefix}' """Dzn
// Generated by: dznpy/support_files v"""f'{VERSION}'"""
"""


DEFAULT_DZN_STRICT_PORT_HH = template_hh('')
MYNAMESPACE_DZN_STRICT_PORT_HH = template_hh('My::Name::Space::')


def test_create_default_namespaced():
    result = sut.create_header()
    assert result.namespace == ns_ids_t('Dzn')
    assert result.filename == 'Dzn_StrictPort.hh'
    assert result.contents == DEFAULT_DZN_STRICT_PORT_HH
    assert result.contents_hash == '3f69c8a923e6f7190d090d711e701754'
    assert 'namespace Dzn {' in result.contents


def test_create_with_prefixing_namespace():
    result = sut.create_header(ns_ids_t('My.Name.Space'))
    assert result.namespace == NamespaceIds(['My', 'Name', 'Space', 'Dzn'])
    assert result.filename == 'My_Name_Space_Dzn_StrictPort.hh'
    assert result.contents == MYNAMESPACE_DZN_STRICT_PORT_HH
    assert 'namespace My::Name::Space::Dzn {' in result.contents


def test_create_fail():
    with pytest.raises(TypeError) as exc:
        sut.create_header(123)
    assert str(exc.value) == ARGUMENT123_NOT_NAMESPACEIDS
