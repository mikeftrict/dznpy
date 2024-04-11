"""
Testsuite validating the cpp_gen module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from unittest import TestCase

# system-under-test
from dznpy.cpp_gen import *

# test data
from testdata_cpp_gen import *


def test_comment():
    assert str(Comment('I see the sun')) == COMMENT_LINE
    assert str(Comment('As the mandalorian says:\nthis is the way.  \n \n'
                       'I have spoken.\n')) == COMMENT_BLOCK


def test_comment_block():
    # each string in the list is considered a comment line
    assert str(CommentBlock(['As the mandalorian says:',
                             'this is the way.  ',
                             ' ',
                             'I have spoken.'])) == COMMENT_BLOCK

    # newline characters in strings will be respected as an end-of-line
    assert str(CommentBlock(['As the mandalorian says:\nthis is the way.  \n \n',
                             'I have spoken.'])) == COMMENT_BLOCK

    # non-str list items are skipped
    assert str(CommentBlock([123, 'As the mandalorian says:\nthis is the way.  \n \n',
                             None,
                             'I have spoken.'])) == COMMENT_BLOCK

    # already commented lines are left in tact; but trailing whitespace is stripped anyhow
    assert str(CommentBlock(['// As the mandalorian says:',
                             '// this is the way.  ',
                             '// ',
                             '// I have spoken.'])) == COMMENT_BLOCK


def test_project_includes():
    assert str(ProjectIncludes(['IToaster.h'])) == PROJECT_INCLUDE
    assert str(ProjectIncludes(['IHeater.h', 'ProjectB/Lunchbox.h'])) == PROJECT_INCLUDES


def test_system_includes():
    assert str(SystemIncludes(['string'])) == SYSTEM_INCLUDE
    assert str(SystemIncludes(['string', 'dzn/pump.hh'])) == SYSTEM_INCLUDES


def test_global_namespace():
    assert str(Namespace(ns_ids=[], contents='')) == GLOBAL_NAMESPACE_EMPTY
    assert str(Namespace(ns_ids=[], contents=CONTENTS_SINGLE_LINE)) == GLOBAL_NAMESPACE_CONTENTS


def test_fqn_namespace():
    fqn_ns_ids = ['My', 'Project', 'XY']
    assert str(Namespace(fqn_ns_ids, contents='')) == FQN_NAMESPACE_EMPTY
    assert str(Namespace(fqn_ns_ids, CONTENTS_SINGLE_LINE)) == FQN_NAMESPACE_CONTENTS


def test_namespace_with_textblock():
    tb = TextBlock([EOL, EOL, CONTENTS_SINGLE_LINE, EOL])
    assert str(Namespace(ns_ids=[], contents=tb)) == GLOBAL_NAMESPACE_TEXTBLOCK


def test_fqn_ok():
    # default:
    sut = Fqn(ns_ids=['My', 'Data'])
    assert sut.ns_ids == ['My', 'Data']
    assert str(sut) == "My::Data"

    # empty ns ids leads to an empty Fqn
    assert str(Fqn(ns_ids=[])) == ''
    assert str(Fqn(ns_ids=[], prefix_root_ns=True)) == ''

    # enable prefixing with the C++ root namespace:
    assert str(Fqn(ns_ids=['My', 'Data'], prefix_root_ns=True)) == "::My::Data"


def test_fqn_fail():
    with pytest.raises(TypeError) as exc:
        Fqn(ns_ids=123)
    assert str(exc.value) == 'NameSpaceIds type expected'


def test_type_default_ok():
    sut = TypeDesc(Fqn(['My', 'Data']))
    assert str(sut.fqn) == 'My::Data'
    assert sut.postfix == TypePostfix.NONE
    assert sut.default_value is None
    assert str(sut) == 'My::Data'


def test_type_with_default_value():
    sut = TypeDesc(Fqn(['My', 'Data']), default_value='123')
    assert sut.default_value == '123'

    with pytest.raises(CppGenError) as exc:
        TypeDesc(Fqn(['My', 'Data']), default_value=123.456)
    assert str(exc.value) == 'default_value must be a string type'


def test_type_const():
    sut = TypeDesc(fqn=Fqn(['My', 'Data']), const=True)
    assert str(sut) == 'const My::Data'


def test_type_other_postfices():
    assert str(TypeDesc(Fqn(['My', 'Data']), postfix=TypePostfix.REFERENCE)) == 'My::Data&'
    assert str(TypeDesc(Fqn(['My', 'Data']), postfix=TypePostfix.POINTER)) == 'My::Data*'
    assert str(TypeDesc(Fqn(['My', 'Data'], prefix_root_ns=True))) == '::My::Data'
    assert str(TypeDesc(Fqn(['Number'], prefix_root_ns=True), const=True)) == 'const ::Number'


def test_struct_decl_fail():
    with pytest.raises(CppGenError) as exc:
        Struct(name='', contents='')
    assert str(exc.value) == 'name must not be empty'


def test_struct_decl_without_contents():
    assert str(Struct(name='MyStruct')) == STRUCT_DECL_ENPTY


def test_struct_decl():
    assert str(Struct(name='MyStruct',
                      contents=TextBlock(CONTENTS_SINGLE_LINE))) == STRUCT_DECL_CONTENTS


def test_class_decl_fail():
    with pytest.raises(CppGenError) as exc:
        Class(name='')
    assert str(exc.value) == 'name must not be empty'


def test_class_decl_without_contents():
    assert str(Class(name='MyClass')) == CLASS_DECL_ENPTY


def test_class_decl():
    assert str(Class(name='MyClass',
                     contents=TextBlock(CONTENTS_MULTI_LINE))) == CLASS_DECL_CONTENTS


def test_access_specified_section():
    assert PUBLIC_SECTION == str(
        AccessSpecifiedSection(AccessSpecifier.PUBLIC, CONTENTS_MULTI_LINE))
    assert PROTECTED_SECTION == str(
        AccessSpecifiedSection(AccessSpecifier.PROTECTED, CONTENTS_SINGLE_LINE))
    assert PRIVATE_SECTION == str(
        AccessSpecifiedSection(AccessSpecifier.PRIVATE, CONTENTS_SINGLE_LINE))
    assert ANYNOMOUS_SECTION == str(
        AccessSpecifiedSection(AccessSpecifier.ANONYMOUS, CONTENTS_MULTI_LINE))


def test_param_with_default1():
    type_desc = TypeDesc(Fqn(['int']), default_value='123')
    sut = Param(type_desc=type_desc, name='number')
    assert sut.name == 'number'
    assert sut.as_decl == 'int number = 123'
    assert sut.as_def == 'int number'


def test_param_with_default2():
    type_desc = TypeDesc(fqn=Fqn(['std', 'string']), postfix=TypePostfix.REFERENCE,
                         const=True, default_value='""')
    sut = Param(type_desc=type_desc, name='message')
    assert str(sut.type_desc) == 'const std::string&'
    assert sut.as_decl == 'const std::string& message = ""'
    assert sut.as_def == 'const std::string& message'


def test_param_without_default():
    type_desc = TypeDesc(fqn=Fqn(['MyType']), postfix=TypePostfix.POINTER, const=False)
    sut = Param(type_desc=type_desc, name='example')
    assert str(sut.type_desc) == 'MyType*'
    assert sut.as_decl == 'MyType* example'
    assert sut.as_def == 'MyType* example'


def test_param_str_fail():
    with pytest.raises(CppGenError) as exc:
        str(Param(type_desc=TypeDesc(Fqn(['int'])), name='number'))
    assert str(exc.value) == 'instead of str(), access the properties as_decl or as_def'


def test_constructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(Constructor(scope=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), access the properties as_decl or as_def'

    with pytest.raises(CppGenError) as exc:
        Constructor(scope=None)
    assert str(exc.value) == 'scope must be a Class or Struct'

    with pytest.raises(CppGenError) as exc:
        Constructor(scope=Class('MyToaster'), initialization='default',
                    member_initlist=['m_count(1)'])
    assert str(exc.value) == 'not allowed to have both a constructor initialization and ' \
                             'a member initializer list'

    with pytest.raises(CppGenError) as exc:
        Constructor(scope=Class('MyToaster'), member_initlist=123)
    assert str(exc.value) == 'the member initializer list must be a list of strings'


def test_constructor_ok():
    class_sut = Constructor(scope=Class('MyToaster'))
    assert class_sut.as_decl == CONSTRUCTOR_DECL_MINIMAL
    assert class_sut.as_def == CONSTRUCTOR_DEF_MINIMAL

    struct_sut = Constructor(scope=Struct('MyToaster'))
    assert struct_sut.as_decl == CONSTRUCTOR_DECL_MINIMAL
    assert struct_sut.as_def == CONSTRUCTOR_DEF_MINIMAL


def test_constructor_params_and_content_ok():
    param1 = param_t(['int'], 'x')
    param2 = param_t(['size_t'], 'y', '123u')
    sut = Constructor(scope=Class('MyToaster'), params=[param1, param2],
                      contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == CONSTRUCTOR_PARAMS_DECL
    assert sut.as_def == CONSTRUCTOR_PARAMS_DEF


def test_explicit_constructor_ok():
    param1 = param_t(['int'], 'x')
    param2 = param_t(['size_t'], 'y', '123u')
    sut = Constructor(scope=Class('MyToaster'), explicit=True, params=[param1, param2],
                      contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == CONSTRUCTOR_EXPLICIT_DECL
    assert sut.as_def == CONSTRUCTOR_PARAMS_DEF


def test_constructor_with_default_initialization():
    sut = Constructor(scope=Class('MyToaster'), initialization='default')
    assert sut.as_decl == CONSTRUCTOR_INITIALIZATION_DEFAULT_DECL
    assert sut.as_def == NOTHING_GENERATED


def test_constructor_with_member_initializer_list_single_item():
    sut = Constructor(scope=Class('MyToaster'),
                      member_initlist=['m_number(1)'])
    assert sut.as_decl == CONSTRUCTOR_DECL_MINIMAL
    assert sut.as_def == CONSTRUCTOR_MEMBER_INITIALIZER_LIST_SIMPLE_DEF


def test_constructor_with_member_initializer_list_multiple_items():
    sut = Constructor(scope=Class('MyToaster'),
                      member_initlist=['m_number(1)', 'm_two{2 }', 'm_xyz ("Two")'])
    assert sut.as_decl == CONSTRUCTOR_DECL_MINIMAL
    assert sut.as_def == CONSTRUCTOR_MEMBER_INITIALIZER_LIST_MULTIPLE_DEF


def test_destructor_fail():
    with pytest.raises(CppGenError) as exc:
        str(Destructor(scope=Class('MySubClass')))
    assert str(exc.value) == 'instead of str(), access the properties as_decl or as_def'

    with pytest.raises(CppGenError) as exc:
        Destructor(scope=None)
    assert str(exc.value) == 'scope must be a Class or Struct'


def test_destructor_ok():
    class_sut = Destructor(scope=Class('MyToaster'))
    assert class_sut.as_decl == DESTRUCTOR_DECL_MINIMAL
    assert class_sut.as_def == DESTRUCTOR_DEF_MINIMAL

    struct_sut = Destructor(scope=Struct('MyToaster'))
    assert struct_sut.as_decl == DESTRUCTOR_DECL_MINIMAL
    assert struct_sut.as_def == DESTRUCTOR_DEF_MINIMAL


def test_destructor_content_ok():
    class_sut = Destructor(scope=Class('MyToaster'), contents=CONTENTS_MULTI_LINE)
    assert class_sut.as_decl == DESTRUCTOR_DECL_MINIMAL
    assert class_sut.as_def == DESTRUCTOR_CONTENT_DEF


def test_destructor_with_default_initialization():
    sut = Destructor(scope=Class('MyToaster'), initialization='default')
    assert sut.as_decl == DESTRUCTOR_INITIALIZATION_DEFAULT_DECL
    assert sut.as_def == NOTHING_GENERATED


def test_destructor_with_default_initialization_and_override():
    sut = Destructor(scope=Class('MyToaster'), override=True, initialization='default')
    assert sut.as_decl == DESTRUCTOR_OVERRIDE_INITIALIZATION_DEFAULT_DECL
    assert sut.as_def == NOTHING_GENERATED


def test_function_fail():
    with pytest.raises(CppGenError) as exc:
        Function(return_type='invalid', name='')
    assert str(exc.value) == 'return_type must be TypeDesc'

    with pytest.raises(CppGenError) as exc:
        Function(return_type=void_t(), name='')
    assert str(exc.value) == 'name must not be empty'

    with pytest.raises(CppGenError) as exc:
        str(Function(return_type=void_t(), name='Calculate'))
    assert str(exc.value) == 'instead of str(), access the properties as_decl or as_def'


def test_function_minimal():
    sut = Function(return_type=void_t(), name='Calculate')
    assert sut.as_decl == FUNCTION_DECL_MINIMAL
    assert sut.as_def == FUNCTION_DEF_MINIMAL


def test_struct_member_function_minimal():
    sut = Function(return_type=void_t(), name='Calculate', scope=Struct('MyStruct'))
    assert sut.as_decl == FUNCTION_DECL_MINIMAL
    assert sut.as_def == STRUCT_MEMBER_FUNCTION_DEF_MINIMAL


def test_class_member_function_minimal():
    sut = Function(return_type=void_t(), name='Calculate', scope=Struct('MyClass'))
    assert sut.as_decl == FUNCTION_DECL_MINIMAL
    assert sut.as_def == CLASS_MEMBER_FUNCTION_DEF_MINIMAL


def test_function_params():
    param1 = param_t(['int'], 'x')
    param2 = param_t(['size_t'], 'y', '123u')
    sut = Function(return_type=void_t(), name='Calculate', params=[param1, param2],
                   contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == FUNCTION_PARAMS_DECL
    assert sut.as_def == FUNCTION_PARAMS_DEF


def test_static_function():
    sut = Function(prefix=FunctionPrefix.STATIC, return_type=int_t(), name='Process',
                   params=[param_t(['int'], 'x')])
    assert sut.as_decl == STATIC_FUNCTION_DECL
    assert sut.as_def == STATIC_FUNCTION_DEF


def test_static_member_function():
    sut = Function(prefix=FunctionPrefix.STATIC, return_type=int_t(), name='Process',
                   params=[param_t(['int'], 'x')], scope=Struct('MyStruct'))
    assert sut.as_decl == STATIC_FUNCTION_DECL
    assert sut.as_def == STATIC_MEMBER_FUNCTION_DEF


def test_virtual_member_function_fail():
    with pytest.raises(CppGenError) as exc:
        Function(prefix=FunctionPrefix.VIRTUAL, return_type=float_t(), name='Calc')
    assert str(exc.value) == 'missing scope for prefix "virtual"'


def test_virtual_member_function():
    sut = Function(prefix=FunctionPrefix.VIRTUAL, return_type=float_t(),
                   name='Calc', params=[param_t(['float'], 'y')],
                   scope=Class('MyClass'))
    assert sut.as_decl == VIRTUAL_MEMBER_FUNCTION_DECL
    assert sut.as_def == VIRTUAL_MEMBER_FUNCTION_DEF


def test_function_initialization_pure_virtual_fail():
    with pytest.raises(CppGenError) as exc:
        Function(return_type=void_t(), name='Calc', initialization='0')
    assert str(exc.value) == 'missing prefix "virtual" when initializing with "=0"'

    with pytest.raises(CppGenError) as exc:
        Function(prefix=FunctionPrefix.VIRTUAL, return_type=void_t(), name='Calc',
                 initialization='0')
    assert str(exc.value) == 'missing scope for prefix "virtual"'


def test_function_initialization_pure_virtual():
    sut = Function(prefix=FunctionPrefix.VIRTUAL, return_type=void_t(),
                   name='Calc', initialization='0', scope=Class('MyClass'))
    assert sut.as_decl == PURE_VIRTUAL_MEMBER_FUNCTION_DECL
    assert sut.as_def == NOTHING_GENERATED


def test_function_const():
    sut = Function(return_type=void_t(), name='Calc', cv='const', contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == FUNCTION_CONST_DECL
    assert sut.as_def == FUNCTION_CONST_DEF


def test_member_function_const():
    sut = Function(return_type=void_t(), name='Calc', cv='const', scope=Class('MyClass'))
    assert sut.as_decl == FUNCTION_CONST_DECL
    assert sut.as_def == MEMBER_FUNCTION_CONST_DEF


def test_member_function_override():
    sut = Function(return_type=void_t(), name='Calc', override=True,
                   contents=CONTENTS_MULTI_LINE,
                   scope=Class('MyClass'))
    assert sut.as_decl == MEMBER_FUNCTION_OVERRIDE_DECL
    assert sut.as_def == MEMBER_FUNCTION_OVERRIDE_DEF


def test_member_variable():
    assert str(MemberVariable(type=float_t(), name='MyNumber')) == 'float MyNumber;'
    assert str(
        MemberVariable(type=TypeDesc(Fqn(['My', 'ILedControl']), postfix=TypePostfix.REFERENCE),
                       name='MyPort')) == 'My::ILedControl& MyPort;'


def test_member_variable_fail():
    with pytest.raises(TypeError) as exc:
        MemberVariable(type=123, name='')
    assert str(exc.value) == 'type of "type" must be TypeDesc'

    with pytest.raises(TypeError) as exc:
        MemberVariable(type=void_t(), name=123)
    assert str(exc.value) == 'name must be a non-empty string'

    with pytest.raises(TypeError) as exc:
        MemberVariable(type=void_t(), name='')
    assert str(exc.value) == 'name must be a non-empty string'


# test the helper functions

def test_gen_fqn_ok():
    """"Test the generate fqn function, good weather"""
    assert gen_fqn(['My', 'Data']) == 'My::Data'
    assert gen_fqn([]) == ''
    assert gen_fqn(None) == ''
    assert gen_fqn(ns_ids=['My', 'Data'], prefix_root_ns=True) == '::My::Data'
    assert gen_fqn(ns_ids=[], prefix_root_ns=True) == ''
    assert gen_fqn(None, True) == ''


