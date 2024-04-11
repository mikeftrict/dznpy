"""
Package providing generating support files that contain generic code for Dezyne C++ development.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import Tuple

# dznpy modules
from ..cpp_gen import gen_fqn
from ..misc_utils import NameSpaceIds, is_namespaceids_instance


def initialize_ns(namespace_prefix: NameSpaceIds) -> Tuple[NameSpaceIds, str]:
    """Initialize a namespace id that ends with Dzn and optionally prefixed
    with a user specified NamespaceIds. Return the result as a combo of this new
    NamespaceIds and its respective string of the C++ variant."""
    fixed_ns = ['Dzn']

    if namespace_prefix is None:
        return fixed_ns, gen_fqn(fixed_ns)
    elif is_namespaceids_instance(namespace_prefix):
        prefixed_ns = namespace_prefix + fixed_ns
        return prefixed_ns, gen_fqn(prefixed_ns)
    else:
        raise TypeError('namespace_prefix is of incorrect type')
