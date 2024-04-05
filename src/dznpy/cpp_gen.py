"""
dznpy/cpp_gen - version 0.2.240304

Python module providing helpers for generating c++ source and header files

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
from dataclasses import dataclass, field
import enum
from typing import List, Dict, Any, Optional
from typing_extensions import Self

# dznpy modules
from .misc_utils import is_strlist_instance, is_namespaceids_instance, plural, NameSpaceIds, \
    TextBlock, EOL, SPACE


class CppGenError(Exception):
    """An error occurred during generating c++ code."""


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


@dataclass
class Fqn:
    """A C++ fully-qualified name"""
    ns_ids: NameSpaceIds
    prefix_root_ns: bool = False

    def __post_init__(self):
        self._str_value = gen_fqn(ns_ids=self.ns_ids, prefix_root_ns=self.prefix_root_ns)

    def __str__(self):
        return self._str_value


@dataclass(frozen=True)
class AccessSpecifiedSection:
    """AccessSpecifiedSection"""
    access_specifier: AccessSpecifier
    contents: TextBlock

    def __str__(self):
        tb = TextBlock(self.access_specifier.value).add(TextBlock(self.contents).indent())
        return str(tb)


@dataclass(frozen=True)
class TypeDesc:
    """TypeDesc"""
    fqn: Fqn
    postfix: TypePostfix = TypePostfix.NONE
    const: bool = False
    default_value: str = None

    def __post_init__(self):
        if self.default_value is not None and not isinstance(self.default_value, str):
            raise CppGenError('default_value must be a string type')

    def __str__(self):
        mandatory = f'{self.fqn}{self.postfix.value}'
        return f'const {mandatory}' if self.const else mandatory


class Param:
    """Param"""

    def __init__(self, type_desc: TypeDesc, name: str):
        self._type_desc = type_desc
        self._name = name

    @property
    def type_desc(self):
        return self._type_desc

    @property
    def name(self):
        return self._name

    def __str__(self):
        raise CppGenError('instead of str(), access the properties as_decl or as_def')

    @property
    def as_decl(self) -> str:
        """Compose the parameter as used in a declaration."""
        if self.type_desc.default_value:
            return f'{self.type_desc} {self.name} = {self.type_desc.default_value}'

        return self.as_def

    @property
    def as_def(self) -> str:
        """Compose the parameter as used in a definition."""
        return f'{self.type_desc} {self.name}'


@dataclass
class Struct:
    """Struct"""
    name: str
    contents: TextBlock = field(default_factory=TextBlock)

    def __post_init__(self):
        if not self.name:
            raise CppGenError('name must not be empty')
        # TODO check contents type equalling TextBlock
        self._struct_class = StructOrClass.STRUCT

    def __str__(self):
        """Return the contents of this dataclass as textblock."""
        if self.contents.lines:
            return str(
                TextBlock([f'{self._struct_class.value} {self.name}', '{', self.contents, '};']))

        return str(TextBlock([f'{self._struct_class.value} {self.name}', '{', '};']))


@dataclass
class Class(Struct):
    """Class"""

    def __post_init__(self):
        if not self.name:
            raise CppGenError('name must not be empty')
        self._struct_class = StructOrClass.CLASS


@dataclass(frozen=True)
class ProjectIncludes:
    """ProjectIncludes"""
    includes: List[str]

    def __str__(self) -> str:
        return str(TextBlock([Comment(f'Project {plural("include", self.includes)}'),
                              [f'#include "{x}"' for x in self.includes]]))


@dataclass(frozen=True)
class SystemIncludes:
    """SystemInclude"""
    includes: List[str]

    def __str__(self) -> str:
        """Return the contents of this dataclass as textblock."""
        return str(TextBlock([Comment(f'System {plural("include", self.includes)}'),
                              [f'#include <{x}>' for x in self.includes]]))


@dataclass
class Namespace:
    """Namespace"""
    ns_ids: NameSpaceIds
    contents: str = ''

    def __str__(self):
        """Return the contents of this dataclass as textblock."""
        ns_ids_str = SPACE + gen_fqn(self.ns_ids) if self.ns_ids else ''
        head = f'namespace{ns_ids_str} {{'
        fqn_tail = f'}} // namespace{ns_ids_str}'

        if self.contents:
            return str(TextBlock([head, self.contents, fqn_tail]))  # multi-line

        return str(TextBlock([f'{head}}}']))  # one-liner


@dataclass(frozen=True)
class CommentBlock:
    """CommentBlock"""
    comments: List[str]

    def __str__(self) -> str:
        """Create a comment block where trailing whitespace has been trimmed. Skip lines
        that already preceed with //. """
        result = ''
        for item in self.comments:
            if isinstance(item, str):
                for line in item.splitlines():
                    stripped = line.rstrip(' ')
                    if line[:2] == '//':
                        result += f'{stripped}{EOL}'
                    else:
                        result += f'// {stripped}{EOL}' if stripped else f'//{EOL}'
        return result


