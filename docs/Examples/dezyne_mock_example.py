"""
Example of generating a GoogleMock struct for a Dezyne interface (non-injectable).

Recipe steps:
1. Read in the Dezyne interface model that was exported as JSON (file IPowerCord.json)
2. Select the interface model IPowerCord in the namespace My.Project.Hal
3. Retrieve all in-events and out-events (names, parameter signature)
4. C++ generate information header
5. C++ generate the system and project includes
6. C++ generate the class IPowerCordMock
  a. Generate the SetupPeerPort() class method, that installs functors for each in-event
  b. Generate TriggerNNN() class methods for each out-event
  c. Generate the MOCK_METHOD GoogleMock statements with an equivalent for each in-event
  d. Generate a public section with substeps a+b+c
  e. Generate a private section that stores a reference to the peer Dezyne port
  f. Integrate all sections into the class
7. Finally combine steps 4, 5 and 6 into finalized C++ file contents

EXAMPLE OUTPUT:

// Generated GoogleMock C++ sourcecode from JSON file: ../../test/dezyne_models/generated/IPowerCord.json
// Note: do not modify manually afterwards

#pragma once

// System includes
#include <functional>
#include <optional>
#include <sstream>

// Project includes
#include "gmock/gmock.h"
#include "IPowerCord.hh"

class IPowerCordMock
{
public:
    void SetupPeerPort(My::Project::Hal::IPowerCord& port)
    {
        m_peerPort = port;

        port.in.Initialize = [this](std::string label) {
            return Initialize(label);
        };

        port.in.Uninitialize = [this](std::shared_ptr<ResultInfo>& info) {
            return Uninitialize(info);
        };

        port.in.IsConnectedToOutlet = [this]() {
            return IsConnectedToOutlet();
        };

        port.in.GetVoltage = [this]() {
            return GetVoltage();
        };

        port.check_bindings();
    }

    // Methods for the interface out events to trigger them on behalf of the Mock object
    void TriggerConnected()
    {
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne peer port not set up");
        m_peerPort.value().get().out.Connected();
    }

    void TriggerDisconnected(My::Project::Hal::Sub::MyLongNamedType exampleParameter)
    {
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne peer port not set up");
        m_peerPort.value().get().out.Disconnected(exampleParameter);
    }

    // Method mocks, expectations programmable by test
    MOCK_METHOD(::My::Result, Initialize, (std::string label));
    MOCK_METHOD(void, Uninitialize, (std::shared_ptr<ResultInfo>& info));
    MOCK_METHOD(bool, IsConnectedToOutlet, ());
    MOCK_METHOD(int, GetVoltage, ());

private:
    std::optional<std::reference_wrapper<My::Project::Hal::IPowerCord>> m_peerPort;
};


Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
from typing import List

from dznpy.ast import Interface, EventDirection
from dznpy.ast_cpp_view import get_formals, expand_event, create_member_function
from dznpy.cpp_gen import Class, AccessSpecifiedSection, AccessSpecifier, Function, void_t, \
    param_ref_t, fqn_t, Comment, SystemIncludes, ProjectIncludes
from dznpy.json_ast import DznJsonAst
from dznpy.ast_view import find_fqn, get_in_events, get_out_events, get_itf_name
from dznpy.scoping import ns_ids_t
from dznpy.text_gen import TextBlock, TB, EOL


def main():
    """Convergence point of executing all example code for the cpp_gen module."""

    json_file_name = '../../test/dezyne_models/generated/IPowerCord.json'

    # 1. Read in the Dezyne interface model (file IPowerCord.dzn)
    dzn_json_ast = DznJsonAst(verbose=True)
    dzn_json_ast.load_file(json_file_name)
    file_contents = dzn_json_ast.process()
    # print(file_contents)

    # 2. Select the interface model IPowerCord in the namespace My.Project.Hal
    find_result = find_fqn(file_contents, ns_ids_t('IPowerCord'), ns_ids_t('My.Project.Hal'))
    # print(f'Has one instance = {find_result.has_one_instance(Interface)}')  # must be True
    itf: Interface = find_result.get_single_instance(Interface)

    # 3. Retrieve all in-events and out-events (names, parameter signature)
    in_events = get_in_events(itf)
    out_events = get_out_events(itf)

    # 4. C++ generate information header
    header_block = TextBlock(chunk_spacing=EOL) + \
                   Comment([f'GoogleMock C++ sourcecode from JSON file: {json_file_name}',
                            'Note: this is generated code']) + \
                   '#pragma once'

    # 5. C++ generate the system and project includes
    includes_block = TB(chunk_spacing=EOL) + \
                     SystemIncludes(['functional', 'optional', 'sstream']) + \
                     ProjectIncludes(['gmock/gmock.h', f'{itf.name}.hh'])

    # 6. C++ generate the class IPowerCordMock
    mock_class = Class(f'{get_itf_name(itf)}Mock')

    # 6.a. Generate the SetupPeerPort() class method, that installs functors for each in-event
    setup_peer_port_fn = Function(parent=mock_class,
                                  return_type=void_t(),
                                  name='SetupPeerPort',
                                  params=[param_ref_t(fqn_t(itf.fqn), 'port')]
                                  )

    setup_peer_port_def = TB(['m_peerPort = port;'], chunk_spacing=EOL)

    for evt in in_events:
        evt_exp = expand_event(evt, itf, file_contents)
        (formals_names, formals_expanded) = get_formals(evt_exp)
        snippet = TB([f'port.in.{evt.name} = [this]({formals_expanded}) {{',
                      f'    return {evt.name}({formals_names});',
                      '};'
                      ])
        setup_peer_port_def += snippet

    setup_peer_port_def += 'port.check_bindings();'
    setup_peer_port_fn.contents = setup_peer_port_def

    # 6.b. Generate TriggerNNN() class methods for each out-event
    trigger_function_defs = TB(chunk_spacing=EOL)

    for evt in out_events:
        evt_exp = expand_event(evt, itf, file_contents)
        (formals_names, _) = get_formals(evt_exp)

        trigger_fn = create_member_function(evt_exp, 'Trigger', mock_class)
        trigger_fn.contents = TB(['if (!m_peerPort.has_value()) throw '  # no comma! for one-liner
                                  'std::runtime_error("Dezyne peer port not set up");',
                                  f'm_peerPort.value().get().out.{evt.name}({formals_names});'
                                  ])
        trigger_function_defs += trigger_fn.as_def(imf=True)  # imf = Inline Member Function

    trigger_functions_block = TB([Comment('Methods for the interface out events to trigger them'
                                          ' on behalf of the Mock object'),
                                  trigger_function_defs])

    # 6.c. Generate the MOCK_METHOD GoogleMock statements with an equivalent for each in-event
    mock_methods_block = TB(Comment('Method mocks, expectations programmable by test'))
    for evt in in_events:
        evt_exp = expand_event(evt, itf, file_contents)
        (formals_names, formals_expanded) = get_formals(evt_exp)
        snippet = f'MOCK_METHOD({evt_exp.return_type}, {evt.name}, ({formals_expanded}));'
        mock_methods_block += snippet

    # 6.d. Generate a public section with substeps a+b+c
    public_contents = TB(chunk_spacing=EOL) + \
                      setup_peer_port_fn.as_def(imf=True) + \
                      trigger_functions_block + \
                      mock_methods_block
    public_section = AccessSpecifiedSection(AccessSpecifier.PUBLIC, public_contents)

    # 6.e. Generate a private section that stores a reference to the peer Dezyne port
    private_contents = TB() + \
                       f'std::optional<std::reference_wrapper<{fqn_t(itf.fqn)}>> m_peerPort;'
    private_section = AccessSpecifiedSection(AccessSpecifier.PRIVATE, private_contents)

    # 6.f. Integrate all sections into the class
    mock_class.decl_contents = TB(chunk_spacing=EOL) + \
                               public_section + \
                               private_section

    # 7. Finally combine steps 4, 5 and 6 into header file contents
    final_result = TB(chunk_spacing=EOL) + \
                   header_block + \
                   includes_block + \
                   mock_class

    print(final_result)


if __name__ == "__main__":
    main()
