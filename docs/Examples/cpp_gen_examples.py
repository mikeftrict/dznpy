"""
Examples of using the cpp_gen module. This module generates C++ code that
takes C++17 as standard (see Namespaces as example).

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system-under-test
from dznpy.cpp_gen import Comment, Fqn, Namespace, Struct, Class, ProjectIncludes, SystemIncludes, \
    AccessSpecifiedSection, AccessSpecifier, TypeDesc, TemplateArg, TypePostfix, fqn_t
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

    # Example of a Type Creation Function for NamespaceIds and the specification to
    # prefix it with the '::' root namespace indication leading to '::My::Deeply::Nested::Project'
    cpprooted_fqn = fqn_t('My.Deeply.Nested.Project', prefix_root_ns=True)
    print(cpprooted_fqn)


def example_namespace():
    """Example of using the cpp_gen namespace construct. Both a global namespace as a
    fully qualified named (FQN) namespaces can be defined. For the FQN namespace the modern
    C++17 ::-delimited notation is used to omit (deep) nesting of 'namespace' keywords.
    The namespace type is a regular Python class instead of a frozen dataclass because it
    supports setting the contents at a later moment."""

    # A global namespace without contents
    global_namespace_ids = NamespaceIds()
    print(Namespace(ns_ids=global_namespace_ids))

    # A global namespace with a simple comment as contents right from the start
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
    struct = Struct(name='MyData', contents=TB(anonynmous_access))
    print(struct)

    # A struct with contents right from the start
    cls = Class(name='MyClass', contents=TB(public_access))
    print(cls)

    # A struct with post assigning contents
    struct = Struct('MyDataCollection')
    struct.contents = TB(private_access)
    print(struct)

    # A class with post assigning contents
    cls = Struct('SomeFunctionality')
    cls.contents = TB(protected_access)
    print(cls)


def example_type_description():
    """Example of using the TypeDesc, a frozen dataclass that describes the type by a
    fully qualified name and optionally a prefix (e.g. '::', 'const') and/or
    postfix (e.g. '&', '*', template argument).
    This class depends on the Fqn type from the same cpp_gen module."""

    # A type description with a simple fully qualified name (without namespace)
    type_simple = TypeDesc(fqname=fqn_t('Door'))
    print(type_simple)

    # A type description with a fully qualified name, without and with a root namespace indicator
    type_fqn = TypeDesc(fqname=fqn_t('My.House.Door'))
    print(type_fqn)
    type_fqn_root_ns = TypeDesc(fqname=fqn_t('My.House.Door', prefix_root_ns=True))
    print(type_fqn_root_ns)

    # A type description with a 'const' prefix
    my_fqn = fqn_t('My.House.Door')
    type_const = TypeDesc(my_fqn, const=True)
    print(type_const)

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


def main():
    """Convergence  """
    # example_includes()
    # example_fqn()
    # example_comment()
    # example_namespace()
    # example_simple_struct_class_access_specification()
    example_type_description()


if __name__ == "__main__":
    main()
