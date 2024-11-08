"""
Module providing C++ code generation of the support file "Dezyne Strict Port".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import Optional

# dznpy modules
from ..dznpy_version import COPYRIGHT
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import CommentBlock, Namespace
from ..misc_utils import TextBlock
from ..scoping import NamespaceIds

# own modules
from . import initialize_ns, create_footer


def header_hh_template(cpp_ns: str) -> str:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return """\
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

"""


def body_hh() -> str:
    """Generate the body of a C++ headerfile with templated fields."""
    return """\
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
"""


def create_header(namespace_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    ns, cpp_ns, file_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh_template(cpp_ns),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{file_ns}_StrictPort.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
