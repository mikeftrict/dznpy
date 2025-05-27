#pragma once
// System include
#include <functional>
#include <optional>

// Project includes
#include "gmock/gmock.h"
#include "IHeaterElement.hh"

class IHeaterElementMock
{
public:
    IHeaterElementMock() {}

    void SetupPeerPort(Some::Vendor::IHeaterElement& port)
    {
        m_peerPort = port;

        port.in.Initialize = [this] {
            Initialize();
        };

        port.in.Uninitialize = [this] {
            Uninitialize();
        };

        port.in.On = [this] {
            On();
        };

        port.in.Off = [this] {
            Off();
        };

        //dzn::check_bindings(port);
    }

    // Method mocks, programmable by test
    MOCK_METHOD(void, Initialize, ());
    MOCK_METHOD(void, Uninitialize, ());
    MOCK_METHOD(void, On, ());
    MOCK_METHOD(void, Off, ());

private:
    std::optional<std::reference_wrapper<Some::Vendor::IHeaterElement>> m_peerPort;
};
