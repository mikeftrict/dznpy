"""
Module providing helpers for generating c++ source and header files

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
import abc
# system modules
from copy import deepcopy
from dataclasses import dataclass, field
import enum
from typing import List, Any, Optional

# dznpy modules
from .misc_utils import assert_t, assert_t_optional, is_strlist_instance, plural
from .scoping import NamespaceIds, ns_ids_t
from .text_gen import Indentizer, BulletList, TB, TextBlock


class CppGenError(Exception):
    """An error occurred during generating C++ code."""


class AccessSpecifier(enum.Enum):
    """Enum to indicate the access specifier."""
    PUBLIC = 'public:'
    PROTECTED = 'protected:'
    PRIVATE = 'private:'
    ANONYMOUS = None


class StructOrClass(enum.Enum):
    """Enum to indicate a struct or class."""
    STRUCT = 'struct'
    CLASS = 'class'


class FunctionPrefix(enum.Enum):
    """Enum to indicate the prefix of a function."""
    MEMBER_FUNCTION = None
    VIRTUAL = 'virtual'
    STATIC = 'static'


class TypePostfix(enum.Enum):
    """Enum to indicate the postfix of a type."""
    NONE = ''
    REFERENCE = '&'
    POINTER = '*'


@dataclass(frozen=True)
class Fqn:
    """Dataclass representing a C++ fully-qualified name by wrapping the NamespaceIds type and
    additionally providing the option to prefix stringification with the C++ root namespace.
    Example for ns_ids = 'my.data':

        My::Data
        ::My::Data
    """
    ns_ids: NamespaceIds
    prefix_root_ns: bool = False

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_t(self.ns_ids, NamespaceIds)

    def __str__(self) -> str:
        """Return the contents of this dataclass as a single string."""
        if not self.ns_ids.items:
            return ''
        all_ids = self.ns_ids.items
        return f'::{"::".join(all_ids)}' if self.prefix_root_ns else '::'.join(all_ids)


@dataclass(frozen=True)
class AccessSpecifiedSection:
    """Dataclass representing a C++ access specified section where the specified
    contents as TextBlock is indented. Example:

        public:
            <contents>

    or

        protected:
            <contents>

    or

        private:
            <contents>

    or in case of anonymous, just:

            <contents>

    """
    access_specifier: AccessSpecifier
    contents: TextBlock

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_t(self.access_specifier, AccessSpecifier)
        assert_t(self.contents, TextBlock)

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        return str(TB(self.access_specifier.value) + TB(self.contents).indent())


@dataclass(frozen=True)
class TemplateArg:
    """Dataclass representing a C++ Template Argument. Example:

        <MyType>
    """
    fqn: Fqn

    def __str__(self) -> str:
        return f'<{self.fqn}>'


@dataclass(frozen=True)
class TypeDesc:
    """Dataclass representing a C++ type description and an optional default value that is used
    by other cpp_gen types such as Param. Example:

        My::Data
        My::Data&
        My::Data*
        ::My::Data<Hal::IHeater>
        const My::Data
    """
    fqname: Fqn
    template_arg: Optional[TemplateArg] = None
    postfix: TypePostfix = TypePostfix.NONE
    const: bool = False
    default_value: str = None

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        if not str(self.fqname):
            raise CppGenError('fqname must not be empty')

        if self.default_value is not None and not isinstance(self.default_value, str):
            raise CppGenError('default_value must be a string type')

    def __str__(self) -> str:
        template_arg = f'{self.template_arg}' if self.template_arg else ''
        mandatory = f'{self.fqname}{template_arg}{self.postfix.value}'
        return f'const {mandatory}' if self.const else mandatory


@dataclass(frozen=True)
class Param:
    """Dataclass representing a C++ parameter as declaration and definition.
    Examples of a declaration:

        MyType* example
        int number = 123
        const std::string& message = ""
        ::My::Data<Hal::IHeater> = {}

    Examples of a definition:

        MyType* example
        int number
        const std::string& message
        ::My::Data<Hal::IHeater>
    """
    type_desc: TypeDesc
    name: str

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> str:
        """Compose the parameter as used in a declaration."""
        if self.type_desc.default_value:
            return f'{self.type_desc} {self.name} = {self.type_desc.default_value}'

        return self.as_def()

    def as_def(self) -> str:
        """Compose the parameter as used in a definition."""
        return f'{self.type_desc} {self.name}'


class Struct:
    """Dataclass representing a C++ struct clause with un-indented contents. The contents
    can be set later after initial construction but note that strict typing checking applues.
    Example:

        struct MyStruct
        {
        <contents>
        };
    """
    _name: str
    _contents: TextBlock

    def __init__(self, name: str, contents: Optional[TextBlock] = None):
        """Initialize with a name and optional initial content."""
        assert_t(name, str)
        assert_t_optional(contents, TextBlock)
        if not name:
            raise CppGenError('name must not be empty')

        self._name = name
        self._contents = contents if contents else TextBlock()
        self._struct_class = StructOrClass.STRUCT

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        if self.contents.lines:
            return str(
                TB([f'{self._struct_class.value} {self.name}', '{', self.contents, '};']))

        return str(TB([f'{self._struct_class.value} {self.name}', '{', '};']))

    @property
    def name(self) -> str:
        """Get the current name of the struct."""
        return self._name

    @property
    def contents(self) -> TextBlock:
        """Get the current contents."""
        return self._contents

    @contents.setter
    def contents(self, value: TextBlock):
        """Set new contents that must be a TextBlock."""
        assert_t(value, TextBlock)
        self._contents = value


@dataclass
class Class(Struct):
    """Dataclass representing a C++ class clause with un-indented contents. The contents
    can be set later after initial construction but note that strict typing checking applues.
    Example:

        struct MyClass
        {
        <contents>
        };
    """

    def __init__(self, name: str, contents: Optional[TextBlock] = None):
        """Initialize with a name and optional initial content."""
        super().__init__(name, contents)
        self._struct_class = StructOrClass.CLASS


@dataclass(frozen=True)
class ProjectIncludes:
    """Dataclass representing a C++ 'system' include statements. Example:

        // Project include
        #include "IToaster.h"

        // Project includes
        #include "IHeater.h"
        #include "ProjectB/Lunchbox.h"
    """
    includes: List[str]

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        if not is_strlist_instance(self.includes):
            raise TypeError('property "includes" must be a list of strings')

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        return str(TB([Comment(f'Project {plural("include", self.includes)}'),
                       [f'#include "{x}"' for x in self.includes]]))


@dataclass(frozen=True)
class SystemIncludes:
    """Dataclass representing a C++ 'project' include statements. Example:

        // System include
        #include <string>

        // System includes
        #include <string>
        #include <dzn/pump.hh>
    """
    includes: List[str]

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        if not is_strlist_instance(self.includes):
            raise TypeError('property "includes" must be a list of strings')

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        return str(TB([Comment(f'System {plural("include", self.includes)}'),
                       [f'#include <{x}>' for x in self.includes]]))


class Namespace:  # pylint: disable=too-few-public-methods
    """Ordinary python class with properties representing a C++ namespace clause with
    unindented contents. The contents can be specified initially or later. In both cases strict
    type checking on the contents apply.
    Example:

        namespace My::Project::XY {
        <contents>
        } // namespace My::Project::XY

    or when contents is absent:

        namespace My::Zone {}

    """
    ns_ids: NamespaceIds
    contents: TextBlock

    def __init__(self, ns_ids: NamespaceIds, contents: Optional[TextBlock] = None):
        """Initialize with a namespace and optional initial content."""
        assert_t(ns_ids, NamespaceIds)
        assert_t_optional(contents, TextBlock)
        self._ns_ids = ns_ids
        self._contents = contents if contents else TextBlock()

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        ns_ids_str = f' {fqn_t(self.ns_ids)}' if self.ns_ids.items else ''
        head = f'namespace{ns_ids_str} {{'
        fqn_tail = f'}} // namespace{ns_ids_str}'

        if self.contents.lines:
            return str(TB([head,
                           self.contents,
                           fqn_tail]))  # multi-line

        return str(TB([f'{head}}}']))  # one-liner

    @property
    def ns_ids(self) -> NamespaceIds:
        """Get the current namespace value."""
        return self._ns_ids

    @property
    def contents(self) -> TextBlock:
        """Get the current contents."""
        return self._contents

    @contents.setter
    def contents(self, value: TextBlock):
        """Set new contents that must be a TextBlock."""
        assert_t(value, TextBlock)
        self._contents = value


class Comment:  # pylint: disable=too-few-public-methods
    """C++ comment class derived from TextBlock that is configured with C++ '//' indentation."""

    _tb: TextBlock

    def __init__(self, content: Optional[Any] = None):
        """Initialize the comment class instance with a prefab C++ Indentizer."""
        self._tb = TextBlock(content)
        self._tb.set_indentor(Indentizer(spaces_count=3, bullet_list=BulletList(glyph='//')))

    def __str__(self) -> str:
        # Generate a C++ multiline comment textstring, by cloning the lines buffer and subsequently
        # applying the C++ '// ' indentation.
        # The original lines buffer stays intact to allow a user further extending the buffer.
        return str(TextBlock(deepcopy(self._tb).indent()))


@dataclass(kw_only=True)
class ParentAndContents:
    """Base dataclass containing generic fields to indicate the parent, a Class or Struct,
    when applicable. And textual contents in the form of a TextBlock, whose assignment is optional
    on creation."""
    parent: Optional[Struct or Class] = field(default=None)
    contents: Optional[TextBlock] = field(default=None)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        if (not isinstance(self.parent, Class)
                and not isinstance(self.parent, Struct)
                and self.parent is not None):
            raise CppGenError('parent must be a Class, Struct or None')

    @abc.abstractmethod
    def as_decl(self) -> TextBlock:
        """Generate a C++ declaration TextBlock."""

    @abc.abstractmethod
    def as_def(self) -> TextBlock:
        """Generate a C++ definition TextBlock."""


@dataclass(kw_only=True)
class Constructor(ParentAndContents):
    """Dataclass representing a C++ constructor where its parent must be assigned to an existing
    instance of a Struct or Class because that determines the name of the constructor function.
    The contents for the constructor definition will be indented.

    Example of a declaration:

        explicit MyToaster(int x, size_t y = 123u);

        MyToaster();

        MyToaster() = default;

    Examples of a definition:

        MyToaster::MyToaster(int x, size_t y)
        {
            <contents>
        }

        MyToaster::MyToaster()
            : m_number(1)
            , m_two{2 }
            , m_xyz ("Two")
        {
            <contents>
        }
    """
    explicit: bool = field(default=False)
    params: List[Param] = field(default_factory=list)
    initialization: str = field(default='')
    member_initlist: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

        if self.initialization and self.member_initlist:
            raise CppGenError('not allowed to have both a constructor initialization and a '
                              'member initializer list')

        if not is_strlist_instance(self.member_initlist):
            raise CppGenError('the member initializer list must be a list of strings')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the constructor declaration as a multiline string."""
        explicit = 'explicit ' if self.explicit else ''
        params = ', '.join([p.as_decl() for p in self.params if p])
        initialization = f' = {self.initialization}' if self.initialization else ''
        full_signature = f'{explicit}{self.parent.name}({params}){initialization};'
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the constructor definition as a multiline string."""
        if self.initialization:
            return TextBlock()  # no definition is generated when declared with initialization

        params = ', '.join([p.as_def() for p in self.params if p])
        member_initlist = TB([': ' + '\n, '.join(self.member_initlist)]).indent() \
            if self.member_initlist else None
        content = TB(self.contents).indent() if self.contents else None
        full_signature = f'{self.parent.name}::{self.parent.name}({params})'

        if member_initlist is None and not content:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   member_initlist,
                   '{',
                   content,
                   '}'])


@dataclass(kw_only=True)
class Destructor(ParentAndContents):
    """Dataclass representing a C++ destructor where its parent must be assigned to an existing
    instance of a Struct or Class because that determines the name of the destructor function.
    The contents for the destructor definition will be indented.

    Example of a declaration:

        ~MyToaster();

        ~MyToaster() override = default;

    Examples of a definition:

        MyToaster::~MyToaster() {}

        MyToaster::~MyToaster()
        {
            <contents>
        }
    """
    override: bool = field(default=False)
    initialization: str = field(default='')

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the destructor declaration as a multiline string."""
        override = ' override' if self.override else ''
        initialization = f' = {self.initialization}' if self.initialization else ''
        full_signature = f'~{self.parent.name}(){override}{initialization};'
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the destructor definition as a multiline string."""
        if self.initialization:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = f'{self.parent.name}::~{self.parent.name}()'

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


@dataclass(kw_only=True)
class Function(ParentAndContents):  # pylint: disable=too-many-instance-attributes
    """Dataclass representing a single C++ function. The contents for the function definition will
    be indented.
    In case it needs to be a class method then a parent (Struct or Class) must be assigned that
    will determine the scope name of the method.

    Example of a declaration:

        void Calculate(int x, size_t y = 123u);

        static int Process(int x);

        virtual void Calc() const = 0;   // with a parent set, e.g. 'MyClass'

    Examples of a definition:

        void Calculate(int x, size_t y)
        {
            <content>
        }

        int Process(int x) {}

        void MyClass::Calc() const
        {
            <content>
        }
    """
    prefix: FunctionPrefix = field(default=FunctionPrefix.MEMBER_FUNCTION)
    return_type: TypeDesc
    name: str
    params: List[Param] = field(default_factory=list)
    cav: str = field(default='')  # = const and volatile type qualifiers
    override: bool = field(default=False)
    initialization: str = field(default='')

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.return_type, TypeDesc):
            raise CppGenError('return_type must be TypeDesc')

        if not self.name:
            raise CppGenError('name must not be empty')

        if self.prefix == FunctionPrefix.VIRTUAL and self.parent is None:
            raise CppGenError('missing parent for prefix "virtual"')

        if self.initialization.startswith('0') and not self.prefix == FunctionPrefix.VIRTUAL:
            raise CppGenError('missing prefix "virtual" when initializing with "=0"')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the function declaration as a multiline string."""
        prefix = f'{self.prefix.value} ' if self.prefix.value is not None else ''
        return_type = f'{self.return_type} ' if self.return_type else ''
        name = self.name
        params = ', '.join([p.as_decl() for p in self.params])
        cav = f' {self.cav}' if self.cav != '' else ''
        override = ' override' if self.override else ''
        initialization = f' = {self.initialization}' if self.initialization != '' else ''
        return TB(f'{prefix}{return_type}{name}({params}){cav}{override}{initialization};')

    def as_def(self) -> TextBlock:
        """Return the function definition as a multiline string."""
        if self.initialization:
            return TextBlock()  # no definition is generated when declared with initialization

        return_type = f'{self.return_type} ' if self.return_type else ''
        parent = f'{self.parent.name}::' if self.parent is not None else ''
        name = self.name
        params = ', '.join([p.as_def() for p in self.params])
        cav = f' {self.cav}' if self.cav != '' else ''
        full_signature = f'{return_type}{parent}{name}({params}){cav}'

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


