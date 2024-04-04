"""
Testsuite covering the ast_view python module - version 0.1.240108

Copyright (c) 2023-2024 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License.
Refer to https://opensource.org/license/mit/ for exact MIT license details.
"""

# system imports
import pytest
from unittest import TestCase

# cots modules
from dznpy import ast, json_ast

# system-under-test
from dznpy import ast_view
from dznpy.ast_view import find_on_fqn, find

# Test data
from testdata_json_ast import *


class DznAstViewTestCase(TestCase):

    def setUp(self):
        self.sut = json_ast.DznJsonAst(json_contents=DZNFILE_EXAMPLE)
        self.sut.process()

    @property
    def fc(self):
        return self.sut.file_contents

    @property
    def example_system(self) -> ast.System:
        return find_on_fqn(self.fc, ['ToasterSystem'], ['My'])


class FindSpecificFqnInFileContentsTest(DznAstViewTestCase):

    def test_find_element_not_found(self):
        result = find_on_fqn(self.fc, ['CannotFindMe'], [])
        assert result is None

    def test_find_fail(self):
        with pytest.raises(TypeError) as exc:
            find_on_fqn(self.fc, 'Some.Path', [])
        assert str(exc.value) == 'The argument is not a NameSpaceIds type'

    def test_find_interface_in_global_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['IToaster'], []), ast.Interface)

    def test_find_foreign_in_global_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['Timer'], []), ast.Foreign)

    def test_find_enum_in_global_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['Result'], []), ast.Enum)

    def test_find_interface_in_sub_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['IHeaterElement'], ['My']), ast.Interface)

    def test_find_component_in_sub_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['Toaster'], ['My']), ast.Component)

    def test_find_system_in_sub_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['ToasterSystem'], ['My']), ast.System)
        assert isinstance(find_on_fqn(self.fc, ['My', 'ToasterSystem'], []), ast.System)
        assert isinstance(find_on_fqn(self.fc, ['My', 'ToasterSystem'], ['My']), ast.System)

    def test_find_extern_in_sub_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['MilliSeconds'], ['My']), ast.Extern)

    def test_find_subint_in_sub_scope(self):
        assert isinstance(find_on_fqn(self.fc, ['SmallInt'], ['My']), ast.SubInt)


class FindItemsInFileContentsTest(DznAstViewTestCase):

    def test_find_element_not_found(self):
        result = find(self.fc, 'CannotFindMe')
        assert isinstance(result, list)
        assert result == []

    def test_find_system(self):
        result = find(self.fc, 'ToasterSystem')
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ast.System)
        assert result[0].fqn == ['My', 'ToasterSystem']


class GetPortNamesTest(DznAstViewTestCase):

    def test_ok(self):
        result = ast_view.get_port_names(self.example_system.ports)
        assert isinstance(result, ast_view.PortNames)
        assert result.provides == {'api'}
        assert result.requires == {'heater'}
