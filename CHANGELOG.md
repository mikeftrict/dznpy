# Changelog

## Changes in 1.3 (DEV) since 1.2

### Noteworthy additions and changes

- [DZNPY-0047](https://github.com/mikeftrict/dznpy/issues/62): Fix bug that indicate types-only Dezyne file would be not
  generatable. This was incorrect.
- [DZNPY-0046](https://github.com/mikeftrict/dznpy/issues/58): Fix support of pre-2.17.0 int AST type.
- [DZNPY-0045](https://github.com/mikeftrict/dznpy/issues/56): Correct testdata for ToasterTest example. With the
  addition of the `unpack_test_data.py` script in the `test` folder it appeared to miss some Dezyne generated files that
  are required by the ToasterTest example project.

## Changes in 1.2 (20251019) since 1.1

### Noteworthy additions and changes

- [DZNPY-0041](https://github.com/mikeftrict/dznpy/issues/46):
    - In `json_ast` refactor the function parse_element(..) according to pylint's complexity indication
    - In `json_ast` rename 'element' to more conventional AST naming 'node' where applicable
    - Solve various minor pylint reported issues
- [DZNPY-0040](https://github.com/mikeftrict/dznpy/issues/41): Changes to `ast` and `json_ast` parser to basically
  support all Dezyne versions starting from 2.11 to 2.19.
- [DZNPY-0039](https://github.com/mikeftrict/dznpy/issues/40):
    - Introduces the RuleOfFive class and related constructors in a new designated `cpp_gen_rule_of_five` module.
    - Extended `cpp_gen.Struct` (and Class) to associate with parent(s), a namespace and a constructor. These constructs
      are required when generating C++ code that involves inheritance and calling the base class constructor in the C++
      definition.
    - Extended `cpp_gen.Namespace` with the option global_namespace_on_empty_ns_ids to specify a true global namespace.
      Fixed the previous strategy to **unnamed** namespace. This can be a minor breaking change for existing code bases.
    - Extended `cpp_gen.AccessSpecifier` with the function str_without_colon().
    - Expanded the code coverage of the project by adding more unit tests.
    - Bumped reference Dezyne 2.17.8 to **2.17.9**.
- [DZNPY-0037](https://github.com/mikeftrict/dznpy/issues/37): Add wheel packaging and push to PyPi.
- [DZNPY-0036](https://github.com/mikeftrict/dznpy/issues/36): Extend `ast_cpp_view.create_member_function()` with the
  keyword override.
- [DZNPY-0035](https://github.com/mikeftrict/dznpy/issues/35): Mitigate empty line below private section in Advanced
  shell headerfile.
- [DZNPY-0014](https://github.com/mikeftrict/dznpy/issues/14):
    - Introduce a Dezyne versioning feature in `dznpy.dzn_exe` to contain, test and compare a version indication with
      the format major.minor.revision.dev-tag (eg 2.17.9.dev-tag).
    - New supporting type `DznFileModelsList` and an associated type creation function is introduced to interpret the
      `dzn parse -l` output which lists the models that are inside a Dezyne file.
    - Module `misc_utils` is extended with the context manager `raii_cd` to change the directory and return safely and
      automatically when exiting the context.

## Changes in 1.1 (20250602) since 1.0

### Breaking changes

- Python 3.10 will be the version required as of now to allow usage of newer features since 3.8.
- In cpp_gen: `Function`, `Constructor` and `Destructor` have been revisited. They inherit from a shared base class to
  reduce redundancy and follow linting feedback. The formerly provided attributes `as_decl` and `as_def` have now been
  replaced with true functions with similar names. Also, they return `TextBlock`.

### Noteworthy additions and changes

- In `requirements.txt` added 3 dependencies on `pylint` and `flake` (intentionally selected versions that are a bit
  more naggy to match the industry). And `pytest-cov` for measuring code coverage.
- Added a documentation how to run and inspect python `code coverage` together with the unit tests of dznpy. Initially
  revealed is that the current code coverage scores reasonable. But it also indicates room for code coverage
  improvements in the near future.
- New module `ast_cpp_view`: that provides helper functions to work on the Dezyne AST and produce results targeted at
  C++ source code generation.
- Extended module `ast_view`: with handy getters for Dezyne events and Interface name. More helpers will be added in the
  future to make dznpy-user-code more simple and straightforward (to read and maintain). Mainly what is being observed
  right now is that a dznpy-user-developer has to deep dive into the AST. Ofcourse he/she has this liberty, but common
  tasks need no reinvention.
- Extended `TextBlock` in `text_gen`: with a `chunk_spacing` in which added content is automatically being preambled by
  spacing. An EOL by default and configurable. This is often used when producing chunks of C++ code where it is desired
  to have some white spacing in between for readability.
- New type `TypeAsIs` in `cpp_gen`: used in conjunction with `ast_cpp_view` helpers where types are expanded to C++
  namespacing where the developer wants to use it with `cpp_gen` constructs.
- Fixed a bug in `cpp_gen` class `Comment`, where it would lose the `indentor` when passing it around as `TextBlock`.
- In `cpp_gen` at the `Function` type, added te optional parameter `imf` (=inline member function) to the `as_def()`
  function meaning it produces C++ definition code that is meant to be included directly in a struct or class
  declaration. See the GoogleMock code generation example where it only concerns a C++ header file (with 'all code').
- Added two helper in `misc_utils`: `assert_union_t` and `assert_union_t_optional`
- Added an example C++ Unit test project `ToasterTest` for VS2022 in combination with GoogleTest/Mock. Note: first the
  new script `fetch_google_libs.py` must be run before building the C++ project.
- Replaced the `GenerateDezyneArtifacts.cmd` Windows shell script with a python script `process_dezyne_models.py` to
  improve maintainability, future expansions and to allow for multicore processing of the files.
- Added documentation in `docs/Examples/cpp_gen_examples.py` to explain and show by programming example houw the
  `cpp_gen` module is to be used.
- Added a how-to-use-dznpy example in `docs/Examples/dezyne_mock_example.py` to explain and show how to generate a C++
  GoogleMock from a Dezyne interface. The output is even being used in the ToasterTest Unit test project.
- Enriched various example Dezyne models a bit with more parameters and types being used. This is meant for the
  `ToasterTest` C++ project. And to show how to generate a GoogleMock from a Dezyne interface where it is interesting to
  see how to handle and forward event parameters.

## Changes in 1.0 (20241208) since 0.5

This is the official first release that is considered stable.

### Breaking changes

- `TextBlock` et al has been moved to the module `text_gen`. Impact is minimal: only update your
  import statements.
- `CommentBlock` has been renamed to `Comment`. Impact is minimal since one can just find and
  replace.

### Noteworthy additions and changes

- [DZNPY-0032](https://github.com/mikeftrict/dznpy/issues/32): documentation and improvements pack:
    - Update `text_gen` module with absorbing the remainder of `code_gen_common`.
    - Complete `cpp_gen` with decent docstrings.
    - Add `trim()` to `TextBlock` to trim (beginning and) ending empty lines from the buffer.
    - Handled a few (unnecessary) flake8 warnings about line length of support files generated code
      templates.
    - Completed the `test_builder` unit tests to also cover the output of `all_sts()`.

- [DZNPY-0030](https://github.com/mikeftrict/dznpy/issues/30): In Advanced Shell generate std::ref
  port functors instead of copying entire ports for MTS ports. The old mechanism 'worked' for Dezyne
  versions until and including 2.17. But for 2.18+ not. With std-reffing each in-event, as what
  Dezyne does, it is ensured that this particular code is compatible with all Dezyne versions (
  including 2.18) so far.
    - Also added in this issue/merge-request is a DummyToaster and DummyExclusiveToaster
      implementation model that comes with an Advanced Shell with only 1 provides port and (because
      it is a stub) no requires ports.

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
