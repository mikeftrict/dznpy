"""
Testsuite validating the scoping module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# dznpy modules

# system-under-test
from dznpy.scoping import *


###############################################################################
# Type NamespaceIds
#


@pytest.mark.parametrize('data',
                         [[], ['a'], ['A'], ['_'], ['My'], ['My', 'Project'], ['My_Project'],
                          ['pROj'], ['_hi'], ['a__b'], ['B_9'], ['C3_']])
def test_namespaceids_ok(data):
    """Test examples of valid construction."""
    sut = NamespaceIds(items=data)
    assert sut.items == data


@pytest.mark.parametrize('data', [None, [None], "My", 1, {}, set(), 3.14, [None, "My"]])
def test_namespaceids_fail1(data):
    """Test examples of invalid construction with an incorrect input type."""
    with pytest.raises(TypeError) as exc:
        NamespaceIds(items=data)
    assert str(exc.value) == f'"{data}" is not a list of zero or more strings'


@pytest.mark.parametrize('data', [[''], ['2'], ['^$'], [')'], ['::'], ['My.Project'], ['My::Project']])
def test_namespaceids_fail2(data):
    """Test examples of invalid construction with illegal characters."""
    with pytest.raises(NamespaceIdsTypeError) as exc:
        NamespaceIds(items=data)
    assert str(exc.value).startswith('namespace id "')
    assert str(exc.value).endswith('" is invalid')


def test_namespaceids_addition():
    """Test example of adding two instances into a new one."""
    one = NamespaceIds(['My'])
    two = NamespaceIds(['Name', 'Spaze'])
    result = one + two
    assert isinstance(result, NamespaceIds)
    assert result.items == ['My', 'Name', 'Spaze']


def test_namespaceids_in_place_addition():
    """Test example adding an other instance to an existing instance."""
    one = NamespaceIds(['My'])
    two = NamespaceIds(['Name', 'Spaze'])
    one += two
    assert one.items == ['My', 'Name', 'Spaze']
    assert two.items == ['Name', 'Spaze'], 'The other instance remains untouched'


###############################################################################
# Type NamespaceIds creation functions
#

@pytest.mark.parametrize('arg,exp_items', [(['My', 'Project'], ['My', 'Project']),
                                           ('My.Project', ['My', 'Project']),
                                           ('My::Project', ['My', 'Project']),
                                           ('Project', ['Project']),
                                           ('', []),
                                           ('My_Project', ['My_Project']),  # underscores are not delimiters!
                                           ('My__', ['My__']),  # underscores are not delimiters!
                                           ('_My_', ['_My_']),  # underscores are not delimiters!
                                           ])
def test_create_namespaceids_functions_ok(arg, exp_items):
    """Test examples of NamespaceIds type creation functions and accepted variations of input."""
    variant1 = namespaceids_t(arg)
    assert isinstance(variant1, NamespaceIds)
    assert variant1.items == exp_items

    variant2 = ns_ids_t(arg)
    assert isinstance(variant2, NamespaceIds)
    assert variant2.items == exp_items


@pytest.mark.parametrize('data', [None, 1, 3.14, set(), {}, [1, 2, 3], 'My.', '.My', 'My . Ns', '::Root', 'My::Ns::', '&addres'])
def test_create_namespaceids_functions_fail(data):
    """Test examples of invalid creation attempts of NamespaceIds."""
    with pytest.raises(NamespaceIdsTypeError):
        namespaceids_t(data)

    with pytest.raises(NamespaceIdsTypeError):
        ns_ids_t(data)


def test_create_namespaceids_no_cloning():
    """Test example of providing a NamespaceIds type as argument results in a pass-through and NO cloning."""
    original = NamespaceIds(['My'])
    result = namespaceids_t(original)
    assert original is result, 'The result is a pass-through of the original'
    assert original == result, 'The contents are equivalent'
    assert original.items is result.items, 'The (deep) contents are equivalent'


###############################################################################
# Type NamespaceIds helper functions
#

def test_assert_namespaceids_type_ok():
    """Test asserting a given parameter argument equals the correct type."""
    assert_t(NamespaceIds(['My', 'Project']), NamespaceIds)
    assert_t(namespaceids_t('My.Project'), NamespaceIds)


@pytest.mark.parametrize('data', [1, 3.14, set(), {}, ['My', 'Project'], 'My.Project'])
def test_assert_namespaceids_type_fail(data):
    """Test examples of asserting a given parameter argument does not equal the correct type."""
    with pytest.raises(TypeError):
        assert_t(data, NamespaceIds)


def test_assert_optional_namespaceids_type_ok():
    """Test asserting a given parameter argument equals the correct type or is None."""
    assert_t_optional(NamespaceIds(['My', 'Project']), NamespaceIds)
    assert_t_optional(None, NamespaceIds)


@pytest.mark.parametrize('data', [1, 3.14, set(), {}, ['My', 'Project'], 'My.Project'])
def test_assert_optional_namespaceids_type_fail(data):
    """Test examples of asserting a given parameter argument does not equal the correct type. But None is ok."""
    with pytest.raises(TypeError):
        assert_t_optional(data, NamespaceIds)


def test_sum_namespaceids_items_ok():
    """Test summing/concatenating a list of NamespaceIds."""
    item1 = ns_ids_t('My')
    item2 = ns_ids_t('Project.XYZ')
    item3 = ns_ids_t('Number')
    sut = [item1, item2, item3]
    result = sum_namespaceids_items(sut)
    assert isinstance(result, NamespaceIds)
    assert result.items == ['My', 'Project', 'XYZ', 'Number']


def test_sum_namespaceids_items_ok_empty():
    """Test summing/concatenating a list of NamespaceIds."""
    result = sum_namespaceids_items([])
    assert result == NamespaceIds()


@pytest.mark.parametrize('data', [None, 1, 3.14, set(), {}, [ns_ids_t('My'), 'Project'], 'My.Project'])
def test_sum_namespaceids_items_fail(data):
    """Test examples of asserting a given parameter argument does not equal the correct type."""
    with pytest.raises(TypeError):
        sum_namespaceids_items(data)


###############################################################################
# Type NamespaceTree
#


def test_namespacetree_ok_default():
    sut = NamespaceTree()
    assert sut.scope_name is None
    assert sut.fqn == NamespaceIds([])  # an empty instance
    assert str(sut) == ''


def test_namespacetree_fail_on_only_scope_name():
    with pytest.raises(ValueError) as exc:
        NamespaceTree(parent=None, scope_name=ns_ids_t('OnlyThis'))
    assert str(exc.value) == 'parent required when constructing with a scope_name'


def test_namespacetree_fail_on_only_parent():
    top = NamespaceTree()
    with pytest.raises(ValueError) as exc:
        NamespaceTree(parent=top, scope_name=None)
    assert str(exc.value) == 'scope_name required when constructing with a parent'


def test_namespacetree_two_level_create():
    top = NamespaceTree()
    child = NamespaceTree(parent=top, scope_name=ns_ids_t('Project'))
    assert child.scope_name == NamespaceIds(['Project'])
    assert child.fqn == NamespaceIds(['Project'])
    assert str(child) == 'Project'


def test_namespacetree_three_level_create():
    top = NamespaceTree()
    child1 = NamespaceTree(parent=top, scope_name=ns_ids_t('My.Project'))
    child2 = NamespaceTree(parent=child1, scope_name=ns_ids_t('XYZ'))
    assert child2.scope_name == NamespaceIds(['XYZ'])
    assert child2.fqn == NamespaceIds(['My', 'Project', 'XYZ'])
    assert str(child2) == 'My.Project.XYZ'


def test_namespacetree_fqn_member_in_root_namespace():
    top = NamespaceTree()
    sut = top.fqn_member_name(ns_ids_t('Heater'))
    assert isinstance(sut, NamespaceIds)
    assert sut.items == ['Heater']


def test_namespacetree_fqn_member_in_two_level_namespace():
    top = NamespaceTree(parent=NamespaceTree(), scope_name=ns_ids_t('My'))
    child = NamespaceTree(parent=top, scope_name=ns_ids_t('Project'))
    assert child.fqn.items == ['My', 'Project']
    sut = child.fqn_member_name(ns_ids_t('Very.Big.Toaster'))
    assert sut.items == ['My', 'Project', 'Very', 'Big', 'Toaster']


def test_namespacetree_fqn_member_fail():
    top = NamespaceTree()
    with pytest.raises(NamespaceIdsTypeError) as exc:
        top.fqn_member_name(ns_ids_t('One.%1'))
    assert str(exc.value) == 'namespace id "%1" is invalid'


###############################################################################
# Type NamespaceIds helper functions
#

def test_assert_namespacetree_type_ok():
    """Test asserting a given parameter argument equals the correct type."""
    sut = NamespaceTree()
    assert_t(sut, NamespaceTree)
    assert_t(NamespaceTree(None, None), NamespaceTree)
    assert_t(NamespaceTree(sut, namespaceids_t('Hello')), NamespaceTree)


@pytest.mark.parametrize('data', [1, 3.14, set(), {}, ['My', 'Project'], 'My.Project'])
def test_assert_namespacetree_type_fail(data):
    """Test examples of asserting a given parameter argument does not equal the correct type."""
    with pytest.raises(TypeError):
        assert_t(data, NamespaceTree)


def test_assert_optional_namespacetree_type_ok():
    """Test asserting a given parameter argument equals the correct type or is None."""
    assert_t_optional(NamespaceTree(), NamespaceTree)
    assert_t_optional(None, NamespaceTree)


@pytest.mark.parametrize('data', [1, 3.14, set(), {}, ['My', 'Project'], 'My.Project'])
def test_assert_optional_namespacetree_type_fail(data):
    """Test examples of asserting a given parameter argument does not equal the correct type. But None is ok."""
    with pytest.raises(TypeError):
        assert_t_optional(data, NamespaceTree)


###############################################################################
# Miscellaneous functions
#


def test_scope_resolution_order_ok():
    """Test valid examples of creating a scope resolution order."""
    assert scope_resolution_order(searchable=namespaceids_t('IToaster'),
                                  calling_scope=namespaceids_t('My.Project')) == \
           [ns_ids_t('My.Project.IToaster'),
            ns_ids_t('My.IToaster'),
            ns_ids_t('IToaster')]

    assert scope_resolution_order(searchable=namespaceids_t('Some.ILed'),
                                  calling_scope=namespaceids_t('My.Project')) == \
           [ns_ids_t('My.Project.Some.ILed'),
            ns_ids_t('My.Some.ILed'),
            ns_ids_t('Some.ILed')]

    assert scope_resolution_order(searchable=namespaceids_t('My.ILed'),
                                  calling_scope=None) == \
           [ns_ids_t('My.ILed')]


def test_scope_resolution_order_ok_clones_calling_scope():
    """Test that the function leaves the calling_scope argument untouched."""
    my_calling_scope = namespaceids_t('My.Project')
    assert len(my_calling_scope.items) == 2
    scope_resolution_order(namespaceids_t('IToaster'), my_calling_scope)
    assert len(my_calling_scope.items) == 2


@pytest.mark.parametrize("searchable,calling_scope,exc", [(None, None, ValueError),
                                                          (123, None, TypeError),
                                                          ('My.Project', None, TypeError),
                                                          (namespaceids_t('My.ILed'), 'SomeString', TypeError)])
def test_scope_resolution_order_arguments_type_fail(searchable, calling_scope, exc):
    """Test examples of failing scope resolution order creation on invalid type of arguments."""
    with pytest.raises(exc):
        scope_resolution_order(searchable, calling_scope)
