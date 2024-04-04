"""
json_ast - version 0.1.240108

Python module providing functionality to parse a Dezyne JSON-formatted AST.

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system modules
import orjson
from .ast import Binding, Bindings, Comment, Component, Data, EventDirection, EndPoint, Enum, \
    Event, Events, Extern, Fields, FileContents, Filename, Foreign, Formal, Formals, \
    FormalDirection, Import, Injected, Instance, Instances, Interface, Namespace, Port, \
    PortDirection, Ports, Range, Root, ScopeName, Signature, SubInt, System, Types
from .misc_utils import NamespaceTrail


class DznJsonError(Exception):
    """An error occurred during processing of JSON Dezyne AST contents."""


class ElementHelper:
    """Element helper class to acquire contents and report failures with a provided context."""

    def __init__(self, element: dict, caller_context: str):
        self._element = element
        self._ctx = caller_context
        if not isinstance(element, dict):
            raise DznJsonError(f'{self._ctx}: element is not of type "dict"')

    def tryget_str_value(self, key_name: str) -> str or None:
        """Try to get the str value of the specified key_name or reply None on failure."""
        if key_name not in self._element:
            return None

        if not isinstance(self._element[key_name], str):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "str"')

        return self._element[key_name]

    def get_str_value(self, key_name: str) -> str:
        """Get the str value of the specified key_name or raise an exception on failure."""
        result = self.tryget_str_value(key_name)
        if result is None:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        return result

    def tryget_dict_value(self, key_name: str) -> dict or None:
        """Try to get the dict value of the specified key_name or reply None on failure."""
        if key_name not in self._element:
            return None

        if not isinstance(self._element[key_name], dict):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "dict"')

        return self._element[key_name]

    def get_dict_value(self, key_name: str) -> dict:
        """Get the dict value of the specified key_name or raise an exception on failure."""
        result = self.tryget_dict_value(key_name)
        if result is None:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        return result

    def get_int_value(self, key_name: str) -> int:
        """Get the int value of the specified key_name or raise an exception on failure."""
        if key_name not in self._element:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        if not isinstance(self._element[key_name], int):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "int"')

        return self._element[key_name]

    def assert_class(self, value: str):
        """Assert a <class> key is present in the element with the specified value. Raise
        an exception on failure."""
        if '<class>' not in self._element:
            raise DznJsonError(f'{self._ctx}: missing "<class>" key')

        if self._element['<class>'] != value:
            raise DznJsonError(f'{self._ctx}: expecting <class> having value "{value}"')

    def get_list_value(self, key_name: str) -> list:
        """Get the list-typed value of the 'elements' key_name. Allowed to be empty."""
        if key_name not in self._element:
            raise DznJsonError(f'{self._ctx}: missing "{key_name}" key')

        if not isinstance(self._element[key_name], list):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "list"')

        return self._element[key_name]


def get_class_value(element: dict) -> str:
    """Get the value of the <class> key in the specified element."""
    if not isinstance(element, dict):
        raise DznJsonError('expecting element to be dictionary')
    if '<class>' not in element:
        raise DznJsonError('Missing <class>')
    return element['<class>']


def parse_binding(element: dict) -> Binding:
    """Parse a 'binding' <class> element."""
    elt = ElementHelper(element, 'parse_binding')
    elt.assert_class('binding')
    return Binding(left=parse_endpoint(elt.get_dict_value('left')),
                   right=parse_endpoint(elt.get_dict_value('right')))


def parse_bindings(element: dict) -> Bindings:
    """Parse a 'bindings' <class> element."""
    elt = ElementHelper(element, 'parse_bindings')
    elt.assert_class('bindings')
    return Bindings(elements=[parse_binding(x) for x in elt.get_list_value('elements')])


def parse_comment(element: dict) -> Comment:
    """Parse a 'comment' <class> element."""
    elt = ElementHelper(element, 'parse_comment')
    elt.assert_class('comment')
    return Comment(elt.get_str_value('string'))


def parse_component(element: dict, parent_ns: NamespaceTrail) -> Component:
    """Parse a 'component' <class> element."""
    elt = ElementHelper(element, 'parse_component')
    elt.assert_class('component')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Component(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                     name=name, ports=parse_ports(elt.get_dict_value('ports')))


def parse_data(element: dict) -> Data:
    """Parse a 'data' <class> element."""
    elt = ElementHelper(element, 'parse_data')
    elt.assert_class('data')
    return Data(value=elt.get_str_value('value'))


def parse_event_direction(value: str) -> EventDirection:
    """Parse a 'direction' value string and return as Direction Enum value."""
    if value == 'in':
        return EventDirection.IN
    if value == 'out':
        return EventDirection.OUT

    raise DznJsonError(f'parse_event_direction: invalid value "{value}"')


def parse_endpoint(element: dict) -> EndPoint:
    """Parse a 'end-point' <class> element."""
    elt = ElementHelper(element, 'parse_endpoint')
    elt.assert_class('end-point')
    return EndPoint(port_name=elt.get_str_value('port_name'),
                    instance_name=elt.tryget_str_value('instance_name'))


def parse_enum(element: dict, parent_ns: NamespaceTrail) -> Enum:
    """Parse a 'enum' <class> element."""
    elt = ElementHelper(element, 'parse_enum')
    elt.assert_class('enum')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Enum(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                name=name, fields=parse_fields(elt.get_dict_value('fields')))


def parse_extern(element: dict, parent_ns: NamespaceTrail) -> Extern:
    """Parse a 'extern' <class> element."""
    elt = ElementHelper(element, 'parse_extern')
    elt.assert_class('extern')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Extern(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name, value=parse_data(elt.get_dict_value('value')))


def parse_event(element: dict) -> Event:
    """Parse a 'event' <class> element."""
    elt = ElementHelper(element, 'parse_event')
    elt.assert_class('event')
    return Event(name=elt.get_str_value('name'),
                 signature=parse_signature(elt.get_dict_value('signature')),
                 direction=parse_event_direction(elt.get_str_value('direction')))


def parse_events(element: dict) -> Events:
    """Parse a 'events' <class> element."""
    elt = ElementHelper(element, 'parse_events')
    elt.assert_class('events')
    return Events(elements=[parse_event(x) for x in elt.get_list_value('elements')])


def parse_fields(element: dict) -> Fields:
    """Parse a 'fields' <class> element."""
    elt = ElementHelper(element, 'parse_fields')
    elt.assert_class('fields')
    return Fields(elt.get_list_value('elements'))


def parse_filename(element: dict) -> Filename:
    """Parse a 'file-name' <class> element."""
    elt = ElementHelper(element, 'parse_filename')
    elt.assert_class('file-name')
    return Filename(elt.get_str_value('name'))


def parse_foreign(element: dict, parent_ns: NamespaceTrail) -> Foreign:
    """Parse a 'foreign' <class> element."""
    elt = ElementHelper(element, 'parse_foreign')
    elt.assert_class('foreign')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Foreign(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                   name=name, ports=parse_ports(elt.get_dict_value('ports')))


def parse_formal_direction(value: str) -> FormalDirection:
    """Parse a 'direction' value string (as part of a formal) and return as
    FormalDirection Enum value."""
    if value == 'in':
        return FormalDirection.IN
    if value == 'out':
        return FormalDirection.OUT
    if value == 'inout':
        return FormalDirection.INOUT

    raise DznJsonError(f'parse_formal_direction: invalid value "{value}"')


def parse_formal(element: dict) -> Formal:
    """Parse a 'formal' <class> element."""
    elt = ElementHelper(element, 'parse_formal')
    elt.assert_class('formal')
    name = elt.get_str_value('name')
    type_name = parse_scope_name(elt.get_dict_value('type_name'))
    direction = parse_formal_direction(elt.get_str_value('direction'))
    return Formal(name=name, type_name=type_name, direction=direction)


def parse_formals(element: dict) -> Formals:
    """Parse a 'formals' <class> element."""
    elt = ElementHelper(element, 'parse_formals')
    elt.assert_class('formals')
    return Formals(elements=[parse_formal(x) for x in elt.get_list_value('elements')])


def parse_import(element: dict) -> Import:
    """Parse a 'import' <class> element."""
    elt = ElementHelper(element, 'parse_import')
    elt.assert_class('import')
    return Import(elt.get_str_value('name'))


def parse_instance(element: dict) -> Instance:
    """Parse a 'instance' <class> element."""
    elt = ElementHelper(element, 'parse_instance')
    elt.assert_class('instance')
    return Instance(name=elt.get_str_value('name'),
                    type_name=parse_scope_name(elt.get_dict_value('type_name')))


def parse_instances(element: dict) -> Instances:
    """Parse a 'instances' <class> element."""
    elt = ElementHelper(element, 'parse_instances')
    elt.assert_class('instances')
    return Instances(elements=[parse_instance(x) for x in elt.get_list_value('elements')])


def parse_interface(element: dict, parent_ns: NamespaceTrail) -> Interface:
    """Parse a 'interface' <class> element."""
    elt = ElementHelper(element, 'parse_interface')
    elt.assert_class('interface')
    name = parse_scope_name(elt.get_dict_value('name'))
    ns_trail = NamespaceTrail(parent_ns, str(name))
    return Interface(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                     ns_trail=ns_trail, name=name,
                     types=parse_types(elt.get_dict_value('types'), ns_trail),
                     events=parse_events(elt.get_dict_value('events')))


def parse_namespace(element: dict) -> Namespace:
    """Parse a 'namespace' <class> element."""
    elt = ElementHelper(element, 'parse_namespace')
    elt.assert_class('namespace')
    return Namespace(scope_name=parse_scope_name(elt.get_dict_value('name')),
                     elements=elt.get_list_value('elements'))


def parse_port(element: dict) -> Port:
    """Parse a 'port' <class> element."""
    elt = ElementHelper(element, 'parse_port')
    elt.assert_class('port')
    return Port(name=elt.get_str_value('name'),
                type_name=parse_scope_name(elt.get_dict_value('type_name')),
                direction=parse_port_direction(elt.get_str_value('direction')),
                formals=parse_formals(elt.get_dict_value('formals')),
                injected=parse_port_injected_indication(element))


def parse_ports(element: dict) -> Ports:
    """Parse a 'ports' <class> element."""
    elt = ElementHelper(element, 'parse_ports')
    elt.assert_class('ports')
    return Ports(elements=[parse_port(x) for x in elt.get_list_value('elements')])


def parse_port_direction(value: str) -> PortDirection:
    """Parse a port 'direction' value string and return as PortDirection Enum value."""
    if value == 'requires':
        return PortDirection.REQUIRES
    if value == 'provides':
        return PortDirection.PROVIDES

    raise DznJsonError(f'parse_port_direction: invalid value "{value}"')


def parse_port_injected_indication(element: dict) -> Injected:
    """Parse a 'port' <class> element and detected an "injected" indication."""
    elt = ElementHelper(element, 'parse_injected_port')
    elt.assert_class('port')
    opt_injected = elt.tryget_str_value('injected?')
    if opt_injected is None:
        return Injected(False)
    if opt_injected == 'injected':
        return Injected(True)

    raise DznJsonError(f'parse_injected_port: invalid "injected?" value "{opt_injected}"')


def parse_range(element: dict) -> Range:
    """Parse a 'range' <class> element."""
    elt = ElementHelper(element, 'parse_range')
    elt.assert_class('range')
    return Range(from_int=elt.get_int_value('from'), to_int=elt.get_int_value('to'))


def parse_subint(element: dict, parent_ns: NamespaceTrail) -> SubInt:
    """Parse a 'subint' <class> element."""
    elt = ElementHelper(element, 'parse_subint')
    elt.assert_class('subint')
    name = parse_scope_name(elt.get_dict_value('name'))
    return SubInt(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name, range=parse_range(elt.get_dict_value('range')))


def parse_root(element: dict) -> Root:
    """Parse a 'root' <class> element."""
    elt = ElementHelper(element, 'parse_root')
    elt.assert_class('root')
    opt_comment = elt.tryget_dict_value('comment')
    return Root(comment=None if opt_comment is None else parse_comment(opt_comment),
                elements=elt.get_list_value('elements'),
                working_dir=elt.get_str_value('working-directory'))


def parse_scope_name(element: dict) -> ScopeName:
    """Parse a 'scope_name' <class> element."""
    elt = ElementHelper(element, 'parse_scope_name')
    elt.assert_class('scope_name')
    ids = elt.get_list_value('ids')
    if len(ids) == 0:
        raise DznJsonError('parse_scope_name: list "ids" is empty')
    return ScopeName(value=ids)


def parse_signature(element: dict) -> Signature:
    """Parse a 'signature' <class> element."""
    elt = ElementHelper(element, 'parse_signature')
    elt.assert_class('signature')
    return Signature(type_name=parse_scope_name(elt.get_dict_value('type_name')),
                     formals=parse_formals(elt.get_dict_value('formals')))


def parse_system(element: dict, parent_ns: NamespaceTrail) -> System:
    """Parse a 'system' <class> element."""
    elt = ElementHelper(element, 'parse_system')
    elt.assert_class('system')
    name = parse_scope_name(elt.get_dict_value('name'))
    return System(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name,
                  ports=parse_ports(elt.get_dict_value('ports')),
                  instances=parse_instances(elt.get_dict_value('instances')),
                  bindings=parse_bindings(elt.get_dict_value('bindings')))


def parse_types(element: dict, parent_ns: NamespaceTrail) -> Types:
    """Parse a 'types' <class> element."""
    elt = ElementHelper(element, 'parse_types')
    elt.assert_class('types')
    elements = []
    for type_item in elt.get_list_value('elements'):
        cls = get_class_value(type_item)
        if cls == 'enum':
            elements.append(parse_enum(type_item, parent_ns))
        elif cls == 'subint':
            elements.append(parse_subint(type_item, parent_ns))
        else:
            print(f'parse_types: skipping item {cls}')
    return Types(elements=elements)


class DznJsonAst:
    """Main class to process Dezyne JSON AST."""

    _ast: dict = None
    _verbose: bool
    _ns_trail: NamespaceTrail
    _file_contents: FileContents

    def __init__(self, json_contents: str = None, verbose: bool = False):
        if json_contents is not None:
            self._ast = orjson.loads(json_contents)
        self._verbose = verbose
        self._ns_trail = NamespaceTrail()
        self._file_contents = FileContents()

    def load_file(self, dezyne_filepath: str):
        """Load Dezyne JSON contents from a file."""
        with open(dezyne_filepath, 'rb') as file:
            self._ast = orjson.loads(file.read())
        return self  # Fluent interface

    def log(self, message):
        """Log a message when verbose has been enabled."""
        if self._verbose:
            print(message)

    @property
    def ast(self) -> dict:
        """Get the (root of the) AST."""
        return self._ast

    @property
    def file_contents(self) -> FileContents:
        """Get the file contents."""
        return self._file_contents

    def process(self) -> FileContents:
        """"Start processing the preloaded Dezyne JSON AST and return the FileContents."""
        root = parse_root(self.ast)
        for element in root.elements:
            self.parse_element(element, self._ns_trail)
        return self.file_contents

    def parse_element(self, element, parent_ns: NamespaceTrail):
        """"Parse an element and identify its type."""
        fc = self.file_contents

        if isinstance(element, dict):
            cls = get_class_value(element)
            if cls == 'component':
                fc.components.append(parse_component(element, parent_ns))
            elif cls == 'enum':
                fc.enums.append(parse_enum(element, parent_ns))
            elif cls == 'extern':
                fc.externs.append(parse_extern(element, parent_ns))
            elif cls == 'foreign':
                fc.foreigns.append(parse_foreign(element, parent_ns))
            elif cls == 'file-name':
                fc.filenames.append(parse_filename(element))
            elif cls == 'import':
                fc.imports.append(parse_import(element))
            elif cls == 'interface':
                interface = parse_interface(element, parent_ns)
                fc.interfaces.append(interface)
                fc.enums.extend(interface.types.enums)
                fc.subints.extend(interface.types.subints)
            elif cls == 'namespace':
                namespace = parse_namespace(element)
                sub_ns = NamespaceTrail(parent=parent_ns,
                                        scope_name=str(namespace.scope_name))
                for sub_element in namespace.elements:
                    self.parse_element(sub_element, sub_ns)
            elif cls == 'system':
                fc.systems.append(parse_system(element, parent_ns))
            elif cls == 'subint':
                fc.subints.append(parse_subint(element, parent_ns))
            else:
                self.log(f'Unknown element class {cls}')
        else:
            self.log('WARNING: skipping non-dict element')
