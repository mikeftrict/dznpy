"""
Module providing common definitions, classes and functions for generating (code) content.

Copyright (c) 2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Any

# dznpy modules
from .misc_utils import EOL, assert_t_optional, flatten_to_strlist, TextBlock
from .scoping import NamespaceIds

# constants
BLANK_LINE = EOL
TEXT_GEN_DO_NOT_MODIFY = 'This is generated code. DO NOT MODIFY manually.'


def chunk(content: Any, appendix: Any = BLANK_LINE) -> Optional[TextBlock]:
    """Pour the stringifiable contents into a textblock as a chunk with an "appendix"
    (which is a blank line by default, that can be customized)."""
    true_contents = flatten_to_strlist(content)
    true_appendix = flatten_to_strlist(appendix)
    return TextBlock([content, true_appendix]) if true_contents else None


def cond_chunk(preamble: Any, content: Any, empty_response: Any, appendix: Any = BLANK_LINE,
               all_or_nothing: bool = False) -> Optional[TextBlock]:
    """Pour the stringifiable "preamble + contents" into a textblock as a chunk
    with an "appendix" (which is a blank line by default, that can be customized).

    Alternatively when the content appears to be 'empty', a different textblock that is a
    stringified "preamble + empty_response" with an appendix is returned.

    Finally, on specifying True for "all_or_nothing", only the literal "empty_response" is
    returned when the "content' appears to be 'empty'."""
    true_preamble = flatten_to_strlist(preamble)
    true_contents = flatten_to_strlist(content)
    true_empty_response = flatten_to_strlist(empty_response)

    if all_or_nothing and not true_contents:
        return empty_response

    return chunk([true_preamble, content], appendix) if true_contents else chunk(
        [true_preamble, true_empty_response], appendix)


@dataclass()
class GeneratedContent:
    """Data class containing generated content, its md5 hash, a designated filename and
    an optional namespace indication."""
    filename: str
    contents: str
    namespace: Optional[NamespaceIds] = field(default=None)

    def __post_init__(self):
        """Postcheck the constructed data class members on validity."""
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
