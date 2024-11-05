"""
Testsuite validating the code_gen_common module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# dznpy modules
from dznpy.scoping import namespaceids_t, NamespaceIds

# system-under-test
from dznpy.code_gen_common import GeneratedContent


def test_generated_content():
    """Test creation with the mininum amount of arguments. Expect a hash calculated on
    the contents."""
    sut = GeneratedContent(filename='filename.txt', contents='Hi There\n')
    assert sut.filename == 'filename.txt'
    assert sut.contents == 'Hi There\n'
    assert sut.namespace is None


def test_generated_content_with_ns():
    """Test creation with the extra specification of a namespace, that is expected to be
    part in the dataclass as member."""
    sut = GeneratedContent('filename.txt', 'Hi There\n', namespace=namespaceids_t('My.Project'))
    assert sut.namespace == NamespaceIds(['My', 'Project'])
