"""
Testsuite validating the ast_cpp_view module

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# own modules
from dznpy import ast, json_ast

# system-under-test
from dznpy.scoping import ns_ids_t

# Test data
from common.helpers import resolve
from dznpy.text_gen import TB
from testdata_json_ast import *

# system-under-test
from dznpy.ast_cpp_view import *

# test constants
DZNJSON_FILE = resolve(__file__, TOASTER_SYSTEM_JSON_FILE)


###############################################################################
# Test helpers
#

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
    assert len(fc.imports) == 15
    assert len(fc.interfaces) == 8
    assert len(fc.subints) == 3
    assert len(fc.systems) == 1
    return fc


###############################################################################
# Test type creation functions
#

def test_expand_type_name_enum_ok():
    """Test a valid example of creating an TypeAsIs instance."""
    r = expand_type_name(name=ScopeName(ns_ids_t('Result')),
                         parent_fqn=ns_ids_t('My'),
                         fct=fc2())
    assert str(r) == '::My::Result'


def test_expand_type_name_extern_ok():
    """Test a valid example of creating an TypeAsIs instance."""
    r = expand_type_name(name=ScopeName(ns_ids_t('PResultInfo')),
                         parent_fqn=ns_ids_t('My.Project'),
                         fct=fc2())
    assert str(r) == 'std::shared_ptr<ResultInfo>'


def test_expand_type_name_int_ok():
    """Test a valid example of creating an TypeAsIs instance."""
    r = expand_type_name(name=ScopeName(ns_ids_t('MediumInt')),
                         parent_fqn=ns_ids_t('My.Project'),
                         fct=fc2())
    assert str(r) == 'int'


def test_expand_type_name_pass_through():
    """Test an example of creating an TypeAsIs instance with passing
    through a name that could not be resolved."""
    r = expand_type_name(name=ScopeName(ns_ids_t('Bogus')),
                         parent_fqn=ns_ids_t(''),
                         fct=fc2())
    assert str(r) == 'Bogus'


def test_expand_event_ok():
    """Test a valid example of creating an EventExpanded instance."""
    fc = fc2()
    itf = fc.interfaces[0]
    evt = itf.events.elements[0]
    exp = EventExpanded(return_type=TypeAsIs(value='void'),
                        name='Create',
                        formals=[FormalExpanded(type=TypeAsIs(value='size_t'),
                                                direction=FormalDirection.IN,
                                                name='waitingTimeMs')])
    assert exp == expand_event(evt, itf, fc)


def test_get_formals_ok():
    """Test a valid example of calling get_formals() that returns a tuple."""
    evt = EventExpanded(return_type=TypeAsIs(value='void'),
                        name='Create',
                        formals=[FormalExpanded(type=TypeAsIs(value='size_t'),
                                                direction=FormalDirection.IN,
                                                name='waitingTimeMs'),
                                 FormalExpanded(type=TypeAsIs(value='int'),
                                                direction=FormalDirection.OUT,
                                                name='number')]
                        )
    assert get_formals(evt) == ('waitingTimeMs, number',
                                'size_t waitingTimeMs, int& number')


def test_create_member_function_default():
    """Test a valid example of creating a default Function."""
    evt_exp = EventExpanded(TypeAsIs('void'), 'SomeEvent',
                            formals=[FormalExpanded(type=TypeAsIs(value='size_t'),
                                                    direction=FormalDirection.IN,
                                                    name='waitingTimeMs')])
    r = create_member_function(evt_exp, 'MyPrefix')

    assert isinstance(r, Function)
    assert str(r.as_decl()) == 'void MyPrefixSomeEvent(size_t waitingTimeMs);\n'
    assert str(r.as_def()) == 'void MyPrefixSomeEvent(size_t waitingTimeMs) {}\n'


def test_create_member_function_with_parent():
    """Test a valid example of creating a default Function."""
    evt_exp = EventExpanded(TypeAsIs('void'), 'SomeEvent', [])
    struct = Struct('MyStruct')
    r = create_member_function(evt_exp, '', struct)

    assert isinstance(r, Function)
    assert str(r.as_decl()) == 'void SomeEvent();\n'
    assert str(r.as_def()) == 'void MyStruct::SomeEvent() {}\n'


def test_create_member_function_with_override():
    """Test a valid example of creating a default Function with override."""
    evt_exp = EventExpanded(TypeAsIs('void'), 'SomeEvent', [])
    r = create_member_function(evt_exp, '', override=True)

    assert isinstance(r, Function)
    assert str(r.as_decl()) == 'void SomeEvent() override;\n'
    assert str(r.as_def()) == 'void SomeEvent() {}\n'
