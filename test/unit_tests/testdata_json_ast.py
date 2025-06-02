"""
Test data for validating the output of the json_ast module.

Copyright (c) 2023-2025 Michael van de Ven <michael@ftr-ict.com>
This is free software, released under the MIT License. Refer to dznpy/LICENSE.
"""

TOASTER_SYSTEM_JSON_FILE = 'generated/ToasterSystem.json'
VSCODE_WORKSPACE_FILE = 'System1.code-workspace'
TOASTER_SYSTEM_CPP_FILE = 'generated/ToasterSystem.cc'

BOGUS_CLASS = '''{"<class>": "bogus" }'''

COMMENT = '''{"<class>": "comment", "string": "// Some comment\\n" }'''

FIELDS = '''{ "<class>": "fields", "elements": ["Ok", "Fail", "Error"] }'''

ENDPOINT1 = '''{"<class>": "end-point", "port_name": "api"}'''

ENDPOINT2 = '''{"<class>": "end-point",
                "instance_name": "mytoaster",
                "port_name": "myport"}'''

BINDING = '''{"<class>": "binding",
              "left": ''' f'{ENDPOINT1}' ''',
              "right": ''' f'{ENDPOINT2}' '''}'''

BINDINGS = '''{"<class>": "bindings", "elements": [''' f'{BINDING}' ''']}'''

DATA = '''{"<class>": "data", "value": "size_t"}'''

ENUM = '''{"<class>": "enum",
           "name": { "<class>": "scope_name", "ids": ["Result"] },
           "fields": ''' f'{FIELDS}' '''}'''

EXTERN = '''{"<class>": "extern",
             "name": { "<class>": "scope_name", "ids": ["MilliSeconds"] },
             "value": ''' f'{DATA}' '''}'''

FILENAME = '''{"<class>": "file-name", "name": "./Toaster.dzn" }'''

FORMAL_IN = '''{"<class>": "formal",
                "expression": "undefined",
                "name": "waitingTimeMs",
                "type_name": {"<class>": "scope_name", "ids": ["MilliSeconds"]},
                "direction": "in"}'''

FORMAL_OUT = '''{"<class>": "formal",
                 "expression": "undefined",
                 "name": "myinfo",
                 "type_name": {"<class>": "scope_name", "ids": ["MyInfo"]},
                 "direction": "out"}'''

FORMAL_INOUT = '''{"<class>": "formal",
                 "expression": "undefined",
                 "name": "toastingTime",
                 "type_name": {"<class>": "scope_name", "ids": ["MilliSeconds"]},
                 "direction": "inout"}'''

FORMALS_EMPTY = '''{"<class>": "formals", "elements": []}'''

FORMALS_ONE_INONLY_ITEM = '''{"<class>": "formals", "elements": [''' f'{FORMAL_IN}' ''']}'''

FORMALS_TWO_MIXED_ITEMS = '''{"<class>": "formals", "elements": [''' f'{FORMAL_IN}, {FORMAL_OUT}' ''']}'''

SIGNATURE_VOID_INONLY_ITEMS = '''{"<class>": "signature",
                "type_name": {"<class>": "scope_name", "ids": ["void"]},
                "formals": ''' f'{FORMALS_ONE_INONLY_ITEM}' '''}'''

SIGNATURE_VALUED_MIXED_ITEMS = '''{"<class>": "signature",
                "type_name": {"<class>": "scope_name", "ids": ["Result"]},
                "formals": ''' f'{FORMALS_TWO_MIXED_ITEMS}' '''}'''

SIGNATURE_VOID_MIXED_ITEMS = '''{"<class>": "signature",
                "type_name": {"<class>": "scope_name", "ids": ["void"]},
                "formals": ''' f'{FORMALS_TWO_MIXED_ITEMS}' '''}'''

EVENT_IN = '''{"<class>": "event",
               "name": "SwitchOn",
               "signature": ''' f'{SIGNATURE_VALUED_MIXED_ITEMS}' ''',
               "direction": "in"}'''

EVENT_OUT = '''{"<class>": "event",
                "name": "Fail",
                "signature": ''' f'{SIGNATURE_VOID_INONLY_ITEMS}' ''',
                "direction": "out"}'''

EVENT_OUT_BOGUS1 = '''{"<class>": "event",
                "name": "Fail",
                "signature": ''' f'{SIGNATURE_VALUED_MIXED_ITEMS}' ''',
                "direction": "out"}'''

EVENT_OUT_BOGUS2 = '''{"<class>": "event",
                "name": "Fail",
                "signature": ''' f'{SIGNATURE_VOID_MIXED_ITEMS}' ''',
                "direction": "out"}'''

EVENTS_EMPTY = '''{"<class>": "events", "elements": []}'''

EVENTS_TWO_ITEMS = '''{"<class>": "events", "elements": [''' f'{EVENT_IN}, {EVENT_OUT}' ''']}'''

IMPORT = '''{"<class>": "import", "name": "ITimer.dzn" }'''

INSTANCE1 = '''{"<class>": "instance",
                "name": "mytoaster",
                "type_name": {"<class>": "scope_name", "ids": ["Toaster"]}}'''

