"""
Module containing classes for selecting ports and their runtime semantics of Dezyne systems
and components.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
import enum
from typing import Dict, Set

# dznpy modules
from ..misc_utils import assert_t, is_strset_instance

# own modules
from .types import AdvShellError, RuntimeSemantics, MultiClientCfgError
from ..scoping import NamespaceIds
from ..text_gen import TextBlock


class PortWildcard(enum.Enum):
    """Enum to indicate how events passing the port are treated."""
    REMAINING = 'Remaining ports'
    ALL = 'All ports'
    NONE = 'None of the ports'


@dataclass(frozen=True)
class PortSelect:
    """Port selection with a wildcard or explicitly named."""
    value: PortWildcard or Set[str]

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if is_strset_instance(self.value):
            if not self.value:
                raise AdvShellError('strset must not be empty')
            if '' in self.value:
                raise AdvShellError('strset must not contain an empty string')
        elif not isinstance(self.value, PortWildcard):
            raise TypeError('wrong type assigned')

    def tryget_strset(self) -> Set[str]:
        """Try to get the actual value as strset. An empty set is returned otherwise."""
        return self.value if is_strset_instance(self.value) else set()

    def is_wildcard_all(self) -> bool:
        """Check whether the port selection equals the wildcard 'ALL'."""
        return isinstance(self.value, PortWildcard) and self.value == PortWildcard.ALL

    def is_not_empty(self) -> bool:
        """Check whether the port selection is not empty, meaning it either has a strset
        with contents or the wildcard equals something else than 'NONE'."""
        return is_strset_instance(self.value) or \
            isinstance(self.value, PortWildcard) and self.value != PortWildcard.NONE

    def match_strset(self, port_name: str) -> bool:
        """Attempt to find and match the specified port_name, when value is a strset."""
        self._check_port_name(port_name)
        return is_strset_instance(self.value) and port_name in self.value

    def match_wildcard(self, port_name: str) -> bool:
        """Attempt to find and match the specified port_name, when value is a wildcard."""
        self._check_port_name(port_name)
        return isinstance(self.value, PortWildcard) and self.value != PortWildcard.NONE

    @staticmethod
    def _check_port_name(port_name: str):
        """Assert check that the specified port name argument is correct."""
        if not isinstance(port_name, str):
            raise TypeError("argument port_name type must be a string")
        if not port_name:
            raise TypeError("argument port_name must not be empty")


@dataclass(frozen=True)
class PortsSemanticsCfg:
    """Data class that assigns single-threaded or multi-threaded runtime semantics to
    selected ports."""
    sts: PortSelect
    mts: PortSelect

    def __str__(self):
        if self.mts.is_wildcard_all():
            return 'All MTS'
        if self.sts.is_wildcard_all():
            return 'All STS'

        sts_explicit_ports = self.sts.tryget_strset()
        mts_explicit_ports = self.mts.tryget_strset()

        explicit_ports = []

        if sts_explicit_ports:
            explicit_ports.append(f'STS={list(sts_explicit_ports)}')

        if mts_explicit_ports:
            explicit_ports.append(f'MTS={list(mts_explicit_ports)}')

        if self.sts.value == PortWildcard.REMAINING:
            explicit_ports.append('STS=[<Remaining ports>]')

        if self.mts.value == PortWildcard.REMAINING:
            explicit_ports.append('MTS=[<Remaining ports>]')

        return ' '.join(explicit_ports)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if self.sts == self.mts:
            raise AdvShellError('properties sts and mts can not have equal contents')

        if [x for x in self.sts.tryget_strset() if x in self.mts.tryget_strset()]:
            raise AdvShellError('properties sts and mts can not overlap')

        if (self.sts.is_wildcard_all() and self.mts.is_not_empty()) or \
                (self.sts.is_not_empty() and self.mts.is_wildcard_all()):
            raise AdvShellError('properties sts and mts can not overlap')

    def match(self, expected_ports: Set[str], label: str) -> Dict[str, RuntimeSemantics]:
        """Match the specified expected ports to be matched in either sts or mts PortSelects."""
        all_explicitly_configured = self.sts.tryget_strset() | self.mts.tryget_strset()
        unmatched = all_explicitly_configured - expected_ports
        if unmatched:
            raise AdvShellError(f'Configured {label} ports {sorted(unmatched)} not matched')

        result: Dict[str, RuntimeSemantics] = {}
        for port in expected_ports:
            # first match the port explicitly in the strsets, or secondly in the wildcards
            if self.sts.match_strset(port):
                result[port] = RuntimeSemantics.STS
            elif self.mts.match_strset(port):
                result[port] = RuntimeSemantics.MTS
            elif self.sts.match_wildcard(port):
                result[port] = RuntimeSemantics.STS
            elif self.mts.match_wildcard(port):
                result[port] = RuntimeSemantics.MTS

        return result


@dataclass(frozen=True)
class MatchedPorts:
    """Data class holding the result of a PortsCfg match with the actual Encapsulee ports."""
    value: Dict[str, RuntimeSemantics]


@dataclass(frozen=True)
class MultiClientPortCfg:
    """A class to store, the user specified configuration for multi-client out-event selector."""
    port_name: str
    claim_event_name: str
    claim_granting_reply_value: NamespaceIds
    release_event_name: str

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        assert_t(self.port_name, str)
        assert_t(self.claim_event_name, str)
        assert_t(self.claim_granting_reply_value, NamespaceIds)
        assert_t(self.release_event_name, str)

        if not self.port_name:
            raise MultiClientCfgError('setting "port_name" must not be empty')
        if not self.claim_event_name:
            raise MultiClientCfgError('setting "claim_event_name" must not be empty')
        if not self.claim_granting_reply_value.items:
            raise MultiClientCfgError('setting "claim_granting_reply_value" must not be empty')
        if not self.release_event_name:
            raise MultiClientCfgError('setting "release_event_name" must not be empty')

    def __str__(self):
        """Stringify the dataclass items as a human friendly readable textblock."""
        return f'Out-event ClientSelector port "{self.port_name}" ' \
               f'(Claim event "{self.claim_event_name}" with ' \
               f'granting reply value "{self.claim_granting_reply_value}", ' \
               f'Release event "{self.release_event_name}")'


@dataclass(frozen=True)
class PortsCfg:
    """Data class containing the configuration of the ports and their semantics."""
    provides: PortsSemanticsCfg
    requires: PortsSemanticsCfg
    multiclient: MultiClientPortCfg = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
        if self.provides.sts.is_not_empty() and self.provides.mts.is_not_empty():
            raise AdvShellError('Mixed STS/MTS provides ports are currently not supported')

    def __str__(self):
        """Stringify the dataclass items as a human friendly readable textblock."""
        items = []

        if self.provides == self.requires:
            items.append(f'> provides/requires: {self.provides}')
        else:
            items.append(f'> provides ports: {self.provides}')
            items.append(f'> requires ports: {self.requires}')

        if self.multiclient:
            items.append(f'> multiclient: {self.multiclient}')

        return str(TextBlock(items))

    def match(self, provides_ports: Set[str], requires_ports: Set[str]) -> MatchedPorts:
        """Match the specified port names in the current onfiguration."""
        result = self.provides.match(provides_ports, 'provides')
        result.update(self.requires.match(requires_ports, 'requires'))
        return MatchedPorts(result)
