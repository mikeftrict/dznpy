#pragma once
// System include
#include <functional>
#include <optional>

// Project includes
#include "gmock/gmock.h"
#include "ILed.hh"


struct InlineStr
{
    template <typename T>
    InlineStr& operator<<(const T& t)
    {
        strStream << t;
        return *this;
    }
    auto str() const { return strStream.str(); }
    operator std::string() const { return str(); }

private:
    std::stringstream strStream;
};

class ILedMock
{
public:
    ILedMock(std::function<void(const std::string& msg)> traceFn =
             [](auto& msg) {
                 std::cout << msg << std::endl;
             })
        : m_traceFn(traceFn)
    {
    }

    void SetupPeerPort(My::ILed& port)
    {
        m_peerPort = port;

        port.in.Initialize = [this] {
            m_traceFn("ILedMock::Initialize() ->");
            Initialize();
            m_traceFn("ILedMock::Initialize() <-");
        };

        port.in.Uninitialize = [this] {
            m_traceFn("ILedMock::Uninitialize() ->");
            Uninitialize();
            m_traceFn("ILedMock::Uninitialize() <-");
        };

        //dzn::check_bindings(port);
    }

    // Method mocks, programmable by test
    MOCK_METHOD(void, Initialize, ());
    MOCK_METHOD(void, Uninitialize, ());

    auto& PortOut()
    {
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne peer port not set up");
        return m_peerPort.value().get().out;
    }

private:
    std::function<void(const std::string& msg)> m_traceFn;
    std::optional<std::reference_wrapper<My::ILed>> m_peerPort;
};
