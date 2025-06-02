"""
Module providing C++ code generation of the support file "Dezyne Misc Utils".

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
from . import distillate_ns, SupportFileCfg, generate_cpp_code


def header_hh() -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Miscellaneous utilities

Description: miscellaneous utilities for generic usage.

Contents:
- capitalize the first character of a std::string or std::wstring.

Examples of CapitalizeFirstChar:

   std::string mystr{"hello"};
   auto result = CapitalizeFirstChar(mystr); // result == std::string("Hello")

   std::wstring mywstr{L"world"};
   auto result = CapitalizeFirstChar(mywstr); // result == std::wstring(L"World")

   auto result = CapitalizeFirstChar(std::string("")); // result = std::string("")

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
template <typename STR_TYPE>
[[nodiscard]] STR_TYPE CapitalizeFirstChar(const STR_TYPE& str)
{
    if (str.empty()) return str;

    STR_TYPE result(str);

    if constexpr (std::is_same_v<STR_TYPE, std::string>)
    {
        std::transform(result.cbegin(), result.cbegin() + 1, result.begin(),
                       [](auto c) { return static_cast<char>(std::toupper(c)); });
    }

    if constexpr (std::is_same_v<STR_TYPE, std::wstring>)
    {
        std::transform(result.cbegin(), result.cbegin() + 1, result.begin(),
                       [](auto c) { return static_cast<wchar_t>(std::towupper(c)); });
    }

    return result;
}
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that provides miscellaneous utilities."""

    namespace, _, file_ns = distillate_ns(ns_prefix)

    cfg = SupportFileCfg(header=header_hh(),
                         body=body_hh(),
                         includes=TextBlock(SystemIncludes(['algorithm',
                                                            'cctype',
                                                            'cwctype',
                                                            'regex',
                                                            'string'])),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_MiscUtils.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
