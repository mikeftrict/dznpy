"""
Module providing helpers for generating c++ source and header files.

The helpers provide for 'building blocks' in which 'content' can be inserted to finally generate
c++ code the developer intents to compile. Important to know: this cpp_gen module takes no
responsibility that the produced text can be compiled. It attempts to closely match C++ conventions
with the 'building blocks'. Since the developer needs to insert content manually, this cpp_gen
module can not guarantee that the final total generated text is compilable.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
# system modules
import abc
import enum
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Any, Optional

# dznpy modules
from .misc_utils import assert_t, assert_t_optional, is_strlist_instance, plural, assert_union_t
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

    @staticmethod
    def str_without_colon(specifier: 'AccessSpecifier') -> str or None:
        """Return the access specifier name without the colon."""
        assert_t(specifier, AccessSpecifier)
        return '' if specifier.value is None else specifier.value.rstrip(':')


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
    POINTER_CONST = '* const'


class TypeConstness(enum.Enum):
    """Enum to indicate the constness of a type: none, prefixed or postfixed."""
    NONE = ''
    PREFIXED = 'const prefix'
    POSTFIXED = 'const postfix'


class FunctionInitialization(enum.Enum):
    """Enum to indicate the initialization of a constructor, destructor or function."""
    NONE = ''
    DEFAULT = ' = default'
    DELETE = ' = delete'
    PURE_VIRTUAL = ' = 0'


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
class TypeAsIs:
    """Dataclass that intentionally lets the user specify the type
    as a string -as is-. Meaning, validity is up to the user.
    """
    value: str

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_t(self.value, str)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TypeDesc:
    """Dataclass representing a C++ type description and an optional default value that is used
    by other cpp_gen types such as Param. Examples:

        My::Data
        My::Data&
        My::Data*
        int* const
        ::My::Data<Hal::IHeater>
        const float
        float const
        const int* const
        int const* const
    """
    fqname: Fqn
    constness: TypeConstness = field(default=TypeConstness.NONE)
    template_arg: Optional[TemplateArg] = field(default=None)
    postfix: TypePostfix = field(default=TypePostfix.NONE)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        if not str(self.fqname):
            raise CppGenError('fqname must not be empty')
        assert_t(self.constness, TypeConstness)
        assert_t_optional(self.template_arg, TemplateArg)
        assert_t(self.postfix, TypePostfix)

    def __str__(self) -> str:
        template_arg = f'{self.template_arg}' if self.template_arg else ''

        if self.constness == TypeConstness.PREFIXED:
            return f'const {self.fqname}{template_arg}{self.postfix.value}'

        if self.constness == TypeConstness.POSTFIXED:
            return f'{self.fqname}{template_arg} const{self.postfix.value}'

        return f'{self.fqname}{template_arg}{self.postfix.value}'


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

    Typically one or more Param instances form a list of parameters as part
    of a Function or Constructor. See their respective classes.
    """
    type: TypeDesc or TypeAsIs
    name: str
    default_value: Optional[str] = field(default=None)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_union_t(self.type, [TypeDesc, TypeAsIs])
        assert_t(self.name, str)
        if not self.name:
            raise TypeError('name must be a non-empty string')
        assert_t_optional(self.default_value, str)

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> str:
        """Compose the parameter as used in a declaration."""
        if self.default_value:
            return f'{self.type} {self.name} = {self.default_value}'

        return self.as_def()

    def as_def(self) -> str:
        """Compose the parameter as used in a definition."""
        return f'{self.type} {self.name}'


@dataclass(frozen=True)
class MemberVariable(Param):
    """Dataclass representing a C++ member variable. Example of a declaration:

        float m_someOtherNumber;
        double m_someNumber = 0.123;

    Note: that MemberVariable has no parent property. Instead, it is up to the developer's
    freedom how to integrate it. An example can be to include it as contents as part of a
    AccessSpecifiedSection.
    """

    def __str__(self) -> str:
        return str(self.as_decl())

    def as_decl(self) -> TextBlock:
        """Compose the parameter as used in a declaration."""
        if self.default_value:
            return TB(f'{self.type} {self.name} = {self.default_value};')

        return TB(f'{self.type} {self.name};')

    def as_def(self) -> TextBlock:
        """Compose the parameter as used in a definition."""
        raise CppGenError('MemberVariable only supports calling as_decl()')


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
    __slots__ = ['_ns_ids', '_contents', '_global_namespace_on_empty_ns_ids']

    def __init__(self, ns_ids: NamespaceIds, contents: Optional[TextBlock] = None,
                 global_namespace_on_empty_ns_ids: bool = False):
        """Initialize with namespace identifiers and optional initial content."""
        assert_t(ns_ids, NamespaceIds)
        assert_t_optional(contents, TextBlock)
        assert_t(global_namespace_on_empty_ns_ids, bool)
        self._ns_ids = ns_ids
        self._contents = contents if contents else TextBlock()
        self._global_namespace_on_empty_ns_ids = global_namespace_on_empty_ns_ids

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        ns_ids_str = f' {fqn_t(self.ns_ids)}' if self.ns_ids.items else ''

        if ns_ids_str == '' and self._global_namespace_on_empty_ns_ids:
            head = None
            fqn_tail = None
        else:
            head = f'namespace{ns_ids_str} {{'
            fqn_tail = f'}} // namespace{ns_ids_str}'

        if self.contents.lines:
            return str(TB([head,
                           self.contents,
                           fqn_tail]))  # multi-line

        return str(TB([f'{head}}}'])) if head else str(TB())  # one-liner

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


