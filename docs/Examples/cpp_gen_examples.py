"""
Examples of using the cpp_gen module. This module generates C++ code that
takes C++17 as standard (see Namespaces as example).

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system-under-test
from dznpy.cpp_gen import Comment, Fqn, Namespace, Struct, Class, ProjectIncludes, SystemIncludes, \
    AccessSpecifiedSection, AccessSpecifier, TypeDesc, TemplateArg, TypePostfix, fqn_t, \
    TypeConstness, void_t, int_t, float_t, double_t, std_string_t, const_std_string_ref_t, Param, \
    MemberVariable, Constructor, FunctionInitialization, Function, decl_var_t, \
    decl_var_ref_t, decl_var_ptr_t, TypeAsIs, param_t, const_param_ref_t, FunctionPrefix
from dznpy.cpp_gen_rule_of_five import Destructor
from dznpy.scoping import NamespaceIds, ns_ids_t
from dznpy.text_gen import TextBlock, TB


def example_comment():
    """Example of using the cpp_gen comment construct.
    Basically the cpp_gen Comment class depends on the TextBlock construct found in text_gen.
    As line prefix two slashes '//' is applied for the entire text block to make it a
    modern C++ compliant comment. Note that cpp_gen Comment does not support '/*' and '*/'
    comment blocks."""

    # Example of a single line comment
    my_comment = Comment(content='My only comment')
    print(my_comment)

    # Example of a multi line comment block
    print(Comment(['Line 1', 'Line 2', 'Line 3']))


def example_includes():
    """Example of using the System Includes and Project IncludesFqn dataclasses."""

    # A default empty list of system includes, resulting in just a comment
    print(SystemIncludes(includes=[]))

    # A single system include
    print(SystemIncludes(includes=['cstdio']))

    # Multiple system includes, the associated comment will be pronounced in plural form
    print(SystemIncludes(includes=['string', 'memory']))

    # A default empty list of project includes, resulting in just a comment
    print(ProjectIncludes(includes=[]))

    # A single project include
    print(ProjectIncludes(includes=['MyProject.h']))

    # Multiple project includes, the associated comment will be pronounced in plural form
    print(ProjectIncludes(includes=['MyProject.h', 'SomeOtherFile.hh']))


def example_fqn():
    """Example of using the Fqn class that depends on the NamespaceIds type from the
    text_gen module."""

    # Example of specifying an empty NamespaceIds
    empty_fqn = Fqn(NamespaceIds([]))
    print(f'An empty NamespaceIds argument leads to an empty Fqn: {str(empty_fqn) == ""}')

    # Example of a worthy NamespaceIds leading to 'My::Project'
    simple_fqn = Fqn(NamespaceIds(['My', 'Project']))
    print(simple_fqn)
    print(simple_fqn.ns_ids)  # directly access and print a NamespaceIds, note it is dot-delimited!

    # Example of a Type Creation Function for NamespaceIds and the specification to
    # prefix it with the '::' root namespace indication leading to '::My::Deeply::Nested::Project'
    cpprooted_fqn = fqn_t('My.Deeply.Nested.Project', prefix_root_ns=True)
    print(cpprooted_fqn)

    # Type Creation Function
    print(fqn_t('My.Project.Garage'))
    print(fqn_t(ns_ids='My.Project.Garage.Door', prefix_root_ns=True))
    print(fqn_t('My.Project.Garage.SideDoor', True))  # omit keywords


def example_namespace():
    """Example of using the cpp_gen namespace construct. Both a global namespace as a
    fully qualified named (FQN) namespaces can be defined. For the FQN namespace the modern
    C++17 ::-delimited notation is used to omit (deep) nesting of 'namespace' keywords.
    The namespace type is a regular Python class instead of a frozen dataclass because it
    supports setting the contents at a later moment."""

    # A global namespace without contents, the stringification will be empty
    global_namespace_ids = NamespaceIds()
    print(Namespace(ns_ids=global_namespace_ids, global_namespace_on_empty_ns_ids=True))

    # A global namespace with a simple comment as contents right from the start
    print(Namespace(ns_ids=NamespaceIds(), contents=TextBlock(Comment('My comment')),
                    global_namespace_on_empty_ns_ids=True))

    # An unnamed namespace without contents
    unnamed_namespace_ids = NamespaceIds()
    print(Namespace(ns_ids=unnamed_namespace_ids))

    # An unnamed namespace with a simple comment as contents right from the start
    print(Namespace(ns_ids=NamespaceIds(), contents=TextBlock(Comment('My comment'))))

    # A fully qualified namespace (FQN) identification without contents
    fqn_namespace_ids = NamespaceIds(['My', 'Name', 'Space'])
    print(Namespace(ns_ids=fqn_namespace_ids))

    # A FQN namespace with another FQN namespace as contents right from the start
    inner_ns = Namespace(ns_ids=NamespaceIds(['Inner']))
    print(Namespace(ns_ids=fqn_namespace_ids, contents=TextBlock(inner_ns)))

    # A FQN namespace with post assigning contents
    my_namespace = Namespace(ns_ids=ns_ids_t('My.Name.Space'))  # using a Type Creation Function
    my_namespace.contents = TB(Struct(name='CalculationData'))  # see alias TB instead of TextBlock
    print(my_namespace)
    print(my_namespace.ns_ids)  # directly access and print, note that one is dot-delimited!


def example_simple_struct_class_access_specification():
    """Example of using the Struct, Class and Access Specification types.
    The struct and class types are a regular Python classes instead of frozen dataclasses because
    they support setting the contents at a later moment."""
    # A struct without contents
    struct = Struct(name='MyData')
    print(struct)

    # A class without contents
    cls = Class('MyClass')
    print(cls)

    # A private access specified section
    private_access = AccessSpecifiedSection(access_specifier=AccessSpecifier.PRIVATE,
                                            contents=TB(Comment('Hello')))
    print(private_access)

    # A public access specified section
    public_access = AccessSpecifiedSection(access_specifier=AccessSpecifier.PUBLIC,
                                           contents=TB(Comment('Hi audience')))
    print(public_access)

    # A protected access specified section
    protected_access = AccessSpecifiedSection(AccessSpecifier.PROTECTED,
                                              TB(Comment('My DM Zone')))
    print(protected_access)

    # An anonymous access specified section
    anonynmous_access = AccessSpecifiedSection(AccessSpecifier.ANONYMOUS,
                                               TB(Comment('In the open')))
    print(anonynmous_access)

    # A struct with contents right from the start
    struct = Struct(name='MyData', decl_contents=TB(anonynmous_access))
    print(struct)

    # A struct with contents right from the start
    cls = Class(name='MyClass', decl_contents=TB(public_access))
    print(cls)

    # A struct with post assigning contents
    struct = Struct('MyDataCollection')
    struct.decl_contents = TB(private_access)
    print(struct)

    # A class with post assigning contents
    cls = Struct('SomeFunctionality')
    cls.decl_contents = TB(protected_access)
    print(cls)


def example_type_description():
    """Example of using the TypeDesc, a dataclass that describes the type by a fully qualified
    name and allows for various options like prefixing (e.g. '::', 'const') and/or
    postfixing (e.g. 'const', '&', '*' '* const', template argument).
    This class depends on the Fqn type from the same cpp_gen module."""

    # A type description with a simple fully qualified name (without namespace)
    type_simple = TypeDesc(fqname=fqn_t('Door'))  # using fqn_t Type Creation Function
    print(type_simple)

    # A type description with a fully qualified name, without and with a root namespace indicator
    type_fqn = TypeDesc(fqname=fqn_t('My.House.Door'))
    print(type_fqn)
    type_fqn_root_ns = TypeDesc(fqname=fqn_t('My.House.Door', prefix_root_ns=True))
    print(type_fqn_root_ns)

    # A type description with a 'const' prefix (in the category 'matter of style')
    my_fqn = fqn_t('My.House.Door')
    type_const_prefix = TypeDesc(my_fqn, constness=TypeConstness.PREFIXED)
    print(type_const_prefix)

    # A type description with a 'const' postfix (in the category 'matter of style')
    my_fqn = fqn_t('float')
    type_const_postfix = TypeDesc(my_fqn, constness=TypeConstness.POSTFIXED)
    print(type_const_postfix)

    # A type description with a Template Argument
    my_fqn = fqn_t('My.House.Door')
    tpl_arg = TemplateArg(fqn_t(['Arch', 'IFrontDoor']))
    type_tpl = TypeDesc(my_fqn, template_arg=tpl_arg)
    print(type_tpl)

    # A type description with a 'C++ reference' postfix
    my_fqn = fqn_t('My.House.Door')
    type_ref = TypeDesc(my_fqn, postfix=TypePostfix.REFERENCE)
    print(type_ref)

    # A type description with a 'C pointer' postfix
    my_fqn = fqn_t('My.House.Door')
    type_ptr = TypeDesc(my_fqn, postfix=TypePostfix.POINTER)
    print(type_ptr)

    # A type description with a 'const C pointer' postfix
    my_fqn = fqn_t('int')
    type_ptr_const = TypeDesc(my_fqn, postfix=TypePostfix.POINTER_CONST)
    print(type_ptr_const)

    # A type description showing all options
    my_fqn = fqn_t('House.Frontdoor', prefix_root_ns=True)
    type_full = TypeDesc(fqname=my_fqn,
                         constness=TypeConstness.POSTFIXED,
                         template_arg=TemplateArg(fqn_t(['Hal', 'IDoor'], prefix_root_ns=True)),
                         postfix=TypePostfix.POINTER_CONST)
    print(type_full)

    # Type Creation Functions
    print(void_t())
    print(int_t())
    print(float_t())
    print(double_t())
    print(std_string_t())
    print(const_std_string_ref_t())


def example_param():
    """Example of using the Param dataclass that is to be used when dealing with parameters that
    are part of functions, constructors and class methods. The dataclass can be asked to generate
    a string for C++ declaration of C++ definition. They mainly differ at the point of C++
    declaration where it is possible to specify a default value.
    The Param dataclass consists of a TypeDesc, a name and optionally a default value."""

    # A simple parameter without a default
    param_double = Param(double_t(), 'number')  # Tip: use TypeDesc Type Creation Helper(s)
    print(param_double.as_decl())
    print(param_double.as_def())

    # A parameter with a default
    param_stdstring = Param(std_string_t(), 'message', '""')
    print(param_stdstring.as_decl())
    print(param_stdstring.as_def())

    # Preview of how multiple parameters are typically part of a function (or constructor)
    my_function = Function(return_type=void_t(),
                           name="MyFunction",
                           params=[param_double, param_stdstring],
                           contents=TB(Comment("Hi there")))
    print(my_function.as_decl())
    print(my_function.as_def())


def example_member_variable():
    """Example of using MemberVariable. The textual output of this dataclass is typically part of
    a Struct or Class contents. It is left to the developer's freedom to integrate this.
    An example could be to include/assign the textual output of one or more MemberVariable
    instances to the contents of a AccessSpecifiedSection.
    Furthermore, a MemberVariable has much in common with Param. Hence, it is derived from it.
    However, MemberVariable only supports as_decl(). The internal function str() will indirectly
    call as_decl(). The reason there is no as_def() is because it's in the nature of MemberVariable
    to be specified in the declaration of the Struct or Class; not in the definition clause."""

    # A simple parameter without a default
    mv_double = MemberVariable(double_t(), 'number')
    print(mv_double.as_decl())
    print(mv_double)  # also supporting str(), but note it post-ambles with a newline

    # A parameter with a default
    mv_stdstring = MemberVariable(std_string_t(), 'message', '"my default str"')
    print(mv_stdstring.as_decl())
    print(mv_stdstring)

    # Preview of how a MemberVariable can be integrated into a Struct
    my_struct = Struct(name='MyData')
    my_struct.decl_contents = TB([AccessSpecifiedSection(AccessSpecifier.ANONYMOUS,
                                                         mv_double.as_decl()),
                                  AccessSpecifiedSection(AccessSpecifier.PRIVATE,
                                                         mv_stdstring.as_decl())
                                  ])
    print(my_struct)

    # Type Creation Functions
    print(decl_var_t(fqn_t('int'), 'number'))
    print(decl_var_ref_t(fqn_t('std.string'), 'message'))
    print(decl_var_ptr_t(fqn_t('double'), 'fract'))


def example_constructor_destructor():
    """Example of using the Constructor and Destructor, in combination with a Class or Struct."""

    # Most basic constructor and destructor for a class.
    # Note: to prevent 'chicken-and-egg',
    # 1. first the class with a name shall be made known, it acts as the 'parent'
    # 2. Constructor and Destructor depend on this name from the 'parent'
    # 3. class declaration contents can now be filled with Constructor and Destructor
    cls = Class('MyClass')
    constr = Constructor(parent=cls)
    destr = Destructor(parent=cls)
    cls.decl_contents = TB([constr.as_decl(), destr.as_decl()])

    print(cls)  # for in the C++ headerfile
    print(constr.as_def())  # C++ sourcefile
    print(destr.as_def())  # C++ sourcefile

    # Explicit marked constructor
    cls = Class('GarageDoor')
    constr = Constructor(parent=cls, explicit=True)
    cls.decl_contents = TB(constr.as_decl())
    print(cls)  # for in the C++ headerfile
    print(constr.as_def())  # C++ sourcefile

    # Constructor parameters
    param_int = Param(int_t(), 'number')
    param_float = Param(float_t(), 'fract')
    cls = Struct('DoorData')
    constr = Constructor(parent=cls, params=[param_int, param_float])
    cls.decl_contents = TB(constr.as_decl())
    print(cls)  # for in the C++ headerfile
    print(constr.as_def())  # C++ sourcefile

    # Constructor with a member initialization list
    # Note: in this case the developer must manually provide the member initialization
    #       and ensure it can be compiled. There is no intelligent logic at this moment
    #       to refer to class member variables
    constr = Constructor(parent=cls,
                         params=[param_int],
                         member_initlist=['m_number(number)', 'm_pi{3.14}'])
    mv_number = MemberVariable(int_t(), 'm_number')  # example class member variable (1)
    mv_double = MemberVariable(double_t(), 'm_pi')  # example class member variable (2)
    cls.decl_contents = TB([constr.as_decl(), mv_number, mv_double])
    print(cls)  # for in the C++ headerfile
    print(constr.as_def())  # C++ sourcefile

    # Constructor initialization
    struct = Struct('Doorbell')
    constr = Constructor(parent=struct, initialization=FunctionInitialization.DEFAULT)
    struct.decl_contents = TB(constr.as_decl())
    print(struct)  # for in the C++ headerfile
    print(constr.as_def())  # No sourcecode, because of '= default/delete' initialization

    # Destructor initialization and override
    cls = Class('HouseDoor')
    destr = Destructor(parent=cls,
                       override=True,
                       initialization=FunctionInitialization.DEFAULT)
    cls.decl_contents = TB(destr.as_decl())
    print(cls)  # for in the C++ headerfile
    print(destr.as_def())  # No sourcecode, because of '= default' initialization


def example_function():
    """Example of using a Function, separately or in combination with a Class or Struct."""

    # An individual function
    func = Function(parent=None,
                    return_type=int_t(),
                    name='Calculate')
    print(func.as_decl())
    print(func.as_def())

    # A struct member function
    struct = Struct('Villa')
    func = Function(parent=struct,
                    return_type=TypeAsIs('Hal::Device'),
                    name='DoorHandle')
    print(func.as_decl())
    print(func.as_def())

    # A virtual class member function with constness ('volatile' is another example)
    cls = Class('Car')
    func = Function(parent=cls,
                    prefix=FunctionPrefix.VIRTUAL,
                    return_type=void_t(),
                    name='Brake',
                    cav='const')
    print(func.as_decl())
    print(func.as_def())

    # A class member function with parameters and -override- of assumed base class virtual method
    cls = Class('Boat')
    p1 = param_t(fqn_t('long'), 'speed', default_value='0')
    p2 = const_param_ref_t(fqn_t('std.string'), 'label')
    func = Function(parent=cls,
                    return_type=void_t(),
                    name='Throttle',
                    params=[p1, p2],
                    override=True)
    func.contents = TB(Comment('Some code'))
    print(func.as_decl())
    print(func.as_def())


def main():
    """Convergence point of executing all example code for the cpp_gen module."""

    example_includes()
    example_fqn()
    example_comment()
    example_namespace()
    example_simple_struct_class_access_specification()
    example_type_description()
    example_param()
    example_member_variable()
    example_constructor_destructor()
    example_function()


if __name__ == "__main__":
    main()
