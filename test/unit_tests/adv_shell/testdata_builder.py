"""
Test data for validating the generated output by the adv_shell module.

Copyright (c) Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# test data/contents from test/dezyne_models/
TOASTER_SYSTEM_JSON_FILE = 'generated/ToasterSystem.json'
STONE_AGE_TOASTER_FILE = 'generated/StoneAgeToaster.json'

CREATOR_INFO = '''\
ABC
DEF
GHI
'''

HH_ALL_STS_ALL_MTS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// Creator information:
// <none>
//
// Configuration:
// - Encapsulee FQN: My.Project.ToasterSystem
// - Source file basename: ToasterSystem
// - Target file basename: ToasterSystemAdvShell
// - Dezyne facilities: Import facilities (by reference) from the user provided dzn::locator argument
// - Port semantics: provides ports: All STS, requires ports: All MTS
//
// Provides ports (Single-threaded):
// - api: IToaster
//
// Requires ports (Multi-threaded):
// - heaterElement: IHeaterElement
// - cord: IPowerCord
// - led: ILed
//
// This is generated code. DO NOT MODIFY manually.

// System includes
#include <dzn/locator.hh>
#include <dzn/pump.hh>
// Project includes
#include "ToasterSystem.hh"
#include "Dzn_StrictPort.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& locator, const std::string& encapsuleeInstanceName = "");
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    // <none>

    // Provides port accessor
    ::Dzn::Sts<::My::Project::IToaster> ProvidesApi();

    // Requires port accessors
    ::Dzn::Mts<::Some::Vendor::IHeaterElement> RequiresHeaterElement();
    ::Dzn::Mts<::My::Project::Hal::IPowerCord> RequiresCord();
    ::Dzn::Mts<::My::ILed> RequiresLed();

private:
    // Facilities
    dzn::pump& m_dispatcher;
    static const dzn::locator& FacilitiesCheck(const dzn::locator& locator);

    // The encapsulated component "ToasterSystem"
    ::My::Project::ToasterSystem m_encapsulee;

    // Boundary provides-port (MTS) to reroute inwards events
    // <none>

    // Boundary requires-ports (MTS) to reroute inwards events
    ::Some::Vendor::IHeaterElement m_rpHeaterElement;
    ::My::Project::Hal::IPowerCord m_rpCord;
    ::My::ILed m_rpLed;
};
} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

CC_ALL_STS_ALL_MTS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// This is generated code. DO NOT MODIFY manually.

// System include
#include <dzn/runtime.hh>
// Project include
#include "ToasterSystemAdvShell.hh"

namespace My::Project {

const dzn::locator& ToasterSystemAdvShell::FacilitiesCheck(const dzn::locator& locator)
{
    // This class imports the required facilities that must be provided by the user via the locator argument.

    if (locator.try_get<dzn::pump>() == nullptr) throw std::runtime_error("ToasterSystemAdvShell: Dispatcher missing (dzn::pump)");
    if (locator.try_get<dzn::runtime>() == nullptr) throw std::runtime_error("ToasterSystemAdvShell: Dezyne runtime missing (dzn::runtime)");

    return locator;
}

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& locator, const std::string& encapsuleeInstanceName)
    : m_dispatcher(FacilitiesCheck(locator).get<dzn::pump>())
    , m_encapsulee(locator)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
    , m_rpLed(m_encapsulee.led)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = encapsuleeInstanceName;
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";
    m_encapsulee.led.meta.provide.name = "led";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    // <None>

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    m_rpCord.out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    m_rpCord.out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
    m_rpLed.out.GlitchOccurred = [&] {
        return m_dispatcher([&] { return m_encapsulee.led.out.GlitchOccurred(); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    m_encapsulee.api.check_bindings();
    m_rpHeaterElement.check_bindings();
    m_rpCord.check_bindings();
    m_rpLed.check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    // <none>

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = m_rpHeaterElement.in;
    m_encapsulee.cord.in = m_rpCord.in;
    m_encapsulee.led.in = m_rpLed.in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}


::Dzn::Sts<::My::Project::IToaster> ToasterSystemAdvShell::ProvidesApi()
{
    return {m_encapsulee.api};
}

::Dzn::Mts<::Some::Vendor::IHeaterElement> ToasterSystemAdvShell::RequiresHeaterElement()
{
    return {m_rpHeaterElement};
}

::Dzn::Mts<::My::Project::Hal::IPowerCord> ToasterSystemAdvShell::RequiresCord()
{
    return {m_rpCord};
}

::Dzn::Mts<::My::ILed> ToasterSystemAdvShell::RequiresLed()
{
    return {m_rpLed};
}

} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

HH_ALL_MTS_ALL_STS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// Creator information:
// <none>
//
// Configuration:
// - Encapsulee FQN: My.Project.ToasterSystem
// - Source file basename: ToasterSystem
// - Target file basename: ToasterSystemAdvShell
// - Dezyne facilities: Create all facilities (dispatcher, runtime and locator)
// - Port semantics: provides ports: All MTS, requires ports: All STS
//
// Provides ports (Multi-threaded):
// - api: IToaster
//
// Requires ports (Single-threaded):
// - heaterElement: IHeaterElement
// - cord: IPowerCord
// - led: ILed
//
// This is generated code. DO NOT MODIFY manually.

// System includes
#include <dzn/locator.hh>
#include <dzn/pump.hh>
#include <dzn/runtime.hh>
// Project includes
#include "ToasterSystem.hh"
#include "Other_Project_Dzn_StrictPort.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName = "");
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::Other::Project::Dzn::Mts<::My::Project::IToaster> ProvidesApi();

    // Requires port accessors
    ::Other::Project::Dzn::Sts<::Some::Vendor::IHeaterElement> RequiresHeaterElement();
    ::Other::Project::Dzn::Sts<::My::Project::Hal::IPowerCord> RequiresCord();
    ::Other::Project::Dzn::Sts<::My::ILed> RequiresLed();

private:
    // Facilities
    dzn::runtime m_runtime;
    dzn::pump m_dispatcher;
    dzn::locator m_locator;
    static const dzn::locator& FacilitiesCheck(const dzn::locator& locator);

    // The encapsulated component "ToasterSystem"
    ::My::Project::ToasterSystem m_encapsulee;

    // Boundary provides-port (MTS) to reroute inwards events
    ::My::Project::IToaster m_ppApi;

    // Boundary requires-port (MTS) to reroute inwards events
    // <none>
};
} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

CC_ALL_MTS_ALL_STS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// This is generated code. DO NOT MODIFY manually.

// System include
#include <dzn/runtime.hh>
// Project include
#include "ToasterSystemAdvShell.hh"

namespace My::Project {

const dzn::locator& ToasterSystemAdvShell::FacilitiesCheck(const dzn::locator& locator)
{
    // This class creates the required facilities. But in case the user provided locator argument already contains some or
    // all facilities, it indicates an execution deployment error. Important: each threaded subsystem has its own exclusive
    // instances of the dispatcher and dezyne runtime facilities. They can never be shared with other threaded subsystems.

    if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping dispatcher found (dzn::pump)");
    if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping Dezyne runtime found (dzn::runtime)");

    return locator;
}

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = encapsuleeInstanceName;
    m_encapsulee.api.meta.require.name = "api";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    m_ppApi.in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    m_ppApi.in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    m_ppApi.in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    m_ppApi.in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    m_ppApi.in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    m_ppApi.in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    m_ppApi.in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    // <None>
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    m_ppApi.check_bindings();
    m_encapsulee.heaterElement.check_bindings();
    m_encapsulee.cord.check_bindings();
    m_encapsulee.led.check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = m_ppApi.out;

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    // <none>

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& ToasterSystemAdvShell::Locator()
{
    return m_locator;
}

::Other::Project::Dzn::Mts<::My::Project::IToaster> ToasterSystemAdvShell::ProvidesApi()
{
    return {m_ppApi};
}

::Other::Project::Dzn::Sts<::Some::Vendor::IHeaterElement> ToasterSystemAdvShell::RequiresHeaterElement()
{
    return {m_encapsulee.heaterElement};
}

::Other::Project::Dzn::Sts<::My::Project::Hal::IPowerCord> ToasterSystemAdvShell::RequiresCord()
{
    return {m_encapsulee.cord};
}

::Other::Project::Dzn::Sts<::My::ILed> ToasterSystemAdvShell::RequiresLed()
{
    return {m_encapsulee.led};
}

} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

HH_ALL_MTS_MIXED_TS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// Creator information:
// <none>
//
// Configuration:
// - Encapsulee FQN: My.Project.ToasterSystem
// - Source file basename: ToasterSystem
// - Target file basename: ToasterSystemAdvShell
// - Dezyne facilities: Create all facilities (dispatcher, runtime and locator)
// - Port semantics: provides ports: All MTS, requires ports: STS=['led'] MTS=[<Remaining ports>]
//
// Provides ports (Multi-threaded):
// - api: IToaster
//
// Requires ports (Single-threaded):
// - led: ILed
//
// Requires ports (Multi-threaded):
// - heaterElement: IHeaterElement
// - cord: IPowerCord
//
// This is generated code. DO NOT MODIFY manually.

// System includes
#include <dzn/locator.hh>
#include <dzn/pump.hh>
#include <dzn/runtime.hh>
// Project includes
#include "ToasterSystem.hh"
#include "Dzn_StrictPort.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName = "");
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::Dzn::Mts<::My::Project::IToaster> ProvidesApi();

    // Requires port accessors
    ::Dzn::Mts<::Some::Vendor::IHeaterElement> RequiresHeaterElement();
    ::Dzn::Mts<::My::Project::Hal::IPowerCord> RequiresCord();
    ::Dzn::Sts<::My::ILed> RequiresLed();

private:
    // Facilities
    dzn::runtime m_runtime;
    dzn::pump m_dispatcher;
    dzn::locator m_locator;
    static const dzn::locator& FacilitiesCheck(const dzn::locator& locator);

    // The encapsulated component "ToasterSystem"
    ::My::Project::ToasterSystem m_encapsulee;

    // Boundary provides-port (MTS) to reroute inwards events
    ::My::Project::IToaster m_ppApi;

    // Boundary requires-ports (MTS) to reroute inwards events
    ::Some::Vendor::IHeaterElement m_rpHeaterElement;
    ::My::Project::Hal::IPowerCord m_rpCord;
};
} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

CC_ALL_MTS_MIXED_TS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// This is generated code. DO NOT MODIFY manually.

// System include
#include <dzn/runtime.hh>
// Project include
#include "ToasterSystemAdvShell.hh"

namespace My::Project {

const dzn::locator& ToasterSystemAdvShell::FacilitiesCheck(const dzn::locator& locator)
{
    // This class creates the required facilities. But in case the user provided locator argument already contains some or
    // all facilities, it indicates an execution deployment error. Important: each threaded subsystem has its own exclusive
    // instances of the dispatcher and dezyne runtime facilities. They can never be shared with other threaded subsystems.

    if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping dispatcher found (dzn::pump)");
    if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping Dezyne runtime found (dzn::runtime)");

    return locator;
}

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = encapsuleeInstanceName;
    m_encapsulee.api.meta.require.name = "api";
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    m_ppApi.in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    m_ppApi.in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    m_ppApi.in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    m_ppApi.in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    m_ppApi.in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    m_ppApi.in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    m_ppApi.in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    m_rpCord.out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    m_rpCord.out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    m_ppApi.check_bindings();
    m_rpHeaterElement.check_bindings();
    m_rpCord.check_bindings();
    m_encapsulee.led.check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = m_ppApi.out;

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = m_rpHeaterElement.in;
    m_encapsulee.cord.in = m_rpCord.in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& ToasterSystemAdvShell::Locator()
{
    return m_locator;
}

::Dzn::Mts<::My::Project::IToaster> ToasterSystemAdvShell::ProvidesApi()
{
    return {m_ppApi};
}

::Dzn::Mts<::Some::Vendor::IHeaterElement> ToasterSystemAdvShell::RequiresHeaterElement()
{
    return {m_rpHeaterElement};
}

::Dzn::Mts<::My::Project::Hal::IPowerCord> ToasterSystemAdvShell::RequiresCord()
{
    return {m_rpCord};
}

::Dzn::Sts<::My::ILed> ToasterSystemAdvShell::RequiresLed()
{
    return {m_encapsulee.led};
}

} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

HH_ALL_STS_MIXED_TS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// Creator information:
//     ABC
//     DEF
//     GHI
//
// Configuration:
// - Encapsulee FQN: StoneAgeToaster
// - Source file basename: StoneAgeToaster
// - Target file basename: StoneAgeToasterImplComp
// - Dezyne facilities: Create all facilities (dispatcher, runtime and locator)
// - Port semantics: provides ports: All STS, requires ports: MTS=['heater'] STS=[<Remaining ports>]
//
// Provides ports (Single-threaded):
// - api: IToaster
//
// Requires ports (Single-threaded):
// - timer: ITimer
//
// Requires ports (Multi-threaded):
// - heater: IHeaterElement
//
// This is generated code. DO NOT MODIFY manually.

// System includes
#include <dzn/locator.hh>
#include <dzn/pump.hh>
#include <dzn/runtime.hh>
// Project includes
#include "StoneAgeToaster.hh"
#include "Dzn_StrictPort.hh"

namespace {
struct StoneAgeToasterImplComp
{
    StoneAgeToasterImplComp(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName = "");
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::Dzn::Sts<::My::Project::IToaster> ProvidesApi();

    // Requires port accessors
    ::Dzn::Mts<::Some::Vendor::IHeaterElement> RequiresHeater();
    ::Dzn::Sts<::ITimer> RequiresTimer();

private:
    // Facilities
    dzn::runtime m_runtime;
    dzn::pump m_dispatcher;
    dzn::locator m_locator;
    static const dzn::locator& FacilitiesCheck(const dzn::locator& locator);

    // The encapsulated component "StoneAgeToaster"
    ::StoneAgeToaster m_encapsulee;

    // Boundary provides-port (MTS) to reroute inwards events
    // <none>

    // Boundary requires-port (MTS) to reroute inwards events
    ::Some::Vendor::IHeaterElement m_rpHeater;
};
} // namespace
// Generated by: dznpy/adv_shell v0.5.DEV
'''

CC_ALL_STS_MIXED_TS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// This is generated code. DO NOT MODIFY manually.

// System include
#include <dzn/runtime.hh>
// Project include
#include "StoneAgeToasterImplComp.hh"

namespace {

const dzn::locator& StoneAgeToasterImplComp::FacilitiesCheck(const dzn::locator& locator)
{
    // This class creates the required facilities. But in case the user provided locator argument already contains some or
    // all facilities, it indicates an execution deployment error. Important: each threaded subsystem has its own exclusive
    // instances of the dispatcher and dezyne runtime facilities. They can never be shared with other threaded subsystems.

    if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error("StoneAgeToasterImplComp: Overlapping dispatcher found (dzn::pump)");
    if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error("StoneAgeToasterImplComp: Overlapping Dezyne runtime found (dzn::runtime)");

    return locator;
}

StoneAgeToasterImplComp::StoneAgeToasterImplComp(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_rpHeater(m_encapsulee.heater)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = encapsuleeInstanceName;
    m_encapsulee.heater.meta.provide.name = "heater";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    // <None>

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    // <None>
}

void StoneAgeToasterImplComp::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    m_encapsulee.api.check_bindings();
    m_rpHeater.check_bindings();
    m_encapsulee.timer.check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    // <none>

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heater.in = m_rpHeater.in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& StoneAgeToasterImplComp::Locator()
{
    return m_locator;
}

::Dzn::Sts<::My::Project::IToaster> StoneAgeToasterImplComp::ProvidesApi()
{
    return {m_encapsulee.api};
}

::Dzn::Mts<::Some::Vendor::IHeaterElement> StoneAgeToasterImplComp::RequiresHeater()
{
    return {m_rpHeater};
}

::Dzn::Sts<::ITimer> StoneAgeToasterImplComp::RequiresTimer()
{
    return {m_encapsulee.timer};
}

} // namespace
// Generated by: dznpy/adv_shell v0.5.DEV
'''

HH_ALL_MTS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// Creator information:
// <none>
//
// Configuration:
// - Encapsulee FQN: My.Project.ToasterSystem
// - Source file basename: ToasterSystem
// - Target file basename: ToasterSystemAdvShell
// - Dezyne facilities: Create all facilities (dispatcher, runtime and locator)
// - Port semantics: provides/requires: All MTS
//
// Provides ports (Multi-threaded):
// - api: IToaster
//
// Requires ports (Multi-threaded):
// - heaterElement: IHeaterElement
// - cord: IPowerCord
// - led: ILed
//
// This is generated code. DO NOT MODIFY manually.

// System includes
#include <dzn/locator.hh>
#include <dzn/pump.hh>
#include <dzn/runtime.hh>
// Project includes
#include "ToasterSystem.hh"
#include "Dzn_StrictPort.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName = "");
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::Dzn::Mts<::My::Project::IToaster> ProvidesApi();

    // Requires port accessors
    ::Dzn::Mts<::Some::Vendor::IHeaterElement> RequiresHeaterElement();
    ::Dzn::Mts<::My::Project::Hal::IPowerCord> RequiresCord();
    ::Dzn::Mts<::My::ILed> RequiresLed();

private:
    // Facilities
    dzn::runtime m_runtime;
    dzn::pump m_dispatcher;
    dzn::locator m_locator;
    static const dzn::locator& FacilitiesCheck(const dzn::locator& locator);

    // The encapsulated component "ToasterSystem"
    ::My::Project::ToasterSystem m_encapsulee;

    // Boundary provides-port (MTS) to reroute inwards events
    ::My::Project::IToaster m_ppApi;

    // Boundary requires-ports (MTS) to reroute inwards events
    ::Some::Vendor::IHeaterElement m_rpHeaterElement;
    ::My::Project::Hal::IPowerCord m_rpCord;
    ::My::ILed m_rpLed;
};
} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''

CC_ALL_MTS = '''\
// Copyright Example Line 1
// Copyright Example Line 2
//
// Advanced Shell
//
// This is generated code. DO NOT MODIFY manually.

// System include
#include <dzn/runtime.hh>
// Project include
#include "ToasterSystemAdvShell.hh"

namespace My::Project {

const dzn::locator& ToasterSystemAdvShell::FacilitiesCheck(const dzn::locator& locator)
{
    // This class creates the required facilities. But in case the user provided locator argument already contains some or
    // all facilities, it indicates an execution deployment error. Important: each threaded subsystem has its own exclusive
    // instances of the dispatcher and dezyne runtime facilities. They can never be shared with other threaded subsystems.

    if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping dispatcher found (dzn::pump)");
    if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error("ToasterSystemAdvShell: Overlapping Dezyne runtime found (dzn::runtime)");

    return locator;
}

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& encapsuleeInstanceName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
    , m_rpLed(m_encapsulee.led)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = encapsuleeInstanceName;
    m_encapsulee.api.meta.require.name = "api";
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";
    m_encapsulee.led.meta.provide.name = "led";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    m_ppApi.in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    m_ppApi.in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    m_ppApi.in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    m_ppApi.in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    m_ppApi.in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    m_ppApi.in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    m_ppApi.in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    m_rpCord.out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    m_rpCord.out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
    m_rpLed.out.GlitchOccurred = [&] {
        return m_dispatcher([&] { return m_encapsulee.led.out.GlitchOccurred(); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    m_ppApi.check_bindings();
    m_rpHeaterElement.check_bindings();
    m_rpCord.check_bindings();
    m_rpLed.check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = m_ppApi.out;

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = m_rpHeaterElement.in;
    m_encapsulee.cord.in = m_rpCord.in;
    m_encapsulee.led.in = m_rpLed.in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& ToasterSystemAdvShell::Locator()
{
    return m_locator;
}

::Dzn::Mts<::My::Project::IToaster> ToasterSystemAdvShell::ProvidesApi()
{
    return {m_ppApi};
}

::Dzn::Mts<::Some::Vendor::IHeaterElement> ToasterSystemAdvShell::RequiresHeaterElement()
{
    return {m_rpHeaterElement};
}

::Dzn::Mts<::My::Project::Hal::IPowerCord> ToasterSystemAdvShell::RequiresCord()
{
    return {m_rpCord};
}

::Dzn::Mts<::My::ILed> ToasterSystemAdvShell::RequiresLed()
{
    return {m_rpLed};
}

} // namespace My::Project
// Generated by: dznpy/adv_shell v0.5.DEV
'''
