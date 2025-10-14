"""
Testsuite validating the cpp_gen module

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from typing import Any

# system-under-test
from dznpy.cpp_gen_rule_of_five import *

# test data
from testdata_cpp_gen import *


# test helpers
def assert_str_eq(left: Any, right: Any):
    """Assert two instances that will be stringified and compared for equal contents and allow
    PyTest to elaborate a nice delta output on failures."""
    assert str(left) == str(right)


def test_copy_constructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(CopyConstructor(parent=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), call as_decl() or as_def()'

    with pytest.raises(CppGenError) as exc:
        CopyConstructor(parent=None)
    assert str(exc.value) == 'parent must be either a Class or Struct'


def test_copy_constructor_ok():
    class_sut = CopyConstructor(parent=Class('MyToaster'))
    assert_str_eq(class_sut.as_decl(), COPY_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), COPY_CONSTRUCTOR_DEF_MINIMAL)


def test_copy_constructor_content_ok():
    class_sut = CopyConstructor(parent=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert_str_eq(class_sut.as_decl(), COPY_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), COPY_CONSTRUCTOR_CONTENT_DEF)


def test_copy_constructor_with_delete_initialization():
    sut = CopyConstructor(parent=Class('MyToaster'),
                          initialization=FunctionInitialization.DELETE)
    assert_str_eq(sut.as_decl(), COPY_CONSTRUCTOR_INITIALIZATION_DELETE_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_copy_assignment_constructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(CopyAssignmentConstructor(parent=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), call as_decl() or as_def()'

    with pytest.raises(CppGenError) as exc:
        CopyAssignmentConstructor(parent=None)
    assert str(exc.value) == 'parent must be either a Class or Struct'


def test_copy_assignment_constructor_ok():
    class_sut = CopyAssignmentConstructor(parent=Class('MyToaster'))
    assert_str_eq(class_sut.as_decl(), COPY_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), COPY_ASSIGNMENT_CONSTRUCTOR_DEF_MINIMAL)


def test_copy_assignment_constructor_content_ok():
    class_sut = CopyAssignmentConstructor(parent=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert_str_eq(class_sut.as_decl(), COPY_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), COPY_ASSIGNMENT_CONSTRUCTOR_CONTENT_DEF)


def test_copy_assignment_constructor_with_delete_initialization():
    sut = CopyAssignmentConstructor(parent=Class('MyToaster'),
                                    initialization=FunctionInitialization.DELETE)
    assert_str_eq(sut.as_decl(), COPY_ASSIGNMENT_CONSTRUCTOR_INITIALIZATION_DELETE_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_move_constructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(MoveConstructor(parent=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), call as_decl() or as_def()'

    with pytest.raises(CppGenError) as exc:
        MoveConstructor(parent=None)
    assert str(exc.value) == 'parent must be either a Class or Struct'


def test_move_constructor_ok():
    class_sut = MoveConstructor(parent=Class('MyToaster'))
    assert_str_eq(class_sut.as_decl(), MOVE_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), MOVE_CONSTRUCTOR_DEF_MINIMAL)


def test_move_constructor_content_ok():
    class_sut = MoveConstructor(parent=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert_str_eq(class_sut.as_decl(), MOVE_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), MOVE_CONSTRUCTOR_CONTENT_DEF)


def test_move_constructor_with_delete_initialization():
    sut = MoveConstructor(parent=Class('MyToaster'),
                          initialization=FunctionInitialization.DELETE)
    assert_str_eq(sut.as_decl(), MOVE_CONSTRUCTOR_INITIALIZATION_DELETE_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_move_assignment_constructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(MoveAssignmentConstructor(parent=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), call as_decl() or as_def()'

    with pytest.raises(CppGenError) as exc:
        MoveAssignmentConstructor(parent=None)
    assert str(exc.value) == 'parent must be either a Class or Struct'


def test_move_assignment_constructor_ok():
    class_sut = MoveAssignmentConstructor(parent=Class('MyToaster'))
    assert_str_eq(class_sut.as_decl(), MOVE_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), MOVE_ASSIGNMENT_CONSTRUCTOR_DEF_MINIMAL)


def test_move_assignment_constructor_content_ok():
    class_sut = MoveAssignmentConstructor(parent=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert_str_eq(class_sut.as_decl(), MOVE_ASSIGNMENT_CONSTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), MOVE_ASSIGNMENT_CONSTRUCTOR_CONTENT_DEF)


def test_move_assignment_constructor_with_delete_initialization():
    sut = MoveAssignmentConstructor(parent=Class('MyToaster'),
                                    initialization=FunctionInitialization.DELETE)
    assert_str_eq(sut.as_decl(), MOVE_ASSIGNMENT_CONSTRUCTOR_INITIALIZATION_DELETE_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_destructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(Destructor(parent=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), call as_decl() or as_def()'

    with pytest.raises(CppGenError) as exc:
        Destructor(parent=None)
    assert str(exc.value) == 'parent must be either a Class or Struct'


def test_destructor_ok():
    class_sut = Destructor(parent=Class('MyToaster'))
    assert_str_eq(class_sut.as_decl(), DESTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), DESTRUCTOR_DEF_MINIMAL)

    struct_sut = Destructor(parent=Struct('MyToaster'))
    assert_str_eq(struct_sut.as_decl(), DESTRUCTOR_DECL_MINIMAL)
    assert_str_eq(struct_sut.as_def(), DESTRUCTOR_DEF_MINIMAL)


def test_destructor_content_ok():
    class_sut = Destructor(parent=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert_str_eq(class_sut.as_decl(), DESTRUCTOR_DECL_MINIMAL)
    assert_str_eq(class_sut.as_def(), DESTRUCTOR_CONTENT_DEF)


def test_destructor_with_default_initialization():
    sut = Destructor(parent=Class('MyToaster'),
                     initialization=FunctionInitialization.DEFAULT)
    assert_str_eq(sut.as_decl(), DESTRUCTOR_INITIALIZATION_DEFAULT_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_destructor_with_default_initialization_and_override():
    sut = Destructor(parent=Class('MyToaster'),
                     override=True,
                     initialization=FunctionInitialization.DEFAULT)
    assert_str_eq(sut.as_decl(), DESTRUCTOR_OVERRIDE_INITIALIZATION_DEFAULT_DECL)
    assert_str_eq(sut.as_def(), NOTHING_GENERATED)


def test_rule_of_five_ok():
    """Test the creation of the RuleOfDive class and its accessors."""
    sut = RuleOfFive(parent=Struct(name='MyStruct'),
                     copy_constr=FunctionInitialization.DELETE,
                     move_constr=FunctionInitialization.DEFAULT,
                     copy_assign_constr=FunctionInitialization.DELETE,
                     move_assign_constr=FunctionInitialization.DEFAULT,
                     destructor=FunctionInitialization.DELETE)

    assert str(sut.as_decl()) == RULE_OF_FIVE_DECL

    assert isinstance(sut.copy_constructor, CopyConstructor)
    assert isinstance(sut.move_constructor, MoveConstructor)
    assert isinstance(sut.copy_assign_constructor, CopyAssignmentConstructor)
    assert isinstance(sut.move_assign_constructor, MoveAssignmentConstructor)
    assert isinstance(sut.destructor, Destructor)
