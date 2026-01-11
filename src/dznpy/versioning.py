"""
Module providing constants and types for versioning dznpy and Dezyne

Copyright (c) 2023-2026 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import re
from functools import total_ordering

DZNPY_COPYRIGHT = '''\
Copyright (c) 2023-2026 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
'''

DZNPY_VERSION = '1.3.260111'


###############################################################################
# Types
#


@total_ordering
class DznVersion:
    """Class that parses the output of dzn.cmd --version and contains the version of Dezyne.
    It offers dunder methods to compare two instances of DznVersion in terms of major, minor and
    revision numbers."""
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
