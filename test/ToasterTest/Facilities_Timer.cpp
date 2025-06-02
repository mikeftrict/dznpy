#include "Facilities_Timer.hh"

namespace Facilities {

Timer::Timer(const dzn::locator& dzn_locator)
    : ::Facilities::skel::Timer(dzn_locator)
    , m_pump(dzn_locator.get<dzn::pump>())
{
}

void Timer::api_Create(size_t waitingTimeMs)
{
    m_pump.handle(reinterpret_cast<size_t>(this), waitingTimeMs, [&]() noexcept {
        api.out.Timeout();
    });
}

void Timer::api_Cancel()
{
    m_pump.remove(reinterpret_cast<size_t>(this));
}

} // namespace Facilities
