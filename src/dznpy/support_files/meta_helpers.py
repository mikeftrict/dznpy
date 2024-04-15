"""
Module providing C++ code generation of the support file "Dezyne Meta Helpers".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules

# dznpy modules
from ..dznpy_version import COPYRIGHT
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import CommentBlock, SystemIncludes, Namespace
from ..misc_utils import TextBlock, NameSpaceIds

# own modules
from . import initialize_ns, create_footer


def header_hh_template(cpp_ns: str) -> str:
    return """\
Dezyne Meta helpers

Description: helper functions for creating Dezyne Port meta

Contents:
- functions to create a Dezyne port where the name (provided, required, or both) are filled in,

Examples:

given a Dezyne port IMyService:

    IMyService port = """ f'{cpp_ns}' """::CreateProvidedPort<IMyService>("api");

    IMyService port = """ f'{cpp_ns}' """::CreateRequiredPort<IMyService>("hal");

    IMyService port = """ f'{cpp_ns}' """::CreatePort<IMyService>("api", "hal");

"""


def body_hh() -> str:
    return """\
template <typename DZN_PORT>
DZN_PORT CreateProvidedPort(const std::string& name)
{
    return DZN_PORT{{{name, nullptr, nullptr, nullptr}, {"", nullptr, nullptr, nullptr}}};
}

template <typename DZN_PORT>
DZN_PORT CreateRequiredPort(const std::string& name)
{
    return DZN_PORT{{{"", nullptr, nullptr, nullptr}, {name, nullptr, nullptr, nullptr}}};
}

template <typename DZN_PORT>
DZN_PORT CreatePort(const std::string& provideName, const std::string& requireName)
{
    return DZN_PORT{{{provideName, nullptr, nullptr, nullptr}, {requireName, nullptr, nullptr, nullptr}}};
}
"""


def create_header(namespace_prefix: NameSpaceIds = None) -> GeneratedContent:
    """Create the c++ header file contents that provides miscellaneous utilities."""

    ns, cpp_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh_template(cpp_ns),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    includes = SystemIncludes(['string', 'dzn/meta.hh'])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{"_".join(ns)}_MetaHelpers.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    includes,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
