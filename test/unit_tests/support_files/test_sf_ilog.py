"""
Testsuite validating the output of generated support file: ILog.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# dznpy modules
from dznpy.misc_utils import namespaceids_t

# systems-under-test
from dznpy.support_files import ilog as sut

# Test data
from dznpy.dznpy_version import VERSION


def template_hh(ns_prefix: str) -> str:
    return """\
// Logging Interface
//
// Description: interfaces for logging informationals, warnings and errors. It is up to the
//              implementor how the actual logging is accomplished.
//              By default, the functors are initialized by a 'muted' implementation.
//
// Contents:
// - ILog: the primer interface/struct for logging messages, with a muted default implementation.
// - ILogWithContext: a decorator variant derived from ILog that requires an existing ILog instance,
//                    on which it prefixes each logged message with a context string.
//
// Example 1:
//
//     """ f'{ns_prefix}' """Dzn::ILog logger1 = {
//         [&](auto msg) { MySofware.LogInfo(msg); },
//         [&](auto msg) { MySofware.LogWarning(msg); },
//         [&](auto msg) { MySofware.LogError(msg); }
//     };
//
//     logger1.Info("Hi there"); // will call MySofware.LogInfo("Hi there")
//
// Example 2:
//
//     """ f'{ns_prefix}' """Dzn::ILogWithContext logger2("MyContext", logger1);
//     logger2.Warning("See ya"); // will ultimately call MySofware.LogWarning("MyContext/See ya")
//
//
// This is generated code. DO NOT MODIFY manually.
//
// Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
// This is free software, released under the MIT License. Refer to dznpy/LICENSE.

// System includes
#include <functional>
#include <string>

namespace """ f'{ns_prefix}' """Dzn {

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

} // namespace """ f'{ns_prefix}' """Dzn
// Generated by: dznpy/support_files v"""f'{VERSION}'"""
"""


DEFAULT_DZN_ILOG_HH = template_hh('')
MYPROJECT_DZN_ILOG_HH = template_hh('MyProject::')


def test_create_default_namespaced():
    result = sut.create_header()
    assert result.namespace == ['Dzn']
    assert result.filename == 'Dzn_ILog.hh'
    assert result.contents == DEFAULT_DZN_ILOG_HH
    assert result.contents_hash == '9380db6b8a596563db6bfde34940019f'
    assert 'namespace Dzn {' in result.contents


def test_create_with_prefixing_namespace():
    result = sut.create_header(namespaceids_t('MyProject'))
    assert result.namespace == ['MyProject', 'Dzn']
    assert result.filename == 'MyProject_Dzn_ILog.hh'
    assert result.contents == MYPROJECT_DZN_ILOG_HH
    assert 'namespace MyProject::Dzn {' in result.contents


def test_create_fail():
    with pytest.raises(TypeError) as exc:
        sut.create_header(123)
    assert str(exc.value) == 'namespace_prefix is of incorrect type'
