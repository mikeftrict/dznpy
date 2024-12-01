"""
Testsuite validating the cpp_gen module

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest

# system-under-test
from dznpy.cpp_gen import *
from dznpy.scoping import NamespaceIds, NamespaceIdsTypeError, ns_ids_t, namespaceids_t

# test data
from common.testdata import *
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
    assert str(Namespace(ns_ids_t([]), contents='')) == GLOBAL_NAMESPACE_EMPTY
    assert str(Namespace(ns_ids_t(''), contents=CONTENTS_SINGLE_LINE)) == GLOBAL_NAMESPACE_CONTENTS


def test_fqn_namespace():
    assert str(Namespace(ns_ids_t('My.Project.XY'), contents='')) == FQN_NAMESPACE_EMPTY
    assert str(Namespace(ns_ids_t('My.Project.XY'), CONTENTS_SINGLE_LINE)) == FQN_NAMESPACE_CONTENTS


def test_namespace_with_textblock():
    tb = TextBlock([EOL, EOL, CONTENTS_SINGLE_LINE, EOL])
    assert str(Namespace(ns_ids=ns_ids_t(''), contents=tb)) == GLOBAL_NAMESPACE_TEXTBLOCK


def test_fqn_ok():
    """Test valid examples of the Fqn class"""
    # default:
    sut = Fqn(ns_ids=ns_ids_t('My.Data'))
    assert sut.ns_ids.items == ['My', 'Data']
    assert str(sut) == "My::Data"

    # empty ns ids leads to an empty Fqn
    assert str(Fqn(ns_ids=ns_ids_t([]))) == ''
    assert str(Fqn(ns_ids=ns_ids_t(''), prefix_root_ns=True)) == ''

    # enable prefixing with the C++ root namespace:
    assert str(Fqn(ns_ids=ns_ids_t('My.Data'), prefix_root_ns=True)) == "::My::Data"


def test_fqn_fail():
    """Test bad weather example of the Fqn class"""
    with pytest.raises(TypeError) as exc:
        Fqn(ns_ids=123)
    assert str(exc.value) == ARGUMENT123_NOT_NAMESPACEIDS


def test_typedesc_ok():
    """Test valid examples of the TypeDesc class"""
    sut = TypeDesc(Fqn(ns_ids_t('My.Data')))
    assert str(sut.fqn) == 'My::Data'
    assert sut.postfix == TypePostfix.NONE
    assert sut.default_value is None
    assert str(sut) == 'My::Data'

    # with default value specified
    assert TypeDesc(fqn_t('My.Data'), default_value='123').default_value == '123'


def test_typedesc_ok_with_template_arg():
    """Test valid examples of the TypeDesc class with a template argument"""
    sut1 = TypeDesc(fqn_t('My.Data', True), template_arg=TemplateArg(fqn_t('Hal.IHeater')))
    assert str(sut1) == '::My::Data<Hal::IHeater>'

    sut2 = TypeDesc(fqn_t('My.Project'), TemplateArg(fqn_t('Toaster', True)))
    assert str(sut2) == 'My::Project<::Toaster>'


def test_typedesc_fail_with_default_value():
    """Test incorrect examples of the TypeDesc class"""
    with pytest.raises(CppGenError) as exc:
        TypeDesc(Fqn(ns_ids_t('My.Data')), default_value=123.456)
    assert str(exc.value) == 'default_value must be a string type'


def test_typedesc_const():
    sut = TypeDesc(fqn=fqn_t('My.Data'), const=True)
    assert str(sut) == 'const My::Data'


def test_typedesc_other_postfices():
    assert str(TypeDesc(fqn_t('My.Data'), postfix=TypePostfix.REFERENCE)) == 'My::Data&'
    assert str(TypeDesc(fqn_t('My_Data_'), postfix=TypePostfix.POINTER)) == 'My_Data_*'
    assert str(TypeDesc(fqn_t('My::Data', prefix_root_ns=True))) == '::My::Data'
    assert str(TypeDesc(fqn_t('Number', True), const=True)) == 'const ::Number'


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
    type_desc = TypeDesc(fqn_t('int'), default_value='123')
    sut = Param(type_desc=type_desc, name='number')
    assert sut.name == 'number'
    assert sut.as_decl == 'int number = 123'
    assert sut.as_def == 'int number'


def test_param_with_default2():
    type_desc = TypeDesc(fqn=fqn_t(['std', 'string']), postfix=TypePostfix.REFERENCE,
                         const=True, default_value='""')
    sut = Param(type_desc=type_desc, name='message')
    assert str(sut.type_desc) == 'const std::string&'
    assert sut.as_decl == 'const std::string& message = ""'
    assert sut.as_def == 'const std::string& message'


def test_param_without_default():
    type_desc = TypeDesc(fqn=fqn_t('MyType'), postfix=TypePostfix.POINTER, const=False)
    sut = Param(type_desc=type_desc, name='example')
    assert str(sut.type_desc) == 'MyType*'
    assert sut.as_decl == 'MyType* example'
    assert sut.as_def == 'MyType* example'


def test_param_str_fail():
    with pytest.raises(CppGenError) as exc:
        str(Param(type_desc=TypeDesc(fqn_t('int')), name='number'))
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
    param1 = param_t(fqn_t('int'), 'x')
    param2 = param_t(fqn_t('size_t'), 'y', '123u')
    sut = Constructor(scope=Class('MyToaster'), params=[param1, param2],
                      contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == CONSTRUCTOR_PARAMS_DECL
    assert sut.as_def == CONSTRUCTOR_PARAMS_DEF


def test_explicit_constructor_ok():
    param1 = param_t(fqn_t('int'), 'x')
    param2 = param_t(fqn_t('size_t'), 'y', '123u')
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
    param1 = param_t(fqn_t('int'), 'x')
    param2 = param_t(fqn_t('size_t'), 'y', '123u')
    sut = Function(return_type=void_t(), name='Calculate', params=[param1, param2],
                   contents=CONTENTS_MULTI_LINE)
    assert sut.as_decl == FUNCTION_PARAMS_DECL
    assert sut.as_def == FUNCTION_PARAMS_DEF


def test_static_function():
    sut = Function(prefix=FunctionPrefix.STATIC, return_type=int_t(), name='Process',
                   params=[param_t(fqn_t('int'), 'x')])
    assert sut.as_decl == STATIC_FUNCTION_DECL
    assert sut.as_def == STATIC_FUNCTION_DEF


def test_static_member_function():
    sut = Function(prefix=FunctionPrefix.STATIC, return_type=int_t(), name='Process',
                   params=[param_t(fqn_t('int'), 'x')], scope=Struct('MyStruct'))
    assert sut.as_decl == STATIC_FUNCTION_DECL
    assert sut.as_def == STATIC_MEMBER_FUNCTION_DEF


def test_virtual_member_function_fail():
    with pytest.raises(CppGenError) as exc:
        Function(prefix=FunctionPrefix.VIRTUAL, return_type=float_t(), name='Calc')
    assert str(exc.value) == 'missing scope for prefix "virtual"'


def test_virtual_member_function():
    sut = Function(prefix=FunctionPrefix.VIRTUAL, return_type=float_t(),
                   name='Calc', params=[param_t(fqn_t('float'), 'y')],
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
        MemberVariable(type=TypeDesc(Fqn(ns_ids_t('My.ILedControl')), postfix=TypePostfix.REFERENCE),
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


###############################################################################
# Test the type creation functions
#


@pytest.mark.parametrize('param,exp_str',
                         [(NamespaceIds(['My', 'Data']), 'My::Data'),
                          (NamespaceIds([]), ''),
                          (namespaceids_t('My::Data'), 'My::Data'),
                          (ns_ids_t('My.Data'), 'My::Data'),
                          (None, ''),
                          ])
def test_fqn_t_ok_default(param, exp_str):
    """Test valid examples of the Fqn type creation function specifying only the mandatory argument."""
    sut = fqn_t(ns_ids=param)
    assert isinstance(sut, Fqn)
    assert str(sut) == exp_str


@pytest.mark.parametrize('param,opt_param,exp_str',
                         [(ns_ids_t('My.Data'), False, 'My::Data'),
                          (ns_ids_t('My.Data'), True, '::My::Data'),
                          (ns_ids_t([]), False, ''),
                          (ns_ids_t([]), True, ''),
                          (None, False, ''),
                          (None, True, ''),
                          ])
def test_fqn_t_ok_optionals(param, opt_param, exp_str):
    """Test valid examples of the Fqn type creation function with using the optional argument."""
    sut = fqn_t(ns_ids=param, prefix_root_ns=opt_param)
    assert isinstance(sut, Fqn)
    assert str(sut) == exp_str


def test_fqn_t_fail():
    """Test failing examples of the Fqn type creation function."""
    with pytest.raises(NamespaceIdsTypeError) as exc:
        fqn_t(123)
    assert str(exc.value) == 'Can not create NamespaceIds from argument "123"'


def test_typedesc_creator_functions():
    assert void_t() == TypeDesc(fqn=Fqn(ns_ids_t('void')))
    assert int_t() == TypeDesc(fqn=Fqn(ns_ids_t('int')))
    assert float_t() == TypeDesc(fqn=Fqn(ns_ids_t('float')))
    assert double_t() == TypeDesc(fqn=Fqn(ns_ids_t('double')))


def test_decl_var_t_ok():
    sut = decl_var_t(fqn_t('My.Type'), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type m_data;'


def test_decl_var_ref_t_ok():
    sut = decl_var_ref_t(fqn_t(['My', 'Type']), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type& m_data;'


def test_decl_var_ptr_t_ok():
    sut = decl_var_ptr_t(fqn_t('My::Type'), 'm_data')
    assert isinstance(sut, MemberVariable)
    assert str(sut) == 'My::Type* m_data;'


def test_param_t_ok():
    sut = param_t(fqn_t('std.string'), 'message')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'std::string message'
    assert sut.as_def == 'std::string message'


def test_param_t_ok_with_default():
    sut = param_t(fqn_t('std::string'), 'message', '"MyDefault"')
    assert sut.as_decl == 'std::string message = "MyDefault"'
    assert sut.as_def == 'std::string message'


def test_const_param_ref_t_ok():
    sut = const_param_ref_t(fqn_t('IBigStruct'), 'data')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct& data'
    assert sut.as_def == 'const IBigStruct& data'


def test_const_param_ref_t_ok_with_default():
    sut = const_param_ref_t(fqn_t('IBigStruct'), 'data', 'nullptr')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct& data = nullptr'
    assert sut.as_def == 'const IBigStruct& data'


def test_const_param_ptr_t_ok():
    sut = const_param_ptr_t(fqn_t(['IBigStruct']), 'data')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct* data'
    assert sut.as_def == 'const IBigStruct* data'


def test_const_param_ptr_t_ok_with_default():
    sut = const_param_ptr_t(fqn_t(['IBigStruct']), 'data', 'nullptr')
    assert isinstance(sut, Param)
    assert sut.as_decl == 'const IBigStruct* data = nullptr'
    assert sut.as_def == 'const IBigStruct* data'
