"""
Example of generating a GoogleMock struct for a Dezyne interface (non-injectable).

Recipe steps:
1. Read in the Dezyne interface model (file IPowerCord.dzn)
2. Select the interface model IPowerCord in the namespace My.Project.Hal
3. Retrieve all in-events and out-events (names, parameter signature)
4. C++ generate information header
5. C++ generate the system and project includes
6. C++ generate the class IPowerCordMock
  a. Generate the SetupPeerPort() class method, that installs functors for each in-event
  b. Generate TriggerNNN() class methods for each out-event
  c. Generate the MOCK_METHOD GoogleMock statements with a equivalent for each in-event
  d. Generate a private section that stores a reference to the peer Dezyne port


GENERATED OUTPUT:

#pragma once
// System include
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

        port.in.IsConnectedToOutlet = [this] {
            return IsConnectedToOutlet();
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
        if (!m_peerPort.has_value()) throw std::runtime_error("Dezyne port not set up");
        m_peerPort.value().get().out.Disconnected(exampleParameter);
    }

    // Method mocks, expectations programmable by test
    MOCK_METHOD(::My::Result, Initialize, (std::string & label));
    MOCK_METHOD(void, Uninitialize, (std::shared_ptr<ResultInfo> & info));
    MOCK_METHOD(bool, IsConnectedToOutlet, ());

private:
    std::optional<std::reference_wrapper<My::Project::Hal::IPowerCord>> m_peerPort;
};


Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""
from typing import List

from dznpy.ast import Interface, EventDirection
from dznpy.ast_cpp_view import get_formals, expand_event, create_member_function
from dznpy.cpp_gen import Class, AccessSpecifiedSection, AccessSpecifier, Function, void_t, Param, \
    param_ref_t, fqn_t
from dznpy.json_ast import DznJsonAst
from dznpy.ast_view import find_fqn, get_in_events, get_out_events, get_itf_name
from dznpy.scoping import ns_ids_t
from dznpy.text_gen import TB, TextBlock, chunk, TAB


def main():
    """Convergence point of executing all example code for the cpp_gen module."""

    # 1. Read in the Dezyne interface model (file IPowerCord.dzn)
    dzn_json_ast = DznJsonAst(verbose=True)
    dzn_json_ast.load_file('../../test/dezyne_models/generated/IPowerCord.json')
    file_contents = dzn_json_ast.process()
    # print(file_contents)

    # 2. Select the interface model IPowerCord in the namespace My.Project.Hal
    find_result = find_fqn(file_contents, ns_ids_t('IPowerCord'), ns_ids_t('My.Project.Hal'))
    print(find_result)
    # print(f'Has one instance = {find_result.has_one_instance(Interface)}')  # must be True
    itf: Interface = find_result.get_single_instance(Interface)

    # 3. Retrieve all in-events and out-events (names, parameter signature)
    in_events = get_in_events(itf)
    out_events = get_out_events(itf)

    # 6. C++ generate the class IPowerCordMock
    mock_class = Class(get_itf_name(itf))

    # 6.a. Generate the SetupPeerPort() class method, that installs functors for each in-event
    setup_peer_port_fn = Function(parent=mock_class,
                                  return_type=void_t(),
                                  name='SetupPeerPort',
                                  params=[param_ref_t(fqn_t(itf.fqn), 'port')]
                                  )

    setup_peer_port_def = TextBlock(['m_peerPort = port;',
                                     ''])

    for evt in in_events:
        evt_exp = expand_event(evt, itf, file_contents)
        (formals_names, formals_expanded) = get_formals(evt_exp)
        snippet = chunk([f'port.in.{evt.name} = [this]({formals_expanded}) {{',
                         f'    return {evt.name}({formals_names});',
                         '};'
                         ])
        setup_peer_port_def += snippet

    setup_peer_port_def += 'port.check_bindings();'
    setup_peer_port_fn.contents = setup_peer_port_def

    # 6.b. Generate TriggerNNN() class methods for each out-event

    trigger_functions_def = TextBlock()
    for evt in out_events:
        evt_exp = expand_event(evt, itf, file_contents)
        (formals_names, _) = get_formals(evt_exp)

        trigger_fn = create_member_function(evt_exp, 'Trigger', mock_class)
        trigger_fn.contents = TB(['if (!m_peerPort.has_value()) throw '  # no comma! for one-liner
                                  'std::runtime_error("Dezyne peer port not set up");',
                                  f'm_peerPort.value().get().out.{evt.name}({formals_names});'
                                  ])
        trigger_functions_def += chunk(trigger_fn.as_def(imf=True))

    # Converge

    public_contents = TB(
        [chunk(setup_peer_port_fn.as_def(imf=True)),  # imf = inline member function
         trigger_functions_def
         ])

    public_section = AccessSpecifiedSection(AccessSpecifier.PUBLIC, public_contents)
    mock_class.decl_contents = TB(public_section)

    print(mock_class)


if __name__ == "__main__":
    main()
