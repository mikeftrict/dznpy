"""
dznpy/adv_shell/types - version 0.2.240304

Python module providing simple and independent types.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
import enum


class AdvShellError(Exception):
    """An error occurred during building of an advanced shell."""


class RuntimeSemantics(enum.Enum):
    """Enum to indicate the flavor of runtime execution semantics."""
    STS = 'Single-threaded runtime semantics'
    MTS = 'Multi-threaded runtime semantics'