@dataclass(frozen=True)
class Comment:
    """Comment"""
    value: str

    def __str__(self) -> str:
        """Create a comment line where trailing whitespace has been trimmed."""
        result = ''
        for line in self.value.splitlines():
            stripped = line.rstrip(' ')
            result += f'// {stripped}{EOL}' if stripped else f'//{EOL}'
        return result


@dataclass
class Constructor:
    """Constructor"""
    scope: Struct or Class
    explicit: bool = field(default=False)
    params: List[Param] = field(default_factory=list)
    initialization: str = field(default='')
    member_initlist: List[str] = field(default_factory=list)
    contents: str = field(default='')

    def __post_init__(self):
        if not isinstance(self.scope, Class) and not isinstance(self.scope, Struct):
            raise CppGenError('scope must be a Class or Struct')
        if self.initialization and self.member_initlist:
            raise CppGenError('not allowed to have both a constructor initialization and a '
                              'member initializer list')
        if not is_strlist_instance(self.member_initlist):
            raise CppGenError('the member initializer list must be a list of strings')

    def __str__(self):
        raise CppGenError('instead of str(), access the properties as_decl or as_def')

    @property
    def as_decl(self) -> str:
        """Return the constructor declaration textblock."""
        explicit = 'explicit ' if self.explicit else ''
        params = ', '.join([p.as_decl for p in self.params])
        initialization = f' = {self.initialization}' if self.initialization else ''
        full_signature = f'{explicit}{self.scope.name}({params}){initialization};'
        return str(TextBlock(full_signature))

    @property
    def as_def(self) -> str:
        """Return the constructor definition textblock."""
        if self.initialization:
            return ''  # no definition is generated when declared with initialization

        params = ', '.join([p.as_def for p in self.params])
        mil = TextBlock([': ' + '\n, '.join([mv for mv in self.member_initlist])]).indent() \
            if self.member_initlist else None
        content = TextBlock(self.contents).indent() if self.contents else None
        full_signature = f'{self.scope.name}::{self.scope.name}({params})'

        if mil is None and not content:
            return str(TextBlock(f'{full_signature} {{}}'))

        return str(TextBlock([full_signature,
                              mil,
                              '{',
                              content,
                              '}']))


