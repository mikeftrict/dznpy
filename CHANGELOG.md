# Changelog

## Changes in 0.5 (DEV) since 0.4

### Additions and other changes

### Processed tickets

## Changes in 0.4 (20240926) since 0.3

### Breaking changes

- Because of the improved/revamped `NamespaceIds et al` and `scoping` module, this release yields
  breaking changes to existing client scripts. Please update your client script (quite easy btw).

### Processed tickets

- [DZNPY-0020](https://github.com/mikeftrict/dznpy/issues/20): Restructure dznpy modules part 1:
    - Add (graphical) documentation of dznpy's structure. Version 0.3 and projected 0.4.
    - Move namespace related types and functions to new module `scoping`

- [DZNPY-0018](https://github.com/mikeftrict/dznpy/issues/18): Correct typo with regard to '
  provides' vs. 'provided'. And apply the plural() function where needed.

- [DZNPY-0016](https://github.com/mikeftrict/dznpy/issues/16): Add all_sts() preset function.

- [DZNPY-0015](https://github.com/mikeftrict/dznpy/issues/15): Bugfix: AdvShell runtime exception
  when having no required ports. When generating an Advanced Shell on a component (or system) that
  has no required ports at all, the adv_shell module will prematurely end with the
  message `NoneType' object has no attribute 'splitlines`.

- [DZNPY-0009](https://github.com/mikeftrict/dznpy/issues/8): Make namespaceids_t() input argument
  more strict. This has been addressed as part of the DZNPY-0020 restructuring.

## Changes in 0.3 (240415) since 0.2

### Additions and other changes

- `dznpy` now comes with PyCharm IDE project files.
- Five new generate-able C++ support files are introduced with provision: ILog, MiscUtils,
  MetaHelpers, MutexWrapped and MultiClientSelector. They will be used by the Advanced Shell
  Multi-Client feature in the next release 0.4 of dznpy. Most of these support files can also serve
  usefulness for Dezyne (or even just C++) software development in general.

### Processed tickets

- [DZNPY-0012](https://github.com/mikeftrict/dznpy/issues/12): Introduce new C++ support file
  `MultiClientSelector.hh` that will closely collaborate with the upcoming Advanced Shell
  Multi-Client feature.

- [DZNPY-0011](https://github.com/mikeftrict/dznpy/issues/11): Introduce new C++ support files
  `MetaHelpers.hh` and `MutexWrapped.hh` for the upcoming Advanced Shell Multi-Client feature.

- [DZNPY-0010](https://github.com/mikeftrict/dznpy/issues/10): Extend GeneratedContent dataclass
  with contents hash. Useful for caching situations.

- [DZNPY-0008](https://github.com/mikeftrict/dznpy/issues/9): Introduce new C++ support
  files `ILog.hh` and `MiscUtils.hh`. The upcoming Advanced Shell Multi-Client feature requires
  these support files. Since they are so generic they can obviously be reused for other types of
  software development activities (Dezyne and vanilla C++ software).

- [DZNPY-0007](https://github.com/mikeftrict/dznpy/issues/7): Move support files to an own (sub)
  package. This ticket will move the code generation of `Dzn_StrictPort.hh` to a dedicated
  package `support_files/strict_port.py`. More support files will be introduced in next tickets that
  will all be placed in this same location.

- [DZNPY-0006](https://github.com/mikeftrict/dznpy/issues/6): Robust GenerateDezyneArtifacts.cmd to
  relative dzn.cmd paths.

- [DZNPY-0005](https://github.com/mikeftrict/dznpy/issues/5): When using PyCharm as IDE, one has
  to (manually) Mark Directory `src` as Sources Root and `test` as Test Sources Root. These settings
  are actually stored in `.idea/dznpy.iml`. This change request adds this project file (and a few
  others) to the archive for developer IDE convenience.

- [DZNPY-0004](https://github.com/mikeftrict/dznpy/issues/4): Until now,
  `unit_tests/adv_shell/test_builder.py` and `unit_tests/test_json_ast.py` had their local resolve()
  helper to determine the absolute filepath of their required Dezyne test files; reasoned from _
  _file__. This logic shall be generalized with extra checks and reporting on the presence of the
  test data folder and subsequently the requested 'dezyne test model filename'.

- [DZNPY-0003](https://github.com/mikeftrict/dznpy/issues/3): Until now, each python artifact had
  the current version of dznpy mentioned in the file header. This is considered redundant. The
  single place where the version number is defined, resides in `dznpy/dznpy_version.py`.

## Changes in 0.2 (240304) since 0.1

### Breaking changes

- As of now, the generated output of Advanced Shell uses the new strict port typing addition. User
  code has to be adapted to this new situation

### Major additions

- **Strict port typing**: The return type of the accessors in an advanced shell indicate
  `Sts<PortType>` or `Mts<PortType>` to enforce correct bindings to
  a peer. This is to prevent that Single-Threaded Runtime Semantics (STS)
  is mistakenly mixed with Multi-Threaded Runtime Semantics (MTS).
  By this explicit typing (a templated wrapper struct), the compiler will
  give errors on developer mistakes.
  Support file (`Dzn_StrictPort.hh`) is generated to provide the necessary header file
  with this wrapper. The namespace (always at least 'Dzn') can be further prefixed via
  the configuration option `support_files_ns_prefix`.

### Additions and other changes

- `misc_utils.py`: addition of the function `plural(singular_noun, ref_collection)` to make
  a singular noun -> plural depending on whether the referenced collection has multiple items.
- `cpp_gen.py`: System- and ProjectIncludes dataclasses now prepend the generated C++ code
  with a comment line such as `// System includes`. Uses the new `misc_utils.plural()`
  helper function produce '... include' or '... includes'.
- `adv_shell.py`: Split up the single big python module into smaller modules, to start with.
  Later releases will further 'cleanse' the structure as it is expected more functionality
  will be added to the advanced shell.

### Solved issues

- adv_shell: `injected` required ports were not excluded from dispatching. This has been
  observed when creating an advanced shell for an implementation component. Fixed now.

### Miscellaneous

- Corrected various docstrings

## 0.1 (240108 - Initial draft)

* The initial draft release of the open source python modules for Dezyne development.
    - `cpp_gen.py`: simple c++ code generator (MVC pattern inspired)
    - `adv_shell.py`: advanced shell generation (uses cpp_gen and ast*)
    - `ast.py`: Dezyne abstract syntax tree elements as python dataclasses
    - `ast_view.py`: Helpers to view and search the Dezyne abstract syntax tree
    - `json_ast.py`: Import Dezyne JSON AST output into Python ast(.py)
    - `misc_utils.py`: Reusable miscelleneous utilities, classes and functions
