"""
Module providing C++ code generation of the support file "Dezyne Strict Port".

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


def header_hh_template(cpp_ns: str) -> str:
    return """\
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

"""


def body_hh() -> str:
    return """\
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
"""


def create_header(namespace_prefix: NameSpaceIds = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    ns, cpp_ns, file_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh_template(cpp_ns),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    includes = SystemIncludes(['functional', 'string'])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{file_ns}_ILog.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    includes,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
