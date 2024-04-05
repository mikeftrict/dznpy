# Changelog

## Changes in 0.2 (240304) since 0.1

* Major changes/additions:
    - **Strict port typing**: The return type of the accessors in an advanced shell indicate
      `Sts<PortType>` or `Mts<PortType>` to enforce correct bindings to
      a peer. This is to prevent that Single-Threaded Runtime Semantics (STS)
      is mistakenly mixed with Multi-Threaded Runtime Semantics (MTS).
      By this explicit typing (a templated wrapper struct), the compiler will
      give errors on developer mistakes.
      Support file (`Dzn_StrictPort.hh`) is generated to provide the necessary header file
      with this wrapper. The namespace (always at least 'Dzn') can be further prefixed via
      the configuration option `support_files_ns_prefix`.

* Other changes/additions:
    - `misc_utils.py`: addition of the function `plural(singular_noun, ref_collection)` to make
      a singular noun -> plural depending on whether the referenced collection has multiple items.
    - `cpp_gen.py`: System- and ProjectIncludes dataclasses now prepend the generated C++ code
      with a comment line such as `// System includes`. Uses the new `misc_utils.plural()`
      helper function produce '... include' or '... includes'.
    - `adv_shell.py`: Split up the single big python module into smaller modules, to start with.
      Later releases will further 'cleanse' the structure as it is expected more functionality
      will be added to the advanced shell.

* Solved issues
    - adv_shell: `injected` required ports were not excluded from dispatching. This has been
      observed when creating an advanced shell for an implementation component. Fixed now.
* Misc
    - Corrected various docstrings

## 0.1 (240108 - Initial draft)

* The initial draft release of the open source python modules for Dezyne development.
    - `cpp_gen.py`: simple c++ code generator (MVC pattern inspired)
    - `adv_shell.py`: advanced shell generation (uses cpp_gen and ast*)
    - `ast.py`: Dezyne abstract syntax tree elements as python dataclasses
    - `ast_view.py`: Helpers to view and search the Dezyne abstract syntax tree
    - `json_ast.py`: Import Dezyne JSON AST output into Python ast(.py)
    - `misc_utils.py`: Reusable miscelleneous utilities, classes and functions
