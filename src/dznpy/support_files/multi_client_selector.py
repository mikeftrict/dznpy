"""
Module providing C++ code generation of the support file "Multi client selector".

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# pylint: disable=line-too-long

# system modules
from typing import Optional

# dznpy modules
from ..cpp_gen import SystemIncludes, ProjectIncludes
from ..scoping import NamespaceIds
from ..text_gen import chunk, GeneratedContent, TextBlock

# own modules
from . import distillate_ns, SupportFileCfg, generate_cpp_code


def header_hh() -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Multi Client Selector

Description: A templated struct that is used in close collaboration with Advanced Shell to
             implement multi client behaviour where one client at the time has access to
             an arbitraged/exclusive port, especially for its out events.

Example: Refer to Advanced Shell examples with a MultiClient port configuration.

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
// Types
using ClientIdentifier = std::string;

template <typename DZN_PORT>
struct MultiClientSelector final
{
    ///////////////////////////////////////////////////////////////////////////
    // Type definitions:
    //

    // Record containing the client identification and an own designated port.
    struct ClientPort
    {
        ClientIdentifier identifier;
        DZN_PORT dznPort;
    };

    // Reference to the current selected client (holding the claim).
    // A value of std::nullopt means no client has been selected.
    using ClientSelect = std::optional<std::reference_wrapper<ClientPort>>;

    // Function type of the callback
    using CallbackInitializePort = std::function<DZN_PORT(const ClientIdentifier&)>;


    ///////////////////////////////////////////////////////////////////////////
    // Construction methods:
    //

    MultiClientSelector(const ILog& log, const std::string& portName, const CallbackInitializePort& cbInitializePort)
        : m_log(portName, log)
        , m_cbInitializePort(cbInitializePort)
        , m_arbiteredPort(CreatePort<DZN_PORT>("arbiter" + CapitalizeFirstChar(portName), "arbitraged" + CapitalizeFirstChar(portName)))
    {
    }

    DZN_PORT& operator()()
    {
        if (m_finalConstructed) throw std::runtime_error("Can not grant write access to arbitered port when final constructed.");
        return m_arbiteredPort;
    }

    void FinalConstruct()
    {
        if (m_finalConstructed) throw std::runtime_error("Already final constructed.");

        for (const auto& [_, client] : m_clients) client.dznPort.check_bindings();

        m_log.check_bindings();
        m_finalConstructed = true;
    }

    // Access a ClientPort indexed by a ClientIdentifier specification. Allocate the ClientPort if not present.
    // This method is called to register each client until the builder process concludes with FinalConstruct().
    ClientPort& Index(const ClientIdentifier& identifier)
    {
        ILogWithContext log("Index", m_log);
        log.Info(identifier);

        if (identifier.empty()) throw std::runtime_error("Argument 'identifier' must not be empty.");

        if (m_clients.count(identifier) == 0)
        {
            log.Info("Allocating ClientPort entry for " + identifier);
            if (m_finalConstructed) throw std::runtime_error("Can not allocate a ClientPort entry when final constructed.");

            m_clients.insert_or_assign(identifier, ClientPort{identifier, m_cbInitializePort(identifier)});
        }

        return m_clients.at(identifier);
    }

    // Get a vector of all currently registered ClientIdentifiers
    auto GetClientIdentifiers() const
    {
        std::vector<ClientIdentifier> result;
        for (auto& kv : m_clients) result.push_back(kv.first);

        return result;
    }


    ///////////////////////////////////////////////////////////////////////////
    // Operational methods:
    //

    const DZN_PORT& Arbitered() { return m_arbiteredPort; } // grant read-only access

    auto CurrentClient() { return m_clientSelect(); } // acquire 'lock-and-data' on the current ClientSelect value

    void Select(const ClientIdentifier& identifier)
    {
        ILogWithContext log("Select", m_log);
        log.Info(identifier);

        if (m_clients.count(identifier) == 0) return log.Error("Identifier " + identifier + " not recognised as a valid registered client.");

        auto lockAndData = CurrentClient();
        auto& clientSelect = *lockAndData;
        if (clientSelect.has_value())
        {
            auto incompliantClient = clientSelect.value().get().identifier;
            log.Warning("Preceeding client " + incompliantClient + " did not release the claim -> overruling it.");
        }

        // Switch to the new client
        clientSelect = m_clients.at(identifier);
    }

    void Deselect(const ClientIdentifier& identifier)
    {
        ILogWithContext log("Deselect", m_log);
        log.Info(identifier);

        if (m_clients.count(identifier) == 0) return log.Error("Identifier " + identifier + " does not exist.");

        auto lockAndData = CurrentClient();
        auto& clientSelect = *lockAndData;
        if (!clientSelect.has_value()) log.Warning("Unexpected, claim already released.");

        // Let go of the client
        clientSelect.reset();
    }

private:
    const ILogWithContext m_log;
    const std::function<DZN_PORT(const ClientIdentifier&)> m_cbInitializePort;
    DZN_PORT m_arbiteredPort;

    bool m_finalConstructed{false};
    std::map<ClientIdentifier, ClientPort> m_clients;
    MutexWrapped<ClientSelect> m_clientSelect;
};
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates the multi client out-event selector."""

    namespace, _, file_ns = distillate_ns(ns_prefix)

    system_includes = SystemIncludes(['optional', 'functional', 'string', 'vector'])
    project_includes = ProjectIncludes([f'{file_ns}_{x}.hh' for x in ['ILog',
                                                                      'MiscUtils',
                                                                      'MetaHelpers',
                                                                      'MutexWrapped']])

    cfg = SupportFileCfg(header=header_hh(),
                         body=body_hh(),
                         includes=TextBlock([chunk(system_includes), project_includes]),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_MultiClientSelector.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
