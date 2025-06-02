"""
Module providing C++ code generation of the support file "Mutex Wrapped".

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# pylint: disable=line-too-long

# system modules
from typing import Optional

# dznpy modules
from ..cpp_gen import SystemIncludes
from ..scoping import NamespaceIds
from ..text_gen import GeneratedContent, TextBlock

# own modules
from . import distillate_ns, SupportFileCfg, generate_cpp_code


def header_hh_template(cpp_ns: str) -> TextBlock:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return TextBlock("""\
Mutex Wrapped helper

Description: A simple concurrent thread safe wrapper to protect a shared resouce of type T.
             Locking and accessing protected data is done with the Operator() method.
             Releasing the lock can be done manually or automatically when the given lock goes
             out of scope (RAII pattern).

Tip: MutexWrap a struct containing multiple members to protect them as a whole. Considered they
     cohesively are 'atomic'. Instead of having separate locks that potentially can yield
     deadlocks when concurrent threads incrementally try to acquire them.


Example:

given """ f'{cpp_ns}' """::MutexWrapped<int> m_threadSafeNumber;

{
   auto lockAndData = m_threadSafeNumber(); // lock and access the data with Operator()
   *lockAndData = 123; // by dereferencing, change value of the protected data

   lockAndData.reset(); // release lock manually, or,
                        // let it go out of scope for automatic RAII release of the lock.
}

""")  # noqa: E501


def body_hh() -> TextBlock:
    """Generate the body of a C++ headerfile with templated fields."""
    return TextBlock("""\
template <typename T>
struct MutexWrapped
{
    // Get access to the protected data. May have to wait on a concurrent claiming thread to unlock
    // it first. When lock has been acquired, the client is given a unique_ptr to the data.
    //
    // Releasing the lock can be achieved as follows:
    // - by either explicitly resetting the unique_ptr, or,
    // - implicitly and guaranteed when the unique_ptr goes out of scope (calls RaiiLockDeleter)
    auto operator()( )
    {
        std::unique_lock lock(m_mutex);
        return std::unique_ptr<T, RaiiLockDeleter>(&m_protectee, RaiiLockDeleter{std::move(lock)});
    }

private:
    T m_protectee;      // default construct typename T
    std::mutex m_mutex; // the mutex coupled to the protectee

    struct RaiiLockDeleter // automatic mechanism to ensure releasing the lock a la RAII
    {
        std::unique_lock<std::mutex> lock;
        void operator()(T*) { if (lock.owns_lock()) lock.unlock(); }
    };
};
""")  # noqa: E501


def create_header(ns_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates the mutex wrapped helper."""

    namespace, cpp_ns, file_ns = distillate_ns(ns_prefix)

    cfg = SupportFileCfg(header=header_hh_template(cpp_ns),
                         body=body_hh(),
                         includes=TextBlock(SystemIncludes(['memory', 'mutex'])),
                         ns_prefix=ns_prefix)

    return GeneratedContent(filename=f'{file_ns}_MutexWrapped.hh',
                            contents=str(generate_cpp_code(cfg)),
                            namespace=namespace)
