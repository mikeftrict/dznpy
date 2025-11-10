"""
Module providing helpers for executing dzn(.cmd) and processing its output.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import re
from dataclasses import field, dataclass
from typing import List


###############################################################################
# Types
#


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
        """Indicate that Dezyne can always be asked to generate code for every Dzn file."""
        return True

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
