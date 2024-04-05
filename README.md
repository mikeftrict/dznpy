# dznpy

Python modules to support in developing software with [Dezyne](https://dezyne.org/).

## Installation

In general, check out latest master and cherrypick anything you desire that improves your software development life with Dezyne.
All material is available under MIT license so feel free to use/copy it. Suggestions, improvements, fixes et al are all welcome.

First of all have Dezyne installed on your system by browsing to https://download.verum.com/download/verum-dezyne/ and
download `verum-dezyne-2.17.8-x86_64-windows.zip` or the `*.msi` version. When unpacking the `*.zip`, ensure to use an
unzipper that preserves all timestamps, for instance `7Zip` suffices. But do **not** use the Windows builtin unzipper.

By default, the tests and data preparation scripts have been configured to an installation path having dzn.cmd here:

    C:\SB\dezyne-2.17.8\dzn.cmd

Of course this installation path can be suited to your situation. Edit and correct the following script(s):

    - test\GenerateDezyneArtifacts.cmd

Then, install the required Python packages `dznpy` relies on. PyCharm will automatically recognise and process the requirements.txt file.
In other cases, install the dependencies manually by typing 

    pip install -r requirements.txt

## Usage

Refer to the respective modules, their readme files and unit tests to understand the mechanics and usage.

