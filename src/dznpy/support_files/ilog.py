"""
Module providing C++ code generation of the support file "Logging interface".

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


def header_hh_template(cpp_ns: str) -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Logging Interface

Description: interfaces for logging informationals, warnings and errors. It is up to the
             implementor how the actual logging is accomplished.
             By default, the functors are initialized by a 'muted' implementation.

Contents:
- ILog: the primer interface/struct for logging messages, with a muted default implementation.
- ILogWithContext: a decorator variant derived from ILog that requires an existing ILog instance,
                   on which it prefixes each logged message with a context string.

Example 1:

    """ f'{cpp_ns}' """::ILog logger1 = {
        [&](auto msg) { MySofware.LogInfo(msg); },
        [&](auto msg) { MySofware.LogWarning(msg); },
        [&](auto msg) { MySofware.LogError(msg); }
    };

    logger1.Info("Hi there"); // will call MySofware.LogInfo("Hi there")

Example 2:

    """ f'{cpp_ns}' """::ILogWithContext logger2("MyContext", logger1);
    logger2.Warning("See ya"); // will ultimately call MySofware.LogWarning("MyContext/See ya")

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
struct ILog
{
    std::function<void(const std::string& message)> Info =    {[](auto){}};
    std::function<void(const std::string& message)> Warning = {[](auto){}};
    std::function<void(const std::string& message)> Error =   {[](auto){}};

    void check_bindings() const
    {
        if (!Info)    throw std::runtime_error("not connected: Info()");
        if (!Warning) throw std::runtime_error("not connected: Warning()");
        if (!Error)   throw std::runtime_error("not connected: Error()");
    }
};

struct ILogWithContext : ILog
{
    ILogWithContext(const std::string& contextStr, const ILog& log): ILog(), context(contextStr), subLog(log)
    {
        Info    = [this](const std::string& message) { subLog.Info(context + "/" + message); };
        Warning = [this](const std::string& message) { subLog.Warning(context + "/" + message); };
        Error   = [this](const std::string& message) { subLog.Error(context + "/" + message); };
    }

    const std::string context;
    const ILog subLog;
};
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    namespace, cpp_ns, file_ns = distillate_ns(ns_prefix)

    cfg = SupportFileCfg(header=header_hh_template(cpp_ns),
                         body=body_hh(),
                         includes=TextBlock(SystemIncludes(['functional', 'string'])),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_ILog.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