@dataclass(frozen=True)
class ParentReference:
    """Dataclass containing properties referencing to a base class/struct"""
    access_specifier: AccessSpecifier
    base: 'Struct' or 'Class'

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        assert_t(self.access_specifier, AccessSpecifier)
        assert_union_t(self.base, [Struct, Class])

    def __str__(self):
        """Stringification of access specification and FQN formatting of the base class."""
        xs_spec = AccessSpecifier.str_without_colon(self.access_specifier)
        base_ns = self.base.namespace.ns_ids if self.base.namespace else ns_ids_t('')
        return f'{xs_spec} {Fqn(base_ns + ns_ids_t(self.base.name))}'


class Struct:
    """Dataclass representing a C++ struct clause with un-indented contents. The contents
    can be set later after initial construction but note that strict typing checking applues.
    Example:

        struct MyStruct
        {
        <contents>
        };
    """
    __slots__ = ['_name', '_decl_contents', '_struct_or_class', '_parents',
                 '_namespace', '_constructor']

    def __init__(self, name: str, decl_contents: Optional[TextBlock] = None):
        """Initialize with a name and optional initial content."""
        assert_t(name, str)
        assert_t_optional(decl_contents, TextBlock)
        if not name:
            raise CppGenError('name must not be empty')

        self._name = name
        self._decl_contents = decl_contents if decl_contents else TextBlock()
        self._struct_or_class = StructOrClass.STRUCT
        self._parents: List[ParentReference] = []
        # install defaults
        self._namespace = Namespace(ns_ids_t(''), global_namespace_on_empty_ns_ids=True)
        self._constructor = Constructor(parent=self)

    def __str__(self) -> str:
        """Return the contents of this dataclass as a multiline string."""
        if self._parents:
            parents_str = ' : ' + ', '.join([str(x) for x in self._parents])
        else:
            parents_str = ''

        if self.decl_contents.lines:
            return str(
                TB([f'{self._struct_or_class.value} {self.name}{parents_str}', '{',
                    self.decl_contents, '};']))

        return str(TB([f'{self._struct_or_class.value} {self.name}{parents_str}', '{', '};']))

    @property
    def name(self) -> str:
        """Get the current name of the struct."""
        return self._name

    @property
    def decl_contents(self) -> TextBlock:
        """Get the current contents."""
        return self._decl_contents

    @decl_contents.setter
    def decl_contents(self, value: TextBlock):
        """Set new contents that must be a TextBlock."""
        assert_t(value, TextBlock)
        self._decl_contents = value

    def add_parent(self, access_specifier: AccessSpecifier, base: 'Struct' or 'Class'):
        """Add a parent Struct or Class to this instance."""
        assert_t(access_specifier, AccessSpecifier)
        assert_union_t(base, [Struct, Class])
        self._parents.append(ParentReference(access_specifier, base))

    @property
    def namespace(self) -> Namespace:
        """Get the namespace instance of this struct."""
        return self._namespace

    @namespace.setter
    def namespace(self, value: 'Constructor'):
        """Set a new namespace instance."""
        assert_t(value, Namespace)
        self._namespace = value

    @property
    def constructor(self) -> 'Constructor':
        """Get the current constructor."""
        return self._constructor

    @constructor.setter
    def constructor(self, value: 'Constructor'):
        """Set a new constructor instance."""
        assert_t(value, Constructor)
        self._constructor = value
        value.parent = self


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

    def __init__(self, name: str, decl_contents: Optional[TextBlock] = None):
        """Initialize with a name and optional initial content."""
        super().__init__(name, decl_contents)
        self._struct_or_class = StructOrClass.CLASS


