"""
Module providing functionality to parse a Dezyne JSON-formatted AST.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
from typing import List, Optional
import orjson  # pylint: disable=no-member

# dznpy modules
from .ast import Binding, Bindings, Comment, Component, Data, EventDirection, EndPoint, Enum, \
    Event, Events, Extern, Fields, FileContents, Filename, Foreign, Formal, Formals, \
    FormalDirection, Import, Injected, Instance, Instances, Interface, Namespace, Port, \
    PortDirection, Ports, Range, Root, ScopeName, Signature, SubInt, System, Types
from .scoping import NamespaceTree, ns_ids_t


class DznJsonError(Exception):
    """An error occurred during processing of JSON Dezyne AST contents."""


class NodeHelper:
    """node helper class to acquire contents and report failures with a provided context."""
    __slots__ = ['_ctx', '_node']

    def __init__(self, node: dict, caller_context: str):
        self._node = node
        self._ctx = caller_context
        if not isinstance(node, dict):
            raise DznJsonError(f'{self._ctx}: node is not of type "dict"')

    def tryget_str_value(self, key_name: str) -> str or None:
        """Try to get the str value of the specified key_name or reply None on failure."""
        if key_name not in self._node:
            return None

        if not isinstance(self._node[key_name], str):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "str"')

        return self._node[key_name]

    def get_str_value(self, key_name: str) -> str:
        """Get the str value of the specified key_name or raise an exception on failure."""
        result = self.tryget_str_value(key_name)
        if result is None:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        return result

    def tryget_dict_value(self, key_name: str) -> dict or None:
        """Try to get the dict value of the specified key_name or reply None on failure."""
        if key_name not in self._node:
            return None

        if not isinstance(self._node[key_name], dict):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "dict"')

        return self._node[key_name]

    def get_dict_value(self, key_name: str) -> dict:
        """Get the dict value of the specified key_name or raise an exception on failure."""
        result = self.tryget_dict_value(key_name)
        if result is None:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        return result

    def get_int_value(self, key_name: str) -> int:
        """Get the int value of the specified key_name or raise an exception on failure."""
        if key_name not in self._node:
            raise DznJsonError(f'{self._ctx}: missing key "{key_name}"')

        if not isinstance(self._node[key_name], int):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "int"')

        return self._node[key_name]

    def assert_class(self, value: str):
        """Assert a <class> key is present in the node with the specified value. Raise
        an exception on failure."""
        if '<class>' not in self._node:
            raise DznJsonError(f'{self._ctx}: missing "<class>" key')

        if self._node['<class>'] != value:
            raise DznJsonError(f'{self._ctx}: expecting <class> having value "{value}"')

    def assert_class_aliased(self, values: List[str]):
        """Assert a <class> key is present in the node with the specified value. Raise
        an exception on failure."""
        if '<class>' not in self._node:
            raise DznJsonError(f'{self._ctx}: missing "<class>" key')

        if not self._node['<class>'] in values:
            raise DznJsonError(f'{self._ctx}: expecting <class> having one of the values {values}')

    def get_list_value(self, key_name: str) -> list:
        """Get the list-typed value of the 'elements' key_name. Allowed to be empty."""
        if key_name not in self._node:
            raise DznJsonError(f'{self._ctx}: missing "{key_name}" key')

        if not isinstance(self._node[key_name], list):
            raise DznJsonError(f'{self._ctx}: key "{key_name}" is not of type "list"')

        return self._node[key_name]


def get_class_value(node: dict) -> str:
    """Get the value of the <class> key in the specified node."""
    if not isinstance(node, dict):
        raise DznJsonError('expecting node to be dictionary')
    if '<class>' not in node:
        raise DznJsonError('Missing <class>')
    return node['<class>']


def parse_binding(node: dict) -> Binding:
    """Parse a 'binding' <class> node."""
    elt = NodeHelper(node, 'parse_binding')
    elt.assert_class('binding')
    return Binding(left=parse_endpoint(elt.get_dict_value('left')),
                   right=parse_endpoint(elt.get_dict_value('right')))


def parse_bindings(node: dict) -> Bindings:
    """Parse a 'bindings' <class> node."""
    elt = NodeHelper(node, 'parse_bindings')
    elt.assert_class('bindings')
    return Bindings(elements=[parse_binding(x) for x in elt.get_list_value('elements')])


def parse_comment(node: dict) -> Comment:
    """Parse a 'comment' <class> node."""
    elt = NodeHelper(node, 'parse_comment')
    elt.assert_class('comment')
    return Comment(elt.get_str_value('string'))


def parse_component(node: dict, parent_ns: NamespaceTree) -> Component:
    """Parse a 'component' <class> node."""
    elt = NodeHelper(node, 'parse_component')
    elt.assert_class('component')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Component(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                     name=name, ports=parse_ports(elt.get_dict_value('ports')))


def parse_data(node: dict) -> Data:
    """Parse a 'data' <class> node."""
    elt = NodeHelper(node, 'parse_data')
    elt.assert_class('data')
    return Data(value=elt.get_str_value('value'))


def parse_event_direction(value: str) -> EventDirection:
    """Parse a 'direction' value string and return as Direction Enum value."""
    if value == 'in':
        return EventDirection.IN
    if value == 'out':
        return EventDirection.OUT

    raise DznJsonError(f'parse_event_direction: invalid value "{value}"')


def parse_endpoint(node: dict) -> EndPoint:
    """Parse a 'end-point' <class> node."""
    elt = NodeHelper(node, 'parse_endpoint')
    elt.assert_class('end-point')
    return EndPoint(port_name=elt.get_str_value('port_name'),
                    instance_name=elt.tryget_str_value('instance_name'))


def parse_enum(node: dict, parent_ns: NamespaceTree) -> Enum:
    """Parse a 'enum' <class> node."""
    elt = NodeHelper(node, 'parse_enum')
    elt.assert_class('enum')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Enum(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                name=name, fields=parse_fields(elt.get_dict_value('fields')))


def parse_extern(node: dict, parent_ns: NamespaceTree) -> Extern:
    """Parse a 'extern' <class> node."""
    elt = NodeHelper(node, 'parse_extern')
    elt.assert_class('extern')
    name = parse_scope_name(elt.get_dict_value('name'))
    return Extern(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name, value=parse_data(elt.get_dict_value('value')))


def parse_event(node: dict) -> Event:
    """Parse a 'event' <class> node."""
    elt = NodeHelper(node, 'parse_event')
    elt.assert_class('event')
    evt = Event(name=elt.get_str_value('name'),
                signature=parse_signature(elt.get_dict_value('signature')),
                direction=parse_event_direction(elt.get_str_value('direction')))

    # detect invalid content (1)
    if evt.direction == EventDirection.OUT and evt.signature.type_name.value != ns_ids_t('void'):
        raise DznJsonError('parse_event: Out events have a -void- return value type')

    # detect invalid content (2)
    if evt.direction == EventDirection.OUT:
        if [f for f in evt.signature.formals.elements if f.direction == FormalDirection.OUT]:
            raise DznJsonError('parse_event: Out events can not have an -out- parameter argument')

    return evt


def parse_events(node: dict) -> Events:
    """Parse a 'events' <class> node."""
    elt = NodeHelper(node, 'parse_events')
    elt.assert_class('events')
    return Events(elements=[parse_event(x) for x in elt.get_list_value('elements')])


def parse_fields(node: dict) -> Fields:
    """Parse a 'fields' <class> node."""
    elt = NodeHelper(node, 'parse_fields')
    elt.assert_class('fields')
    return Fields(elt.get_list_value('elements'))


def parse_filename(node: dict) -> Filename:
    """Parse a 'file-name' <class> node."""
    elt = NodeHelper(node, 'parse_filename')
    elt.assert_class('file-name')
    return Filename(elt.get_str_value('name'))


def parse_foreign(node: dict, parent_ns: NamespaceTree) -> Foreign:
    """Parse a 'foreign' <class> node."""
    elt = NodeHelper(node, 'parse_foreign')
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


def parse_formal(node: dict) -> Formal:
    """Parse a 'formal' <class> node."""
    elt = NodeHelper(node, 'parse_formal')
    elt.assert_class('formal')
    name = elt.get_str_value('name')
    type_name = parse_scope_name(elt.get_dict_value('type_name'))
    direction = parse_formal_direction(elt.get_str_value('direction'))
    return Formal(name=name, type_name=type_name, direction=direction)


def parse_formals(node: dict) -> Formals:
    """Parse a 'formals' <class> node."""
    elt = NodeHelper(node, 'parse_formals')
    elt.assert_class('formals')
    return Formals(elements=[parse_formal(x) for x in elt.get_list_value('elements')])


def parse_import(node: dict) -> Import:
    """Parse a 'import' <class> node."""
    elt = NodeHelper(node, 'parse_import')
    elt.assert_class('import')
    return Import(elt.get_str_value('name'))


def parse_instance(node: dict) -> Instance:
    """Parse a 'instance' <class> node."""
    elt = NodeHelper(node, 'parse_instance')
    elt.assert_class('instance')
    return Instance(name=elt.get_str_value('name'),
                    type_name=parse_scope_name(elt.get_dict_value('type_name')))


def parse_instances(node: dict) -> Instances:
    """Parse a 'instances' <class> node."""
    elt = NodeHelper(node, 'parse_instances')
    elt.assert_class('instances')
    return Instances(elements=[parse_instance(x) for x in elt.get_list_value('elements')])


def parse_interface(node: dict, parent_ns: NamespaceTree) -> Interface:
    """Parse a 'interface' <class> node."""
    elt = NodeHelper(node, 'parse_interface')
    elt.assert_class('interface')
    name = parse_scope_name(elt.get_dict_value('name'))
    ns_trail = NamespaceTree(parent_ns, name.value)
    return Interface(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                     ns_trail=ns_trail, name=name,
                     types=parse_types(elt.get_dict_value('types'), ns_trail),
                     events=parse_events(elt.get_dict_value('events')))


def parse_namespace(node: dict) -> Namespace:
    """Parse a 'namespace' <class> node."""
    elt = NodeHelper(node, 'parse_namespace')
    elt.assert_class('namespace')
    return Namespace(scope_name=parse_scope_name(elt.get_dict_value('name')),
                     elements=elt.get_list_value('elements'))


def parse_port(node: dict) -> Port:
    """Parse a 'port' <class> node."""
    elt = NodeHelper(node, 'parse_port')
    elt.assert_class('port')
    return Port(name=elt.get_str_value('name'),
                type_name=parse_scope_name(elt.get_dict_value('type_name')),
                direction=parse_port_direction(elt.get_str_value('direction')),
                formals=parse_formals(elt.get_dict_value('formals')),
                injected=parse_port_injected_indication(node))


def parse_ports(node: dict) -> Ports:
    """Parse a 'ports' <class> node."""
    elt = NodeHelper(node, 'parse_ports')
    elt.assert_class('ports')
    return Ports(elements=[parse_port(x) for x in elt.get_list_value('elements')])


def parse_port_direction(value: str) -> PortDirection:
    """Parse a port 'direction' value string and return as PortDirection Enum value."""
    if value == 'requires':
        return PortDirection.REQUIRES
    if value == 'provides':
        return PortDirection.PROVIDES

    raise DznJsonError(f'parse_port_direction: invalid value "{value}"')


def parse_port_injected_indication(node: dict) -> Injected:
    """Parse a 'port' <class> node and detected an "injected" indication."""
    elt = NodeHelper(node, 'parse_injected_port')
    elt.assert_class('port')
    opt_injected = elt.tryget_str_value('injected?')
    if opt_injected is None:  # retry with old scheme [<2.15.0]
        opt_injected = elt.tryget_str_value('injected')

    if opt_injected is None:
        return Injected(False)
    if opt_injected == 'injected':
        return Injected(True)

    raise DznJsonError(f'parse_injected_port: invalid value "{opt_injected}"')


def parse_range(node: dict) -> Range:
    """Parse a 'range' <class> node."""
    elt = NodeHelper(node, 'parse_range')
    elt.assert_class('range')
    return Range(from_int=elt.get_int_value('from'), to_int=elt.get_int_value('to'))


def parse_subint(node: dict, parent_ns: NamespaceTree) -> SubInt:
    """Parse a 'subint' <class> node."""
    elt = NodeHelper(node, 'parse_subint')

    # int [2.11.0 - 2.16.5] replaced by subint [>= 2.17.0]
    elt.assert_class_aliased(['int', 'subint'])
    name = parse_scope_name(elt.get_dict_value('name'))
    return SubInt(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name, range=parse_range(elt.get_dict_value('range')))


def parse_root(node: dict) -> Root:
    """Parse a 'root' <class> node."""
    elt = NodeHelper(node, 'parse_root')
    elt.assert_class('root')
    opt_comment = elt.tryget_dict_value('comment')
    return Root(comment=None if opt_comment is None else parse_comment(opt_comment),
                elements=elt.get_list_value('elements'),
                working_dir=elt.tryget_str_value('working-directory'))


def parse_scope_name(node: dict) -> ScopeName:
    """Parse a 'scope_name' <class> node."""
    elt = NodeHelper(node, 'parse_scope_name')
    elt.assert_class('scope_name')
    ids = elt.get_list_value('ids')
    if not ids:
        raise DznJsonError('parse_scope_name: list "ids" is empty')
    return ScopeName(value=ns_ids_t(ids))


def parse_signature(node: dict) -> Signature:
    """Parse a 'signature' <class> node."""
    elt = NodeHelper(node, 'parse_signature')
    elt.assert_class('signature')
    return Signature(type_name=parse_scope_name(elt.get_dict_value('type_name')),
                     formals=parse_formals(elt.get_dict_value('formals')))


def parse_system(node: dict, parent_ns: NamespaceTree) -> System:
    """Parse a 'system' <class> node."""
    elt = NodeHelper(node, 'parse_system')
    elt.assert_class('system')
    name = parse_scope_name(elt.get_dict_value('name'))
    return System(fqn=parent_ns.fqn_member_name(name.value), parent_ns=parent_ns,
                  name=name,
                  ports=parse_ports(elt.get_dict_value('ports')),
                  instances=parse_instances(elt.get_dict_value('instances')),
                  bindings=parse_bindings(elt.get_dict_value('bindings')))


def parse_types(node: dict, parent_ns: NamespaceTree) -> Types:
    """Parse a 'types' <class> node."""
    elt = NodeHelper(node, 'parse_types')
    elt.assert_class('types')
    nodes = []
    for type_item in elt.get_list_value('elements'):
        cls = get_class_value(type_item)
        if cls == 'enum':
            nodes.append(parse_enum(type_item, parent_ns))
        elif cls in ['int', 'subint']:  # int [2.11.0 - 2.16.5] replaced by subint [>= 2.17.0]
            nodes.append(parse_subint(type_item, parent_ns))
        else:
            pass
    return Types(elements=nodes)


class DznJsonAst:
    """Main class to process Dezyne JSON AST."""
    __slots__ = ['_file_contents', '_ns_trail', '_json_ast', '_verbose']

    def __init__(self, json_contents: str = None, verbose: bool = False):
        self._file_contents = FileContents()
        self._ns_trail = NamespaceTree()
        self._json_ast = orjson.loads(json_contents) if json_contents else None

        self._verbose = verbose

    def load_file(self, dezyne_filepath: str):
        """Load Dezyne JSON contents from a file."""
        with open(dezyne_filepath, 'rb') as file:
            self._json_ast = orjson.loads(file.read())  # pylint: disable=no-member
        return self  # Fluent interface

    def log(self, message):
        """Log a message when verbose has been enabled."""
        if self._verbose:
            print(message)

    @property
    def ast(self) -> Optional[dict]:
        """Get the (root node of the) JSON AST."""
        return self._json_ast

    @property
    def file_contents(self) -> FileContents:
        """Get the file contents."""
        return self._file_contents

    def process(self) -> FileContents:
        """Start processing the preloaded Dezyne JSON AST and return the FileContents."""
        root_node = parse_root(self.ast)
        for child_node in root_node.elements:
            self._parse_node(child_node, self._ns_trail)
        return self.file_contents

    def _parse_node(self, node, parent_ns: NamespaceTree):
        """Parse a Dezyne JSON AST node and identify its type."""
        fct = self.file_contents

        if not isinstance(node, dict):
            self.log('WARNING: skipping non-dict node')
            return

        class_value = get_class_value(node)

        node_handlers = {
            'component': lambda e: fct.components.append(parse_component(e, parent_ns)),
            'enum': lambda e: fct.enums.append(parse_enum(e, parent_ns)),
            'extern': lambda e: fct.externs.append(parse_extern(e, parent_ns)),
            'foreign': lambda e: fct.foreigns.append(parse_foreign(e, parent_ns)),
            'file-name': lambda e: fct.filenames.append(parse_filename(e)),
            'import': lambda e: fct.imports.append(parse_import(e)),
            'interface': lambda e: self._handle_interface(e, fct, parent_ns),
            'namespace': lambda e: self._handle_namespace(e, parent_ns),
            'system': lambda e: fct.systems.append(parse_system(e, parent_ns)),
            'subint': lambda e: fct.subints.append(parse_subint(e, parent_ns)),
        }

        handler = node_handlers.get(class_value)
        if handler:
            handler(node)
        else:
            self.log(f'Skipping parsing class value: {class_value}')

    @staticmethod
    def _handle_interface(node, fct, parent_ns):
        """Parse a Dezyne Interface node."""
        interface = parse_interface(node, parent_ns)
        fct.interfaces.append(interface)
        fct.enums.extend(interface.types.enums)
        fct.subints.extend(interface.types.subints)

    def _handle_namespace(self, node, parent_ns):
        """Parse a Dezyne Namespace node."""
        namespace = parse_namespace(node)
        child_ns = NamespaceTree(parent=parent_ns, scope_name=namespace.scope_name.value)
        for child_node in namespace.elements:
            self._parse_node(child_node, child_ns)
