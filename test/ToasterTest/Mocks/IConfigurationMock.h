#pragma once

// Project includes
#include "gmock/gmock.h"
#include "IConfiguration.hh"

class IConfigurationMock
{
public:
    // Constructor that initializes the Dezyne port at the peer-end of the Mock
    IConfigurationMock()
        : m_port{{{"api", nullptr, nullptr, nullptr}, {"", nullptr, nullptr, nullptr}}}
    {
        m_port.in.GetToastingTime = [this](size_t& toastingTime) {
            GetToastingTime(toastingTime);
        };

        //dzn::check_bindings(m_port.dzn_meta);
    }

    // Getter to retrieve the peer-end of the Mock for injection into the Dezyne locator
    IConfiguration& GetInjectablePort() { return m_port; }

    // Method mocks, programmable by test
    MOCK_METHOD(void, GetToastingTime, (size_t& toastingTime));

private:
    IConfiguration m_port;
};