INSTANCE2 = '''{"<class>": "instance",
                "name": "timer1",
                "type_name": {"<class>": "scope_name", "ids": ["Facilities", "Timer"]}}'''

INSTANCES_TWO_ITEMS = '''{"<class>": "instances", "elements": [''' \
                      f'{INSTANCE1}, {INSTANCE2}' \
                      ''']}'''

NAMESPACE = '''{"<class>": "namespace",
                "name": {"<class>": "scope_name", "ids": ["My"]},
                "elements": []}'''

RANGE = '''{"<class>": "range", "from": 2, "to": 5}'''

ROOT = '''{"<class>": "root",
           "comment": {"<class>": "comment", "string": "// My Comment"},
           "elements": [],
           "working-directory": "C:"}'''

PORT_PROVIDES = '''{"<class>": "port",
                    "name": "api",
                    "type_name": {"<class>": "scope_name", "ids": ["IToaster"]},
                    "direction": "provides",
                    "formals": ''' f'{FORMALS_EMPTY}' '''}'''

PORT_REQUIRES = '''{"<class>": "port",
                    "name": "heater",
                    "type_name": {"<class>": "scope_name", "ids": ["IHeaterElement"]},
                    "direction": "requires",
                    "formals": ''' f'{FORMALS_EMPTY}' '''}'''

PORT_REQUIRES_INJECTED = '''{"<class>": "port",
                             "name": "cfg",
                             "type_name": {"<class>": "scope_name", "ids": ["IConfiguration"]},
                             "direction": "requires",
                             "formals": ''' f'{FORMALS_EMPTY}' ''',
                             "injected?": "injected"}'''

PORTS_EMPTY = '''{"<class>": "ports", "elements": []}'''

PORTS_TWO_ITEMS = '''{"<class>": "ports", "elements": [''' \
                  f'{PORT_PROVIDES}, {PORT_REQUIRES}' \
                  ''']}'''

ROOT_WITHOUT_COMMENT = '''{"<class>": "root",
                           "elements": [],
                           "working-directory": "D:"}'''

SCOPE_NAME = '''{"<class>": "scope_name", "ids": ["My"]}'''

SCOPE_NAME_EX = '''{"<class>": "scope_name", "ids": ["My", "Nice", "Type"]}'''

SCOPE_NAME_FAIL = '''{"<class>": "scope_name", "ids": []}'''

SUBINT = '''{"<class>": "subint",
             "name": {"<class>": "scope_name", "ids": ["SmallInt"]},
             "range": ''' f'{RANGE}' '''}'''

TYPES_EMPTY = '''{"<class>": "types", "elements": [] }'''

TYPES_TWO_ITEMS = '''{"<class>": "types", "elements": [''' f'{ENUM}, {SUBINT}' ''']}'''

INTERFACE_EMPTY = '''{"<class>": "interface",
                      "name": {"<class>": "scope_name", "ids": ["IToaster"]},
                      "types":''' f'{TYPES_EMPTY}' ''',
                      "events": ''' f'{EVENTS_EMPTY}' \
                  '''}'''

INTERFACE_TWO_ITEMS = '''{"<class>": "interface",
                          "name": {"<class>": "scope_name", "ids": ["IHeaterElement"]},
                          "types":''' f'{TYPES_TWO_ITEMS}' ''',
                          "events": ''' f'{EVENTS_TWO_ITEMS}' \
                      '''}'''

COMPONENT = '''{"<class>": "component",
                "name": {"<class>": "scope_name", "ids": ["Toaster"]},
                "ports": ''' f'{PORTS_TWO_ITEMS}' \
            '''}'''

FOREIGN = '''{"<class>": "foreign",
             "name": {"<class>": "scope_name", "ids": ["Timer"]},
             "ports": ''' f'{PORTS_TWO_ITEMS}' \
          '''}'''

SYSTEM = '''{"<class>": "system", "name": {"<class>": "scope_name", "ids": ["ToasterSystem"]},
             "ports": ''' f'{PORTS_TWO_ITEMS}' ''',
             "instances": ''' f'{INSTANCES_TWO_ITEMS}' ''',
             "bindings": ''' f'{BINDINGS}' '''}'''

PORT_INJECTED_INDICATION = '''{"<class>": "port", "injected?": "injected"}'''
PORT_INJECTED_INDICATION_ABSENT = '''{"<class>": "port"}'''
PORT_INJECTED_INDICATION_INVALID = '''{"<class>": "port", "injected?": "bogus"}'''

# the following snippet contains an example interface, foreign and an enum in 'global' scope
# while various others dezyne element with fqn identifiers reside in the 'Project' scope:
DZNFILE_EXAMPLE = '''
{"<class>": "root",
 "elements": [''' f'{INTERFACE_EMPTY}, {FOREIGN}, {ENUM}, ' '''
              {"<class>": "namespace",
                "name": {"<class>": "scope_name", "ids": ["Project"]},
                "elements": [''' f'{INTERFACE_TWO_ITEMS}, {COMPONENT}, ' \
                  f'{SYSTEM}, {EXTERN}, {SUBINT}' ''']}
             ],
  "working-directory": "C:"
 }'''
