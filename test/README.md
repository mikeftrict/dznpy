ø# Test

Folder containing unit tests, test data, dezyne models and a VS2022 C++ ToasterTest project (GoogleTest).

## Unit Tests

Before running the unit tests ensure that all test data is present and dezyne models have been processed with
the following commands. Note: the scripts need to be run -in- the test directory:

    cd C:\SB\dznpy\test\

    python process_dezyne_models.py

On errors, inspect the output closely. Most common finding is that you have unpacked dezyne (dzn.cmd) somewhere
else on your system than the default location. Modify the Python script to match your location of `dzn.cmd`.
On rare cases Dezyne reports errors on the models; either they have been altered manually (with errors) or
a complete different version (than 2.17.9) of Dezyne is used. The models should process fine with 2.17.9 and later.
If not, please contact me with your findings.

After this initial step, trigger the unit tests by running **pytest** in the test folder. It will detect
the `pytest.ini` file for the appropriate test configuration to use. Assuming you unpacked `dznpy` to the path `C:\SB\`,
example output will look like:

    cd C:\SB\dznpy\test\

    python -m pytest

    ==================== test session starts ====================
    platform win32 -- Python 3.8.1, pytest-8.1.1, pluggy-1.4.0
    rootdir: C:\SB\dznpy\test
    configfile: pytest.ini
    collected 234 items
    
    unit_tests\test_adv_shell.py ......................... [ 10%]
    unit_tests\test_ast_view.py .......................... [ 17%]
    unit_tests\test_cpp_gen.py ........................... [ 29%]
    unit_tests\test_json_ast.py .......................... [ 58%]
    unit_tests\test_misc_utils.py ........................ [100%]
    
    ==================== 234 passed in 0.34s ====================

To measure code coverage during unittesting, issue the command shown below. Besides the standard py.test output
it will also print code coverage percentages per source file.

    cd C:\SB\dznpy\test\
    python -m pytest --cov=dznpy

    ________________ coverage: platform win32, python 3.10.0-final-0 _________________
    
    Name                                                           Stmts   Miss  Cover
    ----------------------------------------------------------------------------------
    C:\SB\dznpy\src\dznpy\__init__.py                                  0      0   100%
    C:\SB\dznpy\src\dznpy\adv_shell\__init__.py                      100      0   100%
    C:\SB\dznpy\src\dznpy\ ...etc...
           ...etc...       ...etc...
    ----------------------------------------------------------------------------------
    TOTAL                                                           2250     42    98%

To explore the source files and to discover the missed statements, generate a HTML report like following:

    cd C:\SB\dznpy\test\
    python -m coverage html
    
    Wrote HTML report to htmlcov\index.html


## VS2022 Example C++ GoogleTest project

To build and run the Visual Studio 2022 example c++ GoogleTest project, first GoogleTest and GoogleMock C++ source
and header files need to be fetched. This has been automated with running the following script from the 'test' folder:

    python fetch_google_libs.py

After successful retrieval, open the ToasterTest.sln VS2022 solution to build and run the contained project.
As part of this project an example generated GoogleMock of the IPowerCord Dezyne interface is included.
This model is taken as example in the python-as-documentation file: `dznpy/docs/Examples/dezyne_mock_example.py`.
