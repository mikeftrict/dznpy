"""
Testsuite validating the ast_view module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# own modules
from dznpy import ast, json_ast

# system-under-test
from dznpy.scoping import ns_ids_t, NamespaceIds, NamespaceIdsTypeError

# Test data
from common.helpers import resolve
from testdata_json_ast import *

# system-under-test
from dznpy.ast_view import *

# test constants
DZNJSON_FILE = resolve(__file__, TOASTER_SYSTEM_JSON_FILE)


###############################################################################
# Test helpers
#

def fc1() -> ast.FileContents:
    """Load Dezyne JSON example testdata and return the result as a FileContents dataclass."""
    r = json_ast.DznJsonAst(json_contents=DZNFILE_EXAMPLE)
    r.process()
    fc = r.file_contents
    # assert the presence (or absense) of AST instances
    assert len(fc.components) == 1
    assert len(fc.enums) == 2
    assert len(fc.externs) == 1
    assert not fc.filenames
    assert len(fc.foreigns) == 1
    assert not fc.imports
    assert len(fc.interfaces) == 2
    assert len(fc.subints) == 2
    assert len(fc.systems) == 1
    return fc


def fc2() -> ast.FileContents:
    """Load a real Dezyne ToasterSystem.dzn JSON data and return the result as a FileContents dataclass."""
    r = json_ast.DznJsonAst().load_file(DZNJSON_FILE)
    r.process()
    fc = r.file_contents
    # assert the presence (or absense) of AST instances
    assert len(fc.components) == 1
    assert len(fc.enums) == 3
    assert len(fc.externs) == 4
    assert len(fc.filenames) == 10
    assert len(fc.foreigns) == 1
    assert len(fc.imports) == 14
    assert len(fc.interfaces) == 8
    assert len(fc.subints) == 3
    assert len(fc.systems) == 1
    return fc


def example_system() -> ast.System:
    """Retrieve a Dezyne system component from a real file (ToasterSystem.dzn)."""
    r = find_fqn(fc2(), ns_ids_t('ToasterSystem'), ns_ids_t('My.Project'))
    assert r.has_one_instance(ast.System), "The system component must be present in the testdata."
    return r.get_single_instance(ast.System)


def expect_find_result(result: FindResult, list_size: int) -> List[NamespaceIds]:
    """Test helper function to assert the type of the FindResult argument and its expected size of list items.
    As final result, return a list of the NamespaceIds their FQN."""
    assert isinstance(result, FindResult)
    assert len(result.items) == list_size, 'Number of instances in the result'
    return [instance.fqn for instance in result.items]


###############################################################################
# Test FindResult type
#
@pytest.mark.parametrize('param', [None, {}, set(), 'Toaster'])
def test_findresult_construction_fail1(param):
    """Test that the dataclass asserts on incorrect initialized properties."""
    with pytest.raises(TypeError) as exc:
        FindResult(param)
    assert str(exc.value) == 'The type of property "items" must be a list'


@pytest.mark.parametrize('param', [[None], [{}], [set()], ['My', 'Toaster'], fc2().filenames, fc2().imports])
def test_findresult_construction_fail2(param):
    """Test that the dataclass asserts on incorrect initialized properties."""
    with pytest.raises(TypeError) as exc:
        FindResult(param)
    assert 'does not match one of the valid_types' in str(exc.value)


def test_findresult_construction_ok():
    """Test that the dataclass checks on correctly initialized properties."""
    fc = fc2()
    FindResult(fc.components)
    FindResult(fc.enums)
    FindResult(fc.externs)
    FindResult(fc.foreigns)
    FindResult(fc.interfaces)
    FindResult(fc.subints)
    FindResult(fc.systems)


def test_findresult_has_one_instance_true():
    """Test FindResult on finding a single instance."""
    fc = fc2()
    sut = FindResult(fc.systems)
    assert len(fc.systems) == 1, 'Assert the test data is ok before continuing'
    assert sut.has_one_instance()


def test_findresult_has_one_instance_false():
    """Test FindResult on not finding exactly one instance."""
    assert not FindResult([]).has_one_instance(), 'no instances'
    assert not FindResult(fc2().components + fc2().interfaces).has_one_instance(), 'more than 1 instance in the FindResult'


def test_findresult_has_one_instance_with_typehint_true():
    """Test FindResult on finding a single instance with a specific AST typehint."""
    fc = fc2()
    sut = FindResult(fc.systems)
    assert len(fc.systems) == 1, 'Assert the test data is ok before continuing'
    assert sut.has_one_instance(ast_typehint=System)


def test_findresult_has_one_instance_with_typehint_false():
    """Test FindResult on not finding exactly one instance with a specific AST typehint."""
    fc = fc2()
    sut = FindResult(fc.components)
    assert len(fc.components) == 1, 'Assert the test data is ok before continuing'
    assert not sut.has_one_instance(ast_typehint=System)


def test_findresult_has_one_instance_with_invalid_typehint():
    """Test FindResult on finding exactly one instance but the typehint is of an invalid type."""
    fc = fc2()
    sut = FindResult(fc.components)
    assert len(fc.components) == 1, 'Assert the test data is ok before continuing'
    with pytest.raises(FindError) as exc:
        sut.has_one_instance(ast_typehint=int)
    assert str(exc.value) == 'Argument ast_typehint does not match one of the valid_types'


def test_findresult_get_single_instance_ok():
    """Test FindResult on getting a single found instance."""
    sut = FindResult(fc2().systems)
    assert sut.has_one_instance(), 'Assert the test data is ok before continuing'
    assert isinstance(sut.get_single_instance(), System)


def test_findresult_get_single_instance_fail1():
    """Test FindResult on getting a single found instance to fail when no instances were returned."""
    sut = FindResult([])
    assert len(sut.items) == 0, 'Assert the test data (no instances) is ok before continuing'
    with pytest.raises(FindError) as exc:
        sut.get_single_instance()
    assert str(exc.value) == 'The result contains no instance(s) at all'


def test_findresult_get_single_instance_fail2():
    """Test FindResult on getting a single found instance to fail when multiple instances are returned."""
    sut = FindResult(fc2().enums)
    assert len(sut.items) > 1, 'Assert the test data is ok (> 1 instances) before continuing'
    with pytest.raises(FindError) as exc:
        sut.get_single_instance()
    assert str(exc.value) == 'The result contains more than one instance'


def test_findresult_get_single_instance_with_typehint_ok():
    """Test FindResult on getting a single instance with a specific AST typehint."""
    sut = FindResult(fc2().systems)
    assert sut.has_one_instance(), 'Assert the test data is ok before continuing'
    assert isinstance(sut.get_single_instance(ast_typehint=System), System)


def test_findresult_get_single_instance_with_typehint_fail():
    """Test FindResult on getting a single instance with a specific AST typehint."""
    sut = FindResult(fc2().systems)
    assert sut.has_one_instance(), 'Assert the test data is ok before continuing'
    with pytest.raises(FindError) as exc:
        sut.get_single_instance(ast_typehint=Component)
    assert str(exc.value) == "The found instance does not match the ast typehint <class 'dznpy.ast.Component'>"


###############################################################################
# Test find_fqn()
#

def test_find_fqn_one_match_without_as_of_scope():
    """Test matching one AST instance whose FQN NamsepaceIds precisely equals to the ns_ids specified by the caller."""
    fqns = expect_find_result(find_fqn(fc1(), ns_ids_t('Project.SmallInt')), 1)
    assert ns_ids_t('Project.SmallInt') in fqns


def test_find_fqn_one_match_with_as_of_scope():
    """Test matching one AST instance whose FQN NamsepaceIds in combination with the as_of_scope equals to
    the ns_ids specified by the caller."""
    fqns = expect_find_result(find_fqn(fc1(), ns_ids_t('SmallInt'), ns_ids_t('Project')), 1)
    assert ns_ids_t('Project.SmallInt') in fqns


def test_find_fqn_no_matches_without_as_of_scope():
    """Test the scenario where no AST instance is found because the specified ns_ids is not found in the
    root namespace. No as_of_scope was given to attempt deeper scopes. Or an as_of_scope is given which
    does not exist."""
    expect_find_result(find_fqn(fc1(), ns_ids_t('SmallInt')), 0)
    expect_find_result(find_fqn(fc1(), ns_ids_t('SmallInt'), ns_ids_t('Not.Existing.Scope')), 0)


def test_find_fqn_multiple_matches_on_ambiguity_with_as_of_scope():
    """Test matching multiple AST instances whose FQN NamsepaceIds ends equally to the ns_ids to search on
    with an as_of_inner_scope. But note that this scope is put into a scope_resolution_order that will
    progressively peel off to an outer scope, meaning it could ultimately find multiple instances.
    As shown in this test where ambiguely SmallInt is found in Project.IHeaterElment as well in Project.
    This means either there is some ambiguity of the developers models. Or, one should address a more complete
    ns_ids argument to look for."""
    fqns = expect_find_result(find_fqn(fc1(), ns_ids_t('SmallInt'), ns_ids_t('Project.IHeaterElement')), 2)
    assert ns_ids_t('Project.IHeaterElement.SmallInt') in fqns
    assert ns_ids_t('Project.SmallInt') in fqns


def test_find_fqn_single_match_including_as_of_scope():
    """Test matching more precisely an AST instance whose FQN NamespaceIds equally to the ns_ids to search on
    with an as_of_inner_scope."""
    fqns = expect_find_result(find_fqn(fc1(), ns_ids_t('IHeaterElement.SmallInt'), ns_ids_t('Project')), 1)
    assert ns_ids_t('Project.IHeaterElement.SmallInt') in fqns


def test_find_fqn_no_match_including_as_of_scope():
    """Test matching nothing when an as_of_scope is missing will the items is actually one scope deeper
    than the ns_ids specified."""
    fqns = expect_find_result(find_fqn(fc1(), ns_ids_t('IHeaterElement.SmallInt')), 0)
    assert not fqns


def test_find_fqn_single_match_including_non_helping_as_of_scope():
    """Test matching more precisely an AST instance whose FQN NamsepaceIds equals to the ns_ids to search on.
    Even when the as_of_inner_scope comes with a scope_resolution_order that will not matter (or interfere).
    This example reasons from the Toaster.dzn component which wants to lookup  requires interface."""
    fqns = expect_find_result(find_fqn(fc2(), ns_ids_t('Some.Vendor.IHeaterElement'), ns_ids_t('My.Project')), 1)
    assert ns_ids_t('Some.Vendor.IHeaterElement') in fqns


def test_find_fqn_no_match_when_outside_as_of_scope2():
    """Test no match, when the specified ns_ids does not fall into the scope_resolution_order and ultimately
    on checking the outer scope where the AST instance is not found."""
    fqns = expect_find_result(find_fqn(fc2(), ns_ids_t('Vendor.IHeaterElement'), ns_ids_t('My.Project')), 0)
    assert not fqns


def test_find_fqn_fail_wildcard_attempt_not_allowed():
    """Test will not match anything when attempting a endswith_ids a single AST instance."""
    # presume '*Element' hoping to match with 'IHeaterElement', but shall fail
    expect_find_result(find_fqn(fc2(), ns_ids_t('Element'), ns_ids_t('My.Project')), 0)


def test_find_fqn_no_match():
    """No match when the searchable does not exist in the FileContents."""
    fqns = expect_find_result(find_fqn(fc2(), ns_ids_t('CannotFindMe'), ns_ids_t('My.Project')), 0)
    assert not fqns


@pytest.mark.parametrize('lookup,exp_type',
                         [('Toaster', ast.Component),
                          ('Result', ast.Enum),
                          ('MilliSeconds', ast.Extern),
                          ('Facilities.Timer', ast.Foreign),
                          ('IToaster', ast.Interface),
                          ('Some.Vendor.IHeaterElement', ast.Interface),
                          ('SmallInt', ast.SubInt),
                          ('ToasterSystem', ast.System),
                          ])
def test_find_fqn_returned_types(lookup, exp_type):
    r = find_fqn(fc2(), ns_ids_t(lookup), ns_ids_t('My.Project'))
    assert isinstance(r, FindResult)
    assert len(r.items) == 1, "Exactly one instance is expected"
    assert isinstance(r.items[0], exp_type)


###############################################################################
# Test find_any()
#


def test_find_any_multiple_matches1():
    """Test matching multiple AST instances with the same (ending) name."""
    fqns = expect_find_result(find_any(fc1(), ns_ids_t('SmallInt')), 2)
    assert ns_ids_t('Project.IHeaterElement.SmallInt') in fqns
    assert ns_ids_t('Project.SmallInt') in fqns


def test_find_any_multiple_matches2():
    """Test matching multiple AST instances with the same (ending) name."""
    fqns = expect_find_result(find_any(fc2(), ns_ids_t('IHeaterElement')), 3)
    assert ns_ids_t('My.Project.IHeaterElement') in fqns
    assert ns_ids_t('Some.Vendor.IHeaterElement') in fqns
    assert ns_ids_t('IHeaterElement') in fqns


def test_find_any_single_match1():
    """Test matching a single AST instance."""
    fqns = expect_find_result(find_any(fc1(), ns_ids_t('ToasterSystem')), 1)
    assert ns_ids_t('Project.ToasterSystem') in fqns


def test_find_any_single_match2():
    """Test matching a single AST instance."""
    fqns = expect_find_result(find_any(fc2(), ns_ids_t('Vendor.IHeaterElement')), 1)
    assert ns_ids_t('Some.Vendor.IHeaterElement') in fqns


def test_find_any_fail_wildcard_attempt_not_allowed():
    """Test will not match anything when attempting a endswith_ids a single AST instance."""
    # presume '*Element' hoping to match with 'IHeaterElement', but shall fail
    expect_find_result(find_any(fc2(), ns_ids_t('Element')), 0)


def test_find_any_no_match():
    """No match when the searchable does not exist in the FileContents."""
    expect_find_result(find_any(fc2(), ns_ids_t('CannotFindMe')), 0)


def test_find_any_fail_on_invalid_parameters():
    """Test exceptions are being raised on invalid arguments."""
    with pytest.raises(TypeError) as exc:
        find_any(None, ns_ids_t('IHeaterElement'))
    assert str(exc.value) == """Value "None" is not a FileContents type"""

    with pytest.raises(TypeError) as exc:
        find_any(fc1(), 123)
    assert str(
        exc.value) == """Value argument "123" is not equal to the expected type: <class 'dznpy.scoping.NamespaceIds'>, actual type found: <class 'int'>."""


@pytest.mark.parametrize('lookup,exp_type',
                         [('Toaster', ast.Component),
                          ('Result', ast.Enum),
                          ('MilliSeconds', ast.Extern),
                          ('Timer', ast.Foreign),
                          ('IToaster', ast.Interface),
                          ('Vendor.IHeaterElement', ast.Interface),
                          ('SmallInt', ast.SubInt),
                          ('ToasterSystem', ast.System),
                          ])
def test_find_any_returned_types(lookup, exp_type):
    r = find_any(fc2(), ns_ids_t(lookup))
    assert isinstance(r, FindResult)
    assert r.has_one_instance(), "Exactly one instance is expected"
    assert isinstance(r.get_single_instance(), exp_type)


###############################################################################
# Test type creation functions
#


def test_create_portnames_t_ok():
    """Test a valid example of creating a PortNames instance."""
    r = portnames_t(example_system().ports)
    assert isinstance(r, PortNames)
    assert r.provides == {'api'}
    assert r.requires == {'cord', 'heaterElement', 'led'}


@pytest.mark.parametrize('param,exc', [(None, ValueError),
                                       ({}, TypeError),
                                       (set(), TypeError),
                                       (['api', 'cord'], TypeError),
                                       ])
def test_create_portnames_t_fail(param, exc):
    """Test examples of failing creations of a PortNames instance."""
    with pytest.raises(exc):
        portnames_t(param)