@dataclass
class Destructor:
    """Destructor"""
    scope: Struct or Class
    override: bool = field(default=False)
    initialization: str = field(default='')
    contents: str = field(default='')

    def __post_init__(self):
        if not isinstance(self.scope, Class) and not isinstance(self.scope, Struct):
            raise CppGenError('scope must be a Class or Struct')

    def __str__(self):
        raise CppGenError('instead of str(), access the properties as_decl or as_def')

    @property
    def as_decl(self) -> str:
        """Return the constructor declaration textblock."""
        override = ' override' if self.override else ''
        initialization = f' = {self.initialization}' if self.initialization else ''
        full_signature = f'~{self.scope.name}(){override}{initialization};'
        return str(TextBlock(full_signature))

    @property
    def as_def(self) -> str:
        """Return the constructor definition textblock."""
        if self.initialization:
            return ''  # no definition is generated when declared with initialization

        full_signature = f'{self.scope.name}::~{self.scope.name}()'

        if not self.contents:
            return str(TextBlock(f'{full_signature} {{}}'))

        return str(TextBlock([full_signature,
                              '{',
                              TextBlock(self.contents).indent(),
                              '}']))


@dataclass
class Function:
    """Function"""
    return_type: TypeDesc
    name: str
    params: List[Param] = field(default_factory=list)
    prefix: FunctionPrefix = field(default=FunctionPrefix.MEMBER_FUNCTION)
    cv: str = field(default='')
    override: bool = field(default=False)
    initialization: str = field(default='')
    contents: str = field(default='')
    scope: Struct or Class = field(default=None)

    def __post_init__(self):
        if not isinstance(self.return_type, TypeDesc):
            raise CppGenError('return_type must be TypeDesc')
        if self.return_type is None and self.scope is None:
            raise CppGenError('missing scope when return_type is None (con/destructor)')
        if not self.name:
            raise CppGenError('name must not be empty')
        if self.prefix == FunctionPrefix.VIRTUAL and self.scope is None:
            raise CppGenError('missing scope for prefix "virtual"')
        if self.initialization.startswith('0') and not self.prefix == FunctionPrefix.VIRTUAL:
            raise CppGenError('missing prefix "virtual" when initializing with "=0"')

    def __str__(self):
        raise CppGenError('instead of str(), access the properties as_decl or as_def')

    @property
    def as_decl(self) -> str:
        """Create the function declaration textblock."""
        prefix = f'{self.prefix.value} ' if self.prefix.value is not None else ''
        return_type = f'{self.return_type} ' if self.return_type else ''
        name = self.name
        params = ', '.join([p.as_decl for p in self.params])
        cv = f' {self.cv}' if self.cv != '' else ''
        override = ' override' if self.override else ''
        initialization = f' = {self.initialization}' if self.initialization != '' else ''
        return str(
            TextBlock(f'{prefix}{return_type}{name}({params}){cv}{override}{initialization};'))

    @property
    def as_def(self) -> str:
        """Create the function definition textblock."""
        if self.initialization:
            return ''  # no definition is generated when declared with initialization

        return_type = f'{self.return_type} ' if self.return_type else ''
        scope = f'{self.scope.name}::' if self.scope is not None else ''
        name = self.name
        params = ', '.join([p.as_def for p in self.params])
        cv = f' {self.cv}' if self.cv != '' else ''
        full_signature = f'{return_type}{scope}{name}({params}){cv}'

        if not self.contents:
            return str(TextBlock(f'{full_signature} {{}}'))

        return str(TextBlock([full_signature,
                              '{',
                              TextBlock(self.contents).indent(),
                              '}']))


@dataclass(frozen=True)
class MemberVariable:
    """Member Variable"""
    type: TypeDesc
    name: str

    def __post_init__(self):
        if not isinstance(self.type, TypeDesc):
            raise TypeError('type of "type" must be TypeDesc')
        if not isinstance(self.name, str) or not self.name:
            raise TypeError('name must be a non-empty string')

    def __str__(self):
        return f'{self.type} {self.name};'


# helper functions

def gen_fqn(ns_ids: Optional[NameSpaceIds], prefix_root_ns: bool = False) -> str:
    """"Create a fully qualified c++ (namespace) trail from a dezyne JSON NameSpaceIds type.
    Without (=default) or with the root namespace prefixed. An empty ns_ids will lead to
    an empty string response."""
    if not ns_ids:
        return ''
    if not is_namespaceids_instance(ns_ids):
        raise TypeError('NameSpaceIds type expected')

    return f'::{"::".join(ns_ids)}' if prefix_root_ns else '::'.join(ns_ids)


