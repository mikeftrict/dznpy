"""
Module providing helpers related to the 'Rule of Five' for generating c++ source and header files.

The helpers provide for 'building blocks' in which 'content' can be inserted to finally generate
c++ code the developer intents to compile. Important to know: this cpp_gen module takes no
responsibility that the produced text can be compiled. It attempts to closely match C++ conventions
with the 'building blocks'. Since the developer needs to insert content manually, this cpp_gen
module can not guarantee that the final total generated text is compilable.

Copyright (c) 2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from dataclasses import dataclass, field
from dznpy.misc_utils import assert_t, assert_union_t

# dznpy modules
from .text_gen import TB, TextBlock
from .cpp_gen import Class, CppGenError, FunctionInitialization, ParentAndContents, Struct


@dataclass(kw_only=True)
class CopyConstructor(ParentAndContents):
    """Dataclass representing a C++ copy constructor where its parent must be assigned to an
    existing instance of a Struct or Class because that determines the name of the function.
    The contents for the definition will be indented.

    Example of a declaration:

        MyToaster(const MyToaster&);
        MyToaster(const MyToaster&) = delete;

    Examples of a definition:

        MyToaster::MyToaster(const MyToaster& rhs)
        {
            <contents>
        }
    """

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the declaration as a multiline string."""
        full_signature = (f'{self.parent.name}(const {self.parent.name}&)'
                          f'{self.initialization.value};')
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = f'{self.parent.name}::{self.parent.name}(const {self.parent.name}& rhs)'

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


@dataclass(kw_only=True)
class CopyAssignmentConstructor(ParentAndContents):
    """Dataclass representing a C++ copy assignment constructor where its parent must be assigned
    to an existing instance of a Struct or Class because that determines the name of the function.
    The contents for the definition will be indented.

    Example of a declaration:

        MyToaster& operator=(const MyToaster&);
        MyToaster& operator=(const MyToaster&) = delete;

    Examples of a definition:

        MyToaster::MyToaster& operator=(const MyToaster& rhs)
        {
            <contents>
        }
    """

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the declaration as a multiline string."""
        full_signature = (f'{self.parent.name}& operator=(const {self.parent.name}&)'
                          f'{self.initialization.value};')
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = (f'{self.parent.name}::{self.parent.name}& operator=('
                          f'const {self.parent.name}& rhs)')

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


@dataclass(kw_only=True)
class MoveConstructor(ParentAndContents):
    """Dataclass representing a C++ move constructor where its parent must be assigned to an
    existing instance of a Struct or Class because that determines the name of the function.
    The contents for the definition will be indented.

    Example of a declaration:

        MyToaster(MyToaster&&);
        MyToaster(MyToaster&&) = delete;

    Examples of a definition:

        MyToaster::MyToaster(MyToaster&& rhs)
        {
            <contents>
        }
    """

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the declaration as a multiline string."""
        full_signature = f'{self.parent.name}({self.parent.name}&&){self.initialization.value};'
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = (f'{self.parent.name}::{self.parent.name}('
                          f'{self.parent.name}&& rhs)')

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


@dataclass(kw_only=True)
class MoveAssignmentConstructor(ParentAndContents):
    """Dataclass representing a C++ move assignment constructor where its parent must be assigned
    to an existing instance of a Struct or Class because that determines the name of the function.
    The contents for the definition will be indented.

    Example of a declaration:

        MyToaster& operator=(MyToaster&&);
        MyToaster& operator=(MyToaster&&) = delete;

    Examples of a definition:

        MyToaster::MyToaster& operator=(MyToaster&& rhs)
        {
            <contents>
        }
    """

    def __post_init__(self):
        """Post check the constructed data class members on validity."""
        ParentAndContents.__post_init__(self)
        if not isinstance(self.parent, Class) and not isinstance(self.parent, Struct):
            raise CppGenError('parent must be either a Class or Struct')

    def __str__(self) -> str:
        raise CppGenError('instead of str(), call as_decl() or as_def()')

    def as_decl(self) -> TextBlock:
        """Return the declaration as a multiline string."""
        full_signature = (f'{self.parent.name}& operator=({self.parent.name}&&)'
                          f'{self.initialization.value};')
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = (f'{self.parent.name}::{self.parent.name}& operator=('
                          f'{self.parent.name}&& rhs)')

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
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
        full_signature = f'~{self.parent.name}(){override}{self.initialization.value};'
        return TB(full_signature)

    def as_def(self) -> TextBlock:
        """Return the destructor definition as a multiline string."""
        if self.initialization != FunctionInitialization.NONE:
            return TextBlock()  # no definition is generated when declared with initialization

        full_signature = f'{self.parent.name}::~{self.parent.name}()'

        if not self.contents:
            return TB(f'{full_signature} {{}}')

        return TB([full_signature,
                   '{',
                   TB(self.contents).indent(),
                   '}'])


class RuleOfFive:
    """Class containing the rule of five (functions)."""

    __slots__ = ['_copy_constructor', '_move_constructor', '_copy_assign_constructor',
                 '_move_assign_constructor', '_destructor']

    # pylint: disable=too-many-arguments
    def __init__(self, parent: Struct or Class,
                 copy_constr: FunctionInitialization,
                 move_constr: FunctionInitialization,
                 copy_assign_constr: FunctionInitialization,
                 move_assign_constr: FunctionInitialization,
                 destructor: FunctionInitialization):
        # Assert the parameter arguments types
        assert_union_t(parent, [Struct, Class])
        assert_t(copy_constr, FunctionInitialization)
        assert_t(move_constr, FunctionInitialization)
        assert_t(copy_assign_constr, FunctionInitialization)
        assert_t(move_assign_constr, FunctionInitialization)
        assert_t(destructor, FunctionInitialization)
        # Instantiate and store the rule of five classes
        self._copy_constructor = CopyConstructor(parent=parent, initialization=copy_constr)
        self._move_constructor = MoveConstructor(parent=parent, initialization=move_constr)
        self._copy_assign_constructor = CopyAssignmentConstructor(parent=parent,
                                                                  initialization=copy_assign_constr)
        self._move_assign_constructor = MoveAssignmentConstructor(parent=parent,
                                                                  initialization=move_assign_constr)
        self._destructor = Destructor(parent=parent, initialization=destructor)

    def as_decl(self) -> TextBlock:
        """Return the rule of five declaration as a multiline string."""
        return TB([self.copy_constructor.as_decl(),
                   self.move_constructor.as_decl(),
                   self.copy_assign_constructor.as_decl(),
                   self.move_assign_constructor.as_decl(),
                   self.destructor.as_decl()])

    @property
    def copy_constructor(self) -> CopyConstructor:
        """Get the copy constructor instance."""
        return self._copy_constructor

    @property
    def move_constructor(self) -> MoveConstructor:
        """Get the move constructor instance."""
        return self._move_constructor

    @property
    def copy_assign_constructor(self) -> CopyAssignmentConstructor:
        """Get the copy assignment constructor instance."""
        return self._copy_assign_constructor

    @property
    def move_assign_constructor(self) -> MoveAssignmentConstructor:
        """Get the move assignment constructor instance."""
        return self._move_assign_constructor

    @property
    def destructor(self) -> Destructor:
        """Get the donstructor instance."""
        return self._destructor
