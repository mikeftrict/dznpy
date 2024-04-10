"""
Test data for validating the generated output by the advanced shell support_files module.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

from dznpy.dznpy_version import VERSION


def support_file_strict_port_hh(namespace_prefix: str) -> str:
    return """\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// Description: constructs to enforce interconnection of Dezyne ports with the correct and same runtime semantics.
//
// This is generated code. DO NOT MODIFY manually.
//

namespace """f'{namespace_prefix}'"""Dzn {

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
    provided.port.out = required.port.out;
    required.port.in = provided.port.in;
    provided.port.meta.require = required.port.meta.require;
    required.port.meta.provide = provided.port.meta.provide;
}

template <typename P>
void ConnectPorts(Mts<P> provided, Mts<P> required)
{
    provided.port.out = required.port.out;
    required.port.in = provided.port.in;
    provided.port.meta.require = required.port.meta.require;
    required.port.meta.provide = provided.port.meta.provide;
}

} // namespace """f'{namespace_prefix}'"""Dzn
// Version: dznpy/support_files v"""f'{VERSION}'"""
"""


HH_DEFAULT_DZN_STRICT_PORT = support_file_strict_port_hh('')
HH_MYNAMESPACE_DZN_STRICT_PORT = support_file_strict_port_hh('My::Name::Space::')
HH_OTHERPROJECT_STRICT_PORT = support_file_strict_port_hh('Other::Project::')
