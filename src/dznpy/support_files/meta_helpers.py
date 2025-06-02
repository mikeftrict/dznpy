"""
Module providing C++ code generation of the support file "Dezyne Meta Helpers".

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# pylint: disable=line-too-long

# system modules
from typing import Optional

# dznpy modules
from ..cpp_gen import SystemIncludes
from ..scoping import NamespaceIds
from ..text_gen import GeneratedContent, TextBlock

# own modules
from . import distillate_ns, generate_cpp_code, SupportFileCfg


def header_hh_template(cpp_ns: str) -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Dezyne Meta helpers

Description: helper functions for creating Dezyne Port meta

Contents:
- functions to create a Dezyne port where the name (provided, required, or both) are filled in,

Examples:

given a Dezyne port IMyService:

    IMyService port = """ f'{cpp_ns}' """::CreateProvidedPort<IMyService>("api");

    IMyService port = """ f'{cpp_ns}' """::CreateRequiredPort<IMyService>("hal");

    IMyService port = """ f'{cpp_ns}' """::CreatePort<IMyService>("api", "hal");

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
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
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that provides miscellaneous utilities."""

    namespace, cpp_ns, file_ns = distillate_ns(ns_prefix)

    cfg = SupportFileCfg(header=header_hh_template(cpp_ns),
                         body=body_hh(),
                         includes=TextBlock(SystemIncludes(['string', 'dzn/meta.hh'])),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_MetaHelpers.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
