// System includes
#include <chrono>
#include <future>
#include <thread>

// GoogleTest/Mock includes
#include "gtest/gtest.h"
#include "gmock/gmock.h"

// Dezyne runtime includes
#include "dzn/locator.hh"
#include "dzn/runtime.hh"

// Project includes
#include "ToasterSystem.hh"

// Mock includes
#include "Mocks/IConfigurationMock.h"
#include "Mocks/IHeaterElementMock.h"
#include "Mocks/IPowerCordMock.h"
#include "Mocks/ILedMock.h"

namespace testing {

struct Signal
{
    Signal() { Reset(); }

    void Reset()
    {
        m_promise = std::promise<void>();
        m_future = m_promise.get_future();
    }

    void Trigger() { m_promise.set_value(); }

    template <class R, class P>
    [[nodiscard]] testing::AssertionResult AwaitTriggerred(const std::chrono::duration<R, P>& timeout)
    {
        auto s = m_future.wait_for(timeout);
        switch (s)
        {
        case std::future_status::timeout:
            return testing::AssertionFailure() << "Time out (" << timeout.count() << ") waiting on promise";

        case std::future_status::ready:
            Reset();
            return testing::AssertionSuccess();
        default:
            return testing::AssertionFailure() << "Invalid future status when waiting on promise";
        }
    }

private:
    std::promise<void> m_promise;
    std::future<void> m_future;
};

} // namespace testing

using namespace std::chrono_literals;
using namespace testing;

struct ToasterTest : public Test
{
    ToasterTest() {}

    void SetUp() override
    {
        // Prepare and populate Dezyne locator
        dzn_locator.set(dzn_runtime);

        // Prepare and install injectables
        dzn_locator.set(configurationMock.GetInjectablePort());

        // Build SUT
        sut = std::make_unique<My::Project::ToasterSystem>(dzn_locator);

        // Connect topside port
        sut->api.out.Ok = [this] {
            std::cout << "Received Ok()\n";
            signalOk.Trigger();
        };
        sut->api.out.Fail = [this](std::shared_ptr<ResultInfo>) {
            std::cout << "Received Fail()\n";
            signalFail.Trigger();
        };
        sut->api.out.Error = [this](std::shared_ptr<ResultInfo>) {
            std::cout << "Received Error()\n";
            signalError.Trigger();
        };

        // Connect bottomside port(s)
        heaterElementMock.SetupPeerPort(sut->heaterElement);
        powerCordMock.SetupPeerPort(sut->cord);
        ledMock.SetupPeerPort(sut->led);

        // Final checks
        sut->check_bindings();
    }

    dzn::locator dzn_locator;
    dzn::runtime dzn_runtime;

    IConfigurationMock configurationMock;
    IHeaterElementMock heaterElementMock;
    IPowerCordMock powerCordMock;
    ILedMock ledMock;

    std::unique_ptr<My::Project::ToasterSystem> sut;

    Signal signalOk;
    Signal signalFail;
    Signal signalError;
};

TEST_F(ToasterTest, Roundtrip)
{
    InSequence strict_order;

    // Prepare initialization
    EXPECT_CALL(heaterElementMock, Initialize);
    EXPECT_CALL(powerCordMock, Initialize(_));
    EXPECT_CALL(ledMock, Initialize);
    EXPECT_CALL(configurationMock, GetToastingTime).WillOnce(SetArgReferee<0>(10000)); // equals 10 seconds

    // Exercise (1)
    sut->api.in.Initialize();

    // Get and Set toasting time
    size_t previousToastingTime{};
    sut->api.in.GetTime(previousToastingTime);
    EXPECT_EQ(10 * 1000u, previousToastingTime);
    sut->api.in.SetTime(2000u); // equals 2 seconds

    // Prepare switch on and off the toaster
    EXPECT_CALL(powerCordMock, IsConnectedToOutlet).WillOnce(Return(true));
    EXPECT_CALL(heaterElementMock, On);
    EXPECT_CALL(heaterElementMock, Off);

    // Exercise (2)
    std::shared_ptr<ResultInfo> resultInfo;
    auto r = sut->api.in.Toast("My sandwich", resultInfo);
    // Uncomment next line to induce a spontaneous failure
    //powerCordMock.TriggerDisconnected(My::Project::Hal::Sub::MyLongNamedType{123});
    std::this_thread::sleep_for(3s); // Delay test for a few seconds (> 2 seconds configuration)

    // Prepare uninitialization
    EXPECT_CALL(heaterElementMock, Uninitialize);
    EXPECT_CALL(powerCordMock, Uninitialize);
    EXPECT_CALL(ledMock, Uninitialize);

    // Exercise (2)
    sut->api.in.Uninitialize();
}

TEST_F(ToasterTest, AsyncBehaviour)
{
    InSequence strict_order;

    // Prepare initialization
    EXPECT_CALL(heaterElementMock, Initialize);
    EXPECT_CALL(powerCordMock, Initialize(_));
    EXPECT_CALL(ledMock, Initialize);
    EXPECT_CALL(configurationMock, GetToastingTime).WillOnce(SetArgReferee<0>(2500)); // equals 1.5 seconds

    // Exercise (1)
    sut->api.in.Initialize();

    // Prepare switch on and off the toaster
    EXPECT_CALL(powerCordMock, IsConnectedToOutlet).WillOnce(Return(true));
    EXPECT_CALL(heaterElementMock, On);
    EXPECT_CALL(heaterElementMock, Off);

    // Exercise (2)
    std::shared_ptr<ResultInfo> resultInfo;
    auto r = sut->api.in.Toast("My sandwich", resultInfo);
    ASSERT_TRUE(signalOk.AwaitTriggerred(5s));

    // Prepare uninitialization
    EXPECT_CALL(heaterElementMock, Uninitialize);
    EXPECT_CALL(powerCordMock, Uninitialize);
    EXPECT_CALL(ledMock, Uninitialize);

    // Exercise (2)
    sut->api.in.Uninitialize();
}
