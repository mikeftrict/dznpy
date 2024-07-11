"""
Testsuite validating the scoping module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# system-under-test
from dznpy.scoping import *


def test_create_namespaceids_type():
    correct: NameSpaceIds = ['My', 'Project']
    assert is_namespaceids_instance(namespaceids_t(correct)), 'Pass through correct type'
    assert namespaceids_t('My.Project') == correct
    assert namespaceids_t('MyComponent') == ['MyComponent']
    assert is_namespaceids_instance(namespaceids_t('MyComponent')) is True


def test_check_and_assert_namespaceids_type():
    correct: NameSpaceIds = ['My', 'Project']
    assert_namespaceids_instance(correct)
    assert is_namespaceids_instance(correct) is True
    assert is_namespaceids_instance([]) is True, 'an empty list is ok'

    exc_msg = 'The argument is not a NameSpaceIds type'
    assert is_namespaceids_instance(None) is False
    with pytest.raises(TypeError) as exc:
        assert_namespaceids_instance(None)
    assert str(exc.value) == exc_msg

    assert is_namespaceids_instance('My.Project') is False
    with pytest.raises(TypeError) as exc:
        assert_namespaceids_instance('My.Project')
    assert str(exc.value) == exc_msg

    assert is_namespaceids_instance(['One', 2, 3]) is False
    with pytest.raises(TypeError) as exc:
        assert_namespaceids_instance(['One', 2, 3])
    assert str(exc.value) == exc_msg


def test_scope_resolution_order_ok():
    assert scope_resolution_order(searchable=namespaceids_t('IToaster'),
                                  calling_scope=namespaceids_t(['My', 'Project'])) == \
           [['My', 'Project', 'IToaster'], ['My', 'IToaster'], ['IToaster']]

    assert scope_resolution_order(searchable=namespaceids_t(['My', 'ILed']),
                                  calling_scope=namespaceids_t(['My', 'Project'])) == \
           [['My', 'Project', 'My', 'ILed'], ['My', 'My', 'ILed'], ['My', 'ILed']]

    assert scope_resolution_order(searchable=namespaceids_t(['My', 'ILed']),
                                  calling_scope=None) == [['My', 'ILed']]


def test_scope_resolution_order_fail():
    with pytest.raises(TypeError) as exc:
        scope_resolution_order(searchable=None, calling_scope=namespaceids_t(['NS']))
    assert str(exc.value) == 'The argument is not a NameSpaceIds type'

    with pytest.raises(TypeError) as exc:
        scope_resolution_order(searchable=123, calling_scope=namespaceids_t(['NS']))
    assert str(exc.value) == 'The argument is not a NameSpaceIds type'