@dataclass(kw_only=True)
class ParentAndContents:
    """Base dataclass containing generic fields to indicate the parent, a Class or Struct,
    when applicable. And textual contents in the form of a TextBlock, whose assignment is optional
    on creation."""
    parent: Optional[Struct or Class] = field(default=None)
    contents: Optional[TextBlock] = field(default=None)
    initialization: FunctionInitialization = field(default=FunctionInitialization.NONE)

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
            , m_two{2}
            , m_xyz("Two")
        {
            <contents>
        }
    """
    explicit: bool = field(default=False)
    params: List[Param] = field(default_factory=list)
    member_initlist: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

        if self.initialization != FunctionInitialization.NONE and self.member_initlist:
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
        full_signature = f'{explicit}{self.parent.name}({params}){self.initialization.value};'
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the constructor definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
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

    def get_method_fqn(self) -> str:
        """Return the constructor method in full FQN format without parentheses and
        parameter arguments."""
        namespace: Namespace = self.parent.namespace
        return str(Fqn(namespace.ns_ids + ns_ids_t(self.parent.name))) if namespace \
            else str(Fqn(ns_ids_t(self.parent.name)))


@dataclass(kw_only=True)
class Function(ParentAndContents):  # pylint: disable=too-many-instance-attributes
    """Dataclass representing a single C++ function. The contents for the function definition will
    be indented.
    In case it needs to be a class method, then a parent (Struct or Class) must be assigned that
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
    return_type: TypeDesc or TypeAsIs
    name: str
    params: List[Param] = field(default_factory=list)
    cav: str = field(default='')  # = const and volatile type qualifiers
    override: bool = field(default=False)

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        assert_union_t(self.return_type, [TypeDesc, TypeAsIs])

        if not self.name:
            raise CppGenError('name must not be empty')

        if self.prefix == FunctionPrefix.VIRTUAL and self.parent is None:
            raise CppGenError('missing parent for prefix "virtual"')

        if self.initialization == FunctionInitialization.PURE_VIRTUAL \
                and not self.prefix == FunctionPrefix.VIRTUAL:
            raise CppGenError('missing prefix "virtual" when initializing with "=0"')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the function declaration as a multiline TextBlock."""
        prefix = f'{self.prefix.value} ' if self.prefix.value is not None else ''
        return_type = f'{self.return_type} ' if self.return_type else ''
        name = self.name
        params = ', '.join([p.as_decl() for p in self.params])
        cav = f' {self.cav}' if self.cav != '' else ''
        override = ' override' if self.override else ''
        initialization = self.initialization.value
        return TB(f'{prefix}{return_type}{name}({params}){cav}{override}{initialization};')

    def as_def(self, imf=False) -> TextBlock:
        """Return the function definition as a multiline TextBlock. The optional argument
        'imf' (inline member function) can be set to True to omit specifying the scope name of
        the class/struct.
        ."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        return_type = f'{self.return_type} ' if self.return_type else ''
        parent = f'{self.parent.name}::' if self.parent is not None else ''
        parent = '' if imf else parent  # override in case a 'inline member function'
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


def std_string_t() -> TypeDesc:
    """Shortcut helper to create a double TypeDesc"""
    return TypeDesc(fqname=fqn_t('std.string'))


def const_std_string_ref_t() -> TypeDesc:
    """Shortcut helper to create a double TypeDesc"""
    return TypeDesc(fqname=fqn_t('std.string'),
                    constness=TypeConstness.PREFIXED,
                    postfix=TypePostfix.REFERENCE)


def param_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a simple parameter with an optional default value."""
    return Param(type=TypeDesc(fqn), name=name, default_value=default_value)


def param_ref_t(fqn: Fqn, name: str) -> Param:
    """Shortcut helper to create a referenced parameter."""
    return Param(type=TypeDesc(fqname=fqn,
                               postfix=TypePostfix.REFERENCE),
                 name=name)


def const_param_ref_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a const reference parameter with an optional default value."""
    return Param(type=TypeDesc(fqname=fqn,
                               postfix=TypePostfix.REFERENCE,
                               constness=TypeConstness.PREFIXED),
                 name=name,
                 default_value=default_value)


def const_param_ptr_t(fqn: Fqn, name: str, default_value='') -> Param:
    """Shortcut helper to create a const pointer parameter with an optional default value."""
    return Param(type=TypeDesc(fqname=fqn,
                               postfix=TypePostfix.POINTER,
                               constness=TypeConstness.PREFIXED),
                 name=name,
                 default_value=default_value)


def decl_var_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable (without postfix like & or *)."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.NONE), name=name)


def decl_var_ref_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a reference postfix."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.REFERENCE), name=name)


def decl_var_ptr_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a pointer postfix."""
    return MemberVariable(type=TypeDesc(fqname=fqn, postfix=TypePostfix.POINTER), name=name)
