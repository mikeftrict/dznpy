#pragma once
#include <future>
#include "gtest/gtest.h"

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
    [[nodiscard]] AssertionResult AwaitTriggerred(const std::chrono::duration<R, P>& timeout)
    {
        auto s = m_future.wait_for(timeout);
        switch (s)
        {
        case std::future_status::timeout:
            return AssertionFailure() << "Time out (" << timeout.count() << ") waiting on promise";

        case std::future_status::ready:
            Reset();
            return AssertionSuccess();
        default:
            return AssertionFailure() << "Invalid future status when waiting on promise";
        }
    }

private:
    std::promise<void> m_promise;
    std::future<void> m_future;
};

} // namespace testing
