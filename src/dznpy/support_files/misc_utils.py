"""
Module providing C++ code generation of the support file "Dezyne Misc Utils".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules

# dznpy modules
from ..dznpy_version import COPYRIGHT
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import CommentBlock, SystemIncludes, Namespace
from ..misc_utils import TextBlock
from ..scoping import NameSpaceIds

# own modules
from . import initialize_ns, create_footer


def header_hh() -> str:
    return """\
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

"""


def body_hh() -> str:
    return """\
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
"""


def create_header(namespace_prefix: NameSpaceIds = None) -> GeneratedContent:
    """Create the c++ header file contents that provides miscellaneous utilities."""

    ns, cpp_ns, file_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh(),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    includes = SystemIncludes(['algorithm', 'cctype', 'cwctype', 'regex', 'string'])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{file_ns}_MiscUtils.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    includes,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