@dataclass(frozen=True)
class MemberVariable:
    """Dataclass representing a C++ member variable. Example:

        My::ILedControl& myPort;

        float m_someOtherNumber;
    """
    type: TypeDesc
    name: str

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_t(self.type, TypeDesc)
        assert_t(self.name, str)
        if not self.name:
            raise TypeError('name must be a non-empty string')

    def __str__(self) -> str:
        """Return the contents of this dataclass as a single string."""
        return f'{self.type} {self.name};'


###############################################################################
# Type creation functions
#

def fqn_t(ns_ids: Optional[Any], prefix_root_ns: bool = False) -> Fqn:
    """Create a Fqn type from argument 'ns_ids' (any type) that can be accepted or transformed
    into the NamespaceIds type, without (=default) or with the C++ root namespace prefixed.
    An empty 'ns_ids' argument will result into default constructed Fqn type.
    See also: 'nested-namespace-definition'
    Link: https://en.cppreference.com/w/cpp/language/namespace#Namespaces
    """
    if not ns_ids:
        return Fqn(ns_ids_t([]), prefix_root_ns)

    return Fqn(ns_ids_t(ns_ids), prefix_root_ns)


def void_t() -> TypeDesc:
    """Shortcut helper to create a void TypeDesc"""
    return TypeDesc(fqname=fqn_t('void'))


