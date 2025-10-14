"""
Module providing helpers for executing dzn(.cmd) and processing its output.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import re
from dataclasses import field, dataclass
from functools import total_ordering
from typing import List


###############################################################################
# Types
#

@total_ordering
class DznVersion:
    """Class that parses the output of dzn.cmd --version and contains the version of Dezyne."""
    __slots__ = ['_major', '_minor', '_revision', '_dev_tag']

    def __init__(self, dzn_version_output: str):
        pattern = r'\b(\d+)\.(\d+)\.(\d+)(?:\.(\d+-[a-zA-Z0-9]+))?'
        match = re.search(pattern, dzn_version_output)
        if not match:
            raise TypeError(
                f'No valid version-format "x.y.z[.dev-tag]" found in string: {dzn_version_output}')
        self._major = int(match.group(1))
        self._minor = int(match.group(2))
        self._revision = int(match.group(3))
        self._dev_tag = match.group(4) if match.group(4) else None

    def __str__(self) -> str:
        if self._dev_tag is None:
            return f'{self._major}.{self._minor}.{self._revision}'

        return f'{self._major}.{self._minor}.{self._revision}.{self._dev_tag}'

    @property
    def major(self):
        """Retrieve the major number part of the dezyne version"""
        return self._major

    @property
    def minor(self):
        """Retrieve the minor number part of the dezyne version"""
        return self._minor

    @property
    def revision(self):
        """Retrieve the revision number part of the dezyne version"""
        return self._revision

    @property
    def dev_tag(self):
        """Retrieve the developer tag part of the dezyne version"""
        return self._dev_tag

    def __eq__(self, other):
        """Equality operator with a different instance of this class"""
        if not isinstance(other, DznVersion):
            raise TypeError("The 'other' instance must be of type DznVersion")
        return (self.major, self.minor, self._revision) == (
            other.major, other.minor, other._revision)

    def __lt__(self, other):
        """Less-than operator with a different instance of this class"""
        if not isinstance(other, DznVersion):
            raise TypeError("The 'other' instance must be of type DznVersion")
        return (self.major, self.minor, self._revision) < (
            other.major, other.minor, other._revision)


@dataclass(frozen=True)
class DznFileModelsList:
    """Data class storing the occurrences of model types found in a Dezyne file."""
    components: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    foreigns: List[str] = field(default_factory=list)
    systems: List[str] = field(default_factory=list)

    def is_verifiable(self) -> bool:
        """Indicate whether the file can be verified depending on the types of models inside."""
        return bool(self.components or self.interfaces)

    def is_generatable(self) -> bool:
        """Indicate whether the file can be generated depending on the types of models inside."""
        return bool(self.components or self.interfaces or self.foreigns or self.systems)

    def is_wfc_only(self) -> bool:
        """Indicate whether only a well-formedness check can be performed."""
        return bool(not self.components and not self.interfaces and (self.systems or self.foreigns))

    def __str__(self) -> str:
        return (f'Components: {", ".join(self.components)}\n'
                f'Interfaces: {", ".join(self.interfaces)}\n'
                f'Foreigns: {", ".join(self.foreigns)}\n'
                f'Systems: {", ".join(self.systems)}\n')


###############################################################################
# Type creation functions
#

def create_file_models_list(parse_l_output: str) -> DznFileModelsList:
    """List the models that are present in a Dezyne file by returning an instance of the
    type DznFileModelsList."""

    # Temporary lists to collect names
    components = []
    interfaces = []
    foreigns = []
    systems = []

    pattern = re.compile(r'(?P<name>\S+)\s+(?P<type>interface|component|foreign|system)',
                         re.MULTILINE)
    for match in pattern.finditer(parse_l_output):
        name = match.group("name")
        kind = match.group("type")
        if kind == "component":
            components.append(name)
        elif kind == "interface":
            interfaces.append(name)
        elif kind == "foreign":
            foreigns.append(name)
        elif kind == "system":
            systems.append(name)

    return DznFileModelsList(
        components=components,
        interfaces=interfaces,
        foreigns=foreigns,
        systems=systems
    )
