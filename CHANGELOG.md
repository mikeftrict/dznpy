# Changelog

## Changes in 1.0 (DEV) since 0.5

This is the official first release that is considered stable.

### Breaking changes

- `TextBlock` et al has been moved to the module `text_gen`. Impact is minimal: only update your
  import statements.
- `CommentBlock` has been renamed to `Comment`. Impact is minimal since one can just find and
  replace.

### Noteworthy additions and changes

- [DZNPY-0029](https://github.com/mikeftrict/dznpy/issues/29): Generate explicit constructor port
  initialization to be closer with the 2.18/2.19 code generation.
    - Also, the `CommentBlock` class is renamed to `Comment` (replacing the old one). It uses the
      the new TextBlock features.
    - Solved a bunch of PyLint issues.
- [DZNPY-0028](https://github.com/mikeftrict/dznpy/issues/28): Moved `TextBlock` and its cohesively
  related constructs to a (new) module `text_gen`. Also integrate bullet list numbering
  functionality into `TextBlock` itself as part of indentation. Lastly, it adds a header content
  feature to preamble a textblock, without have it affected by indention and/or list bullet-ing.
  Refer to the unit tests for examples.
- The (data) class architecture diagrams of each previous dznpy version have been converged into a
  single Visio document.

### Other processed tickets

## Changes in 0.5 (20241126) since 0.4

### Breaking changes

- In `port_selection.py` renamed the type `PortCfg` to `PortsCfg` to better reflect its actual
  cardinality. The impact is a simple matter of search and replace.
- In `cpp_gen.py` corrected the first parameter type to `Fqn` (instead of `NamespaceIds`) of helper
  functions: `param_t()`, `const_param_ref_t()`, `const_param_ptr_t()`. The impact depends on usage
  of these helper functions and reported back by the Python compiler.

### Noteworthy additions and changes

- [DZNPY-0024](https://github.com/mikeftrict/dznpy/issues/24): Add the MultiClientSelector port
  feature to Advanced Shell code generation. By configuring `PortsCfg` with the new dataclass
  member `multiclient` with an instance of `MultiClientPortCfg`. The developer can designate a
  maximum of **1** provides **MTS** port for multiclient-out-event-selector usage. For now refer to
  the `test_generate_multiclient_selector()` (in `test_builder.py`), together with
  studying the `ExclusiveToaster.dzn` component to learn the required modelling semantics that are
  **mandatory** to let the MultiClientSelector facility to function correctly.
- Extended `code_gen_common.py` with `chunk()` and `cond_chunk()`
- Extended `misc_utils.py` with:
    - new `Indentizer` class to cohesively house indentation logic;
    - new `ListBulletizer` class to prefix a user customizable _bullet_ to each line of a textblock;
      or alternatively only the first line of a textblock;
    - updated `TextBlock` class to use the new `Indentizer` and `ListBulletizer` classes.

### Processed tickets

- [DZNPY-0025](https://github.com/mikeftrict/dznpy/issues/25): Extend example models with
  a Claim-Release example. As a preparation to the MultiClientSelector feature.

- [DZNPY-0023](https://github.com/mikeftrict/dznpy/issues/23): Resolve a round of pylint and flake8
  feedback on the `src` folder. A notable 'correction' was the leaking of `FacilitiesOrigin` through
  a module by an import, but it did not use it. The correct way to import it is from
  the `dznpy.adv_shell.common` module.

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