def test_gen_fqn_fail():
    """"Test the generate fqn function, bad weather"""
    with pytest.raises(TypeError) as exc:
        gen_fqn(123)
    assert str(exc.value) == 'NameSpaceIds type expected'


def test_type_helpers():
    assert void_t() == TypeDesc(fqn=Fqn(['void']))
    assert int_t() == TypeDesc(fqn=Fqn(['int']))
    assert float_t() == TypeDesc(fqn=Fqn(['float']))
    assert double_t() == TypeDesc(fqn=Fqn(['double']))


def test_decl_var_t_helper():
    sut = decl_var_t(Fqn(['My', 'Type']), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type m_data;'


def test_decl_var_ref_t_helper():
    sut = decl_var_ref_t(Fqn(['My', 'Type']), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type& m_data;'


def test_decl_var_ptr_t_helper():
    sut = decl_var_ptr_t(Fqn(['My', 'Type']), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type* m_data;'


def test_param_t_helper():
    sut = param_t(['std', 'string'], 'message')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'std::string message'
    assert sut.as_def == 'std::string message'


def test_param_t_helper_with_default():
    sut = param_t(['std', 'string'], 'message', '"MyDefault"')
    assert sut.as_decl == 'std::string message = "MyDefault"'
    assert sut.as_def == 'std::string message'


def test_const_param_ref_t_helper():
    sut = const_param_ref_t(['IBigStruct'], 'data')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct& data'
    assert sut.as_def == 'const IBigStruct& data'


def test_const_param_ref_t_helper_with_default():
    sut = const_param_ref_t(['IBigStruct'], 'data', 'nullptr')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct& data = nullptr'
    assert sut.as_def == 'const IBigStruct& data'


def test_const_param_ptr_t_helper():
    sut = const_param_ptr_t(['IBigStruct'], 'data')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct* data'
    assert sut.as_def == 'const IBigStruct* data'


def test_const_param_ptr_t_helper_with_default():
    sut = const_param_ptr_t(['IBigStruct'], 'data', 'nullptr')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct* data = nullptr'
    assert sut.as_def == 'const IBigStruct* data'


# test the helper classes

class ContainerTestCase(TestCase):
    sut: Container

    def setUp(self):
        self.sut = Container()

    def test_add_invalid_type(self):
        with pytest.raises(TypeError) as exc:
            self.sut.add_unique(123)
        assert str(exc.value) == 'type can not be added'

    def test_add_one_param(self):
        param_name = 'message'
        param = param_t(['std', 'string'], param_name)
        assert isinstance(self.sut.add_unique(param), Container), 'self is returned (Fluent Itf)'
        assert len(self.sut.params) == 1
        assert param_name in self.sut.params

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique(param)
        assert str(exc.value) == 'Param "message" already present'

    def test_add_list_of_params_ok(self):
        param1 = param_t(['std', 'string'], 'message')
        param2 = const_param_ref_t(['IBigStruct'], 'data', 'nullptr')
        self.sut.add_unique([param1, param2])
        assert len(self.sut.params) == 2
        assert 'message' in self.sut.params
        assert 'data' in self.sut.params

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique([param1, param2])
        assert str(exc.value) == 'Param "message" already present'

    def test_add_one_member_variable(self):
        member_variable_name = 'myNumber'
        var = MemberVariable(type=float_t(), name=member_variable_name)
        self.sut.add_unique(var)
        assert len(self.sut.member_variables) == 1
        assert member_variable_name in self.sut.member_variables

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique(var)
        assert str(exc.value) == 'Member Variable "myNumber" already present'

    def test_add_multiple_member_variables(self):
        var1 = MemberVariable(type=float_t(), name='myNumber')
        var2 = MemberVariable(type=int_t(), name='someIndex')
        self.sut.add_unique([var1, var2])
        assert len(self.sut.member_variables) == 2
        assert 'myNumber' in self.sut.member_variables
        assert 'someIndex' in self.sut.member_variables

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique([var1, var2])
        assert str(exc.value) == 'Member Variable "myNumber" already present'

    def test_add_one_function(self):
        function_name = 'Calculate'
        func = Function(return_type=void_t(), name=function_name)
        self.sut.add_unique(func)
        assert len(self.sut.functions) == 1
        assert function_name in self.sut.functions

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique(func)
        assert str(exc.value) == 'Function "Calculate" already present'

    def test_add_multiple_functions(self):
        func1 = Function(return_type=void_t(), name='Calculate')
        func2 = Function(return_type=int_t(), name='PerformAction', scope=Class('MyClass'))
        self.sut.add_unique([func1, func2])
        assert len(self.sut.functions) == 2
        assert 'Calculate' in self.sut.functions
        assert 'PerformAction' in self.sut.functions

        with pytest.raises(CppGenError) as exc:
            self.sut.add_unique([func2, func1])
        assert str(exc.value) == 'Function "PerformAction" already present'
