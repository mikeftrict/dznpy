"""
Test data for validating the generated output by the support_files modules.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

from dznpy.dznpy_version import VERSION


def template_strict_port_hh(namespace_prefix: str) -> str:
    return """\
// Copyright (c) Michael van de Ven <michael@ftr-ict.com>
// This is free software, released under the MIT License. Refer to dznpy/LICENSE.
//
// Description: helping constructs to ensure correct interconnection of Dezyne ports based
//              on their runtime semantics. Lean on the compiler to yield errors when a developer
//              (mistakenly) attempts to tie two ports that have different semantics.
//              - port enclosures to explicitly indicate the implied runtime semantics.
//              - port interconnect functions that require correct argument types.
//
// This is generated code. DO NOT MODIFY manually.
//

namespace """ f'{namespace_prefix}' """Dzn {

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
    connect(provided, required);
}

template <typename P>
void ConnectPorts(Mts<P> provided, Mts<P> required)
{
    connect(provided, required);
}

} // namespace """ f'{namespace_prefix}' """Dzn
// Version: dznpy/support_files v"""f'{VERSION}'"""
"""


HH_DEFAULT_DZN_STRICT_PORT = template_strict_port_hh('')
HH_MYNAMESPACE_DZN_STRICT_PORT = template_strict_port_hh('My::Name::Space::')
HH_OTHERPROJECT_STRICT_PORT = template_strict_port_hh('Other::Project::')
