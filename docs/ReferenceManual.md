# Reference manual

This document is the entry point for software developers to learn/lookup the usage of this **dznpy**
Python package.

## Software requirements

The software requirements for developing and running the **dznpy** package is not complicated at
all. It minimally requires Python version 3.8 and commonly known dependent packages are specified
in [requirements.txt](https://github.com/mikeftrict/dznpy/blob/main/requirements.txt).

## Modules

### Dezyne grammar

* [ast - Dezyne Abstract Syntax Tree](Modules/ast.md)
* [ast_view - Dezyne AST View](Modules/ast_view.md)
* [json_ast - Dezyne AST JSON Parser](Modules/json_ast.md)

### Text and code generation

* [code_gen_common - Code generation (Common)](Modules/code_gen_common.md)
* [cpp_gen - Code generation (C++)](Modules/cpp_gen.md)

### Common

* [misc_utils - Miscellaneous Utilities](Modules/misc_utils.md)
* [scoping - Scoping (Namespace Constructs)](Modules/scoping.md)

### Support files generation (C++)

* [ilog - Logging Interface](Modules/SupportFiles/ilog.md)
* [meta_helpers - Dezyne Meta helpers](Modules/SupportFiles/meta_helpers.md)
* [misc_utils - Miscellaneous Utilities](Modules/SupportFiles/misc_utils.md)
* [multi_client_selector - Multi Client Selector](Modules/SupportFiles/multi_client_selector.md)
* [mutex_wrapped - Mutex Wrapped](Modules/SupportFiles/mutex_wrapped.md)
* [strict_port - Dezyne Strict Port typing](Modules/SupportFiles/strict_port.md)

### Advanced Shell (C++)

* [adv_shell - Advanced Shell Code generation (C++)](Modules/AdvShell/adv_shell.md)
