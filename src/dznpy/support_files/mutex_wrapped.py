"""
Module providing C++ code generation of the support file "Mutex Wrapped".

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import Optional

# dznpy modules
from ..dznpy_version import COPYRIGHT
from ..code_gen_common import GeneratedContent, BLANK_LINE, TEXT_GEN_DO_NOT_MODIFY
from ..cpp_gen import CommentBlock, SystemIncludes, Namespace
from ..misc_utils import TextBlock
from ..scoping import NamespaceIds

# own modules
from . import initialize_ns, create_footer


def header_hh_template(cpp_ns: str) -> str:
    """Generate the headerpart (a comment block) of a C++ headerfile with templated fields."""
    return """\
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

"""


def body_hh() -> str:
    """Generate the body of a C++ headerfile with templated fields."""
    return """\
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
"""


def create_header(namespace_prefix: Optional[NamespaceIds] = None) -> GeneratedContent:
    """Create the c++ header file contents that facilitates strict port typing."""

    ns, cpp_ns, file_ns = initialize_ns(namespace_prefix)
    header = CommentBlock([header_hh_template(cpp_ns),
                           BLANK_LINE,
                           TEXT_GEN_DO_NOT_MODIFY,
                           BLANK_LINE,
                           COPYRIGHT
                           ])
    includes = SystemIncludes(['memory', 'mutex'])
    body = Namespace(ns, contents=TextBlock([BLANK_LINE, body_hh(), BLANK_LINE]))

    return GeneratedContent(filename=f'{file_ns}_MutexWrapped.hh',
                            contents=str(TextBlock([header,
                                                    BLANK_LINE,
                                                    includes,
                                                    BLANK_LINE,
                                                    body,
                                                    create_footer()])),
                            namespace=ns)
