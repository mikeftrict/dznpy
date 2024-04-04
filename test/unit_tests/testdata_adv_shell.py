"""
Data for testing the adv_shell module - version 0.1.240108

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

DEZYNE_FILE1 = 'dezyne_models/generated/ToasterSystem.json'
DEZYNE_FILE2 = 'dezyne_models/generated/StoneAgeToaster.json'

PORTCFG_STR_ALL_MTS = 'provides/requires: All MTS'

PORTCFG_STR_ALL_STS_ALL_MTS = 'provides ports: All STS, requires ports: All MTS'

PORTCFG_STR_ALL_MTS_ALL_STS = 'provides ports: All MTS, requires ports: All STS'

PORTCFG_STR_ALL_STS_MIXED_TS1 = "provides ports: All STS, requires ports: STS=['sts_glue'] " \
                                "MTS=['mts_glue']"

PORTCFG_STR_ALL_STS_MIXED_TS2 = "provides ports: All STS, requires ports: STS=['sts_glue'] " \
                                "MTS=[<Remaining ports>]"

PORTCFG_STR_ALL_MTS_MIXED_TS1 = "provides ports: All MTS, requires ports: MTS=['mts_glue'] " \
                                "STS=[<Remaining ports>]"

PORTCFG_STR_ALL_MTS_MIXED_TS2 = "provides ports: All MTS, requires ports: STS=['sts_glue'] " \
                                "MTS=['mts_glue']"

COPYRIGHT = '''\
Copyright (c) 2023 by Company
All rights reserved.
'''

CREATOR_INFO = '''\
ABC
DEF
GHI
'''

HH_ALL_STS_ALL_MTS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.
//
// Creator information:
// <none>
//
// Configuration:
// - Encapsulee FQN: My.Project.ToasterSystem
// - Source file basename: ToasterSystem
// - Target file basename: ToasterSystemAdvShell
// - Dezyne facilities: Import facilities (by reference) from the user provides dzn::locator argument
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

#include <dzn/pump.hh>
#include "ToasterSystem.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& locator, const std::string& shellName);
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    // <none>

    // Provides port accessor
    ::My::Project::IToaster& ProvidesApi();

    // Requires port accessors
    ::Some::Vendor::IHeaterElement& RequiresHeaterElement();
    ::My::Project::Hal::IPowerCord& RequiresCord();
    ::My::ILed& RequiresLed();

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
// Version: adv_shell.py v0.1.240108
'''

CC_ALL_STS_ALL_MTS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.

#include "ToasterSystemAdvShell.hh"

namespace My::Project {

const dzn::locator& ToasterSystemAdvShell::FacilitiesCheck(const dzn::locator& locator)
{
    // This class imports the requires facilities that must be provided by the user via the locator argument.

    if (locator.try_get<dzn::pump>() == nullptr) throw std::runtime_error("ToasterSystemAdvShell: Dispatcher missing (dzn::pump)");
    if (locator.try_get<dzn::runtime>() == nullptr) throw std::runtime_error("ToasterSystemAdvShell: Dezyne runtime missing (dzn::runtime)");

    return locator;
}

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& locator, const std::string& shellName)
    : m_dispatcher(FacilitiesCheck(locator).get<dzn::pump>())
    , m_encapsulee(locator)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
    , m_rpLed(m_encapsulee.led)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = shellName;
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";
    m_encapsulee.led.meta.provide.name = "led";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    // <None>

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    RequiresCord().out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    RequiresCord().out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
    RequiresLed().out.GlitchOccurred = [&] {
        return m_dispatcher([&] { return m_encapsulee.led.out.GlitchOccurred(); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    ProvidesApi().check_bindings();
    RequiresHeaterElement().check_bindings();
    RequiresCord().check_bindings();
    RequiresLed().check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    // <none>

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = RequiresHeaterElement().in;
    m_encapsulee.cord.in = RequiresCord().in;
    m_encapsulee.led.in = RequiresLed().in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}


::My::Project::IToaster& ToasterSystemAdvShell::ProvidesApi()
{
    return m_encapsulee.api;
}

::Some::Vendor::IHeaterElement& ToasterSystemAdvShell::RequiresHeaterElement()
{
    return m_rpHeaterElement;
}

::My::Project::Hal::IPowerCord& ToasterSystemAdvShell::RequiresCord()
{
    return m_rpCord;
}

::My::ILed& ToasterSystemAdvShell::RequiresLed()
{
    return m_rpLed;
}

} // namespace My::Project
// Version: adv_shell.py v0.1.240108
'''

HH_ALL_MTS_ALL_STS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.
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

#include <dzn/pump.hh>
#include "ToasterSystem.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName);
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::My::Project::IToaster& ProvidesApi();

    // Requires port accessors
    ::Some::Vendor::IHeaterElement& RequiresHeaterElement();
    ::My::Project::Hal::IPowerCord& RequiresCord();
    ::My::ILed& RequiresLed();

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
// Version: adv_shell.py v0.1.240108
'''

CC_ALL_MTS_ALL_STS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.

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

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = shellName;
    m_encapsulee.api.meta.require.name = "api";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    ProvidesApi().in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    ProvidesApi().in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    ProvidesApi().in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    ProvidesApi().in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    ProvidesApi().in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    ProvidesApi().in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    ProvidesApi().in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    // <None>
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    ProvidesApi().check_bindings();
    RequiresHeaterElement().check_bindings();
    RequiresCord().check_bindings();
    RequiresLed().check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = ProvidesApi().out;

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

::My::Project::IToaster& ToasterSystemAdvShell::ProvidesApi()
{
    return m_ppApi;
}

::Some::Vendor::IHeaterElement& ToasterSystemAdvShell::RequiresHeaterElement()
{
    return m_encapsulee.heaterElement;
}

::My::Project::Hal::IPowerCord& ToasterSystemAdvShell::RequiresCord()
{
    return m_encapsulee.cord;
}

::My::ILed& ToasterSystemAdvShell::RequiresLed()
{
    return m_encapsulee.led;
}

} // namespace My::Project
// Version: adv_shell.py v0.1.240108
'''

HH_ALL_MTS_MIXED_TS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.
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

#include <dzn/pump.hh>
#include "ToasterSystem.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName);
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::My::Project::IToaster& ProvidesApi();

    // Requires port accessors
    ::Some::Vendor::IHeaterElement& RequiresHeaterElement();
    ::My::Project::Hal::IPowerCord& RequiresCord();
    ::My::ILed& RequiresLed();

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
// Version: adv_shell.py v0.1.240108
'''

CC_ALL_MTS_MIXED_TS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.

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

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = shellName;
    m_encapsulee.api.meta.require.name = "api";
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    ProvidesApi().in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    ProvidesApi().in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    ProvidesApi().in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    ProvidesApi().in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    ProvidesApi().in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    ProvidesApi().in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    ProvidesApi().in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    RequiresCord().out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    RequiresCord().out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    ProvidesApi().check_bindings();
    RequiresHeaterElement().check_bindings();
    RequiresCord().check_bindings();
    RequiresLed().check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = ProvidesApi().out;

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = RequiresHeaterElement().in;
    m_encapsulee.cord.in = RequiresCord().in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& ToasterSystemAdvShell::Locator()
{
    return m_locator;
}

::My::Project::IToaster& ToasterSystemAdvShell::ProvidesApi()
{
    return m_ppApi;
}

::Some::Vendor::IHeaterElement& ToasterSystemAdvShell::RequiresHeaterElement()
{
    return m_rpHeaterElement;
}

::My::Project::Hal::IPowerCord& ToasterSystemAdvShell::RequiresCord()
{
    return m_rpCord;
}

::My::ILed& ToasterSystemAdvShell::RequiresLed()
{
    return m_encapsulee.led;
}

} // namespace My::Project
// Version: adv_shell.py v0.1.240108
'''

HH_ALL_STS_MIXED_TS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.
//
// Creator information:
//     ABC
//     DEF
//     GHI
//
// Configuration:
// - Encapsulee FQN: StoneAgeToaster
// - Source file basename: StoneAgeToaster
// - Target file basename: StoneAgeToasterSpecial
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

#include <dzn/pump.hh>
#include "StoneAgeToaster.hh"

namespace {
struct StoneAgeToasterSpecial
{
    StoneAgeToasterSpecial(const dzn::locator& prototypeLocator, const std::string& shellName);
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::My::Project::IToaster& ProvidesApi();

    // Requires port accessors
    ::Some::Vendor::IHeaterElement& RequiresHeater();
    ::ITimer& RequiresTimer();

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
// Version: adv_shell.py v0.1.240108
'''

CC_ALL_STS_MIXED_TS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.

#include "StoneAgeToasterSpecial.hh"

namespace {

const dzn::locator& StoneAgeToasterSpecial::FacilitiesCheck(const dzn::locator& locator)
{
    // This class creates the required facilities. But in case the user provided locator argument already contains some or
    // all facilities, it indicates an execution deployment error. Important: each threaded subsystem has its own exclusive
    // instances of the dispatcher and dezyne runtime facilities. They can never be shared with other threaded subsystems.

    if (locator.try_get<dzn::pump>() != nullptr) throw std::runtime_error("StoneAgeToasterSpecial: Overlapping dispatcher found (dzn::pump)");
    if (locator.try_get<dzn::runtime>() != nullptr) throw std::runtime_error("StoneAgeToasterSpecial: Overlapping Dezyne runtime found (dzn::runtime)");

    return locator;
}

StoneAgeToasterSpecial::StoneAgeToasterSpecial(const dzn::locator& prototypeLocator, const std::string& shellName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_rpHeater(m_encapsulee.heater)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = shellName;
    m_encapsulee.heater.meta.provide.name = "heater";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    // <None>

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    // <None>
}

void StoneAgeToasterSpecial::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    ProvidesApi().check_bindings();
    RequiresHeater().check_bindings();
    RequiresTimer().check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    // <none>

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heater.in = RequiresHeater().in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& StoneAgeToasterSpecial::Locator()
{
    return m_locator;
}

::My::Project::IToaster& StoneAgeToasterSpecial::ProvidesApi()
{
    return m_encapsulee.api;
}

::Some::Vendor::IHeaterElement& StoneAgeToasterSpecial::RequiresHeater()
{
    return m_rpHeater;
}

::ITimer& StoneAgeToasterSpecial::RequiresTimer()
{
    return m_encapsulee.timer;
}

} // namespace
// Version: adv_shell.py v0.1.240108
'''

HH_ALL_MTS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.
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

#include <dzn/pump.hh>
#include "ToasterSystem.hh"

namespace My::Project {
struct ToasterSystemAdvShell
{
    ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName);
    void FinalConstruct(const dzn::meta* parentComponentMeta = nullptr);

    // Facility accessor
    dzn::locator& Locator();

    // Provides port accessor
    ::My::Project::IToaster& ProvidesApi();

    // Requires port accessors
    ::Some::Vendor::IHeaterElement& RequiresHeaterElement();
    ::My::Project::Hal::IPowerCord& RequiresCord();
    ::My::ILed& RequiresLed();

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
// Version: adv_shell.py v0.1.240108
'''

CC_ALL_MTS = '''\
// Copyright (c) 2023 by Company
// All rights reserved.
//
// This is generated code. DO NOT MODIFY manually.

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

ToasterSystemAdvShell::ToasterSystemAdvShell(const dzn::locator& prototypeLocator, const std::string& shellName)
    : m_locator(std::move(FacilitiesCheck(prototypeLocator).clone().set(m_runtime).set(m_dispatcher)))
    , m_encapsulee(m_locator)
    , m_ppApi(m_encapsulee.api)
    , m_rpHeaterElement(m_encapsulee.heaterElement)
    , m_rpCord(m_encapsulee.cord)
    , m_rpLed(m_encapsulee.led)
{
    // Complete the component meta info of the encapsulee and its ports that are configured for MTS
    m_encapsulee.dzn_meta.name = shellName;
    m_encapsulee.api.meta.require.name = "api";
    m_encapsulee.heaterElement.meta.provide.name = "heaterElement";
    m_encapsulee.cord.meta.provide.name = "cord";
    m_encapsulee.led.meta.provide.name = "led";

    // Reroute in-events of boundary provides ports (MTS) via the dispatcher
    ProvidesApi().in.Initialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Initialize(); });
    };
    ProvidesApi().in.Uninitialize = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Uninitialize(); });
    };
    ProvidesApi().in.SetTime = [&](size_t toastingTime) {
        return dzn::shell(m_dispatcher, [&, toastingTime] { return m_encapsulee.api.in.SetTime(toastingTime); });
    };
    ProvidesApi().in.GetTime = [&](size_t& toastingTime) {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.GetTime(toastingTime); });
    };
    ProvidesApi().in.Toast = [&](std::string motd, PResultInfo& info) {
        return dzn::shell(m_dispatcher, [&, motd] { return m_encapsulee.api.in.Toast(motd, info); });
    };
    ProvidesApi().in.Cancel = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Cancel(); });
    };
    ProvidesApi().in.Recover = [&] {
        return dzn::shell(m_dispatcher, [&] { return m_encapsulee.api.in.Recover(); });
    };

    // Reroute out-events of boundary requires ports (MTS) via the dispatcher
    RequiresCord().out.Connected = [&] {
        return m_dispatcher([&] { return m_encapsulee.cord.out.Connected(); });
    };
    RequiresCord().out.Disconnected = [&](Sub::MyLongNamedType exampleParameter) {
        return m_dispatcher([&, exampleParameter] { return m_encapsulee.cord.out.Disconnected(exampleParameter); });
    };
    RequiresLed().out.GlitchOccurred = [&] {
        return m_dispatcher([&] { return m_encapsulee.led.out.GlitchOccurred(); });
    };
}

void ToasterSystemAdvShell::FinalConstruct(const dzn::meta* parentComponentMeta)
{
    // Check the bindings of all boundary ports
    ProvidesApi().check_bindings();
    RequiresHeaterElement().check_bindings();
    RequiresCord().check_bindings();
    RequiresLed().check_bindings();

    // Copy the out-functors of the boundary provides-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.api.out = ProvidesApi().out;

    // Copy the in-functors of the boundary requires-ports (MTS) to the respective ports of the encapsulated component
    m_encapsulee.heaterElement.in = RequiresHeaterElement().in;
    m_encapsulee.cord.in = RequiresCord().in;
    m_encapsulee.led.in = RequiresLed().in;

    // Complete the encapsulated component meta information and check the bindings of all encapsulee ports
    m_encapsulee.dzn_meta.parent = parentComponentMeta;
    m_encapsulee.check_bindings();
}

dzn::locator& ToasterSystemAdvShell::Locator()
{
    return m_locator;
}

::My::Project::IToaster& ToasterSystemAdvShell::ProvidesApi()
{
    return m_ppApi;
}

::Some::Vendor::IHeaterElement& ToasterSystemAdvShell::RequiresHeaterElement()
{
    return m_rpHeaterElement;
}

::My::Project::Hal::IPowerCord& ToasterSystemAdvShell::RequiresCord()
{
    return m_rpCord;
}

::My::ILed& ToasterSystemAdvShell::RequiresLed()
{
    return m_rpLed;
}

} // namespace My::Project
// Version: adv_shell.py v0.1.240108
'''
