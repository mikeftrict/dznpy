"""
dznpy/adv_shell/core/support_files - version 0.2.240304

Python module providing generation of support files that are required for compiling
the generated advanced shell c++ code.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# dznpy modules
from ...dznpy_version import VERSION
from ...cpp_gen import Comment, CommentBlock, Namespace
from ...misc_utils import TextBlock, NameSpaceIds, is_namespaceids_instance

# own modules
from ..common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY

# constants

DESCRIPTION = '''\
Description: constructs to enforce interconnection of Dezyne ports with the correct and same runtime semantics.
'''

BODY_DECL = '''\

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

'''


def create_strict_ports_headerfile(copyright_header: str,
                                   namespace_prefix: NameSpaceIds = None) -> GeneratedContent:
    """Create the support headerfile that facilitates strict port typing."""

    # Namespace prefix argument checking.
    if namespace_prefix is None:
        ns = ['Dzn']
    elif is_namespaceids_instance(namespace_prefix):
        ns = namespace_prefix + ['Dzn']
    else:
        raise TypeError('namespace_prefix is of incorrect type')

    # Create the body of the C++ header file
    header = CommentBlock([copyright_header,
                           BLANK_LINE,
                           DESCRIPTION,
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           ])

    body = Namespace(ns, contents=BODY_DECL)

    footer = Comment(f'Version: dznpy/support_files v{VERSION}')

    return GeneratedContent(filename=f'{"_".join(ns)}_StrictPort.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    body,
                                                    footer])),
                            namespace=ns)
