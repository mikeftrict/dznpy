"""
Module providing common definitions, classes and functions for generating (code) content.

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional

# dznpy modules
from .misc_utils import EOL, assert_t_optional
from .scoping import NamespaceIds

# constants
BLANK_LINE = EOL
TEXT_GEN_DO_NOT_MODIFY = 'This is generated code. DO NOT MODIFY manually.'


@dataclass()
class GeneratedContent:
    """Data class containing generated content, its md5 hash, a designated filename and
    an optional namespace indication."""
    filename: str
    contents: str
    namespace: Optional[NamespaceIds] = field(default=None)

    def __post_init__(self):
        self._contents_hash = hashlib.md5(self.contents.encode('utf-8')).hexdigest().lower()
        assert_t_optional(self.namespace, NamespaceIds)

    @property
    def contents_hash(self):
        """Get the md5 hash of the contents."""
        return self._contents_hash


@dataclass(frozen=True)
class CodeGenResult:
    """Data class containing a list of artifacts as a result of code generation."""
    files: List[GeneratedContent]
