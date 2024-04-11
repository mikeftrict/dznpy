"""
Module providing common definitions, classes and functions for generating (code) content.

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
from typing import List, Optional

# dznpy modules
from .misc_utils import EOL, NameSpaceIds

# constants
BLANK_LINE = EOL
TEXT_GEN_DO_NOT_MODIFY = 'This is generated code. DO NOT MODIFY manually.'


@dataclass(frozen=True)
class GeneratedContent:
    """Data class containing generated content along with a designated filename and
    an optional namespace indication."""
    filename: str
    contents: str
    namespace: Optional[NameSpaceIds] = field(default=None)


@dataclass(frozen=True)
class CodeGenResult:
    """Data class containing a list of artifacts as a result of code generation."""
    files: List[GeneratedContent]
