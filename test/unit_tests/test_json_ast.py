"""
Testsuite validating the json_ast module

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

# system modules
import pytest
from unittest import TestCase
from typing import List
from orjson import JSONDecodeError

# dznpy modules
from dznpy.scoping import NamespaceTree, ns_ids_t, NamespaceIds

# system-under-test
from dznpy import ast, json_ast
from dznpy.json_ast import DznJsonAst, DznJsonError

# test helpers
from common.helpers import resolve
from testdata_json_ast import *

# test constants
DZNJSON_FILE = resolve(__file__, TOASTER_SYSTEM_JSON_FILE)
CPP_FILE = resolve(__file__, TOASTER_SYSTEM_CPP_FILE)
SOME_JSON_FILE = resolve(__file__, VSCODE_WORKSPACE_FILE)


class DznTestCase(TestCase):
    _root_ns: NamespaceTree
    _nested_ns: NamespaceTree

    def setUp(self):
        self._root_ns = NamespaceTree()
        self._nested_ns = NamespaceTree(parent=NamespaceTree(parent=NamespaceTree(), scope_name=ns_ids_t('My')),
                                        scope_name=ns_ids_t('Project'))


class BindingTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_binding(dzn.ast)
        assert str(exc.value) == 'parse_binding: expecting <class> having value "binding"'

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=BINDING)
        sut = json_ast.parse_binding(dzn.ast)
        assert isinstance(sut, ast.Binding)
        assert sut.left.port_name == 'api'
        assert sut.left.instance_name is None
        assert sut.right.port_name == 'myport'
        assert sut.right.instance_name == 'mytoaster'


class BindingsTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_bindings(dzn.ast)
        assert str(exc.value) == 'parse_bindings: expecting <class> having value "bindings"'

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=BINDINGS)
        sut = json_ast.parse_bindings(dzn.ast)
        assert isinstance(sut, ast.Bindings)
        assert len(sut.elements) == 1
        assert sut.elements[0].left.port_name == 'api'
        assert sut.elements[0].right.port_name == 'myport'


class CommentTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_comment', 'comment')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=COMMENT)
        sut = json_ast.parse_comment(dzn.ast)
        assert isinstance(sut, ast.Comment)
        assert sut.value == '// Some comment\n'


class ComponentTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_component', 'component', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=COMPONENT)
        sut = json_ast.parse_component(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Component)
        assert sut.fqn == ns_ids_t('Toaster')
        assert sut.name.value == ns_ids_t('Toaster')
        assert str(sut.name) == 'Toaster'
        assert isinstance(sut.ports, ast.Ports)
        assert len(sut.ports.elements) == 2
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.components) == 1
        assert dzn.file_contents.components[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=COMPONENT)
        sut = json_ast.parse_component(dzn.ast, self._nested_ns)
        assert isinstance(sut, ast.Component)
        assert sut.fqn == ns_ids_t('My.Project.Toaster')
        assert sut.name.value == ns_ids_t('Toaster')
        assert str(sut.name) == 'Toaster'


class DataTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_data', 'data')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=DATA)
        sut = json_ast.parse_data(dzn.ast)
        assert isinstance(sut, ast.Data)
        assert sut.value == 'size_t'


class DirectionsTest(DznTestCase):

    @staticmethod
    def test_formal_direction_ok():
        assert json_ast.parse_formal_direction('in') == ast.FormalDirection.IN
        assert json_ast.parse_formal_direction('out') == ast.FormalDirection.OUT
        assert json_ast.parse_formal_direction('inout') == ast.FormalDirection.INOUT

    @staticmethod
    def test_formal_direction_fail():
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_formal_direction('bogus')
        assert str(exc.value) == 'parse_formal_direction: invalid value "bogus"'

    @staticmethod
    def test_event_direction_ok():
        assert json_ast.parse_event_direction('in') == ast.EventDirection.IN
        assert json_ast.parse_event_direction('out') == ast.EventDirection.OUT

    @staticmethod
    def test_event_direction_fail():
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_event_direction('inout')
        assert str(exc.value) == 'parse_event_direction: invalid value "inout"'

        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_event_direction('bogus')
        assert str(exc.value) == 'parse_event_direction: invalid value "bogus"'


class EndPointTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_endpoint(dzn.ast)
        assert str(exc.value) == 'parse_endpoint: expecting <class> having value "end-point"'

    @staticmethod
    def test_ok_port_name_only():
        dzn = DznJsonAst(json_contents=ENDPOINT1)
        sut = json_ast.parse_endpoint(dzn.ast)
        assert isinstance(sut, ast.EndPoint)
        assert sut.port_name == 'api'
        assert sut.instance_name is None

    @staticmethod
    def test_ok_port_and_instance_name():
        dzn = DznJsonAst(json_contents=ENDPOINT2)
        sut = json_ast.parse_endpoint(dzn.ast)
        assert isinstance(sut, ast.EndPoint)
        assert sut.port_name == 'myport'
        assert sut.instance_name == 'mytoaster'


class EnumTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_enum', 'enum', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=ENUM)
        sut = json_ast.parse_enum(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Enum)
        assert str(sut.name) == 'Result'
        assert sut.name.value == ns_ids_t('Result')
        assert sut.fields.elements == ['Ok', 'Fail', 'Error']
        assert sut.fqn == ns_ids_t('Result')
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.enums) == 1
        assert dzn.file_contents.enums[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=ENUM)
        sut = json_ast.parse_enum(dzn.ast, self._nested_ns)
        assert isinstance(sut, ast.Enum)
        assert str(sut.name) == 'Result'
        assert sut.name.value == ns_ids_t('Result')
        assert sut.fqn == ns_ids_t('My.Project.Result')


class EventTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_event', 'event')

    @staticmethod
    def test_event_direction_in_ok():
        dzn = DznJsonAst(json_contents=EVENT_IN)
        sut = json_ast.parse_event(dzn.ast)
        assert isinstance(sut, ast.Event)
        assert sut.name == 'SwitchOn'
        assert sut.direction == ast.EventDirection.IN
        assert isinstance(sut.signature, ast.Signature)
        assert sut.signature.type_name.value == ns_ids_t('Result')

    @staticmethod
    def test_event_direction_out_ok():
        dzn = DznJsonAst(json_contents=EVENT_OUT)
        sut = json_ast.parse_event(dzn.ast)
        assert isinstance(sut, ast.Event)
        assert sut.name == 'Fail'
        assert sut.direction == ast.EventDirection.OUT
        assert isinstance(sut.signature, ast.Signature)
        assert sut.signature.type_name.value == ns_ids_t('void')

    @staticmethod
    def test_event_direction_out_fail_on_return_type():
        with pytest.raises(DznJsonError) as exc:
            dzn = DznJsonAst(json_contents=EVENT_OUT_BOGUS1)
            json_ast.parse_event(dzn.ast)
        assert str(exc.value) == 'parse_event: Out events have a -void- return value type'

    @staticmethod
    def test_event_direction_out_fail_on_out_formal():
        with pytest.raises(DznJsonError) as exc:
            dzn = DznJsonAst(json_contents=EVENT_OUT_BOGUS2)
            json_ast.parse_event(dzn.ast)
        assert str(exc.value) == 'parse_event: Out events can not have an -out- parameter argument'


class EventsTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_events', 'events')

    @staticmethod
    def test_no_elements():
        dzn = DznJsonAst(json_contents=EVENTS_EMPTY)
        sut = json_ast.parse_events(dzn.ast)
        assert isinstance(sut, ast.Events)
        assert isinstance(sut.elements, list)
        assert len(sut.elements) == 0

    @staticmethod
    def test_two_elements():
        dzn = DznJsonAst(json_contents=EVENTS_TWO_ITEMS)
        sut = json_ast.parse_events(dzn.ast)
        assert isinstance(sut, ast.Events)
        assert len(sut.elements) == 2
        assert sut.elements[0].direction == ast.EventDirection.IN
        assert sut.elements[1].direction == ast.EventDirection.OUT


class ExternTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_extern', 'extern', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=EXTERN)
        sut = json_ast.parse_extern(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Extern)
        assert str(sut.name) == 'MilliSeconds'
        assert sut.name.value == ns_ids_t('MilliSeconds')
        assert sut.fqn == ns_ids_t('MilliSeconds')
        assert isinstance(sut.value, ast.Data)
        assert sut.value.value == 'size_t'
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.externs) == 1
        assert dzn.file_contents.externs[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=EXTERN)
        sut = json_ast.parse_extern(dzn.ast, self._nested_ns)
        assert str(sut.name) == 'MilliSeconds'
        assert sut.name.value == ns_ids_t('MilliSeconds')
        assert sut.fqn == ns_ids_t('My.Project.MilliSeconds')


class FieldsTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_fields', 'fields')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=FIELDS)
        sut = json_ast.parse_fields(dzn.ast)
        assert isinstance(sut, ast.Fields)
        assert sut.elements == ['Ok', 'Fail', 'Error']


class FilenameTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_filename', 'file-name')

    def test_ok(self):
        dzn = DznJsonAst(json_contents=FILENAME)
        sut = json_ast.parse_filename(dzn.ast)
        assert isinstance(sut, ast.Filename)
        assert sut.name == './Toaster.dzn'
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.filenames) == 1
        assert dzn.file_contents.filenames[0] == sut


class ForeignTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_foreign', 'foreign', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=FOREIGN)
        sut = json_ast.parse_foreign(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Foreign)
        assert sut.fqn == ns_ids_t('Timer')
        assert str(sut.name) == 'Timer'
        assert sut.name.value == ns_ids_t('Timer')
        assert isinstance(sut.ports, ast.Ports)
        assert len(sut.ports.elements) == 2
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.foreigns) == 1
        assert dzn.file_contents.foreigns[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=FOREIGN)
        sut = json_ast.parse_foreign(dzn.ast, self._nested_ns)
        assert isinstance(sut, ast.Foreign)
        assert sut.fqn == ns_ids_t('My.Project.Timer')
        assert str(sut.name) == 'Timer'
        assert sut.name.value == ns_ids_t('Timer')


class FormalTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_formal', 'formal')

    @staticmethod
    def test_formal_direction_in_ok():
        dzn = DznJsonAst(json_contents=FORMAL_IN)
        sut = json_ast.parse_formal(dzn.ast)
        assert isinstance(sut, ast.Formal)
        assert (sut.name, str(sut.type_name)) == ('waitingTimeMs', 'MilliSeconds')
        assert sut.type_name.value == ns_ids_t('MilliSeconds')
        assert sut.direction == ast.FormalDirection.IN

    @staticmethod
    def test_formal_direction_out_ok():
        dzn = DznJsonAst(json_contents=FORMAL_OUT)
        sut = json_ast.parse_formal(dzn.ast)
        assert isinstance(sut, ast.Formal)
        assert (sut.name, str(sut.type_name)) == ('myinfo', 'MyInfo')
        assert sut.direction == ast.FormalDirection.OUT

    @staticmethod
    def test_formal_direction_inout_ok():
        dzn = DznJsonAst(json_contents=FORMAL_INOUT)
        sut = json_ast.parse_formal(dzn.ast)
        assert isinstance(sut, ast.Formal)
        assert (sut.name, str(sut.type_name)) == ('toastingTime', 'MilliSeconds')
        assert sut.direction == ast.FormalDirection.INOUT


class FormalsTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_formals', 'formals')

    @staticmethod
    def test_no_elements():
        dzn = DznJsonAst(json_contents=FORMALS_EMPTY)
        sut = json_ast.parse_formals(dzn.ast)
        assert isinstance(sut, ast.Formals)
        assert isinstance(sut.elements, list)
        assert len(sut.elements) == 0

    @staticmethod
    def test_two_elements():
        dzn = DznJsonAst(json_contents=FORMALS_TWO_MIXED_ITEMS)
        sut = json_ast.parse_formals(dzn.ast)
        assert isinstance(sut, ast.Formals)
        assert len(sut.elements) == 2
        assert sut.elements[0].name == 'waitingTimeMs'
        assert sut.elements[1].name == 'myinfo'


class ImportTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_import', 'import')

    def test_ok(self):
        dzn = DznJsonAst(json_contents=IMPORT)
        sut = json_ast.parse_import(dzn.ast)
        assert isinstance(sut, ast.Import)
        assert sut.name == 'ITimer.dzn'
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.imports) == 1
        assert dzn.file_contents.imports[0] == sut


class InjectedIndicationTest(DznTestCase):

    @staticmethod
    def test_true():
        dzn = DznJsonAst(json_contents=PORT_INJECTED_INDICATION)
        sut = json_ast.parse_port_injected_indication(dzn.ast)
        assert sut.value is True

    @staticmethod
    def test_false():
        dzn = DznJsonAst(json_contents=PORT_INJECTED_INDICATION_ABSENT)
        sut = json_ast.parse_port_injected_indication(dzn.ast)
        assert sut.value is False

    @staticmethod
    def test_fail():
        dzn = DznJsonAst(json_contents=PORT_INJECTED_INDICATION_INVALID)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_port_injected_indication(dzn.ast)
        assert str(exc.value) == 'parse_injected_port: invalid value "bogus"'

    @staticmethod
    def test_true_old():
        dzn = DznJsonAst(json_contents=PORT_INJECTED_INDICATION_OLD)
        sut = json_ast.parse_port_injected_indication(dzn.ast)
        assert sut.value is True

    @staticmethod
    def test_fail_old():
        dzn = DznJsonAst(json_contents=PORT_INJECTED_INDICATION_OLD_INVALID)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_port_injected_indication(dzn.ast)
        assert str(exc.value) == 'parse_injected_port: invalid value "bogus"'


class InstanceTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_instance(dzn.ast)
        assert str(exc.value) == 'parse_instance: expecting <class> having value "instance"'

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=INSTANCE1)
        sut = json_ast.parse_instance(dzn.ast)
        assert isinstance(sut, ast.Instance)
        assert sut.name == 'mytoaster'
        assert str(sut.type_name) == 'Toaster'
        assert sut.type_name.value == ns_ids_t('Toaster')


class InstancesTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_instances(dzn.ast)
        assert str(exc.value) == 'parse_instances: expecting <class> having value "instances"'

    @staticmethod
    def test_two_elements():
        dzn = DznJsonAst(json_contents=INSTANCES_TWO_ITEMS)
        sut = json_ast.parse_instances(dzn.ast)
        assert isinstance(sut, ast.Instances)
        assert len(sut.elements) == 2
        assert sut.elements[0].name == 'mytoaster'
        assert str(sut.elements[0].type_name) == 'Toaster'
        assert sut.elements[0].type_name.value == ns_ids_t('Toaster')
        assert sut.elements[1].name == 'timer1'
        assert str(sut.elements[1].type_name) == 'Facilities.Timer'
        assert sut.elements[1].type_name.value == ns_ids_t('Facilities.Timer')


class InterfaceTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_interface', 'interface', self._root_ns)

    def test_no_elements(self):
        dzn = DznJsonAst(json_contents=INTERFACE_EMPTY)
        sut = json_ast.parse_interface(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Interface)
        assert sut.fqn == ns_ids_t('IToaster')
        assert str(sut.name) == 'IToaster'
        assert sut.name.value == ns_ids_t('IToaster')
        assert isinstance(sut.types, ast.Types)
        assert len(sut.types.elements) == 0
        assert isinstance(sut.events, ast.Events)
        assert len(sut.events.elements) == 0
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.interfaces) == 1
        assert dzn.file_contents.interfaces[0] == sut

    def test_two_elements(self):
        dzn = DznJsonAst(json_contents=INTERFACE_TWO_ITEMS)
        sut = json_ast.parse_interface(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Interface)
        assert sut.fqn == ns_ids_t('IHeaterElement')
        assert str(sut.name) == 'IHeaterElement'
        assert sut.name.value == ns_ids_t('IHeaterElement')
        assert len(sut.types.elements) == 2
        assert isinstance(sut.types.elements[0], ast.Enum)
        assert isinstance(sut.types.elements[1], ast.SubInt)
        assert sut.types.elements[0].fqn == ns_ids_t('IHeaterElement.Result')
        assert str(sut.types.elements[0].name) == 'Result'
        assert len(sut.events.elements) == 2

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=INTERFACE_TWO_ITEMS)
        sut = json_ast.parse_interface(dzn.ast, self._nested_ns)
        assert isinstance(sut, ast.Interface)
        assert sut.fqn == ns_ids_t('My.Project.IHeaterElement')
        assert str(sut.name) == 'IHeaterElement'
        assert sut.name.value == ns_ids_t('IHeaterElement')
        assert sut.types.elements[0].fqn == NamespaceIds(['My', 'Project', 'IHeaterElement', 'Result'])
        assert str(sut.types.elements[0].name) == 'Result'

    def test_get_enums_from_types(self):
        dzn = DznJsonAst(json_contents=INTERFACE_TWO_ITEMS)
        sut = json_ast.parse_interface(dzn.ast, self._nested_ns)
        enum_list = sut.types.enums
        assert len(enum_list) == 1
        assert enum_list[0].fqn == ns_ids_t('My.Project.IHeaterElement.Result')

    def test_get_subints_from_types(self):
        dzn = DznJsonAst(json_contents=INTERFACE_TWO_ITEMS)
        sut = json_ast.parse_interface(dzn.ast, self._nested_ns)
        subints_list = sut.types.subints
        assert len(subints_list) == 1
        assert subints_list[0].fqn == ns_ids_t('My.Project.IHeaterElement.SmallInt')

    def test_get_subints_from_types_until_2_16_5_ok(self):
        dzn = DznJsonAst(json_contents=INTERFACE_TWO_ITEMS_INT)
        sut = json_ast.parse_interface(dzn.ast, self._nested_ns)
        subints_list = sut.types.subints
        assert len(subints_list) == 1
        assert subints_list[0].fqn == ns_ids_t('My.Project.IHeaterElement.MediumInt')


class NamespaceTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_namespace', 'namespace')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=NAMESPACE)
        sut = json_ast.parse_namespace(dzn.ast)
        assert isinstance(sut, ast.Namespace)
        assert str(sut.scope_name) == 'My'
        assert sut.scope_name.value == NamespaceIds(['My'])
        assert len(sut.elements) == 0


class PortTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_port', 'port')

    @staticmethod
    def test_provides_ok():
        dzn = DznJsonAst(json_contents=PORT_PROVIDES)
        sut = json_ast.parse_port(dzn.ast)
        assert isinstance(sut, ast.Port)
        assert sut.name == 'api'
        assert str(sut.type_name) == 'IToaster'
        assert sut.type_name.value == ns_ids_t('IToaster')
        assert sut.direction == ast.PortDirection.PROVIDES
        assert len(sut.formals.elements) == 0
        assert sut.injected.value is False

    @staticmethod
    def test_requires_ok():
        dzn = DznJsonAst(json_contents=PORT_REQUIRES)
        sut = json_ast.parse_port(dzn.ast)
        assert isinstance(sut, ast.Port)
        assert sut.name == 'heater'
        assert str(sut.type_name) == 'IHeaterElement'
        assert sut.type_name.value == ns_ids_t('IHeaterElement')
        assert sut.direction == ast.PortDirection.REQUIRES
        assert len(sut.formals.elements) == 0
        assert sut.injected.value is False

    @staticmethod
    def test_requires_injected_ok():
        dzn = DznJsonAst(json_contents=PORT_REQUIRES_INJECTED)
        sut = json_ast.parse_port(dzn.ast)
        assert isinstance(sut, ast.Port)
        assert sut.name == 'cfg'
        assert str(sut.type_name) == 'IConfiguration'
        assert sut.type_name.value == ns_ids_t('IConfiguration')
        assert sut.direction == ast.PortDirection.REQUIRES
        assert len(sut.formals.elements) == 0
        assert sut.injected.value is True


class PortsTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        dzn = DznJsonAst(json_contents=BOGUS_CLASS)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_ports(dzn.ast)
        assert str(exc.value) == 'parse_ports: expecting <class> having value "ports"'

    @staticmethod
    def test_no_elements():
        dzn = DznJsonAst(json_contents=PORTS_EMPTY)
        sut = json_ast.parse_ports(dzn.ast)
        assert isinstance(sut, ast.Ports)
        assert isinstance(sut.elements, list)
        assert len(sut.elements) == 0

    @staticmethod
    def test_two_elements():
        dzn = DznJsonAst(json_contents=PORTS_TWO_ITEMS)
        sut = json_ast.parse_ports(dzn.ast)
        assert isinstance(sut, ast.Ports)
        assert len(sut.elements) == 2
        assert sut.elements[0].name == 'api'
        assert sut.elements[0].direction == ast.PortDirection.PROVIDES
        assert sut.elements[1].name == 'heater'
        assert sut.elements[1].direction == ast.PortDirection.REQUIRES


class PortDirectionTest(DznTestCase):

    @staticmethod
    def test_ok():
        assert json_ast.parse_port_direction('requires') == ast.PortDirection.REQUIRES
        assert json_ast.parse_port_direction('provides') == ast.PortDirection.PROVIDES

    @staticmethod
    def test_fail():
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_port_direction('bogus')
        assert str(exc.value) == 'parse_port_direction: invalid value "bogus"'


class RangeTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_range', 'range')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=RANGE)
        sut = json_ast.parse_range(dzn.ast)
        assert isinstance(sut, ast.Range)
        assert sut.from_int == 2
        assert sut.to_int == 5


class RootTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_root', 'root')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=ROOT)
        sut = json_ast.parse_root(dzn.ast)
        assert isinstance(sut, ast.Root)
        assert sut.comment.value == '// My Comment'
        assert len(sut.elements) == 0
        assert sut.working_dir == 'C:'

    @staticmethod
    def test_without_comment_ok():
        dzn = DznJsonAst(json_contents=ROOT_WITHOUT_COMMENT)
        sut = json_ast.parse_root(dzn.ast)
        assert isinstance(sut, ast.Root)
        assert sut.comment is None
        assert len(sut.elements) == 0
        assert sut.working_dir == 'D:'

    @staticmethod
    def test_without_working_directory_ok():
        dzn = DznJsonAst(json_contents=ROOT_WITHOUT_WORKING_DIRECTORY)
        sut = json_ast.parse_root(dzn.ast)
        assert isinstance(sut, ast.Root)
        assert sut.comment is None
        assert len(sut.elements) == 0
        assert sut.working_dir is None


class ScopeNameTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_scope_name', 'scope_name')

    @staticmethod
    def test_ok_single_id():
        dzn = DznJsonAst(json_contents=SCOPE_NAME)
        sut = json_ast.parse_scope_name(dzn.ast)
        assert isinstance(sut, ast.ScopeName)
        assert str(sut) == 'My'
        assert sut.value == NamespaceIds(['My'])

    @staticmethod
    def test_ok_multiple_ids():
        dzn = DznJsonAst(json_contents=SCOPE_NAME_EX)
        sut = json_ast.parse_scope_name(dzn.ast)
        assert isinstance(sut, ast.ScopeName)
        assert str(sut) == 'My.Nice.Type'
        assert sut.value == NamespaceIds(['My', 'Nice', 'Type'])

    @staticmethod
    def test_fail():
        dzn = DznJsonAst(json_contents=SCOPE_NAME_FAIL)
        with pytest.raises(DznJsonError) as exc:
            json_ast.parse_scope_name(dzn.ast)
        assert str(exc.value) == 'parse_scope_name: list "ids" is empty'


class SignatureTest(DznTestCase):

    @staticmethod
    def test_wrong_class():
        assert_wrong_class(BOGUS_CLASS, 'parse_signature', 'signature')

    @staticmethod
    def test_ok():
        dzn = DznJsonAst(json_contents=SIGNATURE_VALUED_MIXED_ITEMS)
        sut = json_ast.parse_signature(dzn.ast)
        assert isinstance(sut, ast.Signature)
        assert str(sut.type_name) == 'Result'
        assert sut.type_name.value == NamespaceIds(['Result'])
        assert isinstance(sut.formals, ast.Formals)


class SubIntTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_subint', 'subint', self._root_ns,
                           "parse_subint: expecting <class> having one of the values ['int', 'subint']")

    def test_ok(self):
        dzn = DznJsonAst(json_contents=SUBINT)
        sut = json_ast.parse_subint(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.SubInt)
        assert sut.fqn == ns_ids_t('SmallInt')
        assert str(sut.name) == 'SmallInt'
        assert sut.name.value == ns_ids_t('SmallInt')
        assert sut.range.from_int == 2
        assert sut.range.to_int == 5
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.subints) == 1
        assert dzn.file_contents.subints[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=SUBINT)
        sut = json_ast.parse_subint(dzn.ast, self._nested_ns)
        assert sut.fqn == ns_ids_t('My.Project.SmallInt')
        assert str(sut.name) == 'SmallInt'
        assert sut.name.value == ns_ids_t('SmallInt')

    def test_until_2_16_5_ok(self):
        dzn = DznJsonAst(json_contents=INT)
        sut = json_ast.parse_subint(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.SubInt)
        assert sut.fqn == ns_ids_t('MediumInt')
        assert str(sut.name) == 'MediumInt'
        assert sut.name.value == ns_ids_t('MediumInt')
        assert sut.range.from_int == 2
        assert sut.range.to_int == 5
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.subints) == 1
        assert dzn.file_contents.subints[0] == sut


class SystemTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_system', 'system', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=SYSTEM)
        sut = json_ast.parse_system(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.System)
        assert str(sut.name) == 'ToasterSystem'
        assert sut.name.value == ns_ids_t('ToasterSystem')
        assert len(sut.ports.elements) == 2
        assert len(sut.instances.elements) == 2
        assert len(sut.bindings.elements) == 1
        # besides the specific handler, ensure the overall parser recognises it:
        dzn._parse_node(dzn.ast, self._root_ns)
        assert len(dzn.file_contents.systems) == 1
        assert dzn.file_contents.systems[0] == sut

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=SYSTEM)
        sut = json_ast.parse_system(dzn.ast, self._nested_ns)
        assert sut.fqn == ns_ids_t('My.Project.ToasterSystem')
        assert str(sut.name) == 'ToasterSystem'
        assert sut.name.value == ns_ids_t('ToasterSystem')


class TypesTest(DznTestCase):

    def test_wrong_class(self):
        assert_wrong_class(BOGUS_CLASS, 'parse_types', 'types', self._root_ns)

    def test_ok(self):
        dzn = DznJsonAst(json_contents=TYPES_TWO_ITEMS_ENUM_SUBINT)
        sut = json_ast.parse_types(dzn.ast, self._root_ns)
        assert isinstance(sut, ast.Types)
        assert len(sut.elements) == 2
        assert isinstance(sut.elements[0], ast.Enum)
        assert sut.elements[0].fqn == ns_ids_t('Result')
        assert sut.elements[0].fields.elements == ['Ok', 'Fail', 'Error']
        assert isinstance(sut.elements[1], ast.SubInt)
        assert str(sut.elements[1].name) == 'SmallInt'
        assert sut.elements[1].name.value == ns_ids_t('SmallInt')
        assert sut.elements[1].range.from_int == 2
        assert sut.elements[1].range.to_int == 5

    def test_nested_fqn(self):
        dzn = DznJsonAst(json_contents=TYPES_TWO_ITEMS_ENUM_SUBINT)
        sut = json_ast.parse_types(dzn.ast, self._nested_ns)
        assert isinstance(sut, ast.Types)
        assert sut.elements[0].fqn == ns_ids_t('My.Project.Result')
        assert sut.elements[0].fields.elements == ['Ok', 'Fail', 'Error']
        assert sut.elements[1].fqn == ns_ids_t('My.Project.SmallInt')


class LoadFileTest(DznTestCase):

    @staticmethod
    def test_open_some_json_ok():
        sut = DznJsonAst().load_file(SOME_JSON_FILE)
        assert sut._json_ast is not None

    @staticmethod
    def test_open_dezyne_json_ok():
        sut = DznJsonAst().load_file(DZNJSON_FILE)
        assert sut._json_ast is not None

    @staticmethod
    def test_open_json_fail():
        with pytest.raises(JSONDecodeError):
            DznJsonAst().load_file(CPP_FILE)

    @staticmethod
    def test_not_dezyne_json():
        sut = DznJsonAst(verbose=True).load_file(SOME_JSON_FILE)
        with pytest.raises(DznJsonError) as exc:
            sut.process()
        assert str(exc.value) == 'parse_root: missing "<class>" key'

    @staticmethod
    def test_process_entire_dezyne_file():
        sut = DznJsonAst(verbose=True).load_file(DZNJSON_FILE)
        sut.process()
        fc = sut.file_contents
        print(f'\n{fc}')  # uncomment me to inspect the contents visually

        expected_component_fqns = ['My.Project.Toaster']
        assert_items_name_on_fqn(fc.components, expected_component_fqns)

        expected_enums = ['My.Result', 'My.Project.IToaster.State', 'My.Project.CountingUp']
        assert_items_name_on_fqn(fc.enums, expected_enums)

        expected_externs = ['MilliSeconds', 'string',
                            'My.Project.MyLongNamedType', 'My.Project.PResultInfo']
        assert_items_name_on_fqn(fc.externs, expected_externs)

        expected_filenames = ['./Toaster.dzn', '../shared/Facilities/FCTimer.dzn',
                              '../shared/Facilities/ITimer.dzn', './IToaster.dzn',
                              './Hardware/Interfaces/IHeaterElement.dzn',
                              './Hardware/Interfaces/IPowerCord.dzn',
                              './Hardware/Interfaces/ILed.dzn',
                              '../shared/Facilities/IConfiguration.dzn',
                              '../shared/Facilities/Types.dzn', 'ToasterSystem.dzn']
        assert_items_name_on_str(fc.filenames, expected_filenames)

        expected_foreign_fqns = ['Facilities.Timer']
        assert_items_name_on_fqn(fc.foreigns, expected_foreign_fqns)

        expected_imports = ['IToaster.dzn', 'Hardware/Interfaces/IHeaterElement.dzn',
                            'Hardware/Interfaces/IPowerCord.dzn', 'Hardware/Interfaces/ILed.dzn',
                            'ITimer.dzn', 'IConfiguration.dzn', 'Types.dzn', 'ITimer.dzn', 'Types.dzn',
                            'Types.dzn', 'Types.dzn', 'Types.dzn', 'Types.dzn', 'Toaster.dzn',
                            'FCTimer.dzn']
        assert_items_name_on_str(fc.imports, expected_imports)

        expected_itf_fqns = ['My.Project.IToaster', 'Some.Vendor.IHeaterElement', 'IHeaterElement',
                             'My.Project.IHeaterElement', 'My.ILed',
                             'My.Project.Hal.IPowerCord', 'IConfiguration', 'ITimer']
        assert_items_name_on_fqn(fc.interfaces, expected_itf_fqns)

        expected_subints = ['SmallInt', 'My.Project.MediumInt',
                            'Some.Vendor.IHeaterElement.ExampleInt']
        assert_items_name_on_fqn(fc.subints, expected_subints)

        expected_system_fqns = ['My.Project.ToasterSystem']
        assert_items_name_on_fqn(fc.systems, expected_system_fqns)


# testing/assertion helpers


def assert_items_name_on_fqn(collection: list, expected_fqns: List[str]):
    """Assert all expected fqns match the items in collection on their 'fqn' attribute."""
    assert len(collection) == len(expected_fqns)
    for expected_fqn in expected_fqns:
        assert any(
            item for item in collection if item.fqn.items == expected_fqn.split('.')), expected_fqn


def assert_items_name_on_str(collection: list, expected_strs: List[str]):
    """Assert all expected strings match the items in collection on their 'name' attribute."""
    assert len(collection) == len(expected_strs)
    for expected_str in expected_strs:
        assert any(
            item for item in collection if item.name == expected_str), expected_str


def assert_wrong_class(json_contents: str,
                       parse_method_name: str,
                       class_value: str,
                       ns_trail: NamespaceTree = None,
                       custom_exc_msg: str = None):
    dzn = DznJsonAst(json_contents=json_contents)
    with pytest.raises(DznJsonError) as exc:
        method = getattr(json_ast, parse_method_name)
        if ns_trail is None:
            method(dzn.ast)
        else:
            method(dzn.ast, ns_trail)

    if custom_exc_msg is not None:
        assert str(exc.value) == custom_exc_msg
    else:
        assert str(exc.value) == f'{parse_method_name}: expecting <class> having value "{class_value}"'
