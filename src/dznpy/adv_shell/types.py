"""
Module providing simple and independent types.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import enum


class AdvShellError(Exception):
    """An error occurred during building of an advanced shell."""


class MultiClientCfgError(AdvShellError):
    """A user error has been detected in the Multi-client port configuration."""


class RuntimeSemantics(enum.Enum):
    """Enum to indicate the flavor of runtime execution semantics."""
    STS = 'Single-threaded runtime semantics'
    MTS = 'Multi-threaded runtime semantics'