def void_t() -> TypeDesc:
    """Shortcut helper to create a void TypeDesc"""
    return TypeDesc(fqn=Fqn(['void']))


def int_t() -> TypeDesc:
    """Shortcut helper to create a int TypeDesc"""
    return TypeDesc(fqn=Fqn(['int']))


def float_t() -> TypeDesc:
    """Shortcut helper to create a float TypeDesc"""
    return TypeDesc(fqn=Fqn(['float']))


def double_t() -> TypeDesc:
    """Shortcut helper to create a double TypeDesc"""
    return TypeDesc(fqn=Fqn(['double']))


def decl_var_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable (without postfix like & or *)."""
    return MemberVariable(type=TypeDesc(fqn=fqn, postfix=TypePostfix.NONE), name=name)


def decl_var_ref_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a reference postfix."""
    return MemberVariable(type=TypeDesc(fqn=fqn, postfix=TypePostfix.REFERENCE), name=name)


def decl_var_ptr_t(fqn: Fqn, name: str) -> MemberVariable:
    """Shortcut helper to create a member variable with a pointer postfix."""
    return MemberVariable(type=TypeDesc(fqn=fqn, postfix=TypePostfix.POINTER), name=name)


def param_t(ns_ids: NameSpaceIds, name: str, default_value='') -> Param:
    """Shortcut helper to create a simple parameter with an optional default value."""
    return Param(type_desc=TypeDesc(Fqn(ns_ids), default_value=default_value), name=name)


def const_param_ref_t(ns_ids: NameSpaceIds, name: str, default_value='') -> Param:
    """Shortcut helper to create a const reference parameter with an optional default value."""
    return Param(type_desc=TypeDesc(fqn=Fqn(ns_ids),
                                    postfix=TypePostfix.REFERENCE,
                                    const=True,
                                    default_value=default_value), name=name)


def const_param_ptr_t(ns_ids: NameSpaceIds, name: str, default_value='') -> Param:
    """Shortcut helper to create a const pointer parameter with an optional default value."""
    return Param(type_desc=TypeDesc(fqn=Fqn(ns_ids),
                                    postfix=TypePostfix.POINTER,
                                    const=True,
                                    default_value=default_value), name=name)


class Container:
    """Class to contain and lookup instantiated cpp_gen elements"""
    _params = Dict[str, Param]
    _member_variables = Dict[str, MemberVariable]
    _functions = Dict[str, Function]

    def __init__(self):
        self._params = {}
        self._member_variables = {}
        self._functions = {}

    def add_unique(self, addition: Any or List[Any]) -> Self:
        """Add a unique cpp_gen element, or a list of cpp_gen elements to the container.
        Returns self according to the Fluent Interface pattern."""
        if isinstance(addition, list):
            for item in addition:
                self._add_single(item)
        else:
            self._add_single(addition)

        return self

    def _add_single(self, item: Any):
        """Private method to add a single cpp_gen item to the container."""
        if isinstance(item, Param):
            if item.name in self._params:
                raise CppGenError(f'Param "{item.name}" already present')
            self.params[item.name] = item
        elif isinstance(item, MemberVariable):
            if item.name in self._member_variables:
                raise CppGenError(f'Member Variable "{item.name}" already present')
            self.member_variables[item.name] = item
        elif isinstance(item, Function):
            if item.name in self._functions:
                raise CppGenError(f'Function "{item.name}" already present')
            self.functions[item.name] = item
        else:
            raise TypeError('type can not be added')

    @property
    def params(self) -> Dict[str, Param]:
        return self._params

    @property
    def member_variables(self) -> Dict[str, MemberVariable]:
        return self._member_variables

    @property
    def functions(self) -> Dict[str, Function]:
        return self._functions
