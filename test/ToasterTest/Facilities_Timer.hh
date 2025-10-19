#pragma once

// System include
#include <dzn/locator.hh>
#include <dzn/pump.hh>

// Project include
#include "FCTimer.hh"

namespace Facilities {

class Timer : public ::Facilities::skel::Timer
{
public:
    explicit Timer(const dzn::locator& dzn_locator);
    Timer(const Timer&) = delete;
    Timer(Timer&&) = delete;
    Timer& operator=(const Timer&) = delete;
    Timer& operator=(Timer&&) = delete;
    ~Timer() override = default;

    void api_Create(size_t waitingTimeMs) override;
    void api_Cancel() override;

private:
    dzn::pump& m_pump;
};

} // namespace Facilities
