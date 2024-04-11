"""
Module providing a C++ code generation of the syooirt file "Strict Port".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules

# dznpy modules
from ..dznpy_version import VERSION
from ..cpp_gen import Comment, CommentBlock, Namespace
from ..misc_utils import TextBlock, NameSpaceIds, is_namespaceids_instance

# own modules
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY

# dznpy modules

DESCRIPTION = '''\
Description: helping constructs to ensure correct interconnection of Dezyne ports based
             on their runtime semantics. Lean on the compiler to yield errors when a developer
             (mistakenly) attempts to tie two ports that have different semantics.
             - port enclosures to explicitly indicate the implied runtime semantics.
             - port interconnect functions that require correct argument types.
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
    connect(provided, required);
}

template <typename P>
void ConnectPorts(Mts<P> provided, Mts<P> required)
{
    connect(provided, required);
}

'''


def create_header(copyright_header: str,
                  namespace_prefix: NameSpaceIds = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    # Precondition checking
    if namespace_prefix is None:
        ns = ['Dzn']
    elif is_namespaceids_instance(namespace_prefix):
        ns = namespace_prefix + ['Dzn']
    else:
        raise TypeError('namespace_prefix is of incorrect type')

    # Create the C++ body
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
