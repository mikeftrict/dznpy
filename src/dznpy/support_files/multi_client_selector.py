"""
Module providing C++ code generation of the support file "Multi client selector".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import Optional

# dznpy modules
from ..dznpy_version import COPYRIGHT
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import CommentBlock, ProjectIncludes, SystemIncludes, Namespace
from ..scoping import NamespaceIds
from ..text_gen import TextBlock

# own modules
from . import initialize_ns, create_footer


def header_hh_template() -> str:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return """\
Multi Client Selector

Description: A templated struct that is used in close collaboration with Advanced Shell to
             implement multi client behaviour where one client at the time has access to
             an arbitraged/exclusive port, especially for its out events.

Example: Refer to Advanced Shell examples with a MultiClient port configuration.

"""


def body_hh() -> str:
    """Generate the body of a C++ headerfile with templated fields."""
    return """\
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
"""


def create_header(namespace_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    ns, _, file_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh_template(),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    system_includes = SystemIncludes(['optional', 'functional', 'string', 'vector'])
    project_includes = ProjectIncludes([f'{file_ns}_{x}.hh' for x in ['ILog',
                                                                      'MiscUtils',
                                                                      'MetaHelpers',
                                                                      'MutexWrapped']])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{file_ns}_MultiClientSelector.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    system_includes,
                                                    BLANK_LINE,
                                                    project_includes,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
