// Generated GoogleMock C++ sourcecode from JSON file: ../../test/dezyne_models/generated/IPowerCord.json
// Note: do not modify manually afterwards

#pragma once

// System includes
#include <functional>
#include <optional>
#include <sstream>

// Project includes
#include "gmock/gmock.h"
#include "IPowerCord.hh"

class IPowerCordMock
{
public:
    void SetupPeerPort(My::Project::Hal::IPowerCord& port)
    {
        m_peerPort = port;

        port.in.Initialize = [this](std::string label) {
            return Initialize(label);
        };

        port.in.Uninitialize = [this](std::shared_ptr<ResultInfo>& info) {
            return Uninitialize(info);
        };

        port.in.IsConnectedToOutlet = [this]() {
            return IsConnectedToOutlet();
        };

        port.in.GetVoltage = [this]() {
            return GetVoltage();
        };

        port.check_bindings();
    }

    // Methods for the interface out events to trigger them on behalf of the Mock object
    void TriggerConnected()
    {
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne peer port not set up");
        m_peerPort.value().get().out.Connected();
    }

    void TriggerDisconnected(My::Project::Hal::Sub::MyLongNamedType exampleParameter)
    {
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne peer port not set up");
        m_peerPort.value().get().out.Disconnected(exampleParameter);
    }

    // Method mocks, expectations programmable by test
    MOCK_METHOD(::My::Result, Initialize, (std::string label));
    MOCK_METHOD(void, Uninitialize, (std::shared_ptr<ResultInfo> & info));
    MOCK_METHOD(bool, IsConnectedToOutlet, ());
    MOCK_METHOD(int, GetVoltage, ());

private:
    std::optional<std::reference_wrapper<My::Project::Hal::IPowerCord>> m_peerPort;
};
