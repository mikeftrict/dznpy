"""
Module providing C++ code generation of the support file "Dezyne Strict Port".

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# pylint: disable=line-too-long

# system modules
from typing import Optional

# dznpy modules
from ..scoping import NamespaceIds
from ..text_gen import GeneratedContent, TextBlock

# own modules
from . import distillate_ns, SupportFileCfg, generate_cpp_code


def header_hh_template(cpp_ns: str) -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Dezyne Strict Port

Description: helping constructs to ensure correct interconnection of Dezyne ports based
             on their runtime semantics. Lean on the compiler to yield errors when a developer
             (mistakenly) attempts to tie two ports that have different semantics.

Contents:
- Port enclosures to explicitly indicate the implied runtime semantics. An enclosure stores a
  reference to the original Dezyne port instance.
- Port interconnect functions that require correct argument types.

Example:

given a normal port and make it strict 'MTS' and 'STS' inline:

    IMyService m_dznPort{<port-meta>};
    """ f'{cpp_ns}' """::Mts<IMyService> strictMtsPort{m_dznPort};
    """ f'{cpp_ns}' """::Sts<IMyService> strictStsPort{m_dznPort};

return a strict 'STS' port as function return:

    """ f'{cpp_ns}' """::Sts<IMyService> GetStrictPort()
    {
       return {m_dznPort};
    }

interconnect two strict ports:

    """ f'{cpp_ns}' """::ConnectPorts( strictStsPort, GetStrictPort() ); // Ok
    """ f'{cpp_ns}' """::ConnectPorts( strictMtsPort, GetStrictPort() ); // Error during compilation

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
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
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    namespace, cpp_ns, file_ns = distillate_ns(ns_prefix)

    cfg = SupportFileCfg(header=header_hh_template(cpp_ns),
                         body=body_hh(),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_StrictPort.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