def int_t() -> TypeDesc:
    """Shortcut helper to create a int TypeDesc"""
    return TypeDesc(fqname=fqn_t('int'))


def float_t() -> TypeDesc:
    """Shortcut helper to create a float TypeDesc"""
    return TypeDesc(fqname=fqn_t('float'))


def double_t() -> TypeDesc:
    """Shortcut helper to create a double TypeDesc"""
    return TypeDesc(fqname=fqn_t('double'))


def decl_var_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable (without postfix like & or *)."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.NONE), name=name)


def decl_var_ref_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a reference postfix."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.REFERENCE), name=name)


def decl_var_ptr_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a pointer postfix."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.POINTER), name=name)


def param_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a simple parameter with an optional default value."""
    return Param(type_desc=TypeDesc(fqn, default_value=default_value), name=name)


def const_param_ref_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a const reference parameter with an optional default value."""
    return Param(type_desc=TypeDesc(fqname=fqn,
                                    postfix=TypePostfix.REFERENCE,
                                    const=True,
                                    default_value=default_value), name=name)


def const_param_ptr_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a const pointer parameter with an optional default value."""
    return Param(type_desc=TypeDesc(fqname=fqn,
                                    postfix=TypePostfix.POINTER,
                                    const=True,
                                    default_value=default_value), name=name)
