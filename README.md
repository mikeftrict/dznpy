# dznpy

Python modules to support in developing C++ software with [Dezyne](https://dezyne.org/). Mainly, parse Dezyne files into
an Abstract Syntax Tree from which the developer-user of dznpy can 'walk' through with Python helpers. For instance to
generate custom C++ thread-safe shell code (aka Advanced Shell as included) and another example is to generate a
C++17 GoogleMock from a Dezyne interface (example included).

## Installation

In general, check out latest master and cherrypick anything you desire that improves your software development life with
Dezyne.
All material is available under MIT license so feel free to use/copy it. Suggestions, improvements, fixes et al are all
welcome.

First of all have Dezyne installed on your system by browsing to https://download.verum.com/download/verum-dezyne/ and
download `verum-dezyne-2.17.8-x86_64-windows.zip` or the `*.msi` version. When unpacking the `*.zip`, ensure to use an
unzipper that preserves all timestamps, for instance `7Zip` suffices. But do **not** use the Windows builtin unzipper.

By default, the tests and data preparation scripts have been configured to an installation path having dzn.cmd here:

    C:\SB\dezyne-2.17.8\dzn.cmd

Of course this installation path can be suited to your situation. In that case edit/configure the script
`test\process_dezyne_models.py`. Run it at least once after downloading dznpy from GitHub in order for the unit tests
to be able to find their testdata et al. Running the tests is highly recommended before starting to use dznpy. Don't
forget to read test/README.md.

Lastly, install the required Python packages `dznpy` relies on. PyCharm will automatically recognise and process the
requirements.txt file. In other cases, install the dependencies manually by typing

    pip install -r requirements.txt

## Usage

User documentation is something which is in progress. Refer to `docs/Examples/` for explanation by example. Furthermore
refer to the respective modules, their readme files and unit tests to understand the mechanics and usage.
